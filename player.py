import pygame
from olive import Olive

class Player:
  
  def __init__(self, x, y, width, height, screen_width, screen_height, tile_size):
    RED = (255, 0, 0)
    self.normal_image = pygame.transform.scale(pygame.image.load("images/duck.png").convert_alpha(), (width, height))
    self.water_image = pygame.transform.scale(pygame.image.load("images/duck_water.png"), (width, height))
    self.remove_image = pygame.transform.scale(pygame.image.load("images/duck_remove.png"), (width, height))
    self.image = self.normal_image

    self.rect = self.image.get_rect(topleft=(x, y))
    self.rect = pygame.Rect(x, y, width, height)
    self.select_tile = pygame.Rect(x + width, y, width, height); 
    self.speed = 5

    self.tile_size = tile_size

    self.x = x
    self.y = y

    self.screen_width = screen_width
    self.screen_height = screen_height
    self.width = width
    self.height = height

    self.water_mode_start = None
    self.water_mode_duration = 2000
    self.remove_mode_start = None
    self.remove_mode_duration = 4000

    self.px = self.rect.x // self.tile_size
    self.py = self.rect.y // self.tile_size

  def unstuck(self, obstacles):
    for olive in obstacles:
      if not olive.is_obstacle():
        continue
      
      if self.rect.colliderect(olive.rect):
        overlap_x = min(self.rect.right, olive.rect.right) - max(self.rect.left, olive.rect.left)
        overlap_y = min(self.rect.bottom, olive.rect.bottom) - max(self.rect.top, olive.rect.top)
        overlap_area = overlap_x * overlap_y

        player_area = self.rect.width * self.rect.height
        overlap_ratio = overlap_area / player_area

        # Only "unstuck" if the player is at least 50% inside the olive
        if overlap_ratio < 0.5:
            continue

        # Now resolve by pushing player out (same logic as before)
        if self.rect.bottom > olive.rect.top and self.rect.top < olive.rect.top:
          self.rect.bottom = olive.rect.top  # Push up
        elif self.rect.top < olive.rect.bottom and self.rect.bottom > olive.rect.bottom:
          self.rect.top = olive.rect.bottom  # Push down
        elif self.rect.right > olive.rect.left and self.rect.left < olive.rect.left:
          self.rect.right = olive.rect.left  # Push left
        elif self.rect.left < olive.rect.right and self.rect.right > olive.rect.right:
          self.rect.left = olive.rect.right  # Push right

  def move(self, keys, obstacles):
    if self.water_mode_start is not None or self.remove_mode_start is not None:
      return
    
    def get_player_tile():
        return self.rect.centerx // self.tile_size, self.rect.centery // self.tile_size

    def get_adjacent_tile_offset(dx, dy):
        """ Get coordinates for a tile next to the player (never overlaps player tile). """
        player_tile_x, player_tile_y = get_player_tile()
        target_tile_x = player_tile_x + dx
        target_tile_y = player_tile_y + dy
        return target_tile_x * self.tile_size, target_tile_y * self.tile_size
    
    new_rect = self.rect.copy() 
    
    if keys[pygame.K_a] and self.rect.x > 0:
        new_rect.x -= self.speed
        self.select_tile.x, self.select_tile.y = get_adjacent_tile_offset(-1, 0)
        if not any(olive.rect.collidepoint(new_rect.center) for olive in obstacles):
            self.rect.x -= self.speed

    if keys[pygame.K_d] and self.rect.x < self.screen_width - self.rect.width:
        new_rect.x += self.speed
        self.select_tile.x, self.select_tile.y = get_adjacent_tile_offset(1, 0)
        if not any(olive.rect.collidepoint(new_rect.center) for olive in obstacles):
            self.rect.x += self.speed

    new_rect = self.rect.copy() 

    if keys[pygame.K_w] and self.rect.y > 0:
        new_rect.y -= self.speed
        self.select_tile.x, self.select_tile.y = get_adjacent_tile_offset(0, -1)
        if not any(olive.rect.collidepoint(new_rect.center) for olive in obstacles):
            self.rect.y -= self.speed

    if keys[pygame.K_s] and self.rect.y < self.screen_height - self.rect.height:
        new_rect.y += self.speed
        self.select_tile.x, self.select_tile.y = get_adjacent_tile_offset(0, 1)
        if not any(olive.rect.collidepoint(new_rect.center) for olive in obstacles):
            self.rect.y += self.speed



    self.unstuck(obstacles)

  def get_pos(self):
    return (self.rect.x, self.rect.y)

  def plant_olive(self, tile_size, weather):
    # Compute the grid-aligned position using the select_tile's coordinates.
    tile_x = ((self.select_tile.x + tile_size // 2)// tile_size) * tile_size
    tile_y = ((self.select_tile.y + + tile_size // 2) // tile_size) * tile_size 
    return Olive(tile_x, tile_y, tile_size, weather)
  
  def activate_water_mode(self):
    self.image = self.water_image
    self.water_mode_start = pygame.time.get_ticks()

  def activate_remove_mode(self):
    self.image = self.remove_image
    self.remove_mode_start = pygame.time.get_ticks()

  def update(self):
    if self.water_mode_start is not None:
      if pygame.time.get_ticks() - self.water_mode_start > self.water_mode_duration:
        self.water_mode_start = None
        self.image = self.normal_image
    if self.remove_mode_start is not None: 
      if pygame.time.get_ticks() - self.remove_mode_start > self.remove_mode_duration:
        self.remove_mode_start = None
        self.image = self.normal_image

  def draw(self, screen):
    # pygame.draw.rect(screen, self.color, self.rect)
    self.update(); 
    screen.blit(self.image, self.rect)

  def draw_select_tile(self, screen):
    WHITE = (255, 255, 255)
    pygame.draw.rect(screen, WHITE, self.select_tile, width=2)
    