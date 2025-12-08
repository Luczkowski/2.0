"""
Moduł do reprezentacji sieci drogowej jako grafu.
Wierzchołki to skrzyżowania, krawędzie to drogi.
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field


@dataclass
class Intersection:
    """Reprezentuje skrzyżowanie (wierzchołek grafu)."""
    
    id: int
    name: str
    x: float
    y: float
    
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
