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
            print(f"Nie znaleziono ścieżki z {self.vehicle.current_intersection.name} "
                  f"do {destination.name}")
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
        
        print(f"Pojazd {self.vehicle.id}: droga wyznaczona "
              f"({' -> '.join(i.name for i in path)})")
        
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
        
        # Oblicz, jaką odległość pojazd pokonał
        # speed jest w km/h, delta_time w sekundach
        speed_m_s = self.vehicle.speed * 1000 / 3600  # konwersja km/h na m/s
        distance_traveled = speed_m_s * delta_time
        road_length = self.vehicle.current_road.length
        
        # Aktualizuj postęp
        self.vehicle.progress_on_road += distance_traveled / road_length
        
        # Sprawdzenie czy pojazd dotarł do następnego skrzyżowania
        # Może być konieczne przesunięcie się o kilka wierzchołków w jednym frame
        while self.vehicle.progress_on_road >= 1.0:
            self._move_to_next_intersection()
            # Jeśli dotarł do celu, przerwij pętlę
            if self.vehicle.state == VehicleState.ARRIVED:
                break
    
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
            print(f"Pojazd {self.vehicle.id} dotarł do {self.vehicle.current_intersection.name}")
            return
        
        # Ustaw następną drogę (jeśli istnieje)
        next_intersection = self.vehicle.path[self.vehicle.current_path_index + 1]
        road = self.network.get_road_between(
            self.vehicle.current_intersection.id,
            next_intersection.id
        )
        self.vehicle.current_road = road
