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


def render_screen(framebuffer, mem):
    for y in range(HEIGHT):
        base_addr = 0x2400 + (32 * y)

        for i in range(32):
            byte = mem[base_addr + i]
            for bit in range(8):
                x = i * 8 + bit
                color = 255 if (byte & (1 << bit)) else 0
                framebuffer[y, x] = (color, color, color)

    rotated = np.rot90(framebuffer, k=1)
    pygame.surfarray.blit_array(screen, rotated.swapaxes(0, 1))
    pygame.display.flip()


class CRT:
    def __init__(self):
        self.cycles = 0
        self.half_fired = False

    def timing(self, cpu, cycles):
        self.cycles += cycles

        if (
            self.cycles >= CYCLES_PER_HALF_FRAME
            and not (cpu.reg_p & 0x04)
            and not self.half_fired
        ):
            self.half_fired = True
            return 0x0C08

        if self.cycles >= CYCLES_PER_FRAME and not (cpu.reg_p & 0x04):
            self.cycles = 0 #-= CYCLES_PER_FRAME
            self.half_fired = False
            return 0x0C23

        return False


def main():
    # Load the ROM (shared resource)
    mem = mos6502.Memory(file="./si.rom")
    # Initialize CPU
    cpu = mos6502.Processor(mem)
    crt = CRT()
    running = True
    IRQ = False
    framebuffer = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

    while running:
        frame_cycles = 0
        frame_start = time.perf_counter()
        frame_ready = False
        tmp=0

        while tmp < CYCLES_PER_FRAME:
            # Emulate shift register
            if cpu.memory[0x0061] > 0:
                cpu.memory[0x0062] = (cpu.memory[0x0061] << cpu.memory[0x0060]) & 0xFF
                cpu.memory[0x0063] = (cpu.memory[0x0061] << cpu.memory[0x0060]) >> 8
                cpu.memory[0x0061] = 0x00

            if not (cpu.reg_p & 0x10):
                cpu.exec(output=True, zeropage=True, mempage=0x20)
                input()
            else:
                cpu.exec(output=False)
            
            frame_cycles = 10
            tmp += frame_cycles

            IRQ = crt.timing(cpu, frame_cycles)

            if IRQ:
                # Write IRQ handler address to IRQ vector
                cpu.write_word(0xFFFE, IRQ)
                # Push PC to stack; high byte first, then low byte
                cpu.write_byte(cpu.stack_pointer + 0x100, cpu.program_counter // 256)
                cpu.stack_pointer -= 0x01
                cpu.write_byte(cpu.stack_pointer + 0x100, cpu.program_counter % 256)
                cpu.stack_pointer -= 0x01

                # Push status flags
                cpu.write_byte(cpu.stack_pointer + 0x100, cpu.reg_p)
                cpu.stack_pointer -= 0x01

                # Read interrupt vector at $fffe-$ffff
                cpu.program_counter = cpu.read_word(0xFFFE)
                frame_ready = True

        if frame_ready:
            render_screen(framebuffer, mem)

        #for event in pygame.event.get():
        #    if event.type == pygame.QUIT:
        #        running = False
        #    elif event.type == pygame.KEYDOWN:
        #        if event.key in KEY_MAP:
        #            mem[0x00A1] = KEY_MAP[event.key]

        # Throttle to real time (optional but recommended)
        elapsed = time.perf_counter() - frame_start
        target = 1.0 / FPS

        if elapsed < target:
            time.sleep(target - elapsed)


if __name__ == "__main__":
    main()
