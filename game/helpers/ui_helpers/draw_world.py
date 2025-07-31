import pygame


def draw_world(screen, world, camera_x, camera_y, game_x, game_y, tile_size, border_color, menu_color, black, darkness_alpha=0):
    """Draw the world tiles and walls."""
    screen.fill(border_color)
    pygame.draw.rect(screen, menu_color, (0, 0, screen.get_width(), 100))  # Top menu area
    pygame.draw.rect(screen, black, (game_x, game_y, screen.get_width() - 2 * game_x, screen.get_height() - game_y - 50))
    
    buffer = 6
    start_col = (camera_x // tile_size) - buffer
    end_col = ((camera_x + screen.get_width()) // tile_size) + buffer
    start_row = (camera_y // tile_size) - buffer
    end_row = ((camera_y + screen.get_height()) // tile_size) + buffer
    
    visible_walls = []
    for row in range(start_row, end_row):
        for col in range(start_col, end_col):
            tile_type = world.get_tile(col, row)
            rect = pygame.Rect(col * tile_size, row * tile_size, tile_size, tile_size)
            if tile_type == 'W':
                visible_walls.append(rect)
            else:
                draw_rect = rect.move(-camera_x + game_x, -camera_y + game_y)
                pygame.draw.rect(screen, (128, 128, 128), draw_rect)
    
    return visible_walls