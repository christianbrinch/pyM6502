import pygame
import threading
import mos6502
import time
import numpy as np

WIDTH, HEIGHT = 256, 224
SCANLINES = HEIGHT
REFRESH_RATE = 60  # Hz
FRAME_TIME = 1.0 / REFRESH_RATE  # Frame duration
SCANLINE_TIME = FRAME_TIME / (SCANLINES + 38)  # 38 lines of vblank


# Initialize Pygame
pygame.init()
#screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen = pygame.display.set_mode((HEIGHT, WIDTH))
pygame.display.set_caption("SI")
clock = pygame.time.Clock()

# Load the ROM (shared resource)
mem = mos6502.Memory(file='./si.rom')

# Initialize CPU
cpu = mos6502.Processor(mem)
IRQ = False

# Screen buffer 0x2400-0x3fff = 7168 bytes(shared resource)
buffer_lock = threading.Lock()

def cpu_step():
    global IRQ
    global mem
    global cpu
    run = 1
    step=False
    while run:
        # Emulate shift register
        if 8>cpu.memory[0x0060]>0:
            cpu.memory[0x0060] = cpu.memory[0x0060]*0x20

        if not IRQ:
            #if cpu.program_counter == 0x0c6c:
            #    cpu.exec(output=True, zeropage=True, mempage=0x20)
            #    input()
            if not (cpu.reg_p & 0x10):
                cpu.exec(output=True, zeropage=True, mempage=0x20)
                input()
            else:
                cpu.exec(output=False)

        else:
            # Write IRQ handler address to IRQ vector
            cpu.write_word(0xfffe, IRQ)
            # Push PC to stack; high byte first, then low byte
            cpu.write_byte(cpu.stack_pointer+0x100, cpu.program_counter//256)
            cpu.stack_pointer -= 0x01
            cpu.write_byte(cpu.stack_pointer+0x100, cpu.program_counter%256)
            cpu.stack_pointer -= 0x01

            # Push status flags
            cpu.write_byte(cpu.stack_pointer+0x100, cpu.reg_p)
            cpu.stack_pointer -= 0x01

            # Read interrupt vector at $fffe-$ffff
            cpu.program_counter = cpu.read_word(0xfffe)
            IRQ = False


def horizontal_scanning():
    """Function to render the screen buffer line by line (separate thread)."""
    global IRQ
    global mem
    n=0
    q=[]
    intp = 0
    while True:
        n+=1
        frame_start = time.time()
        #screen.fill((0, 0, 0))  # Clear screen at start of frame; good approximation. CRT persistence time is 1-5 µs << ~16µs render time per frame

        for scanline in range(SCANLINES//2):
            # Simulate drawing one scanline, TOP OF THE SCREEN
            base_addr = 0x2400+(32*scanline)
            pixels = np.zeros((WIDTH, 3), dtype=np.uint8)

            for i in range(32):
                byte = mem[base_addr + i]
                for bit in range(8):
                    pixels[i * 8 + (bit)] = 255 if (byte & (1 << bit)) else 0  # Reverse bit order

            pygame.surfarray.pixels3d(screen)[scanline, :, :] = pixels[::-1] # Rotate screen as per SI cabinet design

        # Emulated interrupts
        if not (cpu.reg_p & 0x04) and intp==0 and not IRQ:
            IRQ = 0x0c08
            intp = 1


        for scanline in range(SCANLINES//2):
            scanline += SCANLINES//2
            # Simulate drawing one scanline, BOTTOM OF THE SCREEN
            base_addr = 0x2400+(32*scanline)
            pixels = np.zeros((WIDTH, 3), dtype=np.uint8)

            for i in range(32):
                byte = mem[base_addr + i]
                for bit in range(8):
                    pixels[i * 8 + (bit)] = 255 if (byte & (1 << bit)) else 0  # Reverse bit order

            pygame.surfarray.pixels3d(screen)[scanline, :, :] = pixels[::-1] # Rotate screen as per SI cabinet design


        # Emulated interrupts
        if not (cpu.reg_p & 0x04) and intp == 1 and not IRQ:
            IRQ = 0x0c23
            intp = 0


        pygame.display.flip()
        #while time.time() < frame_start + FRAME_TIME:
        #    pass  # Ensure exact 60 Hz refresh
        q+=[time.time()-frame_start]

    print(sum(q)/len(q))

def main():
    clock_module = threading.Thread(target=cpu_step, daemon=True)
    clock_module.start()

    screen_render = threading.Thread(target=horizontal_scanning, daemon=True)
    screen_render.start()

    global mem

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
                    mem[0x0600] = 0x0a
                if event.key == pygame.K_l:
                    mem[0x0600] = 0x0b
                if event.key == pygame.K_m:
                    mem[0x0600] = 0x0c
                if event.key == pygame.K_n:
                    mem[0x0600] = 0x0d
                if event.key == pygame.K_o:
                    mem[0x0600] = 0x0e
                if event.key == pygame.K_p:
                    mem[0x0600] = 0x0f
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
                    mem[0x0600] = 0x1a
                if event.key == pygame.K_1:
                    mem[0x0600] = 0x1b
                if event.key == pygame.K_2:
                    mem[0x0600] = 0x1c
                if event.key == pygame.K_3:
                    mem[0x0600] = 0x1d
                if event.key == pygame.K_4:
                    mem[0x0600] = 0x1e
                if event.key == pygame.K_5:
                    mem[0x0600] = 0x1f
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
                    mem[0x0600] = 0xaa
                if event.key == pygame.K_BACKSPACE:
                    mem[0x0600] = 0xab
        clock.tick(60)  # Limit the main loop to 60 FPS

    pygame.quit()


if __name__ == "__main__":
    main()
