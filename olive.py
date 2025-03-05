import pygame

class Olive:

  def __init__(self, x, y, tile_size, weather):
    self.tile_size = tile_size
    # Load and scale images for the different stages
    self.image_seed = pygame.image.load("images/olive_seed.png")
    self.image_seed = pygame.transform.scale(self.image_seed, (tile_size, tile_size))

    self.image_teen = pygame.image.load("images/olive_teen.png")
    self.image_teen = pygame.transform.scale(self.image_teen, (tile_size, tile_size))

    self.image_adult = pygame.image.load("images/olive_adult.png")
    self.image_adult = pygame.transform.scale(self.image_adult, (tile_size, tile_size))

    self.image_harvest = pygame.image.load("images/olive_adult_fruit.png")
    self.image_harvest = pygame.transform.scale(self.image_harvest, (tile_size, tile_size))

    self.image_sick = pygame.image.load("images/olive_sick.png")
    self.image_sick = pygame.transform.scale(self.image_sick, (tile_size, tile_size))

    self.image_dead = pygame.image.load("images/olive_dead.png")
    self.image_dead = pygame.transform.scale(self.image_dead, (tile_size, tile_size))
    
    # Start with the seed image
    self.image = self.image_seed

    self.rect = pygame.Rect(x, y, tile_size, tile_size)
    # Record the time (in milliseconds) when the olive was planted
    self.growth_started = False
    self.start_time = None

    self.x = x
    self.y = y
    self.rect = self.image.get_rect(topleft=(x, y))
    self.rect = pygame.Rect(x, y, tile_size, tile_size)

    self.fruit_ready = False
    self.last_production_time = pygame.time.get_ticks()

    self.status = "healthy"
    self.unhealthy_start_time = None
    self.protected = False

    self.weather = weather
    self.infection_rate = self.calculate_infection_rate()

  def calculate_infection_rate(self):
    optimal_weather = 80
    max_rate = 4000  # 2 seconds (fastest infection rate)
    min_rate = 10000  # 10 seconds (slowest infection rate)

    distance = abs(self.weather - optimal_weather)
    rate = min_rate - (min_rate - max_rate) * (1 - (distance / 40))

    return max(max_rate, min_rate, rate) / 1000.0
  
  def start_growth(self):
    if not self.growth_started and self.status == "healthy":
      self.growth_started = True
      self.start_time = pygame.time.get_ticks()
      self.last_production_time = pygame.time.get_ticks()

  def infect(self):
    """Called when an insect reaches this olive."""
    if self.status == "healthy" and not self.protected:
      self.unhealthy_start_time = pygame.time.get_ticks()
      self.status = "unhealthy"
      # Stop any further fruit production.
      self.fruit_ready = True

  def mutant_infect(self):
    if self.status == "healthy":
      self.unhealthy_start_time = pygame.time.get_ticks()
      self.status = "unhealthy"
      # Stop any further fruit production.
      self.fruit_ready = True

  def is_obstacle(self):
    if self.growth_started:
      elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000.0
      # Consider grown (teen/adult) if elapsed time is 2 seconds or more
      return elapsed_time >= 2
    return False
  
  def protect(self):
    self.protected = True
    self.protected_time = pygame.time.get_ticks()
  
  def update_weather(self, new_weather):
    self.weather = new_weather
    self.infection_rate = self.calculate_infection_rate()

  def update(self):
    if not self.growth_started: 
      return
    
    current_time = pygame.time.get_ticks()
    elapsed_time = (current_time - self.start_time) / 1000.0

    if self.status == "healthy":
      if elapsed_time >= 10:
        self.image = self.image_adult
        if not self.fruit_ready and (current_time - self.last_production_time >= 3000):
          self.fruit_ready = True
      elif elapsed_time >= 4: 
        self.image = self.image_teen
      else:
        self.image = self.image_seed

    elif self.status == "unhealthy":
      time_since_infection = (current_time - self.unhealthy_start_time) / 1000.0

      if not self.protected:
        if time_since_infection >= self.infection_rate and self.status != "dead":
          self.image = self.image_dead
          self.status = "dead"
          self.fruit_ready = False
        elif time_since_infection >= self.infection_rate // 2 and self.status != "sick":
          self.image = self.image_sick
          self.status = "sick"

      elif self.protected: 
        time_since_protection = (current_time - self.protected_time) / 1000.0
        if time_since_protection >= 6:
          self.image = self.image_adult
          self.status = "healthy"
          self.fruit_ready = True


    elif self.status == "sick":
      if not self.protected:
        time_since_infection = (current_time - self.unhealthy_start_time) / 1000.0
        if time_since_infection >= self.infection_rate and self.status != "dead":
          self.image = self.image_dead
          self.status = "dead"
          self.fruit_ready = False

      elif self.protected: 
        time_since_protection = (current_time - self.protected_time) / 1000.0
        if time_since_protection >= 4:
          self.image = self.image_adult
          self.status = "unhealthy"
          self.fruit_ready = True

    elif self.status == "dead":
      if self.protected: 
        time_since_protection = (current_time - self.protected_time) / 1000.0
        if time_since_protection >= 2:
          self.image = self.image_sick
          self.status = "sick"
          self.fruit_ready = True

  def harvest(self):
    """If fruit is available, harvest it and reset the production timer."""
    if self.fruit_ready and self.status != "dead":
      self.fruit_ready = False
      self.last_production_time = pygame.time.get_ticks()
      self.image = self.image_adult
      return True 
    return False

  def draw(self, screen):
    self.update(); 
    if self.fruit_ready and self.status != "dead":
      # Draw a simple circle to indicate that an olive is ready for harvest.
      self.image = self.image_harvest
    screen.blit(self.image, self.rect)
