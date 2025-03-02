import sys
import pygame
from player import Player
from map import TileType, Map
from insect import Insect
from mutantInsect import MutantInsect
import random

pygame.init()

# Grid dimensions (11 rows x 15 columns)
COLUMNS = 15
ROWS = 11

# Define a fixed virtual resolution for design (tiles will be square based on this)
BASE_WIDTH, BASE_HEIGHT = 960, 704
# Compute tile size so that they always remain square
tile_size = min(BASE_WIDTH // COLUMNS, BASE_HEIGHT // ROWS)

# Create a virtual surface to draw the game
game_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))

# Open a resizable window
screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("BIOS 15127")

# Create a simple alternating map array with 9 rows and 11 columns.
map_array = [
    [1 if (x + y) % 2 == 0 else 0 for x in range(COLUMNS)]
    for y in range(ROWS)
]

# GREEN = (0, 255, 0)
# BROWN = (139, 69, 19)
BLACK = (0, 0, 0)  # background for letterboxing

GREEN = (144, 238, 144)  # Grass green
DARK_GREEN = (56, 102, 65)
BROWN = (139, 69, 19)    # Wood brown
DARK_BROWN = (100, 50, 0) 
YELLOW = (255, 223, 0)
WHITE = (255, 255, 255)

tile_types = [
    TileType("dirt", DARK_GREEN, False),
    TileType("grass", GREEN, False)
]

center_tile_x = COLUMNS // 2
center_tile_y = ROWS // 2

player_x = center_tile_x * tile_size + tile_size // 2 - tile_size // 2
player_y = center_tile_y * tile_size + tile_size // 2 - tile_size // 2

map_obj = Map(map_array, tile_types, tile_size)
player = Player(player_x, player_y, tile_size, tile_size, BASE_WIDTH, BASE_HEIGHT, tile_size)
olives = {}
pending_olive_removals = []

insect_spawn_timer = pygame.time.get_ticks()
insect_spawn_delay = 5000  # milliseconds
insects = []
mutant_insect_spawn_timer = pygame.time.get_ticks()
mutant_insect_spawn_delay = 5000
mutant_insects = []

protections = 1

score = 0
# Use pygame's consistent built-in font
font = pygame.font.SysFont("Arial", 22)

start_time = pygame.time.get_ticks()  # Get the time when the game starts
total_time = 120000 # 120000  # 2 minutes in milliseconds (120 * 1000)

weather_temperature = random.randint(50, 100)
weather_update_interval = 10000  # 20 seconds in milliseconds
last_weather_update = pygame.time.get_ticks() 

def generate_weighted_temperature(current_temp):
  """Generate a new temperature close to the current temperature."""
  new_temp = round(random.gauss(current_temp, 5))  # Normal distribution centered at current_temp
  return max(50, min(100, new_temp))  # Keep within range

def reset_game():
  global player, olives, insects, pending_olive_removals, start_time, game_over
  global total_time, weather_temperature, last_weather_update, score, mutant_insects 

  player = Player(player_x, player_y, tile_size, tile_size, BASE_WIDTH, BASE_HEIGHT, tile_size)
  olives = {}
  insects = []
  mutant_insects = []
  pending_olive_removals = []
  start_time = pygame.time.get_ticks()
  weather_temperature = random.randint(50, 100)
  last_weather_update = pygame.time.get_ticks() 
  score = 0
  game_over = False

  # Reset timer to full time
  total_time = 120000  # 60 seconds again

font_big = pygame.font.SysFont('Arial', 50, bold=True)
font_small = pygame.font.SysFont('Arial', 30)
font_smallest = pygame.font.SysFont('Arial', 20)

def draw_button(screen, text, rect, color, text_color):
  pygame.draw.rect(screen, color, rect, border_radius=10)
  label = font_small.render(text, True, text_color)
  label_rect = label.get_rect(center=rect.center)
  screen.blit(label, label_rect)

def draw_gameover_screen(screen, score):
  screen.fill(GREEN)

  # Draw wood-like panel
  panel_rect = pygame.Rect(100, 100, 400, 500)
  pygame.draw.rect(screen, BROWN, panel_rect, border_radius=30)
  pygame.draw.rect(screen, DARK_BROWN, panel_rect, 5, border_radius=30)

  # Draw "Game Over"
  game_over_text = font_big.render("GAME OVER", True, WHITE)
  screen.blit(game_over_text, (panel_rect.centerx - game_over_text.get_width() // 2, 140))

  # Draw level (static for now, or you could pass level if needed)
  info_text = font_small.render("Your Scored", True, WHITE)
  screen.blit(info_text, (panel_rect.centerx - info_text.get_width() // 2, 200))

  # Draw score
  score_text = font_big.render(f"{score:,}", True, YELLOW)
  screen.blit(score_text, (panel_rect.centerx - score_text.get_width() // 2, 250))

  # Draw buttons (Restart)
  restart_button = pygame.Rect(panel_rect.centerx - 100, 350, 200, 50)
  menu_button = pygame.Rect(panel_rect.centerx - 100, 420, 200, 50)

  draw_button(screen, "RESTART", restart_button, WHITE, BROWN)
  draw_button(screen, "MAIN MENU", menu_button, WHITE, BROWN)
  
  pygame.display.flip()
  return restart_button, menu_button  # Game should not restart yet

def draw_start_screen(screen):
  screen.fill(GREEN)

  # Wooden panel
  panel_rect = pygame.Rect(100, 100, 400, 500)
  pygame.draw.rect(screen, BROWN, panel_rect, border_radius=30)
  pygame.draw.rect(screen, DARK_BROWN, panel_rect, 5, border_radius=30)

  # Title
  title_text = font_big.render("WELCOME!", True, WHITE)
  screen.blit(title_text, (panel_rect.centerx - title_text.get_width() // 2, 140))

  # Play button
  play_button = pygame.Rect(panel_rect.centerx - 150, 220, 300, 50)
  draw_button(screen, "PLAY", play_button, WHITE, BROWN)

  # Instructions button
  instructions_button = pygame.Rect(panel_rect.centerx - 150, 290, 300, 50)
  draw_button(screen, "INSTRUCTIONS", instructions_button, WHITE, BROWN)

  # Exit button
  exit_button = pygame.Rect(panel_rect.centerx - 150, 360, 300, 50)
  draw_button(screen, "EXIT", exit_button, WHITE, BROWN)

  pygame.display.flip()

  return play_button, instructions_button, exit_button


def draw_instructions_screen(screen):
    screen.fill(GREEN)

    screen_width, screen_height = screen.get_size()

    # Make the panel wider and centered
    panel_width = 800
    panel_height = 500
    panel_x = (screen_width - panel_width) // 2
    panel_y = (screen_height - panel_height) // 2

    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

    pygame.draw.rect(screen, BROWN, panel_rect, border_radius=30)
    pygame.draw.rect(screen, DARK_BROWN, panel_rect, 5, border_radius=30)

    instructions_text = [
        "INSTRUCTIONS",
        "1. Use WASD keys to move, P to plant, O to water, and R to remove",
        "2. Watering and removing plants takes time",
        "3. Collect olives from tree for points using SPACE",
        "4. Use L to protect or revive a tree (1 per game)",
        "5. Remove bugs by left clicking on them with your mouse before they",
        "    infect your trees",
        "6. Collect as many points before the time runs out!",
        "7. Dead trees cannot produce olives", 
        ""
    ]

    # Start Y position based on panel position (more flexible)
    y = panel_y + 40
    text_padding_left = 30  # Left margin padding inside the panel

    for line in instructions_text:
        text_surface = font_smallest.render(line, True, WHITE)
        screen.blit(text_surface, (panel_x + text_padding_left, y))
        y += 40

    # Position the BACK button within the panel
    back_button = pygame.Rect(panel_rect.centerx - 100, panel_y + panel_height - 70, 200, 50)
    draw_button(screen, "BACK", back_button, WHITE, BROWN)

    pygame.display.flip()

    return back_button

#------------------- MAIN GAME LOOP -----------------------------

reset_game()

running = True
clock = pygame.time.Clock()

in_start_screen = True
in_instructions_screen = False
game_running = False
game_over = False

while running:
    screen.fill(GREEN)
    clock.tick(60)

    if in_start_screen:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
      
        play_btn, instr_btn, exit_btn = draw_start_screen(screen)
        pygame.display.flip()

        if event.type == pygame.MOUSEBUTTONDOWN:  # Left click
          mouse_pos = pygame.mouse.get_pos()

          if play_btn.collidepoint(mouse_pos):
            in_start_screen = False
            game_running = True  # Start the game
            start_time = pygame.time.get_ticks()
            break
          elif instr_btn.collidepoint(mouse_pos):
            in_start_screen = False
            in_instructions_screen = True
            break
          elif exit_btn.collidepoint(mouse_pos):
            pygame.quit()
            sys.exit()
            break

    elif in_instructions_screen:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        back_btn = draw_instructions_screen(screen)
        pygame.display.flip()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if back_btn.collidepoint(mouse_pos):
                in_instructions_screen = False
                in_start_screen = True  # Back to start screen

    elif game_over:
       for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        restart_button, menu_button = draw_gameover_screen(screen, score)

        if event.type == pygame.MOUSEBUTTONDOWN:
          mouse_pos = pygame.mouse.get_pos()
          if restart_button.collidepoint(mouse_pos):
            reset_game()
            game_running = True
            break
          elif menu_button.collidepoint(mouse_pos):
            reset_game()
            in_start_screen = True
            break

    elif game_running:
        elapsed_time = pygame.time.get_ticks() - start_time
        remaining_time = max(0, (total_time - elapsed_time) // 1000)
        minutes = remaining_time // 60
        seconds = remaining_time % 60
        timer_text = f"{minutes:02}:{seconds:02}"

        current_time = pygame.time.get_ticks()
        if current_time - last_weather_update >= weather_update_interval:
          weather_temperature = generate_weighted_temperature(weather_temperature)  # Pick a new temperature
          last_weather_update = current_time  # Reset the timer

        for olive in olives.values():
          olive.update_weather(weather_temperature)

        if remaining_time <= 0:
          game_over = True
          game_running = False
          continue

        if not game_over:
          for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if not game_over:   
              # Update display mode if window is resized
              if event.type == pygame.VIDEORESIZE:
                  screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
              if (event.type == pygame.KEYDOWN and player.water_mode_start is None and 
                  player.remove_mode_start is None):
                if event.key == pygame.K_p:
                    olive = player.plant_olive(map_obj.tile_size, weather_temperature)
                    tile_coord = (olive.rect.x // map_obj.tile_size, olive.rect.y // map_obj.tile_size)
                    if tile_coord not in olives:
                        olives[tile_coord] = olive
                if event.key == pygame.K_o:
                    for olive in olives.values():
                        if player.select_tile.colliderect(olive.rect):
                            olive.start_growth()
                    player.activate_water_mode()
                if event.key == pygame.K_SPACE:
                  for olive in olives.values():
                    if olive.fruit_ready and player.select_tile.colliderect(olive.rect):
                      if olive.harvest(): 
                        score += 1000
                if event.key == pygame.K_l:
                    for olive in olives.values():
                      if player.select_tile.colliderect(olive.rect):
                          if protections > 0:
                            olive.protect()
                            protections = protections - 1

                if event.key == pygame.K_r: 
                  for tile_coord, olive in olives.items():
                    if player.select_tile.colliderect(olive.rect):
                        removal_time = pygame.time.get_ticks() + 4000  # 4 seconds later
                        pending_olive_removals.append((tile_coord, removal_time))
                        break
                    
                  player.activate_remove_mode()

              if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for insect in insects[:]:  
                  if insect.rect.collidepoint(mouse_pos):
                      insects.remove(insect)
                for mutant_insect in mutant_insects[:]:
                  if mutant_insect.rect.collidepoint(mouse_pos):
                      mutant_insects.remove(mutant_insect)

              if remaining_time <= 0:
                game_over = True
                game_running = False
                break

                          
        # Spawn insects periodically if there are olives
        if olives and remaining_time > total_time // (1000 * 2):
            current_time = pygame.time.get_ticks()
            if (current_time - insect_spawn_timer >= insect_spawn_delay):
                new_insect = Insect(BASE_WIDTH, BASE_HEIGHT, olives)
                insects.append(new_insect)
                insect_spawn_timer = current_time

        if olives and remaining_time < total_time // (1000 * 2):
            current_time = pygame.time.get_ticks()
            if (current_time - mutant_insect_spawn_timer >= mutant_insect_spawn_delay):
                new_mutant_insect = MutantInsect(BASE_WIDTH, BASE_HEIGHT, olives)
                mutant_insects.append(new_mutant_insect)
                mutant_insect_spawn_timer = current_time

        current_time = pygame.time.get_ticks()
        for tile_coord, removal_time in pending_olive_removals[:]:
            if current_time >= removal_time:
                if tile_coord in olives:
                    del olives[tile_coord]
                pending_olive_removals.remove((tile_coord, removal_time))

        keys = pygame.key.get_pressed()
        obstacles = [olive for olive in olives.values() if olive.is_obstacle()]
        player.move(keys, obstacles)

        # Draw all game elements on the virtual game_surface
        game_surface.fill(GREEN)
        map_obj.draw(game_surface)

        for olive in olives.values():
          if olive.protected == True: 
            BROWN = (139, 69, 19)
            pygame.draw.rect(game_surface, BROWN, olive.rect)

        player.draw_select_tile(game_surface)

        for olive in olives.values():
          if olive.rect.bottom < player.rect.bottom:
            olive.draw(game_surface)
        player.draw(game_surface)
        for olive in olives.values():
          if olive.rect.bottom >= player.rect.bottom:
            olive.draw(game_surface)
        
        insects_to_remove = []
        mutant_insects_to_remove = []
        for insect in insects:
          if insect.update():  # If update() returns True, the insect has flown away
              insects_to_remove.append(insect)
          else:
              insect.draw(game_surface)

        for mutant_insect in mutant_insects:
          if mutant_insect.update():  # If update() returns True, the insect has flown away
              mutant_insects_to_remove.append(mutant_insect)
          else:
              mutant_insect.draw(game_surface)

        for insect in insects_to_remove:
          insects.remove(insect)

        for mutant_insect in mutant_insects_to_remove:
          mutant_insects.remove(mutant_insect)
          
        score_text = font.render("Score: " + str(score), True, (255, 255, 255))
        game_surface.blit(score_text, (10, 10))

        # **Draw Countdown Timer in the Middle**
        text_surface = font.render(timer_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(BASE_WIDTH // 2, 10 + font.get_height() // 2))  # Center at top middle
        game_surface.blit(text_surface, text_rect)

        weather_text = font.render(f"Weather: {weather_temperature}°F", True, (255, 255, 255))
        weather_rect = weather_text.get_rect(topright=(BASE_WIDTH - 10, 10))  # Align right
        game_surface.blit(weather_text, weather_rect)

        # When drawing to the actual screen, compute a uniform scale factor so tiles remain square.
        window_width, window_height = screen.get_size()
        scale_factor = min(window_width / BASE_WIDTH, window_height / BASE_HEIGHT)
        scaled_width = int(BASE_WIDTH * scale_factor)
        scaled_height = int(BASE_HEIGHT * scale_factor)
        scaled_surface = pygame.transform.scale(game_surface, (scaled_width, scaled_height))

        # Center the scaled surface on the window (adding letterboxing if necessary)
        x = (window_width - scaled_width) // 2
        y = (window_height - scaled_height) // 2
        screen.fill(BLACK)
        screen.blit(scaled_surface, (x, y))
        pygame.display.flip()

pygame.quit()
