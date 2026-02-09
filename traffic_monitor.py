from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, Tuple, Optional


@dataclass(frozen=True)
class DirectionKey:
    from_id: int
    to_id: Optional[int]


class TrafficMonitor:
    """Monitor przepustowości przejazdów przez skrzyżowania."""

    def __init__(self, window_seconds: float = 60.0):
        self.window_seconds = max(1.0, window_seconds)
        self._time: float = 0.0
        self._events: Dict[int, Dict[DirectionKey, deque]] = defaultdict(lambda: defaultdict(deque))

    def _to_per_minute(self, count_in_window: int) -> int:
        """Przelicza liczbę zdarzeń w oknie na pojazdy/min i zaokrągla do int."""
        rate = (float(count_in_window) / self.window_seconds) * 60.0
        return int(round(rate))

    @property
    def time(self) -> float:
        return self._time

    def update(self, delta_time: float) -> None:
        """Aktualizuje czas monitora i usuwa stare zdarzenia spoza okna."""
        if delta_time <= 0:
            return
        self._time += delta_time
        cutoff = self._time - self.window_seconds

        for intersection_id, dir_map in self._events.items():
            for key, dq in dir_map.items():
                while dq and dq[0] < cutoff:
                    dq.popleft()

    def record_pass(self, intersection_id: int, from_id: int, to_id: Optional[int]) -> None:
        """Rejestruje przejazd pojazdu przez skrzyżowanie."""
        key = DirectionKey(from_id=from_id, to_id=to_id)
        self._events[intersection_id][key].append(self._time)

    def get_counts_for_intersection(self, intersection_id: int) -> Dict[Tuple[int, Optional[int]], int]:
        """Zwraca mapę (from_id, to_id) -> liczba zdarzeń w oknie `window_seconds` (bez przeliczeń)."""
        dir_map = self._events.get(intersection_id, {})
        return {(k.from_id, k.to_id): len(dq) for k, dq in dir_map.items()}

    def get_rates_for_intersection(self, intersection_id: int) -> Dict[Tuple[int, Optional[int]], int]:
        """Zwraca mapę (from_id, to_id) -> przepustowość (pojazdy/min) w oknie `window_seconds`."""
        dir_map = self._events.get(intersection_id, {})
        return {(k.from_id, k.to_id): self._to_per_minute(len(dq)) for k, dq in dir_map.items()}

    def get_total_rate_for_intersection(self, intersection_id: int) -> int:
        """Zwraca sumaryczną przepustowość (pojazdy/min) przez skrzyżowanie w oknie `window_seconds`."""
        dir_map = self._events.get(intersection_id, {})
        return self._to_per_minute(sum(len(dq) for dq in dir_map.values()))

    def get_corridor_rate(self, corridor_node_ids: list[int]) -> int:
        """Zwraca sumę przepustowości (pojazdy/min) dla korytarza transportowego."""
        if len(corridor_node_ids) < 2:
            return 0

        total_count = 0
        for i in range(len(corridor_node_ids) - 1):
            from_id = corridor_node_ids[i]
            to_id = corridor_node_ids[i + 1]
            counts_into_to = self.get_counts_for_intersection(to_id)
            total_count += sum(
                count for (src_id, _next_id), count in counts_into_to.items() if src_id == from_id
            )

        return self._to_per_minute(total_count)

    def get_all_intersections_rates(self) -> Dict[int, Dict[Tuple[int, Optional[int]], int]]:
        """Zwraca przepustowości (pojazdy/min) dla wszystkich skrzyżowań."""
        return {
            iid: {(k.from_id, k.to_id): self._to_per_minute(len(dq)) for k, dq in dir_map.items()}
            for iid, dir_map in self._events.items()
        }

    def clear(self) -> None:
        """Czyści wszystkie zarejestrowane zdarzenia i resetuje czas."""
        self._events.clear()
        self._time = 0.0
