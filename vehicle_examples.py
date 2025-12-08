"""
Przykłady użycia systemu pojazdów.
"""

from examples import create_example_network, create_grid_network
from visualization import RoadNetworkVisualizer
from vehicle import Vehicle


def demo_single_vehicle():
    """Demonstracja pojedynczego pojazdu."""
    print("\n" + "="*60)
    print("DEMO: Pojedynczy pojazd")
    print("="*60)
    
    # Utwórz sieć
    network = create_example_network()
    
    # Utwórz wizualizację
    visualizer = RoadNetworkVisualizer(title="Demo: Pojedynczy pojazd")
    visualizer.load_network(network)
    
    # Utwórz pojazd
    start = network.get_intersection(0)
    vehicle = Vehicle(id=0, current_intersection=start, speed=50.0)
    visualizer.add_vehicle(vehicle)
    
    # Wyznacz cel
    destination = network.get_intersection(3)
    if visualizer.vehicle_controllers:
        visualizer.vehicle_controllers[0].set_destination(destination)
    
    print("Pojazd startuje z Skrzyżowania A i jedzie do Skrzyżowania D")
    visualizer.run()


def demo_multiple_vehicles():
    """Demonstracja wielu pojazdów."""
    print("\n" + "="*60)
    print("DEMO: Wiele pojazdów (bez kolizji)")
    print("="*60)
    
    # Utwórz większą sieć
    network = create_grid_network(3, 3, 80)
    
    # Utwórz wizualizację
    visualizer = RoadNetworkVisualizer(title="Demo: Wiele pojazdów", 
                                       width=1000, height=1000)
    visualizer.load_network(network)
    
    # Utwórz pojazdy z różnymi trasami
    routes = [
        (0, 8, 60, "V0: 0->8"),
        (2, 6, 50, "V1: 2->6"),
        (8, 0, 40, "V2: 8->0"),
    ]
    
    for vehicle_id, (start_id, dest_id, speed, description) in enumerate(routes):
        start = network.get_intersection(start_id)
        destination = network.get_intersection(dest_id)
        
        vehicle = Vehicle(id=vehicle_id, current_intersection=start, speed=speed)
        visualizer.add_vehicle(vehicle)
        
        if visualizer.vehicle_controllers:
            controller = visualizer.vehicle_controllers[vehicle_id]
            controller.set_destination(destination)
            print(f"{description} (prędkość: {speed} km/h)")
    
    visualizer.run()


if __name__ == "__main__":
    # Odkomentuj aby uruchomić demo
    demo_single_vehicle()
    # demo_multiple_vehicles()
