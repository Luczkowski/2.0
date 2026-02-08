"""
Przykłady wykorzystania grafu sieci drogowej.
"""

from graph import RoadNetwork, TrafficLight, TrafficLightState, TrafficLightController, TrafficLightPhase


def create_example_network() -> RoadNetwork:
    """Tworzy przykładową sieć drogową."""
    network = RoadNetwork()
    
    # Skrzyżowania
    A = network.add_intersection("Grunwaldzka x Droga Zielona", 0, 0)
    B = network.add_intersection("Droga Zielona x Gospody", 180, 0)
    C = network.add_intersection("Grunwaldzka x Pomorska", 0, 150)
    D = network.add_intersection("Pomorska x Gospody x Chłopska", 200, 125)
    E = network.add_intersection("Jelitkowo", 325, 100)
    F = network.add_intersection("Grunwaldzka x Piastowska x Rybińskiego", 0, 200)
    G = network.add_intersection("Piastowska x Chłopska", 220, 175)
    H = network.add_intersection("Piastowsaka E", 275, 170)
    I = network.add_intersection("Piastowska x Droszyńskiego", 50, 195)
    J = network.add_intersection("Grunwaldzka x Kołobrzeska", 30, 400)
    K = network.add_intersection("Kołobrzeska x Rzeczypospolitej", 250, 370)
    L = network.add_intersection("Chłopska x Jagiellońska", 230, 235)
    M = network.add_intersection("Chłopska x Komorowskiego", 240, 295)
    N = network.add_intersection("Droszyńskiego x Komorowskiego", 75, 275)
    O = network.add_intersection("Obrońców Wybrzerza E", 460, 280)
    P = network.add_intersection("Jagiellońska E", 450, 220)
    R = network.add_intersection("Kołobrzeska E", 470, 355)
    S = network.add_intersection("Rybińskiego W", -50, 200)
    
    # Punkty pośrednie
    C.is_destination = False
    D.is_destination = False
    F.is_destination = False
    G.is_destination = False
    I.is_destination = False
    L.is_destination = False
    M.is_destination = False
    
    # Sygnalizację świetlna
    # Faza 1: Pojazdy z B mogą jechać przez 5 sekund
    # Faza 2: Pojazdy z A (przez diagonal) mogą jechać przez 5 sekund
    C.traffic_light_controller = TrafficLightController([
        TrafficLightPhase(allowed_directions={A.id, F.id}, duration=5.0),
        TrafficLightPhase(allowed_directions={D.id}, duration=5.0)
    ])
    D.traffic_light_controller = TrafficLightController([
        TrafficLightPhase(allowed_directions={B.id, G.id}, duration=5.0),
        TrafficLightPhase(allowed_directions={C.id, E.id}, duration=5.0)
    ])
    F.traffic_light_controller = TrafficLightController([
        TrafficLightPhase(allowed_directions={C.id, J.id}, duration=5.0),
        TrafficLightPhase(allowed_directions={S.id, I.id}, duration=5.0)
    ])
    I.traffic_light_controller = TrafficLightController([
        TrafficLightPhase(allowed_directions={F.id, G.id}, duration=5.0),
        TrafficLightPhase(allowed_directions={N.id}, duration=5.0)
    ])
    G.traffic_light_controller = TrafficLightController([
        TrafficLightPhase(allowed_directions={D.id, L.id}, duration=5.0),
        TrafficLightPhase(allowed_directions={I.id, H.id}, duration=5.0)
    ])
    L.traffic_light_controller = TrafficLightController([
        TrafficLightPhase(allowed_directions={G.id, M.id}, duration=5.0),
        TrafficLightPhase(allowed_directions={P.id}, duration=5.0)
    ])
    M.traffic_light_controller = TrafficLightController([
        TrafficLightPhase(allowed_directions={L.id, K.id}, duration=5.0),
        TrafficLightPhase(allowed_directions={N.id, O.id}, duration=5.0)
    ])
    K.traffic_light_controller = TrafficLightController([
        TrafficLightPhase(allowed_directions={M.id}, duration=5.0),
        TrafficLightPhase(allowed_directions={R.id, J.id}, duration=5.0),
        
    ])
    O.traffic_light_controller = TrafficLightController([
        TrafficLightPhase(allowed_directions={P.id, R.id}, duration=5.0),
        TrafficLightPhase(allowed_directions={M.id}, duration=5.0)
    ])
    
    # Drogi
    roads = [
            (A.id, B.id),
            (A.id, C.id),
            (B.id, D.id),
            (C.id, D.id),
            (D.id, E.id),
            (C.id, F.id),
            (F.id, I.id),
            (I.id, G.id),
            (G.id, H.id),
            (D.id, G.id),
            (J.id, F.id),
            (J.id, K.id),
            (I.id, N.id),
            (N.id, M.id),
            (G.id, L.id),
            (L.id, M.id),
            (K.id, M.id),
            (M.id, O.id),
            (O.id, P.id),
            (P.id, L.id),
            (K.id, R.id),
            (O.id, R.id),
            (F.id, S.id),
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
        (0, 0.25),
        (1, 0.1),
        (4, 0.1),
        (7, 0.2),
        (9, 0.25),
        (10, 0.25),
        (13, 0.2),
        (14, 0.25),
        (15, 0.2),
        (16, 0.2),
        (17, 0.25),
    ]
    
    for intersection_id, spawn_rate in spawner_configs:
        fleet.add_spawner(
            spawn_intersection=network.get_intersection(intersection_id),
            spawn_rate=spawn_rate
        )
