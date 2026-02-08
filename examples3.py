"""
Przykłady wykorzystania grafu sieci drogowej.
"""

from graph import RoadNetwork, TrafficLight, TrafficLightState, TrafficLightController, TrafficLightPhase


def create_example_network() -> RoadNetwork:
    """Tworzy przykładową sieć drogową."""
    network = RoadNetwork()
    
    # Skrzyżowania
    A = network.add_intersection("A Kielnińska x Barniewicka", 300, 0)
    B = network.add_intersection("B Barniewicka x Nowy Świat", 0, 600)
    C = network.add_intersection("C Kielnińska W",250, -50)
    D = network.add_intersection("D Wodnika x Nowy Świat", 650, 600)
    E = network.add_intersection("E Wodnika x Kielnińska", 650, 150)
    F = network.add_intersection("F Nowy Świat W", -100, 600)
    G = network.add_intersection("G Planetarna S", 0, 700)
    H = network.add_intersection("H Nowy Świat x Koziorożca", 450, 600)
    I = network.add_intersection("I Nowy Świat x Zeua", 200, 600)
    J = network.add_intersection("J Spacerowa E", 750, 50)
    K = network.add_intersection("K Nowy Świat x Penelopy", 150, 650)
    L = network.add_intersection("L Wodnika S", 650, 700)
    M = network.add_intersection("M Wodnika x Junony", 650, 450)
    N = network.add_intersection("N Wodnika x Jednorożca", 650, 300)
    O = network.add_intersection("O Kielnińska x Balcerskiego", 450, 75)
    P = network.add_intersection("P Barniewicka x Niedziałkowskiego", 225, 150)
    R = network.add_intersection("R Barniewicka x Junony", 150, 400)
    S = network.add_intersection("S Balcerskiego x Niedziałkowskiego", 375, 225)
    T = network.add_intersection("T Zeusa x Niedziałkowskiego", 512, 262)
    U = network.add_intersection("U Kielnińska E", 750, 150)
    W = network.add_intersection("W Jednorożca E", 750, 300)
    Y = network.add_intersection("Y Marsa E", 750, 450)
    Z = network.add_intersection("Z Junony x Koziorożca", 450, 450)
    AA = network.add_intersection("AA Junony x Zeusa", 250, 430)

    # Punkty pośrednie
    A.is_destination = False
    B.is_destination = False
    D.is_destination = False
    E.is_destination = False
    H.is_destination = False
    I.is_destination = False
    M.is_destination = False
    N.is_destination = False
    O.is_destination = False
    P.is_destination = False
    R.is_destination = False
    
    # Sygnalizację świetlna
    # Faza 1: Pojazdy z B mogą jechać przez 5 sekund
    # Faza 2: Pojazdy z A (przez diagonal) mogą jechać przez 5 sekund

    # To są jedyne światłą na Osowej, są wyłączone, aby przetestować sieć bez sygnalizacji świetlnej

    # O.traffic_light_controller = TrafficLightController([
    #     TrafficLightPhase(allowed_directions={A.id, E.id}, duration=5.0),
    #     TrafficLightPhase(allowed_directions={S.id}, duration=5.0)
    # ])

    # Teoretyczne światła do testów, sygmalizacja umieszczona na drogach wokół dzielnicy
    
    # A.traffic_light_controller = TrafficLightController([
    #     TrafficLightPhase(allowed_directions={C.id, O.id}, duration=5.0),
    #     TrafficLightPhase(allowed_directions={P.id}, duration=5.0)
    # ])
    # O.traffic_light_controller = TrafficLightController([
    #     TrafficLightPhase(allowed_directions={A.id, E.id}, duration=5.0),
    #     TrafficLightPhase(allowed_directions={S.id}, duration=5.0)
    # ])
    # E.traffic_light_controller = TrafficLightController([
    #     TrafficLightPhase(allowed_directions={O.id, U.id}, duration=5.0),
    #     TrafficLightPhase(allowed_directions={J.id, N.id, T.id}, duration=5.0)
    # ])
    # B.traffic_light_controller = TrafficLightController([
    #     TrafficLightPhase(allowed_directions={F.id, I.id}, duration=5.0),
    #     TrafficLightPhase(allowed_directions={R.id, G.id}, duration=5.0)
    # ])
    # I.traffic_light_controller = TrafficLightController([
    #     TrafficLightPhase(allowed_directions={B.id, H.id}, duration=5.0),
    #     TrafficLightPhase(allowed_directions={AA.id, K.id}, duration=5.0)
    # ])
    # H.traffic_light_controller = TrafficLightController([
    #     TrafficLightPhase(allowed_directions={I.id, D.id}, duration=5.0),
    #     TrafficLightPhase(allowed_directions={Z.id}, duration=5.0)
    # ])
    # D.traffic_light_controller = TrafficLightController([
    #     TrafficLightPhase(allowed_directions={H.id}, duration=5.0),
    #     TrafficLightPhase(allowed_directions={M.id, L.id}, duration=5.0)
    # ])
    # P.traffic_light_controller = TrafficLightController([
    #     TrafficLightPhase(allowed_directions={S.id}, duration=5.0),
    #     TrafficLightPhase(allowed_directions={A.id, R.id}, duration=5.0)
    # ])
    # R.traffic_light_controller = TrafficLightController([
    #     TrafficLightPhase(allowed_directions={AA.id}, duration=5.0),
    #     TrafficLightPhase(allowed_directions={P.id, B.id}, duration=5.0)
    # ])
    # M.traffic_light_controller = TrafficLightController([
    #     TrafficLightPhase(allowed_directions={Y.id, Z.id}, duration=5.0),
    #     TrafficLightPhase(allowed_directions={N.id, D.id}, duration=5.0)
    # ])
    # N.traffic_light_controller = TrafficLightController([
    #     TrafficLightPhase(allowed_directions={W.id, T.id}, duration=5.0),
    #     TrafficLightPhase(allowed_directions={M.id, E.id}, duration=5.0)
    # ])
    
    # Drogi
    roads = [
            (F.id, B.id),
            (G.id, B.id),
            (B.id, I.id),
            (I.id, K.id),
            (I.id, H.id),
            (H.id, D.id),
            (A.id, C.id),
            (E.id, J.id),
            (L.id, D.id),
            (M.id, D.id),
            (M.id, N.id),
            (N.id, E.id),
            (A.id, O.id),
            (E.id, O.id),
            (A.id, P.id),
            (B.id, R.id),
            (P.id, R.id),
            (S.id, P.id),
            (S.id, O.id),
            (S.id, T.id),
            (T.id, N.id),
            (T.id, E.id),
            (U.id, E.id),
            (W.id, N.id),
            (Y.id, M.id),
            (Z.id, M.id),
            (Z.id, T.id),
            (Z.id, H.id),
            (AA.id, I.id),
            (AA.id, Z.id),
            (AA.id, T.id),
            (AA.id, R.id),
        ]
        
    for from_id, to_id in roads:
        network.add_two_way_road(
            from_id=from_id,
            to_id=to_id,
            speed_limit=50,
            lanes=2
        )

    return network

def setup_example_spawners(fleet, network):
    """
    Konfiguruje spawnery pojazdów dla przykładowej sieci.
    
    Args:
        fleet: Obiekt VehicleFleet
        network: Obiekt RoadNetwork
    """
    spawner_configs = [
        (2, 0.25),
        (5, 0.1),
        (6, 0.1),
        (9, 0.25),
        (10, 0.1),
        (11, 0.25),
        (17, 0.15),
        (18, 0.15),
        (19, 0.2),
        (20, 0.2),
        (21, 0.2),
        (22, 0.15),
        (23, 0.15),
    ]
    
    for intersection_id, spawn_rate in spawner_configs:
        fleet.add_spawner(
            spawn_intersection=network.get_intersection(intersection_id),
            spawn_rate=spawn_rate
        )
