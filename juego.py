import pygame
import sys
import random
from pygame.locals import *

# Inicialización de pygame
pygame.init()

# Constantes del juego
TILE_SIZE = 30
ROWS, COLS = 15, 15
WIDTH, HEIGHT = TILE_SIZE * COLS, TILE_SIZE * ROWS + 50
FPS = 10

# Paleta de colores morados
BLACK = (0, 0, 0)
PURPLE_WALL = (102, 51, 153)       # Morado oscuro para paredes
PURPLE_DOT = (230, 230, 250)       # Lavanda para puntos
PURPLE_GHOST = (186, 85, 211)      # Morado medio para fantasma
PURPLE_TEXT = (255, 255, 255)      # Blanco para texto
YELLOW_PACMAN = (255, 255, 0)      # Amarillo para Pac-Man (se mantiene para contraste)
WHITE = (255, 255, 255)

# Mapa del laberinto (1 = pared, 0 = camino, 2 = punto)
level = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 1, 1, 2, 1, 2, 1, 2, 1, 2, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1],
    [1, 2, 1, 2, 2, 2, 1, 2, 1, 2, 2, 2, 1, 2, 1],
    [1, 2, 1, 1, 1, 2, 1, 2, 1, 2, 1, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 1, 1, 1, 2, 1, 2, 1, 2, 1, 1, 1, 2, 1],
    [1, 2, 1, 2, 2, 2, 1, 2, 1, 2, 2, 2, 1, 2, 1],
    [1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 1, 1, 2, 1, 2, 1, 2, 1, 2, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Configuración de la ventana
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Comic Sans MS", 24)

# Estados del juego
MENU = 0
PLAYING = 1
GAME_OVER = 2
WIN = 3
game_state = MENU

# Posiciones iniciales
pacman_pos = [1, 1]
ghost_pos = [7, 7]
score = 0
direction = [0, 0]
ghost_direction = [0, 1]

def draw_maze():
    for row in range(ROWS):
        for col in range(COLS):
            tile = level[row][col]
            rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            
            if tile == 1:  # Pared
                pygame.draw.rect(screen, PURPLE_WALL, rect, border_radius=3)
            elif tile == 2:  # Punto
                pygame.draw.circle(screen, PURPLE_DOT, 
                                 (col * TILE_SIZE + TILE_SIZE // 2, 
                                  row * TILE_SIZE + TILE_SIZE // 2), 
                                 3)

def draw_pacman():
    pac_rect = pygame.Rect(
        pacman_pos[1] * TILE_SIZE + 2, 
        pacman_pos[0] * TILE_SIZE + 2, 
        TILE_SIZE - 4, TILE_SIZE - 4
    )
    
    # Animación de apertura/cierre de boca
    mouth_angle = pygame.time.get_ticks() % 1000 / 500 * 0.8
    
    # Determinar dirección de la boca
    if direction == [0, 1]:  # Derecha
        start_angle = 0.2 + mouth_angle
        end_angle = 2 * 3.14 - 0.2 - mouth_angle
    elif direction == [0, -1]:  # Izquierda
        start_angle = 3.14 + 0.2 + mouth_angle
        end_angle = 3.14 - 0.2 - mouth_angle
    elif direction == [-1, 0]:  # Arriba
        start_angle = 3.14/2 + 0.2 + mouth_angle
        end_angle = 3.14/2 - 0.2 - mouth_angle
    elif direction == [1, 0]:  # Abajo
        start_angle = 3*3.14/2 + 0.2 + mouth_angle
        end_angle = 3*3.14/2 - 0.2 - mouth_angle
    else:  # Sin movimiento (boca cerrada)
        start_angle = 0
        end_angle = 2 * 3.14
    
    pygame.draw.arc(screen, YELLOW_PACMAN, pac_rect, start_angle, end_angle, TILE_SIZE // 2 - 2)

def draw_ghost():
    ghost_rect = pygame.Rect(
        ghost_pos[1] * TILE_SIZE + 2, 
        ghost_pos[0] * TILE_SIZE + 2, 
        TILE_SIZE - 4, TILE_SIZE - 4
    )
    pygame.draw.rect(screen, PURPLE_GHOST, ghost_rect, border_radius=TILE_SIZE//2)
    
    # Ojos del fantasma
    eye_radius = TILE_SIZE // 6
    pygame.draw.circle(screen, WHITE, 
                      (ghost_pos[1] * TILE_SIZE + TILE_SIZE // 3, 
                       ghost_pos[0] * TILE_SIZE + TILE_SIZE // 3), 
                      eye_radius)
    pygame.draw.circle(screen, WHITE, 
                      (ghost_pos[1] * TILE_SIZE + 2 * TILE_SIZE // 3, 
                       ghost_pos[0] * TILE_SIZE + TILE_SIZE // 3), 
                      eye_radius)
    pygame.draw.circle(screen, BLACK, 
                      (ghost_pos[1] * TILE_SIZE + TILE_SIZE // 3, 
                       ghost_pos[0] * TILE_SIZE + TILE_SIZE // 3), 
                      eye_radius // 2)
    pygame.draw.circle(screen, BLACK, 
                      (ghost_pos[1] * TILE_SIZE + 2 * TILE_SIZE // 3, 
                       ghost_pos[0] * TILE_SIZE + TILE_SIZE // 3), 
                      eye_radius // 2)

def move_entity(pos, direction):
    new_row = pos[0] + direction[0]
    new_col = pos[1] + direction[1]
    
    if 0 <= new_row < ROWS and 0 <= new_col < COLS and level[new_row][new_col] != 1:
        return [new_row, new_col]
    return pos

def ghost_ai():
    directions = [[0, 1], [1, 0], [0, -1], [-1, 0]]
    valid_directions = []
    
    for d in directions:
        new_pos = move_entity(ghost_pos, d)
        if new_pos != ghost_pos:
            valid_directions.append(d)
    
    if valid_directions:
        return random.choice(valid_directions)
    return [0, 0]

def draw_menu():
    screen.fill(BLACK)
    
    title = font.render("PAC-MAN", True, PURPLE_GHOST)
    start_text = font.render("Presiona ESPACIO para comenzar", True, PURPLE_TEXT)
    controls = font.render("Usa las flechas para mover a Pac-Man", True, PURPLE_TEXT)
    
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2))
    screen.blit(controls, (WIDTH // 2 - controls.get_width() // 2, HEIGHT // 2 + 50))

def draw_game_over(win):
    screen.fill(BLACK)
    
    if win:
        message = font.render("¡GANASTE!", True, (200, 162, 200))  # Morado claro
    else:
        message = font.render("GAME OVER", True, PURPLE_GHOST)
    
    score_text = font.render(f"Puntuación: {score}", True, PURPLE_TEXT)
    restart = font.render("Presiona R para reiniciar", True, PURPLE_TEXT)
    
    screen.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGHT // 3))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
    screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT // 2 + 50))

def reset_game():
    global pacman_pos, ghost_pos, score, game_state, direction
    
    # Resetear posiciones
    pacman_pos = [1, 1]
    ghost_pos = [7, 7]
    direction = [0, 0]
    score = 0
    
    # Restaurar puntos
    for row in range(ROWS):
        for col in range(COLS):
            if level[row][col] == 0:
                level[row][col] = 2
    
    game_state = PLAYING

# Bucle principal del juego
running = True
while running:
    clock.tick(FPS)
    
    # Manejo de eventos
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if game_state == MENU and event.key == K_SPACE:
                reset_game()
            elif game_state in (GAME_OVER, WIN) and event.key == K_r:
                reset_game()
            elif game_state == PLAYING:
                if event.key == K_UP: direction = [-1, 0]
                elif event.key == K_DOWN: direction = [1, 0]
                elif event.key == K_LEFT: direction = [0, -1]
                elif event.key == K_RIGHT: direction = [0, 1]
    
    # Lógica del juego
    if game_state == PLAYING:
        # Movimiento de Pac-Man
        pacman_pos = move_entity(pacman_pos, direction)
        
        # Comer puntos
        if level[pacman_pos[0]][pacman_pos[1]] == 2:
            level[pacman_pos[0]][pacman_pos[1]] = 0
            score += 10
        
        # Movimiento del fantasma
        if random.random() < 0.2:  # 20% de probabilidad de cambiar dirección
            ghost_direction = ghost_ai()
        ghost_pos = move_entity(ghost_pos, ghost_direction)
        
        # Colisión con fantasma
        if pacman_pos == ghost_pos:
            game_state = GAME_OVER
        
        # Verificar victoria
        if all(2 not in row for row in level):
            game_state = WIN
    
    # Dibujado
    screen.fill(BLACK)
    
    if game_state == MENU:
        draw_menu()
    elif game_state in (GAME_OVER, WIN):
        draw_game_over(game_state == WIN)
    else:
        draw_maze()
        draw_pacman()
        draw_ghost()
        
        # Mostrar puntuación
        score_text = font.render(f"Puntos: {score}", True, PURPLE_TEXT)
        screen.blit(score_text, (10, HEIGHT - 40))
    
    pygame.display.flip()

pygame.quit()
sys.exit()