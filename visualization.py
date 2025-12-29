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
    COLOR_TRAFFIC_LIGHT_GREEN = (0, 255, 0)
    COLOR_TRAFFIC_LIGHT_RED = (255, 0, 0)
    COLOR_TRAFFIC_LIGHT_BORDER = (50, 50, 50)
    
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
        
        # Kontrola świateł
        self.selected_intersection: int | None = None
        self.show_light_controls = False

        # Kontrola spawnera
        self.show_spawn_controls: bool = False
        

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
        
        # Sprawdź czy istnieje droga w przeciwnym kierunku (dwukierunkowa)
        has_reverse = False
        if self.network:
            reverse_road = self.network.get_road_between(road.to_intersection.id, road.from_intersection.id)
            has_reverse = reverse_road is not None
        
        # Jeśli droga jest dwukierunkowa, przesuń ją o połowę szerokości na bok
        if has_reverse:
            # Oblicz wektor prostopadły do drogi
            dx = x2 - x1
            dy = y2 - y1
            length = math.sqrt(dx**2 + dy**2)
            
            if length > 0:
                # Znormalizuj wektor
                dx /= length
                dy /= length
                
                # Wektor prostopadły (obrót o 90 stopni)
                perp_dx = -dy
                perp_dy = dx
                
                # Przesunięcie (połowa szerokości drogi)
                offset = self.ROAD_WIDTH
                
                x1 += perp_dx * offset
                y1 += perp_dy * offset
                x2 += perp_dx * offset
                y2 += perp_dy * offset
        
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
        
        # Rysuj sygnalizację świetlną jeśli istnieje
        if intersection.traffic_light:
            self._draw_traffic_light(x, y, intersection.traffic_light)
        elif intersection.traffic_light_controller:
            self._draw_traffic_light_controller(x, y, intersection.traffic_light_controller, intersection)
    
    def _draw_traffic_light(self, x: int, y: int, traffic_light):
        """Rysuje sygnalizację świetlną przy skrzyżowaniu."""
        # Pozycja światła (nad skrzyżowaniem)
        light_x = x + 20
        light_y = y - 20
        light_radius = 8
        
        # Rysuj obramowanie
        pygame.draw.rect(self.screen, self.COLOR_TRAFFIC_LIGHT_BORDER,
                        (light_x - 12, light_y - 25, 24, 50), border_radius=5)
        pygame.draw.rect(self.screen, (200, 200, 200),
                        (light_x - 11, light_y - 24, 22, 48), border_radius=5)
        
        # Rysuj czerwone światło (góra)
        red_color = self.COLOR_TRAFFIC_LIGHT_RED if traffic_light.is_red() else (100, 100, 100)
        pygame.draw.circle(self.screen, red_color, (light_x, light_y - 10), light_radius)
        
        # Rysuj zielone światło (dół)
        green_color = self.COLOR_TRAFFIC_LIGHT_GREEN if traffic_light.is_green() else (100, 100, 100)
        pygame.draw.circle(self.screen, green_color, (light_x, light_y + 10), light_radius)
    
    def _draw_traffic_light_controller(self, x: int, y: int, controller, intersection):
        """Rysuje kontroler sygnalizacji z wieloma fazami."""
        current_phase = controller.get_current_phase()
        
        # Pobierz litery dozwolonych kierunków (ID skrzyżowań)
        allowed_ids = current_phase.allowed_directions
        allowed_text = ", ".join(str(id) for id in sorted(allowed_ids))
        
        # Pozycja nad skrzyżowaniem
        label_x = x + 25
        label_y = y - 25
        
        # Rysuj tło dla tekstu
        bg_width = 40
        bg_height = 20
        pygame.draw.rect(self.screen, self.COLOR_TRAFFIC_LIGHT_GREEN,
                        (label_x - bg_width//2, label_y - bg_height//2, bg_width, bg_height), 
                        border_radius=3)
        pygame.draw.rect(self.screen, self.COLOR_TRAFFIC_LIGHT_BORDER,
                        (label_x - bg_width//2, label_y - bg_height//2, bg_width, bg_height), 
                        width=2, border_radius=3)
        
        # Rysuj tekst z dozwolonymi kierunkami
        text = self.font_small.render(allowed_text, True, (0, 0, 0))
        text_rect = text.get_rect(center=(label_x, label_y))
        self.screen.blit(text, text_rect)
    
    def _draw_vehicle(self, vehicle: Vehicle):
        """Rysuje samochód na ekranie."""
        vx, vy = vehicle.get_current_position()
        
        # Oblicz przesunięcie dla drogi dwukierunkowej
        offset_x, offset_y = 0, 0
        if vehicle.current_road and self.network:
            # Sprawdź czy droga jest dwukierunkowa
            reverse_road = self.network.get_road_between(
                vehicle.current_road.to_intersection.id,
                vehicle.current_road.from_intersection.id
            )
            
            if reverse_road is not None:
                # Oblicz wektor prostopadły do drogi (w współrzędnych świata)
                dx = (vehicle.current_road.to_intersection.x - 
                      vehicle.current_road.from_intersection.x)
                dy = (vehicle.current_road.to_intersection.y - 
                      vehicle.current_road.from_intersection.y)
                length = math.sqrt(dx**2 + dy**2)
                
                if length > 0:
                    # Znormalizuj wektor
                    dx /= length
                    dy /= length
                    
                    # Wektor prostopadły (obrót o 90 stopni)
                    perp_dx = -dy
                    perp_dy = dx
                    
                    # Przesunięcie (połowa szerokości drogi)
                    offset = self.ROAD_WIDTH / self.scale
                    
                    offset_x = perp_dx * offset
                    offset_y = perp_dy * offset
        
        # Zastosuj przesunięcie do pozycji pojazdu
        x, y = self._world_to_screen(vx + offset_x, vy + offset_y)
        
        # Rysuj pojazd jako prostokąt
        vehicle_width = 8
        vehicle_height = 5
        
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
        # text = self.font_small.render(f"V{vehicle.id}", True, self.COLOR_TEXT)
        # text_rect = text.get_rect(center=(x, y - 15))
        # self.screen.blit(text, text_rect)
    
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
            "Kliknij skrzyżowanie - wybierz",
            "T - pokaż/ukryj kontrolę świateł",
            "[1-9] - wybierz fazę",
            "+ / - - zmień czas fazy (±1s)",
            "SHIFT + / - - zmień o ±5s",
            "[ / ] - zmień częstotliwość spawnu"
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

        # Informacje o spawnerach
        if self.selected_intersection is not None:
            spawners = self._get_spawners_for_selected_intersection()
            y_offset += 10
            self.screen.blit(
                self.font.render("Spawners:", True, self.COLOR_TEXT),
                (10, y_offset)
            )
            y_offset += 20

            for idx, spawner in enumerate(spawners):
                text = (
                    f"#{idx} "
                    f"rate={spawner.spawn_rate:.2f} pojazdów/s"
                )
                self.screen.blit(
                    self.font_small.render(text, True, self.COLOR_TEXT),
                    (10, y_offset)
                )
                y_offset += 18
    
    def _draw_light_control_panel(self):
        """Rysuje panel kontroli świateł dla wybranego skrzyżowania."""
        if not self.show_light_controls or self.selected_intersection is None:
            return
        
        intersection = self.network.get_intersection(self.selected_intersection)
        if not intersection or not intersection.traffic_light_controller:
            return
        
        controller = intersection.traffic_light_controller
        
        # Panel na prawej stronie
        panel_x = self.width - 300
        panel_y = 10
        panel_width = 290
        panel_height = 200
        
        # Tło panelu
        pygame.draw.rect(self.screen, (240, 240, 220),
                        (panel_x, panel_y, panel_width, panel_height),
                        border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 100),
                        (panel_x, panel_y, panel_width, panel_height),
                        width=2, border_radius=10)
        
        # Nagłówek
        title = f"Kontrola: {intersection.name}"
        text = self.font.render(title, True, (0, 0, 0))
        self.screen.blit(text, (panel_x + 10, panel_y + 10))
        
        # Informacje o fazach
        y = panel_y + 40
        for i, phase in enumerate(controller.phases):
            dirs = ", ".join(str(d) for d in sorted(phase.allowed_directions))
            is_current = i == controller.current_phase_index
            
            # Kolor tła dla aktywnej fazy
            if is_current:
                pygame.draw.rect(self.screen, (200, 255, 200),
                               (panel_x + 5, y - 2, panel_width - 10, 22),
                               border_radius=3)
            
            marker = "→" if is_current else " "
            phase_text = f"{marker} [{i+1}] Faza {i}: {phase.duration:.1f}s"
            text = self.font_small.render(phase_text, True, (0, 0, 0))
            self.screen.blit(text, (panel_x + 10, y))
            
            y += 20
            dir_text = f"    Kierunki: {dirs}"
            text = self.font_small.render(dir_text, True, (60, 60, 60))
            self.screen.blit(text, (panel_x + 10, y))
            y += 25
        
        # Instrukcje
        y = panel_y + panel_height - 30
        instr_text = "Wybierz [1-9], +/- zmień czas"
        text = self.font_small.render(instr_text, True, (100, 100, 100))
        self.screen.blit(text, (panel_x + 10, y))
    
    def run(self):
        """Główna pętla wizualizacji."""
        running = True
        selected_phase = 0  # Aktualnie wybrana faza do edycji
        
        while running:
            delta_time = self.clock.tick(60) / 1000.0  # Czas w sekundach
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_t:
                        # Toggle panel kontroli
                        self.show_light_controls = not self.show_light_controls
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                                     pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                        # Wybór fazy (1-9)
                        selected_phase = event.key - pygame.K_1
                    elif event.key in [pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS]:
                        # Zwiększ czas fazy
                        self._adjust_selected_light_phase(selected_phase, 
                                                          5.0 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1.0)
                    elif event.key in [pygame.K_MINUS, pygame.K_KP_MINUS]:
                        # Zmniejsz czas fazy
                        self._adjust_selected_light_phase(selected_phase,
                                                          -5.0 if pygame.key.get_mods() & pygame.KMOD_SHIFT else -1.0)
                    elif event.key == pygame.K_LEFTBRACKET:  # [
                        self._adjust_selected_spawner_rate(-0.1)

                    elif event.key == pygame.K_RIGHTBRACKET:  # ]
                        self._adjust_selected_spawner_rate(0.1)
                elif event.type == pygame.MOUSEMOTION:
                    self._update_hover(event.pos[0], event.pos[1])
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Lewy przycisk myszy
                        # Wybierz skrzyżowanie
                        if self.hovered_intersection is not None:
                            self.selected_intersection = self.hovered_intersection
                            self.show_light_controls = True
                            selected_phase = 0
            
            # Aktualizuj pojazdy
            self.update_vehicles(delta_time)
            
            # Aktualizuj sygnalizacje świetlne
            if self.network:
                for intersection in self.network.get_all_intersections():
                    if intersection.traffic_light:
                        intersection.traffic_light.update(delta_time)
                    if intersection.traffic_light_controller:
                        intersection.traffic_light_controller.update(delta_time)
            
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
            
            # Rysuj panel kontroli świateł
            self._draw_light_control_panel()
            
            # Zaktualizuj ekran
            pygame.display.flip()
        
        pygame.quit()
    
    def _adjust_selected_light_phase(self, phase_index: int, delta: float):
        """Dostosowuje czas trwania fazy dla wybranego skrzyżowania."""
        if self.selected_intersection is None:
            return
        
        intersection = self.network.get_intersection(self.selected_intersection)
        if not intersection or not intersection.traffic_light_controller:
            return
        
        controller = intersection.traffic_light_controller
        if 0 <= phase_index < len(controller.phases):
            controller.adjust_phase_duration(phase_index, delta)
            print(f"Faza {phase_index} skrzyżowania {intersection.name}: "
                  f"{controller.phases[phase_index].duration:.1f}s")

    def _get_spawners_for_selected_intersection(self):
        if not self.fleet or self.selected_intersection is None:
            return []

        return [
            spawner
            for spawner in self.fleet.spawners
            if spawner.spawn_intersection.id == self.selected_intersection
        ]

    def _adjust_selected_spawner_rate(self, delta: float):
        """Zwiększa lub zmniejsza częstotliwość spawnu (λ) dla wybranego skrzyżowania."""
        if not self.fleet or self.selected_intersection is None:
            return

        for spawner in self.fleet.spawners:
            if spawner.spawn_intersection.id == self.selected_intersection:
                spawner.spawn_rate = max(0.0, spawner.spawn_rate + delta)