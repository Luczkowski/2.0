"""
Przykłady wykorzystania grafu sieci drogowej.
"""

from graph import RoadNetwork


def create_example_network() -> RoadNetwork:
    """Tworzy przykładową sieć drogową."""
    network = RoadNetwork()
    
    # Dodaj skrzyżowania
    A = network.add_intersection("Skrzyżowanie A", 0, 0)
    B = network.add_intersection("Skrzyżowanie B", 100, 0)
    C = network.add_intersection("Skrzyżowanie C", 100, 100)
    D = network.add_intersection("Skrzyżowanie D", 0, 100)
    
    # Dodaj drogi
    network.add_road(
        from_id=A.id,
        to_id=B.id,
        length=100,
        speed_limit=50,
        lanes=2
    )

    network.add_road(
        from_id=B.id,
        to_id=A.id,
        length=100,
        speed_limit=50,
        lanes=2
    )
    
    network.add_road(
        from_id=B.id,
        to_id=C.id,
        length=100,
        speed_limit=50,
        lanes=2
    )
    
    network.add_road(
        from_id=C.id,
        to_id=D.id,
        length=100,
        speed_limit=50,
        lanes=1
    )
    
    network.add_road(
        from_id=D.id,
        to_id=A.id,
        length=100,
        speed_limit=50,
        lanes=1
    )
    
    # Dodatkowo - drogi diagonalne
    network.add_road(
        from_id=A.id,
        to_id=C.id,
        length=141.4,
        speed_limit=60,
        lanes=1
    )
    
    return network

