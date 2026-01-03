"""
Moduł do zarządzania flotą pojazdów w symulacji.
"""

import random
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

        self.vehicles.append(vehicle)
        controller = VehicleController(vehicle, self.network, self.monitor)
        self.controllers.append(controller)
        
        # Wylosuj cel
        destination = self._get_random_destination(vehicle.current_intersection)
        if destination:
            controller.set_destination(destination)
        
        return controller
    
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
