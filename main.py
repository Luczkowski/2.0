"""
Główny plik testowy sieciulatora ruchu drogowego.
"""
# Zmiana pliku z przykłądami
# from examples import create_example_network, setup_example_spawners
from examples2 import create_example_network, setup_example_spawners

from visualization import RoadNetworkVisualizer
from fleet import VehicleFleet
from traffic_monitor import TrafficMonitor


def main():
    """Główna funkcja programu."""
    
    # Utwórz sieć
    network = create_example_network()
    
    # Utwórz wizualizację
    visualizer = RoadNetworkVisualizer()
    visualizer.load_network(network)
    
    # Utwórz flotę
    fleet = VehicleFleet(network)
    visualizer.set_fleet(fleet)

    # Utwórz monitor przepustowości i podłącz do floty
    monitor = TrafficMonitor(window_seconds=60.0)
    fleet.set_monitor(monitor)

    # Konfiguruj spawnery
    setup_example_spawners(fleet, network)

    visualizer.run()


if __name__ == "__main__":
    main()
