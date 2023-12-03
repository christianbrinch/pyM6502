import pygame
import numpy as np
import mos6502
from importlib import reload

reload(mos6502)

SIZE = height, width = 320, 320


def main():

    screen = pygame.display.set_mode(SIZE)
    clock = pygame.time.Clock()

    mem = mos6502.Memory()
    mem = mos6502.load(
        mem, 0x0600, [0xa9, 0x40, 0xe9, 0x80, 0x8d, 0x00, 0x00])
    cpu = mos6502.Processor(mem)
    cpu.reset()

    done = False
    k = 0
    while cpu.flag_b:
        cpu.exec(1)
        k += 1

        # Random number generator
        # cpu.memory[0x00fe] = np.random.randint(255)

        # Draw screen
        vmem = np.array([[cpu.memory[0x0200+(a//10)*32+(b//10)]
                        for a in range(320)] for b in range(320)])
        surface = pygame.surfarray.make_surface(vmem)
        screen.blit(surface, (0, 0))

        # Get player input
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            cpu.memory[0xff] = 0x08
        elif key[pygame.K_RIGHT]:
            cpu.memory[0xff] = 0x02
        elif key[pygame.K_UP]:
            cpu.memory[0xff] = 0x01
        elif key[pygame.K_DOWN]:
            cpu.memory[0xff] = 0x04

        # Update and wait for next clock cycle
        pygame.display.update()
        clock.tick(60)

        print("A: ", hex(cpu.reg_a))
        print("X: ", hex(cpu.reg_x))
        print("Y: ", hex(cpu.reg_y))
        print("PC:", hex(cpu.program_counter))
        print("SP:", hex(cpu.stack_pointer))
        print("NV-BDIZC")
        print(f"{int(cpu.flag_n)}{int(cpu.flag_v)}1{int(cpu.flag_b)}{int(cpu.flag_d)}{int(cpu.flag_i)}{int(cpu.flag_z)}{int(cpu.flag_c)}")

        print("Zero page:")
        for j in range(16):
           addr = j*16
           print(f"{hex(addr)}:", [''.join('{:02X}').format(i)
                 for i in cpu.memory[addr:addr+16]])
        # print("Stack:")
        # for j in range(16):
        #    addr = j*16+0x100
        #    print(f"{hex(addr)}:", [''.join('{:02X}').format(i)
        #          for i in cpu.memory[addr:addr+16]])

        # print("Video memory:")
        # for j in range(64):
        #   addr = j*16+0x0200
        #   print(f"{hex(addr)}:", [''.join('{:02X}').format(i)
        #         for i in cpu.memory[addr:addr+16]])
        # input()
