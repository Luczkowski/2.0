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
        spawn_intersection=network.get_intersection(0),
        spawn_rate=0.25
    )
    fleet.add_spawner(
        spawn_intersection=network.get_intersection(1),
        spawn_rate=0.10
    )
    fleet.add_spawner(
        spawn_intersection=network.get_intersection(6),
        spawn_rate=0.2
    )
    fleet.add_spawner(
        spawn_intersection=network.get_intersection(8),
        spawn_rate=0.2
    )
    fleet.add_spawner(
        spawn_intersection=network.get_intersection(10),
        spawn_rate=0.10
    )
    fleet.add_spawner(
        spawn_intersection=network.get_intersection(11),
        spawn_rate=0.2
    )
    fleet.add_spawner(
        spawn_intersection=network.get_intersection(14),
        spawn_rate=0.25
    )
    fleet.add_spawner(
        spawn_intersection=network.get_intersection(15),
        spawn_rate=0.1
    )

    visualizer.run()


if __name__ == "__main__":
    main()
