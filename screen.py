import pygame
import threading
import time
import numpy as np

# Screen dimensions
WIDTH, HEIGHT = 40, 200

buffer_lock = threading.Lock()

def horizontal_scanning():
    """Function to render the screen buffer line by line (separate thread)."""
    global mem
    while True:
        with buffer_lock:
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    color = mem[0xe000+(40*y)+x]
                    screen.set_at((x, y), color)
                pygame.display.update(pygame.Rect(0, y, WIDTH, 1))  # Update one line
                time.sleep(1 / (HEIGHT * 60))  # Simulate horizontal scanning at 60 Hz



