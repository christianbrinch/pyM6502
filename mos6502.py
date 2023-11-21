''' MOS-6502 memory emulation '''

__author__ = "Christian Brinch"
__copyright__ = "Copyright 2023"
__credits__ = ["Christian Brinch"]
__license__ = "AFL 3.0"
__version__ = "1.0"
__maintainer__ = "Christian Brinch"
__email__ = "brinch.c@gmail.com"

import sys

class Memory:
    ''' Memory for the MOS-6502 '''

    def __init__(self, size: int = 65536):
        ''' Initialize the memory to size. Default to 64K bytes.'''

        self.size = size
        self.memory = [0] * size
        print(f"Memory initialized to {size} bytes.")

    def __getitem__(self, address: int):
        ''' Get the value at address. '''
        return self.memory[address]

    def __setitem__(self, address: int, value: int):
        ''' Set address to value. '''
        if value.bit_length() > 8:
            raise ValueError("Value too large")
        self.memory[address] = value
        return self.memory[address]


class Processor:
    ''' The MOS-6502 processor '''

    def __init__(self, memory: Memory):
        ''' Initialize the CPU '''

        self.memory = memory
        self.reg_a = 0  # Accumulator A
        self.reg_x = 0  # Incex register X
        self.reg_y = 0  # Incex register Y

        self.program_counter = 0  # Program counter
        self.stack_pointer = 0  # Stack pointer
        self.cycles = 0  # Clock cycles

        self.flag_c = True  # Status flag - Carry Flag
        self.flag_z = True  # Status flag - Zero Flag
        self.flag_i = True  # Status flag - Interrupt Disable
        self.flag_d = True  # Status flag - Decimal Mode Flag
        self.flag_b = True  # Status flag - Break Command
        self.flag_v = True  # Status flag - Overflow Flag
        self.flag_n = True  # Status flag - Negative Flag


    def reset(self):
        ''' Reset processor. Program counter is initialized to FCE2 and 
            stack counter to 01FD. '''
        self.program_counter = 0xfce2  # Hardcoded start vector post-reset
        self.stack_pointer = 0x01fd  # Hardcoded stack pointer post-reset
        self.cycles = 0
        self.flag_i = True
        self.flag_d = False
        self.flag_b = False
        self.flag_c = False
        self.flag_v = False
        self.flag_z = False
        self.flag_n = False

    def read_byte(self, address: int):
        self.cycles += 1
        return self.memory[address]

    def write_byte(self, address: int, value: int):
        self.cycles += 1
        self.memory[address] = value

    def read_word(self, address: int):
        ''' Read a word from memory. '''

        if sys.byteorder == "little":
            data = self.read_byte(address) | (self.read_byte(address + 1) << 8)
        else:
            data = (self.read_byte(address) << 8) | self.read_byte(address + 1)
        return data

    def write_word(self, address: int, value: int) -> None:
        ''' Split a word to two bytes and write to memory. '''
        
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

    OPCODES = [
        #  0  |  1   |  2   |  3   |  4   |  5   |  6   |  7   |  8   |  9   |  A   |  B   |  C   |  D   |  E   |  F   |
        "brk", "ora", "nop", "slo", "nop", "ora", "asl", "slo", "php", "ora", "asl", "nop", "nop", "ora", "asl", "slo",  # 0
        "bpl", "ora", "nop", "slo", "nop", "ora", "asl", "slo", "clc", "ora", "nop", "slo", "nop", "ora", "asl", "slo",  # 1
        "jsr", "and", "nop", "rla", "bit", "and", "rol", "rla", "plp", "and", "rol", "nop", "bit", "and", "rol", "rla",  # 2
        "bmi", "and", "nop", "rla", "nop", "and", "rol", "rla", "sec", "and", "nop", "rla", "nop", "and", "rol", "rla",  # 3
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

    def exec(self, cycles: int = 0):
        while (self.cycles < cycles) or (cycles == 0):
            print(f"Register A: {self.reg_a}. Clock cycles: {self.cycles}. Program counter: {self.program_counter}")
            print(f"Clock cycles: {self.cycles}")
            input()
            if self.flag_b:
                break
            q=self.cycles
            opcode = self.fetch_byte()
            print("self.ins_" + self.OPCODES[opcode] + "(\"" + self.ADDRESSING[opcode] + "\")")
            eval("self.ins_" + self.OPCODES[opcode] + "(\"" + self.ADDRESSING[opcode] + "\")")
            print(f"Cost: {self.cycles-q}")

    def check(self, byte, carry=False, zero=False, neg=False):
        if carry and byte > 0xff:
            self.flag_c = True
        if zero and byte == 0x00:
            slef.flag_z = True
        if neg and format(byte, '#010b')[2]: # Does not work properly
            self.flag_n = True


    def ins_adc(self, mode):
        ''' Add with carry '''
        if addr == 'imm':
            self.reg_a += self.fetch_byte()
        elif addr == 'zp':
            self.reg_a += self.read_byte(self.fetch_byte())
        else:
            print(f"Unknown mode {mode}")
            self.flag_b = True
        
        self.check(self.reg_a, 'carry', 'zero', 'neg')
        if self.flag_c:
            self.reg_a -= 0x100

    def ins_asl(self, mode):
        ''' Arithmetic shift left '''
        if mode == 'acc':
            self.cycles += 1
            self.reg_a = self.reg_a << 1
            self.check(self.reg_a, 'carry', 'zero', 'neg')
            if self.flag_c:
                self.reg_a -= 0x100
        elif mode == 'zp':
            self.cycles += 1
            addr = self.fetch_byte()
            tmp = self.read_byte(addr) << 1
            self.check(tmp, 'carry', 'zero', 'neg')
            if self.flag_c:
                tmp -= 0x100
            self.write_byte(addr, tmp)
        elif mode == 'zpx':
            self.cycles += 2
            addr = self.fetch_byte()
            tmp = (self.read_byte(addr) + self.reg_x) << 1
            self.check(tmp, 'carry', 'zero', 'neg')
            if self.flag_c:
                tmp -= 0x100
            self.write_byte(addr, tmp)
        else:
            print(f"Unknown mode {mode}")
            Self.flag_b = True

    def ins_brk(self, mode):
        ''' Break - end program '''
        self.flag_b = True

    def ins_inx(self, mode):
        ''' Increment X '''
        if mode == 'imp':
            self.cycles += 1
            self.reg_x += 0x01
        else:
            print(f"Unknown mode {mode}")
            self.flag_b = True
       
        self.check(self.reg_x, False, 'zero', 'neg')

    def ins_jsr(self, mode):
        ''' Jump to subroutine '''
        if mode == 'abs':
            self.cycles += 1
            self.write_word(self.stack_pointer, self.program_counter-0x01)
            self.stack_pointer -= 0x01
            self.program_counter = self.fetch_word()
        else:
            print(f"Unknown mode {mode}")
            self.flag_b = True

    def ins_lda(self, mode):
        ''' load register A '''
        if mode == 'imm':
            self.cycles += 1
            self.reg_a = self.fetch_byte()
        elif mode == 'zp':
            self.cycles += 2
            self.reg_a = self.read_byte(self.fetch_byte())
        elif mode == 'zpx':
            self.cycles += 3
            self.reg_a = self.read_byte(self.fetch_byte()+ self.reg_x)
        else:
            print(f"Unknown mode {mode}")
            self.flag_b = True

        self.check(self.reg_a, False, 'zero', 'neg') 

    def ins_nop(self, mode):
        ''' No operations '''
        self.cycles += 1

    def ins_ora(self, mode):
        ''' Logical inclusive OR '''
        if mode == 'imm':
            self.reg_a = self.reg_a | self.fetch_byte()
        elif mode == 'abs':
            self.cycles += 1 
            self.reg_a = self.reg_a | self.fetch_word()

        else:
            print(f"Unknown mode {mode}")
            self.flag_b = True

        self.check(self.reg_a, False, 'zero', 'neg') 

    def ins_rol(self, mode):
        ''' Rotate bits to the left '''
        if mode == 'acc':
            self.check(self.reg_a, 'carry', 'zero', False)
            #self.reg_a = self_reg_a << 1

        else:
            print(f"Unknown mode {mode}")
            self.flag_b = True


    def ins_rts(self, mode):
        ''' Return from subroutine '''
        self.cycles += 3
        if mode == 'imp':
            self.program_counter = self.read_word(self.stack_pointer)
            self.stack_pointer += 0x01
        else:
            print(f"Unknown mode {mode}")
            self.flag_b = True

    def ins_sec(self, mode):
        ''' Set carry flag '''
        if mode == 'imp':
            self.cycles += 1
            self.flag_c = True
        else:
            print(f"Unknown mode {mode}")
            self.flag_b = True


    def ins_sta(self, mode):
        ''' Store register A '''
        if mode == 'zp':
            self.cycles += 2
            self.write_byte(self.fetch_byte(), self.reg_a)
        elif mode == 'zpx':
            self.cycles += 3
            self.write_byte(self.fetch_byte()+self.reg_x, self.reg_a)
        else:
            print(f"Unknown mode {mode}")
            self.flag_b = True
 

    def ins_tax(self, mode):
        ''' Transfer A to X '''
        if mode == 'imp':
            self.cycles += 1
            self.reg_x = self.reg_a
        else:
            print(f"Unknown mode {mode}")
            self.flag_b = True
        
        self.check(self.reg_x, False, 'zero', 'neg')



def load(bank, address, program):
    for opc in program:
        bank[address]=opc
        address+=1
    return bank



mem = Memory()
# Load Snake
mem = load(mem, 0x0600, [0x20, 0x06, 0x06, 0x20, 0x38, 0x06, 0x20, 0x0d, 0x06, 0x20, 0x2a, 0x06, 0x60, 0xa9, 0x02, 0x85,
                         0x02, 0xa9, 0x04, 0x85, 0x03, 0xa9, 0x11, 0x85, 0x10, 0xa9, 0x10, 0x85, 0x12, 0xa9, 0x0f, 0x85, 
                         0x14, 0xa9, 0x04, 0x85, 0x11, 0x85, 0x13, 0x85, 0x15, 0x60, 0xa5, 0xfe, 0x85, 0x00, 0xa5, 0xfe, 
                         0x29, 0x03, 0x18, 0x69, 0x02, 0x85, 0x01, 0x60, 0x20, 0x4d, 0x06, 0x20, 0x8d, 0x06, 0x20, 0xc3, 
                         0x06, 0x20, 0x19, 0x07, 0x20, 0x20, 0x07, 0x20, 0x2d, 0x07, 0x4c, 0x38, 0x06, 0xa5, 0xff, 0xc9, 
                         0x77, 0xf0, 0x0d, 0xc9, 0x64, 0xf0, 0x14, 0xc9, 0x73, 0xf0, 0x1b, 0xc9, 0x61, 0xf0, 0x22, 0x60, 
                         0xa9, 0x04, 0x24, 0x02, 0xd0, 0x26, 0xa9, 0x01, 0x85, 0x02, 0x60, 0xa9, 0x08, 0x24, 0x02, 0xd0, 
                         0x1b, 0xa9, 0x02, 0x85, 0x02, 0x60, 0xa9, 0x01, 0x24, 0x02, 0xd0, 0x10, 0xa9, 0x04, 0x85, 0x02, 
                         0x60, 0xa9, 0x02, 0x24, 0x02, 0xd0, 0x05, 0xa9, 0x08, 0x85, 0x02, 0x60, 0x60, 0x20, 0x94, 0x06, 
                         0x20, 0xa8, 0x06, 0x60, 0xa5, 0x00, 0xc5, 0x10, 0xd0, 0x0d, 0xa5, 0x01, 0xc5, 0x11, 0xd0, 0x07, 
                         0xe6, 0x03, 0xe6, 0x03, 0x20, 0x2a, 0x06, 0x60, 0xa2, 0x02, 0xb5, 0x10, 0xc5, 0x10, 0xd0, 0x06, 
                         0xb5, 0x11, 0xc5, 0x11, 0xf0, 0x09, 0xe8, 0xe8, 0xe4, 0x03, 0xf0, 0x06, 0x4c, 0xaa, 0x06, 0x4c, 
                         0x35, 0x07, 0x60, 0xa6, 0x03, 0xca, 0x8a, 0xb5, 0x10, 0x95, 0x12, 0xca, 0x10, 0xf9, 0xa5, 0x02, 
                         0x4a, 0xb0, 0x09, 0x4a, 0xb0, 0x19, 0x4a, 0xb0, 0x1f, 0x4a, 0xb0, 0x2f, 0xa5, 0x10, 0x38, 0xe9, 
                         0x20, 0x85, 0x10, 0x90, 0x01, 0x60, 0xc6, 0x11, 0xa9, 0x01, 0xc5, 0x11, 0xf0, 0x28, 0x60, 0xe6, 
                         0x10, 0xa9, 0x1f, 0x24, 0x10, 0xf0, 0x1f, 0x60, 0xa5, 0x10, 0x18, 0x69, 0x20, 0x85, 0x10, 0xb0, 
                         0x01, 0x60, 0xe6, 0x11, 0xa9, 0x06, 0xc5, 0x11, 0xf0, 0x0c, 0x60, 0xc6, 0x10, 0xa5, 0x10, 0x29, 
                         0x1f, 0xc9, 0x1f, 0xf0, 0x01, 0x60, 0x4c, 0x35, 0x07, 0xa0, 0x00, 0xa5, 0xfe, 0x91, 0x00, 0x60, 
                         0xa6, 0x03, 0xa9, 0x00, 0x81, 0x10, 0xa2, 0x00, 0xa9, 0x01, 0x81, 0x10, 0x60, 0xa2, 0x00, 0xea, 
                         0xea, 0xca, 0xd0, 0xfb, 0x60])

cpu = Processor(mem)
cpu.reset()
cpu.program_counter = 0x0600


mem = load(mem, 0x0000, [0xa9, 0x80, 0x0a])
cpu = Processor(mem)
cpu.reset()
cpu.program_counter = 0x0000



cpu.exec(6)

print(hex(cpu.reg_a))
print(hex(cpu.reg_x))
print(hex(cpu.reg_y))
print("N V B D I Z C")
print(int(cpu.flag_n),int(cpu.flag_v),int(cpu.flag_b),int(cpu.flag_d),int(cpu.flag_i),int(cpu.flag_z),int(cpu.flag_c))
