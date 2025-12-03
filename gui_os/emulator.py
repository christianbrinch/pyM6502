import threading
import time
import pygame
import mos6502

WIDTH, HEIGHT = 640, 400

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("6502 emulator")
clock = pygame.time.Clock()

# Initialize memory (shared resource)
mem = mos6502.Memory(file="os.rom")

# Initialize CPU
cpu = mos6502.Processor(mem)

# Screen buffer 0xe000-0xff40 = 8000 bytes(shared resource)
buffer_lock = threading.Lock()


def cpu_step(cpu, mem):
    run = 1
    step = False
    while run:
        if step:
            print("Press enter")
            input()
        with buffer_lock:
            if not step:
                cpu.exec(output=False)
            else:
                cpu.exec(output=True, zeropage=True, mempage=2)
            if not (cpu.reg_p & 0x16):
                step = True


def horizontal_scanning(mem):
    """Function to render the screen buffer line by line (separate thread)."""
    """
    while True:
        for y in range(HEIGHT//2):
            for x in range(WIDTH//16):
                for bit,p in enumerate('{0:08b}'.format(mem[0xe000+(40*y)+x])):
                    color = 3*[255*int(p)]
                    screen.set_at((2*(8*x+bit), 2*y), color)
                    screen.set_at((2*(8*x+bit)+1, 2*y), color)
                    screen.set_at((2*(8*x+bit), 2*y+1), [0.6*i for i in color])
                    screen.set_at((2*(8*x+bit)+1, 2*y+1), [0.6*i for i in color])
                pygame.display.update(pygame.Rect(0, 2*y, WIDTH, 1))  # Update one line
                time.sleep(1 / (HEIGHT * 60))  # Simulate horizontal scanning at 60 Hz
    """
    buffer = pygame.Surface((WIDTH, HEIGHT))
    while True:
        px = pygame.PixelArray(buffer)
        addr = 0xE000
        for y in range(HEIGHT // 2):
            for x in range(WIDTH // 16):
                byte = mem[addr]
                addr += 1

                for bit in range(8):
                    p = (byte >> (7 - bit)) & 1
                    color = (255 * p, 255 * p, 255 * p)
                    sx = 2 * (8 * x + bit)
                    sy = 2 * y
                    px[sx, sy] = color
                    px[sx + 1, sy] = color
                    px[sx, sy + 1] = (int(color[0] * 0.6),) * 3
                    px[sx + 1, sy + 1] = (int(color[0] * 0.6),) * 3
        del px
        screen.blit(buffer, (0, 0))
        pygame.display.flip()


def main():
    clock_module = threading.Thread(
        target=cpu_step,
        args=(
            cpu,
            mem,
        ),
        daemon=True,
    )
    clock_module.start()

    screen_render = threading.Thread(
        target=horizontal_scanning, args=(mem,), daemon=True
    )
    screen_render.start()

    # Main Pygame loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    mem[0x0600] = 0x00
                if event.key == pygame.K_b:
                    mem[0x0600] = 0x01
                if event.key == pygame.K_c:
                    mem[0x0600] = 0x02
                if event.key == pygame.K_d:
                    mem[0x0600] = 0x03
                if event.key == pygame.K_e:
                    mem[0x0600] = 0x04
                if event.key == pygame.K_f:
                    mem[0x0600] = 0x05
                if event.key == pygame.K_g:
                    mem[0x0600] = 0x06
                if event.key == pygame.K_h:
                    mem[0x0600] = 0x07
                if event.key == pygame.K_i:
                    mem[0x0600] = 0x08
                if event.key == pygame.K_j:
                    mem[0x0600] = 0x09
                if event.key == pygame.K_k:
                    mem[0x0600] = 0x0A
                if event.key == pygame.K_l:
                    mem[0x0600] = 0x0B
                if event.key == pygame.K_m:
                    mem[0x0600] = 0x0C
                if event.key == pygame.K_n:
                    mem[0x0600] = 0x0D
                if event.key == pygame.K_o:
                    mem[0x0600] = 0x0E
                if event.key == pygame.K_p:
                    mem[0x0600] = 0x0F
                if event.key == pygame.K_q:
                    mem[0x0600] = 0x10
                if event.key == pygame.K_r:
                    mem[0x0600] = 0x11
                if event.key == pygame.K_s:
                    mem[0x0600] = 0x12
                if event.key == pygame.K_t:
                    mem[0x0600] = 0x13
                if event.key == pygame.K_u:
                    mem[0x0600] = 0x14
                if event.key == pygame.K_v:
                    mem[0x0600] = 0x15
                if event.key == pygame.K_w:
                    mem[0x0600] = 0x16
                if event.key == pygame.K_x:
                    mem[0x0600] = 0x17
                if event.key == pygame.K_y:
                    mem[0x0600] = 0x18
                if event.key == pygame.K_z:
                    mem[0x0600] = 0x19
                if event.key == pygame.K_0:
                    mem[0x0600] = 0x1A
                if event.key == pygame.K_1:
                    mem[0x0600] = 0x1B
                if event.key == pygame.K_2:
                    mem[0x0600] = 0x1C
                if event.key == pygame.K_3:
                    mem[0x0600] = 0x1D
                if event.key == pygame.K_4:
                    mem[0x0600] = 0x1E
                if event.key == pygame.K_5:
                    mem[0x0600] = 0x1F
                if event.key == pygame.K_6:
                    mem[0x0600] = 0x20
                if event.key == pygame.K_7:
                    mem[0x0600] = 0x21
                if event.key == pygame.K_8:
                    mem[0x0600] = 0x22
                if event.key == pygame.K_9:
                    mem[0x0600] = 0x23
                if event.key == pygame.K_SPACE:
                    mem[0x0600] = 0x24
                if event.key == pygame.K_RETURN:
                    mem[0x0600] = 0xAA
                if event.key == pygame.K_BACKSPACE:
                    mem[0x0600] = 0xAB
        clock.tick(60)  # Limit the main loop to 60 FPS

    pygame.quit()


if __name__ == "__main__":
    main()
