"""
Moduł do wizualizacji sieci drogowej za pomocą pygame.
"""

import pygame
import math
from typing import Tuple, List, Optional
from graph import RoadNetwork, Intersection, Road
from vehicle import Vehicle, VehicleController


class RoadNetworkVisualizer:
    """Klasa do wizualizacji sieci drogowej."""
    
    # Kolory
    COLOR_BACKGROUND = (240, 240, 240)
    COLOR_ROAD = (100, 100, 100)
    COLOR_ROAD_LANE = (200, 200, 200)
    COLOR_INTERSECTION = (0, 100, 200)
    COLOR_INTERSECTION_HOVER = (0, 150, 255)
    COLOR_TEXT = (50, 50, 50)
    COLOR_ARROW = (150, 0, 0)
    COLOR_VEHICLE = (255, 50, 50)
    
    # Wymiary
    INTERSECTION_RADIUS = 12
    ARROW_SIZE = 20
    ROAD_WIDTH = 8
    
    def __init__(self, 
                 width: int = 1200,
                 height: int = 800,
                 title: str = "Symulator Ruchu Drogowego"):
        """
        Inicjalizuje wizualizator.
        
        Args:
            width: Szerokość okna
            height: Wysokość okna
            title: Tytuł okna
        """
        pygame.init()
        self.width = width
        self.height = height
        self.title = title
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 16)
        
        self.network: RoadNetwork | None = None
        self.offset_x = 50
        self.offset_y = 50
        self.scale = 1.0
        self.hovered_intersection: int | None = None
        
        # Flota pojazdów
        self.fleet = None
        

    def load_network(self, network: RoadNetwork, auto_scale: bool = True):
        """
        Ładuje sieć do wizualizacji.
        
        Args:
            network: Sieć drogowa do wyświetlenia
            auto_scale: Czy automatycznie skalować siatkę
        """
        self.network = network
        if auto_scale and network.num_intersections() > 0:
            self._calculate_scale()
    
    def _calculate_scale(self):
        """Automatycznie oblicza skalę do wyświetlenia całej sieci."""
        if not self.network or self.network.num_intersections() == 0:
            return
        
        intersections = self.network.get_all_intersections()
        
        # Znajdź granice sieci
        min_x = min(i.x for i in intersections)
        max_x = max(i.x for i in intersections)
        min_y = min(i.y for i in intersections)
        max_y = max(i.y for i in intersections)
        
        # Oblicz skalę aby zmieścić sieć w oknie
        width_available = self.width - 2 * self.offset_x
        height_available = self.height - 2 * self.offset_y
        
        network_width = max_x - min_x
        network_height = max_y - min_y
        
        if network_width == 0:
            network_width = 1
        if network_height == 0:
            network_height = 1
        
        scale_x = width_available / network_width
        scale_y = height_available / network_height
        
        self.scale = min(scale_x, scale_y) * 0.9  # 90% aby zostawić margines
        
        # Wycentruj sieć
        self.offset_x = self.offset_x + (width_available - network_width * self.scale) / 2
        self.offset_y = self.offset_y + (height_available - network_height * self.scale) / 2
    
    def _world_to_screen(self, x: float, y: float) -> Tuple[int, int]:
        """Konwertuje współrzędne świata na ekran."""
        screen_x = int(self.offset_x + x * self.scale)
        screen_y = int(self.offset_y + y * self.scale)
        return screen_x, screen_y
    
    def _screen_to_world(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """Konwertuje współrzędne ekranu na świat."""
        x = (screen_x - self.offset_x) / self.scale
        y = (screen_y - self.offset_y) / self.scale
        return x, y
    
    def set_fleet(self, fleet):
        """Ustawia flotę pojazdów do wizualizacji."""
        self.fleet = fleet
    
    def update_vehicles(self, delta_time: float):
        """Aktualizuje flotę pojazdów."""
        if self.fleet:
            self.fleet.update(delta_time)
    
    def _draw_road(self, road: Road):
        """Rysuje drogę z strzałką kierunkową."""
        x1, y1 = self._world_to_screen(road.from_intersection.x, road.from_intersection.y)
        x2, y2 = self._world_to_screen(road.to_intersection.x, road.to_intersection.y)
        
        # Rysuj główną linię drogi
        pygame.draw.line(self.screen, self.COLOR_ROAD, (x1, y1), (x2, y2), self.ROAD_WIDTH)
        
        # Rysuj strzałkę kierunkową
        self._draw_arrow(x1, y1, x2, y2)
    
    def _draw_arrow(self, x1: int, y1: int, x2: int, y2: int):
        """Rysuje strzałkę wskazującą kierunek drogi."""
        # Punkt środkowy drogi
        mid_x = (x1 + x2) // 2
        mid_y = (y1 + y2) // 2
        
        # Wektor kierunku
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx**2 + dy**2)
        
        if length < 1:
            return
        
        # Znormalizuj wektor
        dx /= length
        dy /= length
        
        # Punkty strzałki
        arrow_size = self.ARROW_SIZE
        arrow_angle = math.pi / 6  # 30 stopni
        
        # Koniec strzałki
        end_x = mid_x + dx * arrow_size
        end_y = mid_y + dy * arrow_size
        
        # Boki strzałki
        side_angle = math.atan2(dy, dx)
        left_x = end_x - arrow_size * math.cos(side_angle + arrow_angle)
        left_y = end_y - arrow_size * math.sin(side_angle + arrow_angle)
        
        right_x = end_x - arrow_size * math.cos(side_angle - arrow_angle)
        right_y = end_y - arrow_size * math.sin(side_angle - arrow_angle)
        
        # Rysuj strzałkę
        pygame.draw.polygon(self.screen, self.COLOR_ARROW, 
                           [(end_x, end_y), (left_x, left_y), (right_x, right_y)])
    
    def _draw_intersection(self, intersection: Intersection):
        """Rysuje skrzyżowanie."""
        x, y = self._world_to_screen(intersection.x, intersection.y)
        
        # Wybierz kolor w zależności od stanu (hover)
        color = (self.COLOR_INTERSECTION_HOVER 
                 if self.hovered_intersection == intersection.id 
                 else self.COLOR_INTERSECTION)
        
        # Rysuj koło
        pygame.draw.circle(self.screen, color, (x, y), self.INTERSECTION_RADIUS)
        pygame.draw.circle(self.screen, self.COLOR_TEXT, (x, y), self.INTERSECTION_RADIUS, 2)
        
        # Rysuj ID skrzyżowania
        text = self.font_small.render(str(intersection.id), True, self.COLOR_TEXT)
        text_rect = text.get_rect(center=(x, y))
        self.screen.blit(text, text_rect)
    
    def _draw_vehicle(self, vehicle: Vehicle):
        """Rysuje samochód na ekranie."""
        vx, vy = vehicle.get_current_position()
        x, y = self._world_to_screen(vx, vy)
        
        # Rysuj pojazd jako prostokąt
        vehicle_width = 16
        vehicle_height = 10
        
        # Oblicz kąt, w którym jedzie pojazd
        angle = 0
        if vehicle.current_road:
            dx = (vehicle.current_road.to_intersection.x - 
                  vehicle.current_road.from_intersection.x)
            dy = (vehicle.current_road.to_intersection.y - 
                  vehicle.current_road.from_intersection.y)
            angle = math.atan2(dy, dx)
        
        # Utwórz powierzchnię pojazdu i obróć ją
        vehicle_surface = pygame.Surface((vehicle_width, vehicle_height), pygame.SRCALPHA)
        pygame.draw.ellipse(vehicle_surface, (255, 50, 50), vehicle_surface.get_rect())
        
        # Obróć powierzchnię
        rotated_surface = pygame.transform.rotate(vehicle_surface, -math.degrees(angle))
        rotated_rect = rotated_surface.get_rect(center=(x, y))
        
        self.screen.blit(rotated_surface, rotated_rect)
        
        # Rysuj ID pojazdu
        text = self.font_small.render(f"V{vehicle.id}", True, self.COLOR_TEXT)
        text_rect = text.get_rect(center=(x, y - 15))
        self.screen.blit(text, text_rect)
    
    def _update_hover(self, mouse_x: int, mouse_y: int):
        """Aktualizuje informację o najechaniu myszką na skrzyżowanie."""
        self.hovered_intersection = None
        
        if not self.network:
            return
        
        for intersection in self.network.get_all_intersections():
            ix, iy = self._world_to_screen(intersection.x, intersection.y)
            dist = ((ix - mouse_x)**2 + (iy - mouse_y)**2) ** 0.5
            
            if dist < self.INTERSECTION_RADIUS + 5:
                self.hovered_intersection = intersection.id
                break
    
    def _draw_info_panel(self):
        """Rysuje panel informacyjny."""
        if not self.network:
            return
        
        num_vehicles = self.fleet.num_vehicles() if self.fleet else 0
        
        info_lines = [
            f"Skrzyżowania: {self.network.num_intersections()}",
            f"Drogi: {self.network.num_roads()}",
            f"Pojazdy: {num_vehicles}",
            "",
            "Sterowanie:",
            "ESC - zamknij",
            "Najdź myszkę nad skrzyżowanie aby zobaczyć szczegóły"
        ]
        
        y_offset = 10
        for line in info_lines:
            text = self.font_small.render(line, True, self.COLOR_TEXT)
            self.screen.blit(text, (10, y_offset))
            y_offset += 25
        
        # Informacje o najechaniu
        if self.hovered_intersection is not None:
            intersection = self.network.get_intersection(self.hovered_intersection)
            if intersection:
                outgoing = self.network.get_outgoing_roads(intersection.id)
                detail_text = f"{intersection.name} ({len(outgoing)} wychodzących dróg)"
                text = self.font.render(detail_text, True, self.COLOR_INTERSECTION)
                self.screen.blit(text, (10, self.height - 40))
    
    def run(self):
        """Główna pętla wizualizacji."""
        running = True
        
        while running:
            delta_time = self.clock.tick(60) / 1000.0  # Czas w sekundach
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEMOTION:
                    self._update_hover(event.pos[0], event.pos[1])
            
            # Aktualizuj pojazdy
            self.update_vehicles(delta_time)
            
            # Rysuj tło
            self.screen.fill(self.COLOR_BACKGROUND)
            
            # Rysuj sieć
            if self.network:
                # Rysuj drogi
                for road in self.network.get_all_roads():
                    self._draw_road(road)
                
                # Rysuj skrzyżowania
                for intersection in self.network.get_all_intersections():
                    self._draw_intersection(intersection)
                
                # Rysuj pojazdy z floty
                if self.fleet:
                    for vehicle in self.fleet.get_vehicles():
                        self._draw_vehicle(vehicle)
            
            # Rysuj panel informacyjny
            self._draw_info_panel()
            
            # Zaktualizuj ekran
            pygame.display.flip()
        
        pygame.quit()
