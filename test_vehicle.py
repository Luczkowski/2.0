"""
Test logiki poruszania się pojazdu.
"""

from graph import RoadNetwork
from vehicle import Vehicle, VehicleController, VehicleState


def test_vehicle_movement():
    """Test ruchu pojazdu przez całą ścieżkę."""
    
    # Utwórz prostą sieć: A -> B -> C
    network = RoadNetwork()
    a = network.add_intersection("A", 0, 0)
    b = network.add_intersection("B", 100, 0)
    c = network.add_intersection("C", 200, 0)
    
    # Drogi: A->B (100m), B->C (100m)
    network.add_road(a.id, b.id, 100, 50)
    network.add_road(b.id, c.id, 100, 50)
    
    # Utwórz pojazd w A
    vehicle = Vehicle(id=0, current_intersection=a, speed=100.0)  # 100 km/h
    controller = VehicleController(vehicle, network)
    
    # Ustaw cel na C
    controller.set_destination(c)
    
    print(f"Start: {vehicle.current_intersection.name}, state: {vehicle.state.value}")
    print(f"Path: {' -> '.join(i.name for i in vehicle.path)}")
    print(f"Path index: {vehicle.current_path_index}, Length: {len(vehicle.path)}")
    
    # Symuluj ruch
    # 100 km/h = 100000 m / 3600 s = ~27.78 m/s
    # Droga 100m pokonana w ~3.6 sekundy
    
    time_steps = [0.5] * 20  # 10 sekund, powinna być wystarczająco
    
    for i, dt in enumerate(time_steps):
        controller.update(dt)
        x, y = vehicle.get_current_position()
        print(f"Step {i+1} (dt={dt}s): pos={vehicle.current_intersection.name}, "
              f"coords=({x:.1f}, {y:.1f}), "
              f"progress={vehicle.progress_on_road:.3f}, "
              f"index={vehicle.current_path_index}, "
              f"state={vehicle.state.value}")
        
        if vehicle.state == VehicleState.ARRIVED:
            print(f"✓ Pojazd dotarł do celu!")
            break
    
    assert vehicle.state == VehicleState.ARRIVED, "Pojazd nie dotarł do celu!"
    assert vehicle.current_intersection == c, "Pojazd nie jest w docelowym miejscu!"
    print("\n✓ Test zaliczony!")


if __name__ == "__main__":
    test_vehicle_movement()
