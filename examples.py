"""
Przykłady wykorzystania grafu sieci drogowej.
"""

from graph import RoadNetwork, TrafficLight, TrafficLightState, TrafficLightController, TrafficLightPhase


def create_example_network() -> RoadNetwork:
    """Tworzy przykładową sieć drogową."""
    network = RoadNetwork()
    
    # Skrzyżowania
    A = network.add_intersection("Skrzyżowanie A", 0, 0)
    B = network.add_intersection("Skrzyżowanie B", 100, 0)
    C = network.add_intersection("Skrzyżowanie C", 0, 50)
    D = network.add_intersection("Skrzyżowanie D", 100, 50)
    E = network.add_intersection("Skrzyżowanie E", 0, 200)
    F = network.add_intersection("Skrzyżowanie F", 100, 200)
    G = network.add_intersection("Skrzyżowanie G", 100, 100)
    H = network.add_intersection("Skrzyżowanie H", 100, 150)
    I = network.add_intersection("Skrzyżowanie I", 200, 150)
    J = network.add_intersection("Skrzyżowanie J", 30, 50)
    K = network.add_intersection("Skrzyżowanie K", 30, 100)
    L = network.add_intersection("Skrzyżowanie L", 200, 110)
    M = network.add_intersection("Skrzyżowanie M", 200, 190)
    
    # Punkty pośrednie
    J.is_destination = False
    H.is_destination = False
    G.is_destination = False
    D.is_destination = False
    C.is_destination = False
    L.is_destination = False
    M.is_destination = False
    
    # Sygnalizację świetlna
    # Faza 1: Pojazdy z B mogą jechać przez 5 sekund
    # Faza 2: Pojazdy z A (przez diagonal) mogą jechać przez 5 sekund
    C.traffic_light_controller = TrafficLightController([
        TrafficLightPhase(allowed_directions={A.id, E.id}, duration=5.0),
        TrafficLightPhase(allowed_directions={J.id}, duration=5.0)
    ])
    J.traffic_light_controller = TrafficLightController([
        TrafficLightPhase(allowed_directions={C.id, D.id}, duration=5.0),
        TrafficLightPhase(allowed_directions={K.id}, duration=5.0)
    ])
    H.traffic_light_controller = TrafficLightController([
        TrafficLightPhase(allowed_directions={G.id, F.id}, duration=5.0),
        TrafficLightPhase(allowed_directions={K.id, I.id}, duration=5.0)
    ])
    G.traffic_light_controller = TrafficLightController([
        TrafficLightPhase(allowed_directions={D.id, H.id}, duration=5.0),
        TrafficLightPhase(allowed_directions={L.id}, duration=5.0)
    ])
    D.traffic_light_controller = TrafficLightController([
        TrafficLightPhase(allowed_directions={G.id, B.id}, duration=5.0),
        TrafficLightPhase(allowed_directions={J.id}, duration=5.0)
    ])
    
    # Drogi
    network.add_two_way_road(
        from_id=A.id,
        to_id=B.id,
        speed_limit=50,
        lanes=2
    )
    
    network.add_two_way_road(
        from_id=A.id,
        to_id=C.id,
        speed_limit=50,
        lanes=2
    )
    
    network.add_two_way_road(
        from_id=B.id,
        to_id=D.id,
        speed_limit=50,
        lanes=1
    )
    
    network.add_two_way_road(
        from_id=C.id,
        to_id=J.id,
        speed_limit=50,
        lanes=1
    )

    network.add_two_way_road(
        from_id=D.id,
        to_id=J.id,
        speed_limit=50,
        lanes=1
    )

    network.add_two_way_road(
        from_id=C.id,
        to_id=E.id,
        speed_limit=50,
        lanes=1
    )

    network.add_two_way_road(
        from_id=D.id,
        to_id=G.id,
        speed_limit=50,
        lanes=1
    )

    network.add_two_way_road(
        from_id=E.id,
        to_id=F.id,
        speed_limit=50,
        lanes=1
    )

    network.add_two_way_road(
        from_id=G.id,
        to_id=H.id,
        speed_limit=50,
        lanes=1
    )

    network.add_two_way_road(
        from_id=H.id,
        to_id=F.id,
        speed_limit=50,
        lanes=1
    )

    network.add_two_way_road(
        from_id=G.id,
        to_id=L.id,
        speed_limit=50,
        lanes=1
    )

    network.add_two_way_road(
        from_id=I.id,
        to_id=L.id,
        speed_limit=50,
        lanes=1
    )

    network.add_two_way_road(
        from_id=F.id,
        to_id=M.id,
        speed_limit=50,
        lanes=1
    )

    network.add_two_way_road(
        from_id=I.id,
        to_id=M.id,
        speed_limit=50,
        lanes=1
    )

    network.add_two_way_road(
        from_id=H.id,
        to_id=I.id,
        speed_limit=50,
        lanes=1
    )

    network.add_two_way_road(
        from_id=H.id,
        to_id=K.id,
        speed_limit=50,
        lanes=1
    )
    network.add_two_way_road(
        from_id=J.id,
        to_id=K.id,
        speed_limit=50,
        lanes=1
    )
    
    return network

