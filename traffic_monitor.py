"""
Moduł do mierzenia przepustowości w sieci.
Zlicza liczbę pojazdów przejeżdżających przez skrzyżowania
z rozbiciem na kierunki (od -> do) w czasie ostatnich 60 sekund.
Jednostka: pojazdy/minutę.
"""

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, Tuple, Optional, Iterable


@dataclass(frozen=True)
class DirectionKey:
    """Klucz kierunku przejazdu przez skrzyżowanie.
    from_id: ID skrzyżowania, z którego pojazd wjechał na skrzyżowanie
    to_id: ID skrzyżowania, do którego pojazd wyjechał ze skrzyżowania (None dla celu)
    """
    from_id: int
    to_id: Optional[int]


class TrafficMonitor:
    """Monitor przepustowości przejazdów przez skrzyżowania.

    Przechowuje dla każdego skrzyżowania mapę (from->to) -> lista znaczników czasu zdarzeń
    i udostępnia metryki w oknie ostatnich `window_seconds`.
    """

    def __init__(self, window_seconds: float = 60.0):
        self.window_seconds = max(1.0, window_seconds)
        self._time: float = 0.0
        # events[intersection_id][DirectionKey] = deque[timestamps]
        self._events: Dict[int, Dict[DirectionKey, deque]] = defaultdict(lambda: defaultdict(deque))

    @property
    def time(self) -> float:
        return self._time

    def update(self, delta_time: float) -> None:
        """Aktualizuje czas monitora i usuwa stare zdarzenia spoza okna."""
        if delta_time <= 0:
            return
        self._time += delta_time
        cutoff = self._time - self.window_seconds
        # Prune stare wpisy efektywnie, tylko istniejące klucze
        for intersection_id, dir_map in self._events.items():
            for key, dq in dir_map.items():
                while dq and dq[0] < cutoff:
                    dq.popleft()

    def record_pass(self, intersection_id: int, from_id: int, to_id: Optional[int]) -> None:
        """Rejestruje przejazd pojazdu przez skrzyżowanie."""
        key = DirectionKey(from_id=from_id, to_id=to_id)
        self._events[intersection_id][key].append(self._time)

    def get_rates_for_intersection(self, intersection_id: int) -> Dict[Tuple[int, Optional[int]], int]:
        """Zwraca mapę (from_id, to_id) -> liczba pojazdów/min w okresie 60 s."""
        dir_map = self._events.get(intersection_id, {})
        return {(k.from_id, k.to_id): len(dq) for k, dq in dir_map.items()}

    def get_total_rate_for_intersection(self, intersection_id: int) -> int:
        """Zwraca sumaryczną liczbę pojazdów/min przez skrzyżowanie w okresie 60 s."""
        dir_map = self._events.get(intersection_id, {})
        return sum(len(dq) for dq in dir_map.values())

    def get_all_intersections_rates(self) -> Dict[int, Dict[Tuple[int, Optional[int]], int]]:
        """Zwraca informację dla wszystkich skrzyżowań."""
        return {iid: {(k.from_id, k.to_id): len(dq) for k, dq in dir_map.items()}
                for iid, dir_map in self._events.items()}

    def clear(self) -> None:
        """Czyści wszystkie zarejestrowane zdarzenia i resetuje czas."""
        self._events.clear()
        self._time = 0.0
