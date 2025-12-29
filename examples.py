"""
Przykłady wykorzystania grafu sieci drogowej.
"""

from graph import RoadNetwork, TrafficLight, TrafficLightState, TrafficLightController, TrafficLightPhase


def create_example_network() -> RoadNetwork:
    """Tworzy przykładową sieć drogową."""
    network = RoadNetwork()
    
    # Skrzyżowania
    A = network.add_intersection("Grunwaldzka N", 520, -100)
    B = network.add_intersection("Wojska Polskiego W", 220, 0)
    C = network.add_intersection("Grunwaldzka x Wojska Polskiego", 660, 65)
    D = network.add_intersection("Grunwaldzka x Szymanowskiego", 740, 165)
    E = network.add_intersection("Grunwaldzka x Żołnierzy Wyklętych", 940, 400)
    F = network.add_intersection("Grunwaldzka x Partyzantów x Jaśkowa Dolina", 1470, 820)
    G = network.add_intersection("Wiadukt kolejowy", 1250, 50)
    H = network.add_intersection("Żołnierzy Wyklętych x Chrzanowskiego x Partyzantów", 480, 620)
    I = network.add_intersection("Żołnierzy Wyklętych S", 0, 800)
    J = network.add_intersection("Chrzanowskiego x Szymanowskiego", 325, 435)
    K = network.add_intersection("Chrzanowskiego N", 0, 25)
    L = network.add_intersection("Jaśkowa Dolina S", 1000, 1200)
    M = network.add_intersection("Grunwaldzka x Do Studzienki", 1770, 1050)
    N = network.add_intersection("Do Studzienki S", 1370, 1450)
    
    # Punkty pośrednie
    C.is_destination = False
    D.is_destination = False
    E.is_destination = False
    F.is_destination = False
    H.is_destination = False
    J.is_destination = False
    
    # Sygnalizację świetlna
    # Faza 1: Pojazdy z B mogą jechać przez 5 sekund
    # Faza 2: Pojazdy z A (przez diagonal) mogą jechać przez 5 sekund
    # C.traffic_light_controller = TrafficLightController([
    #     TrafficLightPhase(allowed_directions={A.id, E.id}, duration=5.0),
    #     TrafficLightPhase(allowed_directions={J.id}, duration=5.0)
    # ])
    # J.traffic_light_controller = TrafficLightController([
    #     TrafficLightPhase(allowed_directions={C.id, D.id}, duration=5.0),
    #     TrafficLightPhase(allowed_directions={K.id}, duration=5.0)
    # ])
    # H.traffic_light_controller = TrafficLightController([
    #     TrafficLightPhase(allowed_directions={G.id, F.id}, duration=5.0),
    #     TrafficLightPhase(allowed_directions={K.id, I.id}, duration=5.0)
    # ])
    # G.traffic_light_controller = TrafficLightController([
    #     TrafficLightPhase(allowed_directions={D.id, H.id}, duration=5.0),
    #     TrafficLightPhase(allowed_directions={L.id}, duration=5.0)
    # ])
    # D.traffic_light_controller = TrafficLightController([
    #     TrafficLightPhase(allowed_directions={G.id, B.id}, duration=5.0),
    #     TrafficLightPhase(allowed_directions={J.id}, duration=5.0)
    # ])
    
    # Drogi
    network.add_two_way_road(
        from_id=A.id,
        to_id=C.id,
        speed_limit=50,
        lanes=2
    )
    network.add_two_way_road(
        from_id=C.id,
        to_id=D.id,
        speed_limit=50,
        lanes=2
    )
    network.add_two_way_road(
        from_id=D.id,
        to_id=E.id,
        speed_limit=50,
        lanes=2
    )
    network.add_two_way_road(
        from_id=E.id,
        to_id=F.id,
        speed_limit=50,
        lanes=2
    )
    network.add_two_way_road(
        from_id=G.id,
        to_id=E.id,
        speed_limit=50,
        lanes=2
    )
    network.add_two_way_road(
        from_id=H.id,
        to_id=I.id,
        speed_limit=50,
        lanes=2
    )
    network.add_two_way_road(
        from_id=H.id,
        to_id=J.id,
        speed_limit=50,
        lanes=2
    )
    network.add_two_way_road(
        from_id=J.id,
        to_id=K.id,
        speed_limit=50,
        lanes=2
    )
    network.add_two_way_road(
        from_id=H.id,
        to_id=F.id,
        speed_limit=50,
        lanes=2
    )
    network.add_two_way_road(
        from_id=B.id,
        to_id=C.id,
        speed_limit=50,
        lanes=2
    )
    network.add_two_way_road(
        from_id=D.id,
        to_id=J.id,
        speed_limit=50,
        lanes=2
    )
    network.add_two_way_road(
        from_id=E.id,
        to_id=H.id,
        speed_limit=50,
        lanes=2
    )
    network.add_two_way_road(
        from_id=F.id,
        to_id=L.id,
        speed_limit=50,
        lanes=2
    )
    network.add_two_way_road(
        from_id=F.id,
        to_id=M.id,
        speed_limit=50,
        lanes=2
    )
    network.add_two_way_road(
        from_id=M.id,
        to_id=N.id,
        speed_limit=50,
        lanes=2
    )
    return network

