''' MOS-6502 memory emulation '''

__author__ = "Christian Brinch"
__copyright__ = "Copyright 2023"
__credits__ = ["Christian Brinch"]
__license__ = "AFL 3.0"
__version__ = "1.0"
__maintainer__ = "Christian Brinch"
__email__ = "brinch.c@gmail.com"


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
        self.stack_counter = 0  # Stack pointer
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
        self.flag_b = True

    def read_byte(self, address: int):
        self.cycles += 1
        return self.memory[address]

    def write_byte(self, address: int, value: int):
        self.cycles += 1
        self.memory[address] = value

    def fetch_byte(self):
        '''Fetch a byte from memory. '''
        data = self.read_byte(self.program_counter)
        self.program_counter += 1
        return data

    def exec(self, cycles: int = 0):
        while (self.cycles < cycles) or (cycles == 0):
            opcode = self.fetch_byte()
            if opcode == 0xea:
                self.ins_nop()
            if opcode == 0xa9:
                self.ins_lda_imm()
            if opcode == 0xaa:
                self.ins_tax_imp()
            if opcode == 0xe8:
                self.ins_inx_imp()
            if opcode == 0x69:
                self.ins_adc_imm()
            if opcode == 0x00:
                self.ins_brk_imp()
            if opcode == 0x85:
                self.ins_sta_zer()
            if opcode == 0x65:
                self.ins_adc_zer()

    def ins_nop(self):
        ''' No operations '''
        self.cycles += 2

    def ins_brk_imp(self):
        ''' Break - end program '''
        self.cycles = 1000

    def ins_lda_imm(self):
        ''' load register a'''
        self.cycles += 2
        self.reg_a = self.fetch_byte()

    def ins_sta_zer(self):
        self.cycles += 3
        cpu.write_byte(self.fetch_byte(), self.reg_a)

    def ins_tax_imp(self):
        self.cycles += 2
        self.reg_x = self.reg_a

    def ins_inx_imp(self):
        self.cycles += 2
        self.reg_x += 0x01

    def ins_adc_imm(self):
        self.cycles += 2
        self.reg_a += self.fetch_byte()
        if self.reg_a > 0xff:
            self.reg_a -= 0x100
            self.flag_c = True

    def ins_adc_zer(self):
        self.cycles += 3
        self.reg_a += self.read_byte(self.fetch_byte())
        if self.reg_a > 0xff:
            self.reg_a -= 0x100
            self.flag_c = True


mem = Memory()
mem[0xfce2:0xfce2+6] = [0xa9, 0x80, 0x85, 0x01, 0x65, 0x01, 0x00]
cpu = Processor(mem)
cpu.reset()


cpu.exec(20)

print(hex(cpu.reg_a))
print(hex(cpu.reg_x))
print(hex(cpu.reg_y))
print(cpu.flag_c)
