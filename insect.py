import pygame
import random
import math

class Insect:
    
  def __init__(self, screen_width, screen_height, olives):
    self.screen_width = screen_width
    self.screen_height = screen_height
    self.size = 32  # Size of the insect in pixels
    self.speed = 0.75  # Movement speed in pixels per frame

    # Randomly choose a side to spawn off-screen.
    side = random.choice(['left', 'right', 'top', 'bottom'])
    if side == 'left':
      x = -self.size
      y = random.randint(0, screen_height)
    elif side == 'right':
      x = screen_width
      y = random.randint(0, screen_height)
    elif side == 'top':
      x = random.randint(0, screen_width)
      y = -self.size
    else:  # 'bottom'
      x = random.randint(0, screen_width)
      y = screen_height

    # Use a Vector2 for smooth position updates.
    self.pos = pygame.math.Vector2(x, y)

    # Load and scale the insect image.
    self.image = pygame.transform.scale(pygame.image.load("images/insect.png"), (self.size, self.size))
    self.rect = self.image.get_rect(topleft=(int(self.pos.x), int(self.pos.y)))

    # Randomly choose an olive to target (if any exist).
    grown_olives = []
    for olive in olives.values():
      if olive.growth_started:  # Only include olives that have started growing
        grown_olives.append(olive)

    # Pick a target if there are any grown olives
    if len(grown_olives) > 0:
      self.target = random.choice(grown_olives)
    else:
      self.target = None

    self.arrived = False  # Flag to indicate if the insect reached its target

    self.birth_time = pygame.time.get_ticks()
    self.amplitude = random.uniform(2, 5)  # Maximum offset in pixels
    self.frequency = random.uniform(2, 4)

    self.leaving = False  # Indicates if the insect is flying away
    self.departure_start_time = None  # Time when the insect started its departure
    self.exit_target = None  # Position where the insect will fly away

  def update(self):
    current_time = pygame.time.get_ticks()

    if self.leaving:
      # Move towards the off-screen exit target
      direction = self.exit_target - self.pos
      distance = direction.length()

      if distance <= self.speed:
        return True  # Mark for removal when off-screen
      else:
        direction_norm = direction.normalize()
        perpendicular = pygame.math.Vector2(-direction_norm.y, direction_norm.x)
        
        elapsed = (pygame.time.get_ticks() - self.departure_start_time) / 1000.0
        offset_amount = self.amplitude * math.sin(elapsed * self.frequency)
        wave_offset = perpendicular * offset_amount

        base_movement = direction_norm * self.speed
        self.pos += base_movement + wave_offset

      self.rect.topleft = (int(self.pos.x), int(self.pos.y))
      return False  # Still flying away

    elif self.target and not self.arrived:
      # Move towards the olive tree
      target_center = pygame.math.Vector2(self.target.rect.center)
      direction = target_center - self.pos
      distance = direction.length()

      if distance <= self.speed:
        self.pos = target_center
        self.arrived = True
        if self.target:
          self.target.infect()
          self.departure_start_time = pygame.time.get_ticks()  # Start departure timer
      else:
        direction_norm = direction.normalize()
        perpendicular = pygame.math.Vector2(-direction_norm.y, direction_norm.x)
        elapsed = (pygame.time.get_ticks() - self.birth_time) / 1000.0
        offset_amount = self.amplitude * math.sin(elapsed * self.frequency)
        wave_offset = perpendicular * offset_amount
        base_movement = direction_norm * self.speed
        self.pos += base_movement + wave_offset

      self.rect.topleft = (int(self.pos.x), int(self.pos.y))
      return False  # Still flying

    elif self.arrived and self.departure_start_time is not None:
      # Check if 2 seconds have passed since infection
      if current_time - self.departure_start_time >= 2000:
        self.leaving = True  # Start leaving
        self.choose_exit_location()

    return False

  
  def choose_exit_location(self):
    """Selects a random off-screen position for the insect to fly to."""
    side = random.choice(['left', 'right', 'top', 'bottom'])
    if side == 'left':
        self.exit_target = pygame.math.Vector2(-self.size, random.randint(0, self.screen_height))
    elif side == 'right':
        self.exit_target = pygame.math.Vector2(self.screen_width + self.size, random.randint(0, self.screen_height))
    elif side == 'top':
        self.exit_target = pygame.math.Vector2(random.randint(0, self.screen_width), -self.size)
    else:  # 'bottom'
        self.exit_target = pygame.math.Vector2(random.randint(0, self.screen_width), self.screen_height + self.size)

  def draw(self, screen):
      """Call update and then draw the insect on the screen."""
      self.update()
      screen.blit(self.image, self.rect)
