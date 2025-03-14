''' MOS-6502 memory emulation

    Usage:
        mem = Memory(file="path/to/bin/file")
        cpu = Processor(mem)
        cpu.exec(output=True, zeropage=True, mempage=128)
'''

__author__ = "Christian Brinch"
__copyright__ = "Copyright 2023"
__credits__ = ["Christian Brinch"]
__license__ = "AFL 3.0"
__version__ = "1.0"
__maintainer__ = "Christian Brinch"
__email__ = "brinch.c@gmail.com"

import sys
import instructions
from importlib import reload
from colorama import Fore, Style

reload(instructions)

class Memory:
    ''' Memory for the MOS-6502 '''

    def __init__(self, size: int = 65536, file: str = '', address: int = 0):
        ''' Initialize the memory to size. Default to 64K bytes.'''

        self.size = size
        self.memory = [0] * size
        if file:
            self.load_file(file, address)
        print(f"Memory initialized to {size} bytes.")

    def __getitem__(self, address: int):
        ''' Get the value at address. '''
        if 0x0000 < address > self.size:
            raise ValueError("Memory address is not valid")
        return self.memory[address]

    def __setitem__(self, address: int, value: int):
        ''' set address to value. '''
        if 0x0000 < address > self.size:
            raise ValueError("Memory address is not valid")
        if value.bit_length() > 8:
            raise ValueError("Value too large")
        self.memory[address] = value
        return self.memory[address]

    def load(self, program, address=0x0000):
        ''' Load program into memory at address'''
        for byte in program:
            self[address] = byte
            address += 0x01

    def load_file(self, file, address=0x0000):
        ''' Load program from file into memory at address
            File should be a binary byte code file.
        '''
        f = open(file, mode='rb')
        prog = f.read()
        self.load(list(prog), address)
        f.close()


class Processor:
    ''' The MOS-6502 processor '''

    def __init__(self, memory: Memory):
        ''' Initialize the CPU '''

        self.memory = memory
        self.reg_a = 0  # Accumulator A
        self.reg_x = 0  # Index register X
        self.reg_y = 0  # Index register Y
        self.reg_p = int("00110100", 2)  # NV-BDIZC Status flags

        self.program_counter = 0x0000        # Program counter
        self.stack_pointer = 0xff            # stack pointer
        self.cycles = 0                      # Clock cycles

        self.ins = instructions.Set()
        self.reset()

    def reset(self):
        ''' Reset processor. Program counter is initialized to FCE2 and
            stack counter to 01FD. '''
        self.program_counter = self.read_word(0xfffc)  # Hardcoded start vector post-reset
        self.stack_pointer = 0xff       # Hardcoded stack pointer post-reset
        self.cycles = 0
        self.reg_p = int("00110100", 2) # NV-BDIZC

    def toggle(self, bit, value):
        ''' Toggle a bit in register p based on value
            Flags: NV-BDIZC
        '''
        self.reg_p = (self.reg_p & ~(1 << bit)) | (bool(value) << bit)
        return

    def read_byte(self, address: int):
        return self.memory[address]

    def write_byte(self, address: int, value: int):
        self.memory[address] = value

    def read_word(self, address: int):
        ''' Read a word from memory. '''

        if sys.byteorder == "little":
            data = self.read_byte(address) | (self.read_byte(address + 1) << 8)
        else:
            data = (self.read_byte(address) << 8) | self.read_byte(address + 1)
        return data

    def write_word(self, address: int, value: int) -> None:
        ''' split a word to two bytes and write to memory. '''

        if sys.byteorder == "little":
            self.write_byte(address, value & 0xFF)
            self.write_byte(address + 1, (value >> 8) & 0xFF)
        else:
            self.write_byte(address, (value >> 8) & 0xFF)
            self.write_byte(address + 1, value & 0xFF)

    def fetch_byte(self):
        ''' Fetch a byte from memory. '''
        data = self.read_byte(self.program_counter)
        self.program_counter += 1
        return data

    def fetch_word(self):
        ''' Fetch a word from memory. '''
        data = self.read_word(self.program_counter)
        self.program_counter += 2
        return data

    ADDRESSING = [
        #  0  |  1   |  2   |  3   |  4   |  5   |  6   |  7   |  8   |  9   |  A   |  B   |  C   |  D   |  E   |  F   |
        "imp", "inx", "imp", "inx", "zp",  "zp",  "zp",  "zp",  "imp", "imm", "acc", "imm", "abs", "abs", "abs", "abs",  # 0
        "rel", "iny", "imp", "iny", "zpx", "zpx", "zpx", "zpx", "imp", "aby", "imp", "aby", "abx", "abx", "abx", "abx",  # 1
        "abs", "inx", "imp", "inx", "zp",  "zp",  "zp",  "zp",  "imp", "imm", "acc", "imm", "abs", "abs", "abs", "abs",  # 2
        "rel", "iny", "imp", "iny", "zpx", "zpx", "zpx", "zpx", "imp", "aby", "imp", "aby", "abx", "abx", "abx", "abx",  # 3
        "imp", "inx", "imp", "inx", "zp",  "zp",  "zp",  "zp",  "imp", "imm", "acc", "imm", "abs", "abs", "abs", "abs",  # 4
        "rel", "iny", "imp", "iny", "zpx", "zpx", "zpx", "zpx", "imp", "aby", "imp", "aby", "abx", "abx", "abx", "abx",  # 5
        "imp", "inx", "imp", "inx", "zp",  "zp",  "zp",  "zp",  "imp", "imm", "acc", "imm", "ind", "abs", "abs", "abs",  # 6
        "rel", "iny", "imp", "iny", "zpx", "zpx", "zpx", "zpx", "imp", "aby", "imp", "aby", "abx", "abx", "abx", "abx",  # 7
        "imm", "inx", "imm", "inx", "zp",  "zp",  "zp",  "zp",  "imp", "imm", "imp", "imm", "abs", "abs", "abs", "abs",  # 8
        "rel", "iny", "imp", "iny", "zpx", "zpx", "zpy", "zpy", "imp", "aby", "imp", "aby", "abx", "abx", "aby", "aby",  # 9
        "imm", "inx", "imm", "inx", "zp",  "zp",  "zp",  "zp",  "imp", "imm", "imp", "imm", "abs", "abs", "abs", "abs",  # A
        "rel", "iny", "imp", "iny", "zpx", "zpx", "zpy", "zpy", "imp", "aby", "imp", "aby", "abx", "abx", "aby", "aby",  # B
        "imm", "inx", "imm", "inx", "zp",  "zp",  "zp",  "zp",  "imp", "imm", "imp", "imm", "abs", "abs", "abs", "abs",  # C
        "rel", "iny", "imp", "iny", "zpx", "zpx", "zpx", "zpx", "imp", "aby", "imp", "aby", "abx", "abx", "abx", "abx",  # D
        "imm", "inx", "imm", "inx", "zp",  "zp",  "zp",  "zp",  "imp", "imm", "imp", "imm", "abs", "abs", "abs", "abs",  # E
        "rel", "iny", "imp", "iny", "zpx", "zpx", "zpx", "zpx", "imp", "aby", "imp", "aby", "abx", "abx", "abx", "abx",  # F
    ]

    OPCODEs = [
        #  0  |  1   |  2   |  3   |  4   |  5   |  6   |  7   |  8   |  9   |  A   |  B   |  C   |  D   |  E   |  F   |
        "brk", "ora", "nop", "slo", "nop", "ora", "asl", "slo", "php", "ora", "asl", "nop", "nop", "ora", "asl", "slo",  # 0
        "bpl", "ora", "nop", "slo", "nop", "ora", "asl", "slo", "clc", "ora", "nop", "slo", "nop", "ora", "asl", "slo",  # 1
        "jsr", "AND", "nop", "rla", "bit", "AND", "rol", "rla", "plp", "AND", "rol", "nop", "bit", "AND", "rol", "rla",  # 2
        "bmi", "AND", "nop", "rla", "nop", "AND", "rol", "rla", "sec", "AND", "nop", "rla", "nop", "AND", "rol", "rla",  # 3
        "rti", "eor", "nop", "sre", "nop", "eor", "lsr", "sre", "pha", "eor", "lsr", "nop", "jmp", "eor", "lsr", "sre",  # 4
        "bvc", "eor", "nop", "sre", "nop", "eor", "lsr", "sre", "cli", "eor", "nop", "sre", "nop", "eor", "lsr", "sre",  # 5
        "rts", "adc", "nop", "rra", "nop", "adc", "ror", "rra", "pla", "adc", "ror", "nop", "jmp", "adc", "ror", "rra",  # 6
        "bvs", "adc", "nop", "rra", "nop", "adc", "ror", "rra", "sei", "adc", "nop", "rra", "nop", "adc", "ror", "rra",  # 7
        "nop", "sta", "nop", "sax", "sty", "sta", "stx", "sax", "dey", "nop", "txa", "nop", "sty", "sta", "stx", "sax",  # 8
        "bcc", "sta", "nop", "nop", "sty", "sta", "stx", "sax", "tya", "sta", "txs", "nop", "nop", "sta", "nop", "nop",  # 9
        "ldy", "lda", "ldx", "lax", "ldy", "lda", "ldx", "lax", "tay", "lda", "tax", "nop", "ldy", "lda", "ldx", "lax",  # A
        "bcs", "lda", "nop", "lax", "ldy", "lda", "ldx", "lax", "clv", "lda", "tsx", "lax", "ldy", "lda", "ldx", "lax",  # B
        "cpy", "cmp", "nop", "dcp", "cpy", "cmp", "dec", "dcp", "iny", "cmp", "dex", "nop", "cpy", "cmp", "dec", "dcp",  # C
        "bne", "cmp", "nop", "dcp", "nop", "cmp", "dec", "dcp", "cld", "cmp", "nop", "dcp", "nop", "cmp", "dec", "dcp",  # D
        "cpx", "sbc", "nop", "isb", "cpx", "sbc", "inc", "isb", "inx", "sbc", "nop", "sbc", "cpx", "sbc", "inc", "isb",  # E
        "beq", "sbc", "nop", "isb", "nop", "sbc", "inc", "isb", "sed", "sbc", "nop", "isb", "nop", "sbc", "inc", "isb",  # F
    ]

    def exec(self, cycles: int = 0, output=False, zeropage=False, mempage=0):
        t = self.program_counter
        opcode = self.fetch_byte()
        tmp = [t+k for k in range(self.program_counter-t)]

        eval("self.ins." + self.OPCODEs[opcode] +
             "(self, \"" + self.ADDRESSING[opcode] + "\")")
        tmp = [t+k for k in range(self.program_counter-t)]

        if output:
            print()
            print(f"{Fore.CYAN}PC{Style.RESET_ALL} 0x{self.program_counter:0>04x} "
                  f"{Fore.CYAN}Reg A{Style.RESET_ALL} 0x{self.reg_a:0>2x} "
                  f"{Fore.CYAN}Reg X{Style.RESET_ALL} 0x{self.reg_x:0>2x} "
                  f"{Fore.CYAN}Reg Y{Style.RESET_ALL} 0x{self.reg_y:0>2x} "
                  f"{Fore.CYAN}SP{Style.RESET_ALL} 0x{self.stack_pointer:0>2x}{' '*12}"
                  f"{Fore.CYAN}NV-BDIZC{Style.RESET_ALL} "
                  f"{self.reg_p:>08b}"
                  f"{' '*11}"
                  f"{Fore.CYAN}OPcode{Style.RESET_ALL} 0x{Fore.YELLOW}{opcode:0>2x}{Style.RESET_ALL} "
                  f"{self.OPCODEs[opcode]}:{self.ADDRESSING[opcode]}")

            print()
        if zeropage:
            print(f"{Fore.CYAN}Zero page{Style.RESET_ALL}", end='')
            if mempage:
                print(f"{' '*52} {Fore.CYAN}Page{Style.RESET_ALL} 0x{256*mempage:0>4x}", end='')
            print('')
            for j in range(16):
                addr = j*16

                print(f"{Fore.CYAN}0x{addr:0>2x}{Style.RESET_ALL} ", end='')

                for i in range(16):
                    if addr+i in tmp:
                        print(
                            f'{Fore.YELLOW}{self.memory[addr+i]:0>2x}{Style.RESET_ALL} ', end='')
                    else:
                        print(f'{self.memory[addr+i]:0>2x} ', end='')
                print(f"{' '*9}", end='')
                if mempage:
                    for i in range(16):
                        if 256*mempage+addr+i in tmp:
                            print(
                                f'{Fore.YELLOW}{self.memory[256*mempage+addr+i]:0>2x}{Style.RESET_ALL} ', end='')
                        else:
                         print(
                            f'{self.memory[256*mempage+addr+i]:0>2x} ', end='')
                print('')
