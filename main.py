"""
Główny plik testowy sieciulatora ruchu drogowego.
"""

import argparse
from pathlib import Path

from examples import create_example_network
from fleet import VehicleFleet
from traffic_monitor import TrafficMonitor


def _configure_fleet_and_monitor(network):
    """Konfiguruje flotę, spawner-y i monitor przepustowości."""
    fleet = VehicleFleet(network)

    # Utwórz monitor przepustowości i podłącz do floty
    monitor = TrafficMonitor(window_seconds=60.0)
    fleet.set_monitor(monitor)

    # Spawner-y (jak w trybie wizualizacji)
    fleet.add_spawner(spawn_intersection=network.get_intersection(0), spawn_rate=0.25)
    fleet.add_spawner(spawn_intersection=network.get_intersection(1), spawn_rate=0.10)
    fleet.add_spawner(spawn_intersection=network.get_intersection(6), spawn_rate=0.2)
    fleet.add_spawner(spawn_intersection=network.get_intersection(8), spawn_rate=0.2)
    fleet.add_spawner(spawn_intersection=network.get_intersection(10), spawn_rate=0.10)
    fleet.add_spawner(spawn_intersection=network.get_intersection(11), spawn_rate=0.2)
    fleet.add_spawner(spawn_intersection=network.get_intersection(13), spawn_rate=0.1)
    fleet.add_spawner(spawn_intersection=network.get_intersection(14), spawn_rate=0.25)
    fleet.add_spawner(spawn_intersection=network.get_intersection(15), spawn_rate=0.1)

    return fleet, monitor


def _run_headless(duration_seconds: float, dt: float, output_path: Path) -> None:
    """Uruchamia symulację bez UI przez określony czas symulatora i zapisuje raport."""
    network = create_example_network()
    fleet, monitor = _configure_fleet_and_monitor(network)

    sim_time = 0.0
    dt = max(1e-6, float(dt))
    duration_seconds = max(0.0, float(duration_seconds))

    while sim_time < duration_seconds:
        step = min(dt, duration_seconds - sim_time)
        fleet.update(step)
        network.update_traffic_lights(step)
        sim_time += step

    # Raport: średnia przepustowość (pojazdy/min) z okna ostatniej minuty
    lines = []
    lines.append(f"czas_symulacji_s=\t{duration_seconds:.3f}")
    lines.append(f"okno_s=\t{monitor.window_seconds:.3f}")
    lines.append("")
    lines.append("intersection_id\tname\tthroughput_per_min")

    for intersection in sorted(network.get_all_intersections(), key=lambda i: i.id):
        rate = monitor.get_total_rate_for_intersection(intersection.id)
        lines.append(f"{intersection.id}\t{intersection.name}\t{rate}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _append_direction_breakdown(lines, network, monitor: TrafficMonitor) -> None:
    """Dopisuje do raportu rozbicie przepustowości na kierunki (from->to) per skrzyżowanie."""
    lines.append("")
    lines.append("---")
    lines.append("Rozbicie na kierunki (pojazdy/min w oknie ostatniej minuty)")
    lines.append("Format: intersection_id\tname\tfrom_id\tto_id\tthroughput_per_min")

    for intersection in sorted(network.get_all_intersections(), key=lambda i: i.id):
        rates = monitor.get_rates_for_intersection(intersection.id)
        if not rates:
            continue

        # Sortuj malejąco po przepustowości, potem deterministycznie po kierunku
        for (from_id, to_id), count in sorted(
            rates.items(),
            key=lambda kv: (-kv[1], kv[0][0], -1 if kv[0][1] is None else kv[0][1]),
        ):
            to_txt = "dest" if to_id is None else str(to_id)
            lines.append(f"{intersection.id}\t{intersection.name}\t{from_id}\t{to_txt}\t{count}")


def main():
    """Główna funkcja programu."""
    parser = argparse.ArgumentParser(description="Symulator ruchu drogowego")
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Uruchom symulację automatycznie (bez UI) i wygeneruj raport.")
    parser.add_argument(
        "--duration",
        type=float,
        default=600.0,
        help="Czas symulatora w sekundach (domyślnie 600 = 10 minut).")
    parser.add_argument(
        "--dt",
        type=float,
        default=0.1,
        help="Krok czasowy symulacji w sekundach (domyślnie 0.1).")
    parser.add_argument(
        "--out",
        type=str,
        default="throughput_last_minute.txt",
        help="Ścieżka pliku wyjściowego z raportem.")
    parser.add_argument(
        "--directions",
        action="store_true",
        help="Dodaj do raportu rozbicie przepustowości na kierunki (from->to).")

    args = parser.parse_args()

    if args.auto:
        out_path = Path(args.out)
        # Wykonaj symulację i bazowy raport
        network = create_example_network()
        fleet, monitor = _configure_fleet_and_monitor(network)

        sim_time = 0.0
        dt = max(1e-6, float(args.dt))
        duration_seconds = max(0.0, float(args.duration))

        while sim_time < duration_seconds:
            step = min(dt, duration_seconds - sim_time)
            fleet.update(step)
            network.update_traffic_lights(step)
            sim_time += step

        lines = []
        lines.append(f"czas_symulacji_s=\t{duration_seconds:.3f}")
        lines.append(f"okno_s=\t{monitor.window_seconds:.3f}")
        lines.append("")
        lines.append("intersection_id\tname\tthroughput_per_min")
        for intersection in sorted(network.get_all_intersections(), key=lambda i: i.id):
            rate = monitor.get_total_rate_for_intersection(intersection.id)
            lines.append(f"{intersection.id}\t{intersection.name}\t{rate}")

        if args.directions:
            _append_direction_breakdown(lines, network, monitor)

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    # Tryb interaktywny (pygame) – import lokalny, żeby nie wymagać pygame w trybie headless.
    from visualization import RoadNetworkVisualizer

    network = create_example_network()
    visualizer = RoadNetworkVisualizer()
    visualizer.load_network(network)

    fleet, _monitor = _configure_fleet_and_monitor(network)
    visualizer.set_fleet(fleet)
    visualizer.run()


if __name__ == "__main__":
    main()
