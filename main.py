"""
Główny plik testowy sieciulatora ruchu drogowego.
"""

from examples import create_example_network, print_network_info
from visualization import RoadNetworkVisualizer
from fleet import VehicleFleet


def main():
    """Główna funkcja programu."""
    print("🚗 SYMULATOR RUCHU DROGOWEGO\n")
    
    # Utwórz sieć
    network = create_example_network()
    print_network_info(network)
    
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
    
    print(f"\n🚗 Spawner pojazydów w {spawn_point.name}")
    print("   Interwał: 1-3 sekundy")
    print("   Prędkość: 40-70 km/h")
    
    # Wyświetl wizualizację
    print("\nOtwarcie wizualizacji pygame...")
    visualizer.run()


if __name__ == "__main__":
    main()
