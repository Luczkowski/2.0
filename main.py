import argparse
import random
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

    # Spawnery
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

        # Sortuj malejąco po przepustowości, potem po kierunku
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
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Ziarno generatora liczb losowych dla trybu --auto (deterministyczne wyniki).")
    parser.add_argument(
        "--corridor",
        nargs="+",
        default=None,
        help=(
            "Jeden lub więcej korytarzy transportowych jako listy węzłów (ID wierzchołków), "
            "rozdzielone przecinkiem. Przykład: --corridor 0 2 3 4 5 12 14, 14 12 5 4 3 2 0"
        ),
    )

    args = parser.parse_args()

    if args.auto:
        if args.seed is not None:
            random.seed(args.seed)
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
        lines.append(f"zakonczone_przejazdy=\t{fleet.get_completed_trips_count()}")
        lines.append(f"sredni_czas_przejazdu_s=\t{fleet.get_average_travel_time():.3f}")
        lines.append(f"sredni_czas_stania_na_swiatlach_s=\t{fleet.get_average_red_light_wait_time():.3f}")
        lines.append(f"srednia_dlugosc_kolejki_na_swiatlach=\t{fleet.get_average_queue_length_at_lights():.3f}")
        lines.append("")
        lines.append("intersection_id\tname\tthroughput_per_min")
        for intersection in sorted(network.get_all_intersections(), key=lambda i: i.id):
            rate = monitor.get_total_rate_for_intersection(intersection.id)
            lines.append(f"{intersection.id}\t{intersection.name}\t{rate}")

        if args.directions:
            _append_direction_breakdown(lines, network, monitor)

        if args.corridor:
            corridors: list[list[int]] = [[]]
            for raw_token in args.corridor:
                token = raw_token.strip()
                if token == ",":
                    if not corridors[-1]:
                        raise SystemExit("Nieprawidłowy korytarz: pusty segment między przecinkami.")
                    corridors.append([])
                    continue

                # Obsłuż przypadek "14," (przecinek przyklejony do liczby)
                token_has_comma = token.endswith(",")
                if token_has_comma:
                    token = token[:-1]

                try:
                    corridors[-1].append(int(token))
                except ValueError:
                    raise SystemExit(
                        f"Nieprawidłowy węzeł w korytarzu: '{raw_token}'. Podaj ID wierzchołka jako liczbę całkowitą."
                    )

                if token_has_comma:
                    if not corridors[-1]:
                        raise SystemExit("Nieprawidłowy korytarz: pusty segment przed przecinkiem.")
                    corridors.append([])

            # Usuń ewentualny pusty ostatni segment (np. jeśli wejście kończy się przecinkiem)
            if corridors and not corridors[-1]:
                corridors.pop()
            if not corridors:
                raise SystemExit("Nie podano żadnego poprawnego korytarza.")

            lines.append("")
            lines.append("---")
            lines.append("Korytarze transportowe (pojazdy/min w oknie ostatniej minuty)")
            lines.append("Format: nodes\tthroughput_per_min")

            for corridor_ids in corridors:
                if len(corridor_ids) < 2:
                    raise SystemExit("Korytarz musi zawierać co najmniej dwa węzły.")

                corridor_intersections = [network.get_intersection(iid) for iid in corridor_ids]
                missing_ids = [iid for iid, inter in zip(corridor_ids, corridor_intersections) if inter is None]
                if missing_ids:
                    raise SystemExit(f"Nie znaleziono skrzyżowania o ID={missing_ids[0]} (korytarz).")

                corridor_names = [inter.name for inter in corridor_intersections if inter is not None]
                corridor_rate = monitor.get_corridor_rate(corridor_ids)
                lines.append(f"{' -> '.join(corridor_names)}\t{corridor_rate}")

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    # Tryb interaktywny (pygame)
    from visualization import RoadNetworkVisualizer

    network = create_example_network()
    visualizer = RoadNetworkVisualizer()
    visualizer.load_network(network)

    fleet, _monitor = _configure_fleet_and_monitor(network)
    visualizer.set_fleet(fleet)
    visualizer.run()


if __name__ == "__main__":
    main()
