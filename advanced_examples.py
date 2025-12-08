"""
Bardziej zaawansowane przykłady sieci drogowych.
"""

from graph import RoadNetwork


def create_grid_network(cols: int, rows: int, spacing: float = 100) -> RoadNetwork:
    """
    Tworzy sieć drogową w formie siatki.
    
    Args:
        cols: Liczba kolumn
        rows: Liczba wierszy
        spacing: Odległość między skrzyżowaniami
    
    Returns:
        Sieć w formie siatki
    """
    network = RoadNetwork()
    
    # Dodaj skrzyżowania
    intersections = {}
    for i in range(rows):
        for j in range(cols):
            name = f"Int({i},{j})"
            x = j * spacing
            y = i * spacing
            intersection = network.add_intersection(name, x, y)
            intersections[(i, j)] = intersection
    
    # Dodaj drogi poziome
    for i in range(rows):
        for j in range(cols - 1):
            from_int = intersections[(i, j)]
            to_int = intersections[(i, j + 1)]
            network.add_road(
                from_id=from_int.id,
                to_id=to_int.id,
                length=spacing,
                speed_limit=50,
                lanes=2
            )
    
    # Dodaj drogi pionowe
    for i in range(rows - 1):
        for j in range(cols):
            from_int = intersections[(i, j)]
            to_int = intersections[(i + 1, j)]
            network.add_road(
                from_id=from_int.id,
                to_id=to_int.id,
                length=spacing,
                speed_limit=50,
                lanes=2
            )
    
    return network


def create_complex_network() -> RoadNetwork:
    """Tworzy złożoną sieć drogową z różnymi topologiami."""
    network = RoadNetwork()
    
    # Główny ring
    ring = []
    for i in range(6):
        import math
        angle = 2 * math.pi * i / 6
        x = 200 + 150 * math.cos(angle)
        y = 200 + 150 * math.sin(angle)
        intersection = network.add_intersection(f"Ring{i}", x, y)
        ring.append(intersection)
    
    # Połącz ring
    for i in range(6):
        network.add_road(
            from_id=ring[i].id,
            to_id=ring[(i + 1) % 6].id,
            length=155,
            speed_limit=60,
            lanes=2
        )
    
    # Centrum
    center = network.add_intersection("Center", 200, 200)
    
    # Połącz centrum z ringiem
    for intersection in ring:
        network.add_road(
            from_id=center.id,
            to_id=intersection.id,
            length=150,
            speed_limit=50,
            lanes=1
        )
    
    # Obwodnica
    outer_ring = []
    for i in range(8):
        import math
        angle = 2 * math.pi * i / 8
        x = 200 + 300 * math.cos(angle)
        y = 200 + 300 * math.sin(angle)
        intersection = network.add_intersection(f"Outer{i}", x, y)
        outer_ring.append(intersection)
    
    # Połącz obwodnicę
    for i in range(8):
        network.add_road(
            from_id=outer_ring[i].id,
            to_id=outer_ring[(i + 1) % 8].id,
            length=237,
            speed_limit=80,
            lanes=3
        )
    
    # Połącz ring z obwodnicą
    for i in range(6):
        network.add_road(
            from_id=ring[i].id,
            to_id=outer_ring[i].id,
            length=150,
            speed_limit=70,
            lanes=2
        )
    
    return network


if __name__ == "__main__":
    from visualization import RoadNetworkVisualizer
    
    print("Tworzenie sieci w formie siatki 4x4...")
    grid_network = create_grid_network(4, 4, 80)
    
    visualizer = RoadNetworkVisualizer(title="Sieć - Siatka 4x4")
    visualizer.load_network(grid_network)
    visualizer.run()
