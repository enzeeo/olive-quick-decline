import pygame

class TileType():
  def __init__(self, type, color, is_solid):
    self.type = type
    # self.image = image
    self.color = pygame.Surface((100, 100))
    self.color.fill(color)
    self.is_solid = is_solid

class Map():
  def __init__(self, map_array, tile_type, tile_size):
    self.tile_type = tile_type
    self.tile_size = tile_size
    
    self.tiles = []
    for row in map_array:
      self.tiles_row = []
      for col in row: 
        self.tiles_row.append(col)
      self.tiles.append(self.tiles_row)

  def draw(self, screen):
    for y, row in enumerate(self.tiles): 
      for x, tile in enumerate(row): 
        location = (x * self.tile_size, y * self.tile_size)
        image = self.tile_type[tile].color
        screen.blit(image, location)
