"""
Moduł do reprezentacji samochodów i ich nawigacji w sieci drogowej.
"""

from typing import List, Optional, Deque
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
import math

from graph import RoadNetwork, Intersection, Road


class VehicleState(Enum):
    """Stany pojazdu."""
    IDLE = "idle"                    # Stoi na miejscu
    DRIVING = "driving"              # Jedzie
    ARRIVED = "arrived"              # Dotarł do celu


@dataclass
class Vehicle:
    """Reprezentuje samochód w sieci."""
    
    id: int
    current_intersection: Intersection
    speed: float = 50.0  # km/h
    state: VehicleState = VehicleState.IDLE
    
    # Nawigacja
    destination: Optional[Intersection] = None
    path: List[Intersection] = field(default_factory=list)  # Ścieżka do celu
    current_path_index: int = 0  # Aktualny indeks w ścieżce
    
    # Pozycja na drodze
    progress_on_road: float = 0.0  # Procent drogi (0.0 - 1.0)
    current_road: Optional[Road] = None  # Aktualna droga
    
    def __repr__(self) -> str:
        return (f"Vehicle(id={self.id}, "
                f"pos={self.current_intersection.name}, "
                f"state={self.state.value}, "
                f"dest={self.destination.name if self.destination else 'None'})")
    
    def get_current_position(self) -> tuple[float, float]:
        """Zwraca aktualną pozycję pojazdu (interpolacja między wierzchołkami)."""
        if self.current_road is None or self.progress_on_road <= 0.0:
            return self.current_intersection.x, self.current_intersection.y
        
        # Interpoluj pozycję między start a end drogi
        x1 = self.current_road.from_intersection.x
        y1 = self.current_road.from_intersection.y
        x2 = self.current_road.to_intersection.x
        y2 = self.current_road.to_intersection.y
        
        # Ogranicz postęp do [0, 1]
        progress = min(1.0, max(0.0, self.progress_on_road))
        
        x = x1 + (x2 - x1) * progress
        y = y1 + (y2 - y1) * progress
        
        return x, y
    
    def has_reached_destination(self) -> bool:
        """Sprawdza czy pojazd dotarł do celu."""
        return (self.state == VehicleState.ARRIVED and 
                self.current_intersection == self.destination)


class PathFinder:
    """Klasa do wyszukiwania ścieżek w sieci drogowej."""
    
    @staticmethod
    def find_shortest_path(network: RoadNetwork,
                           start: Intersection,
                           end: Intersection) -> List[Intersection]:
        """
        Znajduje najkrótszą ścieżkę między dwoma skrzyżowaniami (BFS).
        
        Args:
            network: Sieć drogowa
            start: Skrzyżowanie początkowe
            end: Skrzyżowanie docelowe
        
        Returns:
            Lista skrzyżowań reprezentujących ścieżkę
        """
        if start == end:
            return [start]
        
        queue: Deque = deque([(start, [start])])
        visited = {start.id}
        
        while queue:
            current, path = queue.popleft()
            
            # Sprawdź sąsiadów
            for road in network.get_outgoing_roads(current.id):
                neighbor = road.to_intersection
                
                if neighbor.id in visited:
                    continue
                
                new_path = path + [neighbor]
                
                if neighbor == end:
                    return new_path
                
                visited.add(neighbor.id)
                queue.append((neighbor, new_path))
        
        # Brak ścieżki
        return []


class VehicleController:
    """Kontroler do zarządzania pojazdem i jego ruchem."""
    
    def __init__(self, vehicle: Vehicle, network: RoadNetwork):
        """
        Inicjalizuje kontroler pojazdu.
        
        Args:
            vehicle: Pojazd do kontrolowania
            network: Sieć drogowa
        """
        self.vehicle = vehicle
        self.network = network
        self.other_vehicles: List[Vehicle] = []  # Lista innych pojazdów do sprawdzania kolizji
    
    def set_destination(self, destination: Intersection) -> bool:
        """
        Ustawia cel dla pojazdu i wyznacza ścieżkę.
        
        Args:
            destination: Docelowe skrzyżowanie
        
        Returns:
            True jeśli znaleziono ścieżkę, False w przeciwnym razie
        """
        if destination == self.vehicle.current_intersection:
            self.vehicle.state = VehicleState.ARRIVED
            self.vehicle.destination = destination
            return True
        
        # Znajdź ścieżkę
        path = PathFinder.find_shortest_path(
            self.network,
            self.vehicle.current_intersection,
            destination
        )
        
        if not path:
            return False
        
        # Ustaw ścieżkę i start
        self.vehicle.destination = destination
        self.vehicle.path = path
        self.vehicle.current_path_index = 0
        self.vehicle.state = VehicleState.DRIVING
        self.vehicle.progress_on_road = 0.0
        
        # Ustaw pierwszą drogę
        if len(path) > 1:
            next_intersection = path[1]
            road = self.network.get_road_between(
                self.vehicle.current_intersection.id,
                next_intersection.id
            )
            self.vehicle.current_road = road
        
        return True
    
    def update(self, delta_time: float):
        """
        Aktualizuje pozycję pojazdu.
        
        Args:
            delta_time: Czas upłynięty od ostatniej aktualizacji (w sekundach)
        """
        if self.vehicle.state != VehicleState.DRIVING:
            return
        
        if not self.vehicle.current_road:
            return
        
        # Sprawdź czy na następnym skrzyżowaniu jest czerwone światło
        next_intersection = self.vehicle.path[self.vehicle.current_path_index + 1]
        current_intersection = self.vehicle.current_intersection
        
        has_red_light = False
        if next_intersection.traffic_light_controller:
            # Nowy system z fazami
            has_red_light = next_intersection.traffic_light_controller.is_red_for_direction(current_intersection.id)
        elif next_intersection.traffic_light:
            # Stary system
            has_red_light = next_intersection.traffic_light.is_red_for_direction(current_intersection.id)
        
        # Oblicz, jaką odległość pojazd pokonał
        # speed jest w km/h, delta_time w sekundach
        speed_m_s = self.vehicle.speed * 1000 / 3600  # konwersja km/h na m/s
        distance_traveled = speed_m_s * delta_time
        road_length = self.vehicle.current_road.length
        
        # Sprawdź czy jest pojazd przed nami na tej samej drodze
        min_safe_distance = 0.03  # 3% długości drogi jako minimalna bezpieczna odległość
        vehicle_ahead_progress = self._check_vehicle_ahead()
        
        # Aktualizuj postęp
        proposed_progress = self.vehicle.progress_on_road + distance_traveled / road_length
        
        # Sprawdź kolizję z pojazdem przed nami
        if vehicle_ahead_progress is not None:
            max_progress = vehicle_ahead_progress - min_safe_distance
            proposed_progress = min(proposed_progress, max_progress)
        
        # Jeśli jest czerwone światło, zatrzymaj się przed skrzyżowaniem
        if has_red_light:
            max_red_light_progress = 0.95
            proposed_progress = min(proposed_progress, max_red_light_progress)
        
        self.vehicle.progress_on_road = proposed_progress
        
        # Sprawdzenie czy pojazd dotarł do następnego skrzyżowania
        # Może być konieczne przesunięcie się o kilka wierzchołków w jednym frame
        while self.vehicle.progress_on_road >= 1.0:
            self._move_to_next_intersection()
            # Jeśli dotarł do celu, przerwij pętlę
            if self.vehicle.state == VehicleState.ARRIVED:
                break
    
    def _check_vehicle_ahead(self) -> Optional[float]:
        """
        Sprawdza czy jest pojazd przed nami na tej samej drodze.
        
        Returns:
            Progress pojazdu przed nami lub None jeśli nie ma pojazdu
        """
        if not self.vehicle.current_road:
            return None
        
        min_progress_ahead = None
        
        for other in self.other_vehicles:
            # Ignoruj siebie
            if other.id == self.vehicle.id:
                continue
            
            # Sprawdź czy jest na tej samej drodze
            if (other.current_road and 
                other.current_road.id == self.vehicle.current_road.id):
                # Sprawdź czy jest przed nami
                if other.progress_on_road > self.vehicle.progress_on_road:
                    if min_progress_ahead is None or other.progress_on_road < min_progress_ahead:
                        min_progress_ahead = other.progress_on_road
        
        return min_progress_ahead
    
    def _move_to_next_intersection(self):
        """Przenosi pojazd na następne skrzyżowanie w ścieżce."""
        # Przejdź do następnego wierzchołka
        self.vehicle.current_path_index += 1
        self.vehicle.current_intersection = self.vehicle.path[self.vehicle.current_path_index]
        
        # Przyszły postęp (jeśli pojazd jechał szybciej niż długość drogi)
        excess_progress = self.vehicle.progress_on_road - 1.0
        self.vehicle.progress_on_road = excess_progress
        
        # Sprawdź czy dotarł do celu
        if self.vehicle.current_path_index >= len(self.vehicle.path) - 1:
            # Dotarł do celu
            self.vehicle.state = VehicleState.ARRIVED
            self.vehicle.progress_on_road = 0.0
            self.vehicle.current_road = None
            return
        
        # Ustaw następną drogę (jeśli istnieje)
        next_intersection = self.vehicle.path[self.vehicle.current_path_index + 1]
        road = self.network.get_road_between(
            self.vehicle.current_intersection.id,
            next_intersection.id
        )
        self.vehicle.current_road = road
        next_intersection = self.vehicle.path[self.vehicle.current_path_index + 1]
        road = self.network.get_road_between(
            self.vehicle.current_intersection.id,
            next_intersection.id
        )
        self.vehicle.current_road = road
