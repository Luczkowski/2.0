"""
Główny plik testowy sieciulatora ruchu drogowego.
"""

from examples import create_example_network
from visualization import RoadNetworkVisualizer
from fleet import VehicleFleet


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
    
    # Dodaj spawner w skrzyżowaniu 0
    spawn_point = network.get_intersection(0)
    fleet.add_spawner(
        spawn_intersection=spawn_point,
        spawn_interval_min=1.0,
        spawn_interval_max=3.0,
        speed_min=40.0,
        speed_max=70.0
    )

    visualizer.run()


if __name__ == "__main__":
    main()
