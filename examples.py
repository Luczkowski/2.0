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


def print_network_info(network: RoadNetwork):
    """Wyświetla informacje o sieci."""
    print(f"\n{'='*60}")
    print(f"Sieć drogowa: {network}")
    print(f"{'='*60}\n")
    
    print("SKRZYŻOWANIA:")
    for intersection in network.get_all_intersections():
        print(f"  {intersection}")
    
    print("\nDROGI:")
    for road in network.get_all_roads():
        print(f"  {road}")
    
    print("\nDROGI WYCHODZĄCE Z KAŻDEGO SKRZYŻOWANIA:")
    for intersection in network.get_all_intersections():
        outgoing_roads = network.get_outgoing_roads(intersection.id)
        print(f"  {intersection.name} ({intersection.id}):")
        for road in outgoing_roads:
            print(f"    -> {road.to_intersection.name} ({road.to_intersection.id})")
    
    print("\nSĄSIEDZTWO:")
    for intersection in network.get_all_intersections():
        neighbors = network.get_neighbors(intersection.id)
        neighbor_names = [n.name for n in neighbors]
        print(f"  {intersection.name}: {neighbor_names}")


if __name__ == "__main__":
    # Utwórz i wyświetl przykładową sieć
    network = create_example_network()
    print_network_info(network)
    
    # Przykład: znalezienie drogi między dwoma skrzyżowaniami
    print(f"\nTest get_road_between:")
    road = network.get_road_between(from_id=0, to_id=1)
    if road:
        print(f"  Droga z A do B: {road}")
    else:
        print("  Droga nie istnieje")
    
    road = network.get_road_between(from_id=1, to_id=0)
    if road:
        print(f"  Droga z B do A: {road}")
    else:
        print("  Brak drogi z B do A (ta jest jednokierunkowa)")
