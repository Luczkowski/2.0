"""
Przykłady wykorzystania grafu sieci drogowej.
"""

from graph import RoadNetwork, TrafficLight, TrafficLightState, TrafficLightController, TrafficLightPhase


def create_example_network() -> RoadNetwork:
    """Tworzy przykładową sieć drogową."""
    network = RoadNetwork()
    
    # Dodaj skrzyżowania
    A = network.add_intersection("Skrzyżowanie A", 100, 0)
    B = network.add_intersection("Skrzyżowanie B", 100, 200)
    C = network.add_intersection("Skrzyżowanie C", 0, 100)
    D = network.add_intersection("Skrzyżowanie D", 200, 100)
    E = network.add_intersection("Skrzyżowanie E", 100, 100)
    
    # Skrzyżowanie C nie może być celem (tylko punkt pośredni)
    E.is_destination = False
    
    # Dodaj sygnalizację świetlną na skrzyżowaniu C z fazami
    # Faza 1: Pojazdy z B mogą jechać przez 5 sekund
    # Faza 2: Pojazdy z A (przez diagonal) mogą jechać przez 5 sekund
    E.traffic_light_controller = TrafficLightController([
        TrafficLightPhase(allowed_directions={A.id,B.id}, duration=5.0),
        TrafficLightPhase(allowed_directions={C.id, D.id}, duration=5.0)
    ])
    
    # Dodaj drogi
    network.add_two_way_road(
        from_id=A.id,
        to_id=E.id,
        length=100,
        speed_limit=50,
        lanes=2
    )
    
    network.add_two_way_road(
        from_id=B.id,
        to_id=E.id,
        length=100,
        speed_limit=50,
        lanes=2
    )
    
    network.add_two_way_road(
        from_id=C.id,
        to_id=E.id,
        length=100,
        speed_limit=50,
        lanes=1
    )
    
    network.add_two_way_road(
        from_id=D.id,
        to_id=E.id,
        length=100,
        speed_limit=50,
        lanes=1
    )
    
    return network

