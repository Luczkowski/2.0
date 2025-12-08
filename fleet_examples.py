"""
Zaawansowane przykłady floty pojazdów.
"""

from advanced_examples import create_grid_network
from visualization import RoadNetworkVisualizer
from fleet import VehicleFleet


def demo_single_spawner():
    """Demo z jednym spawnerem."""
    print("\n" + "="*60)
    print("DEMO: Jeden spawner")
    print("="*60)
    
    # Utwórz sieć
    network = create_grid_network(3, 3, 100)
    
    # Utwórz wizualizację
    visualizer = RoadNetworkVisualizer(width=1000, height=1000,
                                      title="Demo: Jeden spawner")
    visualizer.load_network(network)
    
    # Utwórz flotę
    fleet = VehicleFleet(network)
    visualizer.set_fleet(fleet)
    
    # Dodaj spawner
    spawn_point = network.get_intersection(0)
    fleet.add_spawner(spawn_point, 0.8, 2.0, 30.0, 60.0)
    
    print(f"Spawner w {spawn_point.name}")
    visualizer.run()


def demo_multiple_spawners():
    """Demo z wieloma spawnerami."""
    print("\n" + "="*60)
    print("DEMO: Wielokrotne spawnery")
    print("="*60)
    
    # Utwórz sieć
    network = create_grid_network(4, 4, 80)
    
    # Utwórz wizualizację
    visualizer = RoadNetworkVisualizer(width=1200, height=1200,
                                      title="Demo: Wielokrotne spawnery")
    visualizer.load_network(network)
    
    # Utwórz flotę
    fleet = VehicleFleet(network)
    visualizer.set_fleet(fleet)
    
    # Dodaj spawner w narożnikach
    spawners_config = [
        (0, "Lewy górny", 1.0, 2.5),
        (3, "Prawy górny", 1.2, 2.0),
        (12, "Lewy dolny", 0.9, 2.3),
        (15, "Prawy dolny", 1.5, 2.5),
    ]
    
    for intersection_id, name, min_interval, max_interval in spawners_config:
        spawn_point = network.get_intersection(intersection_id)
        fleet.add_spawner(
            spawn_point,
            spawn_interval_min=min_interval,
            spawn_interval_max=max_interval,
            speed_min=35.0,
            speed_max=75.0
        )
        print(f"Spawner w {spawn_point.name} ({name})")
    
    visualizer.run()


if __name__ == "__main__":
    # demo_single_spawner()
    demo_multiple_spawners()
