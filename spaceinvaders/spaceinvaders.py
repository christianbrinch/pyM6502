import os
import sys
import time

import numpy as np
import pygame

sys.path.append(os.path.abspath(".."))
import mos6502

WIDTH, HEIGHT = 256, 224
CPU_FREQ = 1_000_000  # 1 MHz 6502 (adjust if needed)
FPS = 60

CYCLES_PER_FRAME = CPU_FREQ // FPS
CYCLES_PER_HALF_FRAME = CYCLES_PER_FRAME // 2


KEY_MAP = {
    pygame.K_a: 0x20,
    pygame.K_d: 0x30,
    pygame.K_c: 0x01,
    pygame.K_1: 0x04,
    pygame.K_2: 0x02,
    pygame.K_SPACE: 0x10,
}

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((HEIGHT, WIDTH))
pygame.display.set_caption("SI")


def render_screen(mem):
    # Create a (HEIGHT, 32*8) array from memory bytes
    video_mem = np.array(mem[0x2400 : 0x2400 + 32 * HEIGHT], dtype=np.uint8)
    video_mem = video_mem.reshape((HEIGHT, 32))

    # Unpack bits into pixels (0 or 255)
    framebuffer = np.unpackbits(video_mem, axis=1, bitorder="little")[:, ::-1] * 255

    # Stack into 3 channels (RGB)
    rgb_frame = np.stack([framebuffer] * 3, axis=2)

    # Blit to screen
    pygame.surfarray.blit_array(screen, rgb_frame)
    pygame.display.flip()


class CRT:
    def __init__(self):
        self.cycles = 0
        self.half_fired = False

    def timing(self, cycles):
        self.cycles += cycles
        self.video_status = 0

        if self.cycles >= CYCLES_PER_HALF_FRAME and not self.half_fired:
            self.half_fired = True
            self.video_status = 0
            return "midscreen"

        if self.cycles >= CYCLES_PER_FRAME:
            self.cycles = 0
            self.half_fired = False
            self.video_status = 1
            return "vblank"

        return False


def main():
    # Load the ROM
    mem = mos6502.Memory(file="./si.rom")
    # Initialize CPU
    cpu = mos6502.Processor(mem)
    # Initialize the screen
    crt = CRT()
    running = True
    IRQ = False
    target = 1.0 / FPS
    qc = 0

    while running:
        frame_cycles = 0
        frame_start = time.perf_counter()
        frame_ready = False
        tmp = 0
        frame_cycles = 5

        while tmp < CYCLES_PER_FRAME:
            # Emulate shift register
            if cpu.memory[0x0061] > 0:
                cpu.memory[0x0062] = (cpu.memory[0x0061] << cpu.memory[0x0060]) & 0xFF
                cpu.memory[0x0063] = (cpu.memory[0x0061] << cpu.memory[0x0060]) >> 8
                cpu.memory[0x0061] = 0x00

            if not (cpu.reg_p & 0x10):
                # print(f"{cpu.reg_p:>08b}")
                cpu.exec(output=True, zeropage=True, mempage=0x20)
                input()
                # cpu.reg_p |= 0x10
            else:
                cpu.exec(output=False)

            tmp += frame_cycles

            IRQ = crt.timing(frame_cycles)

            if IRQ:
                cpu.memory[0x00AF] = crt.video_status
                cpu.raise_irq()
                if IRQ == "vblank":
                    frame_ready = True

        if frame_ready:
            render_screen(mem)

        # for event in pygame.event.get():
        #    if event.type == pygame.QUIT:
        #        running = False
        #    elif event.type == pygame.KEYDOWN:
        #        if event.key in KEY_MAP:
        #            mem[0x00A1] = KEY_MAP[event.key]

        # Throttle to real time (optional but recommended)
        elapsed = time.perf_counter() - frame_start

        if elapsed < target:
            time.sleep(target - elapsed)


if __name__ == "__main__":
    main()
