import pygame
import sys, math
from game_util import *

pygame.init()
font = pygame.font.SysFont(None, 24)
clock = pygame.time.Clock()

small_font = pygame.font.SysFont("verdana", 36, True)
text_offset = 13

FPS = 60
FramePerSec = pygame.time.Clock()

width, height = 640, 640
screen = pygame.display.set_mode((width, height))

n = 6
x_buff, y_buff = 20, 20
dot_radius = 30
point_buff = (width - (2 * x_buff) - (n * 2 * dot_radius)) / (n - 1)
mid_x = (width - 2 * x_buff) / 2

triangle = build_board(n)

centers = []

for row in range(n):
    y_position = y_buff + dot_radius + row * (point_buff + 2 * dot_radius)
    x_positions = [x_buff + mid_x + (point_buff / 2 + dot_radius) * k for k in list(range(-row, row + 1, 2))]

    row_centers = []
    for x_pos in x_positions: 
        row_centers.append((x_pos, y_position))
    centers.append(row_centers)

color_lookup = {"r": (255, 0, 0),
                "g": (0, 255, 0),
                "b": (0, 0, 255),
                ".": (0, 0, 0)}

my_font = pygame.font.SysFont('Comic Sans MS', 30)
cheats = False
current_color = "r"
blah = True
while True:
    screen.fill((255, 255, 255))

    pygame.draw.circle(screen, color_lookup[current_color], (x_buff, y_buff), dot_radius)

    for row in range(n):
        pygame.draw.line(screen, (0, 0, 0), centers[row][0], centers[row][-1], 3)            # Across
        pygame.draw.line(screen, (0, 0, 0), centers[row][-1], centers[n-1][row], 3)          # Down Left
        pygame.draw.line(screen, (0, 0, 0), centers[row][0], centers[n-1][n - row - 1], 3)   # Down Right  

    poly_count = 0
    for row in range(n):
        for index in range(row + 1):
            center = centers[row][index]
            if triangle[row][index] == ".":
                pygame.draw.circle(screen, (255, 255, 255), center, dot_radius)
                pygame.draw.circle(screen, (0, 0, 0), center, dot_radius, 3)
            else:
                pygame.draw.circle(screen, color_lookup[triangle[row][index]], center, dot_radius)
                pygame.draw.circle(screen, (0, 0, 0), center, dot_radius, 3)
                text_surface = small_font.render(triangle[row][index].upper(), False, (0, 0, 0))
                screen.blit(text_surface, (center[0] - text_offset, center[1] - text_offset - 8))

            """if row < n - 1:
                corners = triangle[row][index] + triangle[row + 1][index] + triangle[row+1][index+1]
                if "r" in corners and "g" in corners and "b" in corners:
                    poly_count += 1
                    moved_center = (centers[row][index][0], centers[row][index][1] + point_buff / 2 + 2 * dot_radius)
                    pygame.draw.circle(screen, (255, 0, 255), moved_center, dot_radius)
            if row > 0 and 0 < index and index < row:
                corners = triangle[row][index] +  triangle[row - 1][index - 1] +  triangle[row - 1][index]
                if "r" in corners and "g" in corners and "b" in corners:
                    poly_count += 1
                    moved_center = (centers[row][index][0], centers[row][index][1] - point_buff / 2 - 2 * dot_radius)
                    pygame.draw.circle(screen, (255, 0, 255), moved_center, dot_radius)"""

    text_surface = my_font.render(str(poly_count), False, (255, 0, 255))
    screen.blit(text_surface, (width - 4 * x_buff, y_buff))


    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                print("resetting!")
                triangle = build_board(n)
            if event.key == pygame.K_SPACE:
                current_color = {"r": "g", "g": "b", "b": "r"}[current_color]
            if event.key == pygame.K_p:
                triangle = random_triangle(n)
            if event.key == pygame.K_c:
                cheats = True
                

        if event.type == pygame.MOUSEBUTTONUP:
            done = False
            x, y = pygame.mouse.get_pos()
            for row in range(n):
                for index in range(row + 1):
                    center = centers[row][index]
                    dist = math.hypot(center[0] - x, center[1] - y)
                    if dist <= dot_radius:
                        if (index != 0 or current_color in "rg") and (index != row or current_color in "rb") and (row != n - 1 or current_color in "gb"):
                            if triangle[row][index] == "." or cheats:
                                triangle[row] = triangle[row][:index] + current_color + triangle[row][index+1:]
                            else:
                                print("already color")
                        else:
                            print("bad color!")
                        done = True
                        break

                if done: break

    pygame.display.flip()
    pygame.time.Clock()