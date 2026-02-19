"""
Moduł do zarządzania flotą pojazdów w symulacji.
"""

import random
import math
from typing import List, Callable, Optional
from vehicle import Vehicle, VehicleController, VehicleState
from graph import RoadNetwork, Intersection
from typing import Optional
try:
    from traffic_monitor import TrafficMonitor
except Exception:
    TrafficMonitor = None


class VehicleSpawner:
    """Generuje nowe pojazdy w losowych odstępach czasu."""
    
    def __init__(self,
                 spawn_intersection: Intersection,
                 network: RoadNetwork,
                 spawn_rate: float = 0.25,
                 speed_min: float = 30.0,
                 speed_max: float = 80.0):
        """
        Inicjalizuje generator pojazdów.
        
        Args:
            spawn_intersection: Skrzyżowanie, gdzie pojawiają się pojazdy
            network: Sieć drogowa
            spawn_rate: Średnia liczba pojazdów na sekundę (λ)
            speed_min: Minimalna prędkość pojazdu (km/h)
            speed_max: Maksymalna prędkość pojazdu (km/h)
        """
        self.spawn_intersection = spawn_intersection
        self.network = network
        self.spawn_rate = spawn_rate
        self.speed_min = speed_min
        self.speed_max = speed_max
        
        self.time_since_last_spawn = 0.0
        self.next_spawn_interval = self._next_interval()
        # Lokalny licznik ID nie jest używany — ID nadawane globalnie w flocie
        self.vehicle_id_counter = 0

    def _next_interval(self) -> float:
        """Generuj interwał czasu między zdarzeniami (rozkład wykładniczy).

        Interwały w procesie Poissona są niezależne i mają rozkład
        wykładniczy z parametrem λ (spawn_rate), gdzie E[T] = 1/λ.
        """
        if self.spawn_rate <= 0:
            return float("inf")

        return random.expovariate(self.spawn_rate)
    
    def _get_random_destination(self) -> Optional[Intersection]:
        """
        Wybiera losowe skrzyżowanie jako cel.
        Unika spawnu jako celu (jeśli sieć ma więcej niż 1 skrzyżowanie).
        Wybiera tylko skrzyżowania które mogą być celami (is_destination=True).
        """
        all_intersections = self.network.get_all_intersections()
        
        if len(all_intersections) <= 1:
            return None
        
        # Wybierz losowe, ale nie spawn_intersection i tylko te które mogą być celami
        available = [i for i in all_intersections 
                    if i.id != self.spawn_intersection.id and i.is_destination]
        return random.choice(available) if available else None
    
    def update(self, delta_time: float) -> Optional[Vehicle]:
        """
        Aktualizuje timer spawnu i zwraca nowy pojazd jeśli należy go stworzyć.
        
        Args:
            delta_time: Czas upłynięty od ostatniej aktualizacji (sekundy)
        
        Returns:
            Nowy pojazd lub None jeśli nie należy spawować
        """
        self.time_since_last_spawn += delta_time
        
        if self.time_since_last_spawn >= self.next_spawn_interval:
            # Zachowaj nadmiar czasu (overshoot), aby nie zafałszować tempa
            # kolejnych spawnow. Resetowanie do 0.0 powoduje systematyczne
            # zaniżanie odstępów i zaburza średni rate.
            self.time_since_last_spawn -= self.next_spawn_interval
            self.next_spawn_interval = self._next_interval()
            
            # Utwórz nowy pojazd
            speed = random.uniform(self.speed_min, self.speed_max)
            # ID zostanie nadane globalnie przez flotę, użyj placeholdera
            vehicle = Vehicle(
                id=-1,
                current_intersection=self.spawn_intersection,
                speed=speed
            )
            
            return vehicle
        
        return None


class VehicleFleet:
    """Zarządza flotą pojazdów w symulacji."""
    
    def __init__(self, network: RoadNetwork):
        """
        Inicjalizuje flotę.
        
        Args:
            network: Sieć drogowa
        """
        self.network = network
        self.vehicles: List[Vehicle] = []
        self.controllers: List[VehicleController] = []
        self.spawners: List[VehicleSpawner] = []
        self._vehicle_id_counter: int = 0
        self.monitor: Optional[TrafficMonitor] = None
        self._sim_time: float = 0.0
        self._spawn_times: dict[int, float] = {}
        self._completed_trips_count: int = 0
        self._total_travel_time: float = 0.0
        self._total_red_light_wait_time: float = 0.0
        self._queue_length_time_integral: float = 0.0
        self._queue_length_measurement_time: float = 0.0

    def set_monitor(self, monitor: TrafficMonitor):
        """Ustawia monitor przepustowości dla floty."""
        self.monitor = monitor
    
    def add_spawner(self,
                    spawn_intersection: Intersection,
                    spawn_rate: float = 0.25,
                    speed_min: float = 30.0,
                    speed_max: float = 80.0) -> VehicleSpawner:
        """
        Dodaje generator pojazdów.
        
        Args:
            spawn_intersection: Skrzyżowanie spawnu
            spawn_rate: Średnia liczba pojazdów na sekundę (λ)
            speed_min: Minimalna prędkość (km/h)
            speed_max: Maksymalna prędkość (km/h)
        
        Returns:
            Utworzony spawner
        """
        spawner = VehicleSpawner(
            spawn_intersection=spawn_intersection,
            network=self.network,
            spawn_rate=spawn_rate,
            speed_min=speed_min,
            speed_max=speed_max
        )
        self.spawners.append(spawner)
        return spawner
    
    def update(self, delta_time: float):
        """
        Aktualizuje flotę.
        - Generuje nowe pojazdy
        - Aktualizuje istniejące pojazdy
        - Usuwa pojazdy które dotarły do celu
        
        Args:
            delta_time: Czas upłynięty (sekundy)
        """
        if delta_time > 0:
            self._sim_time += delta_time

        # Zaktualizuj czas monitora zanim nastąpią zdarzenia przejazdów
        if self.monitor:
            self.monitor.update(delta_time)
        # Spawn nowych pojazdów
        for spawner in self.spawners:
            new_vehicle = spawner.update(delta_time)
            if new_vehicle:
                self.add_vehicle(new_vehicle)
        
        # Zaktualizuj listę innych pojazdów dla każdego kontrolera
        for controller in self.controllers:
            controller.other_vehicles = self.vehicles
        
        # Aktualizuj istniejące pojazdy
        for controller in self.controllers:
            controller.update(delta_time)
        
        # Usuń pojazdy które dotarły do celu
        vehicles_to_remove = []
        for i, vehicle in enumerate(self.vehicles):
            if vehicle.state == VehicleState.ARRIVED:
                vehicles_to_remove.append(i)
        
        # Usuń od konca aby nie zniszczyć indeksów
        for i in reversed(vehicles_to_remove):
            removed_vehicle = self.vehicles.pop(i)
            self.controllers.pop(i)
            start_time = self._spawn_times.pop(removed_vehicle.id, None)
            if start_time is not None:
                travel_time = max(0.0, self._sim_time - start_time)
                self._completed_trips_count += 1
                self._total_travel_time += travel_time
                self._total_red_light_wait_time += max(0.0, removed_vehicle.red_light_wait_time)

        # Aktualizuj średnią czasową długość kolejki na czerwonym świetle.
        if delta_time > 0:
            current_queue_length = sum(1 for vehicle in self.vehicles if vehicle.is_waiting_at_red_light)
            self._queue_length_time_integral += current_queue_length * delta_time
            self._queue_length_measurement_time += delta_time
    
    def add_vehicle(self, vehicle: Vehicle) -> VehicleController:
        """
        Dodaje pojazd do floty.
        
        Args:
            vehicle: Pojazd do dodania
        
        Returns:
            Kontroler pojazdu
        """
        # Nadaj globalnie unikalne ID
        vehicle.id = self._vehicle_id_counter
        self._vehicle_id_counter += 1
        self._spawn_times[vehicle.id] = self._sim_time

        self.vehicles.append(vehicle)
        controller = VehicleController(vehicle, self.network, self.monitor)
        self.controllers.append(controller)
        
        # Wylosuj cel
        destination = self._get_random_destination(vehicle.current_intersection)
        if destination:
            controller.set_destination(destination)
        
        return controller

    def get_average_travel_time(self) -> float:
        """Zwraca średni czas przejazdu (sekundy) dla zakończonych przejazdów."""
        if self._completed_trips_count == 0:
            return 0.0
        return self._total_travel_time / self._completed_trips_count

    def get_completed_trips_count(self) -> int:
        """Zwraca liczbę pojazdów, które ukończyły przejazd."""
        return self._completed_trips_count

    def get_average_red_light_wait_time(self) -> float:
        """Zwraca średni czas stania na światłach (sekundy) dla zakończonych przejazdów."""
        if self._completed_trips_count == 0:
            return 0.0
        return self._total_red_light_wait_time / self._completed_trips_count

    def get_average_queue_length_at_lights(self) -> float:
        """Zwraca średnią długość kolejki na światłach (liczba pojazdów)."""
        if self._queue_length_measurement_time <= 0:
            return 0.0
        return self._queue_length_time_integral / self._queue_length_measurement_time

    def get_average_speed(self) -> float:
        """Zwraca średnią prędkość aktywnych pojazdów (km/h)."""
        if not self.vehicles:
            return 0.0
        return sum(vehicle.speed for vehicle in self.vehicles) / len(self.vehicles)

    def get_speed_percentile(self, percentile: float) -> float:
        """Zwraca percentyl prędkości aktywnych pojazdów (km/h)."""
        if not self.vehicles:
            return 0.0

        p = min(1.0, max(0.0, percentile))
        speeds = sorted(vehicle.speed for vehicle in self.vehicles)
        rank = max(0, math.ceil(p * len(speeds)) - 1)
        return speeds[rank]
    
    def _get_random_destination(self, exclude_intersection: Intersection) -> Optional[Intersection]:
        """
        Wybiera losowy cel, unikając danego skrzyżowania.
        Wybiera tylko skrzyżowania które mogą być celami (is_destination=True).
        """
        all_intersections = self.network.get_all_intersections()
        available = [i for i in all_intersections 
                    if i.id != exclude_intersection.id and i.is_destination]
        return random.choice(available) if available else None
    
    def get_vehicles(self) -> List[Vehicle]:
        """Zwraca listę wszystkich aktywnych pojazdów."""
        return self.vehicles.copy()
    
    def num_vehicles(self) -> int:
        """Zwraca liczbę aktywnych pojazdów."""
        return len(self.vehicles)
