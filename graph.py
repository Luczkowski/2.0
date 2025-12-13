"""
Moduł do reprezentacji sieci drogowej jako grafu.
Wierzchołki to skrzyżowania, krawędzie to drogi.
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum


class TrafficLightState(Enum):
    """Stany sygnalizacji świetlnej."""
    GREEN = "green"
    RED = "red"


@dataclass
class TrafficLightPhase:
    """Reprezentuje jedną fazę sygnalizacji (które kierunki mają zielone)."""
    allowed_directions: Set[int]  # ID skrzyżowań z których można wjechać
    duration: float  # Czas trwania fazy w sekundach


class TrafficLightController:
    """Kontroler sygnalizacji świetlnej z wieloma fazami."""
    
    def __init__(self, phases: List[TrafficLightPhase]):
        """
        Inicjalizuje kontroler świateł.
        
        Args:
            phases: Lista faz świateł (kolejność definiuje cykl)
        """
        self.phases = phases
        self.current_phase_index = 0
        self.time_in_phase = 0.0
    
    def adjust_phase_duration(self, phase_index: int, delta: float):
        """
        Dynamicznie zmienia czas trwania danej fazy.
        
        Args:
            phase_index: Indeks fazy do zmiany
            delta: Zmiana czasu w sekundach (może być ujemna)
        """
        if 0 <= phase_index < len(self.phases):
            new_duration = max(1.0, self.phases[phase_index].duration + delta)
            self.phases[phase_index].duration = new_duration
    
    def set_phase_duration(self, phase_index: int, duration: float):
        """
        Ustawia czas trwania danej fazy.
        
        Args:
            phase_index: Indeks fazy do zmiany
            duration: Nowy czas trwania w sekundach
        """
        if 0 <= phase_index < len(self.phases):
            self.phases[phase_index].duration = max(1.0, duration)
    
    def get_phase_info(self) -> str:
        """
        Zwraca informacje o wszystkich fazach.
        
        Returns:
            Tekst z informacjami o fazach i ich czasach
        """
        info = []
        for i, phase in enumerate(self.phases):
            dirs = ", ".join(str(d) for d in sorted(phase.allowed_directions))
            marker = "→" if i == self.current_phase_index else " "
            info.append(f"{marker} Faza {i}: {phase.duration:.1f}s (kierunki: {dirs})")
        return "\n".join(info)
    
    def update(self, delta_time: float):
        """Aktualizuje kontroler i przełącza fazy."""
        self.time_in_phase += delta_time
        
        current_phase = self.phases[self.current_phase_index]
        if self.time_in_phase >= current_phase.duration:
            # Przejdź do następnej fazy
            self.current_phase_index = (self.current_phase_index + 1) % len(self.phases)
            self.time_in_phase = 0.0
    
    def is_green_for_direction(self, from_intersection_id: int) -> bool:
        """
        Sprawdza czy dany kierunek ma zielone światło.
        
        Args:
            from_intersection_id: ID skrzyżowania z którego nadjeżdża pojazd
            
        Returns:
            True jeśli zielone dla tego kierunku
        """
        current_phase = self.phases[self.current_phase_index]
        return from_intersection_id in current_phase.allowed_directions
    
    def is_red_for_direction(self, from_intersection_id: int) -> bool:
        """
        Sprawdza czy dany kierunek ma czerwone światło.
        
        Args:
            from_intersection_id: ID skrzyżowania z którego nadjeżdża pojazd
            
        Returns:
            True jeśli czerwone dla tego kierunku
        """
        return not self.is_green_for_direction(from_intersection_id)
    
    def get_current_phase(self) -> TrafficLightPhase:
        """Zwraca aktualną fazę."""
        return self.phases[self.current_phase_index]


@dataclass
class TrafficLight:
    """Reprezentuje sygnalizację świetlną z kontrolą kierunków (deprecated - użyj TrafficLightController)."""
    
    state: TrafficLightState = TrafficLightState.GREEN
    green_duration: float = 10.0  # Czas świecenia zielonego (sekundy)
    red_duration: float = 5.0      # Czas świecenia czerwonego (sekundy)
    time_in_state: float = 0.0     # Czas w aktualnym stanie
    allowed_directions: Optional[Set[int]] = None  # ID skrzyżowań z których można wjechać (None = wszystkie)
    
    def update(self, delta_time: float):
        """Aktualizuje stan sygnalizacji."""
        self.time_in_state += delta_time
        
        # Sprawdź czy pora zmienić stan
        if self.state == TrafficLightState.GREEN and self.time_in_state >= self.green_duration:
            self.state = TrafficLightState.RED
            self.time_in_state = 0.0
        elif self.state == TrafficLightState.RED and self.time_in_state >= self.red_duration:
            self.state = TrafficLightState.GREEN
            self.time_in_state = 0.0
    
    def is_red(self) -> bool:
        """Sprawdza czy światło jest czerwone."""
        return self.state == TrafficLightState.RED
    
    def is_green(self) -> bool:
        """Sprawdza czy światło jest zielone."""
        return self.state == TrafficLightState.GREEN
    
    def is_red_for_direction(self, from_intersection_id: int) -> bool:
        """
        Sprawdza czy światło jest czerwone dla danego kierunku.
        
        Args:
            from_intersection_id: ID skrzyżowania z którego nadjeżdża pojazd
            
        Returns:
            True jeśli czerwone dla tego kierunku
        """
        if self.allowed_directions is None:
            # Brak ograniczeń kierunkowych - standardowe światło
            return self.is_red()
        
        # Jeśli światło jest zielone i kierunek jest dozwolony
        if self.is_green() and from_intersection_id in self.allowed_directions:
            return False
        
        # W przeciwnym razie czerwone
        return True


@dataclass
class Intersection:
    """Reprezentuje skrzyżowanie (wierzchołek grafu)."""
    
    id: int
    name: str
    x: float
    y: float
    traffic_light: Optional[TrafficLight] = None
    traffic_light_controller: Optional[TrafficLightController] = None
    is_destination: bool = True  # Czy skrzyżowanie może być celem podróży
    
    def __repr__(self) -> str:
        return f"Intersection(id={self.id}, name='{self.name}', pos=({self.x}, {self.y}))"
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Intersection):
            return False
        return self.id == other.id


@dataclass
class Road:
    """Reprezentuje drogę (krawędź grafu)."""
    
    id: int
    from_intersection: Intersection
    to_intersection: Intersection
    length: float
    speed_limit: float  # km/h
    lanes: int = 1
    
    def __repr__(self) -> str:
        return (f"Road(id={self.id}, "
                f"from={self.from_intersection.id}, "
                f"to={self.to_intersection.id}, "
                f"length={self.length}m, "
                f"speed_limit={self.speed_limit}km/h)")
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Road):
            return False
        return self.id == other.id


class RoadNetwork:
    """Graf reprezentujący sieć drogową."""
    
    def __init__(self):
        """Inicjalizuje pustą sieć drogową."""
        self.intersections: Dict[int, Intersection] = {}
        self.roads: Dict[int, Road] = {}
        self._adj_list: Dict[int, List[Road]] = {}
        self._intersection_counter = 0
        self._road_counter = 0
    
    def add_intersection(self, name: str, x: float, y: float) -> Intersection:
        """
        Dodaje nowe skrzyżowanie do sieci.
        
        Args:
            name: Nazwa skrzyżowania
            x: Współrzędna X
            y: Współrzędna Y
        
        Returns:
            Utworzone skrzyżowanie
        """
        intersection = Intersection(
            id=self._intersection_counter,
            name=name,
            x=x,
            y=y
        )
        self.intersections[intersection.id] = intersection
        self._adj_list[intersection.id] = []
        self._intersection_counter += 1
        return intersection
    
    def add_road(self,
                 from_id: int,
                 to_id: int,
                 length: float,
                 speed_limit: float,
                 lanes: int = 1) -> Road:
        """
        Dodaje nową drogę między dwoma skrzyżowaniami.
        
        Args:
            from_id: ID skrzyżowania początkowego
            to_id: ID skrzyżowania końcowego
            length: Długość drogi w metrach
            speed_limit: Ograniczenie prędkości w km/h
            lanes: Liczba pasów ruchu
        
        Returns:
            Utworzona droga
        
        Raises:
            ValueError: Jeśli któreś ze skrzyżowań nie istnieje
        """
        if from_id not in self.intersections or to_id not in self.intersections:
            raise ValueError(
                f"Jedno ze skrzyżowań nie istnieje (from_id={from_id}, to_id={to_id})"
            )
        
        road = Road(
            id=self._road_counter,
            from_intersection=self.intersections[from_id],
            to_intersection=self.intersections[to_id],
            length=length,
            speed_limit=speed_limit,
            lanes=lanes
        )
        self.roads[road.id] = road
        self._adj_list[from_id].append(road)
        self._road_counter += 1
        return road
    
    def get_intersection(self, intersection_id: int) -> Optional[Intersection]:
        """Zwraca skrzyżowanie o danym ID."""
        return self.intersections.get(intersection_id)
    
    def get_road(self, road_id: int) -> Optional[Road]:
        """Zwraca drogę o danym ID."""
        return self.roads.get(road_id)
    
    def get_outgoing_roads(self, intersection_id: int) -> List[Road]:
        """Zwraca wszystkie drogi wychodzące ze skrzyżowania."""
        if intersection_id not in self._adj_list:
            raise ValueError(f"Skrzyżowanie {intersection_id} nie istnieje")
        return self._adj_list[intersection_id]
    
    def get_neighbors(self, intersection_id: int) -> List[Intersection]:
        """Zwraca wszystkie sąsiadujące skrzyżowania."""
        neighbors = []
        for road in self.get_outgoing_roads(intersection_id):
            neighbors.append(road.to_intersection)
        return neighbors
    
    def get_road_between(self,
                         from_id: int,
                         to_id: int) -> Optional[Road]:
        """Zwraca drogę między dwoma skrzyżowaniami, jeśli istnieje."""
        for road in self.get_outgoing_roads(from_id):
            if road.to_intersection.id == to_id:
                return road
        return None
    
    def get_all_intersections(self) -> List[Intersection]:
        """Zwraca listę wszystkich skrzyżowań."""
        return list(self.intersections.values())
    
    def get_all_roads(self) -> List[Road]:
        """Zwraca listę wszystkich dróg."""
        return list(self.roads.values())
    
    def num_intersections(self) -> int:
        """Zwraca liczbę skrzyżowań w sieci."""
        return len(self.intersections)
    
    def num_roads(self) -> int:
        """Zwraca liczbę dróg w sieci."""
        return len(self.roads)
    
    def __repr__(self) -> str:
        return (f"RoadNetwork(intersections={self.num_intersections()}, "
                f"roads={self.num_roads()})")
