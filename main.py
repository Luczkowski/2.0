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
    fleet.add_spawner(
        spawn_intersection=network.get_intersection(0)
    )
    fleet.add_spawner(
        spawn_intersection=network.get_intersection(1)
    )
    fleet.add_spawner(
        spawn_intersection=network.get_intersection(4)
    )
    fleet.add_spawner(
        spawn_intersection=network.get_intersection(5)
    )
    fleet.add_spawner(
        spawn_intersection=network.get_intersection(8)
    )
    fleet.add_spawner(
        spawn_intersection=network.get_intersection(10)
    )

    visualizer.run()


if __name__ == "__main__":
    main()
