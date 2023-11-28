''' MOS-6502 instruction set '''

__author__ = "Christian Brinch"
__copyright__ = "Copyright 2023"
__credits__ = ["Christian Brinch"]
__license__ = "AFL 3.0"
__version__ = "1.0"
__maintainer__ = "Christian Brinch"
__email__ = "brinch.c@gmail.com"


class Set:
    ''' Addressing modes '''

    def get(self, obj, mode):
        if mode == 'imm':
            return obj.fetch_byte()
        elif mode == 'abs':
            return obj.read_byte(obj.fetch_word())
        elif mode == 'abx':
            return obj.read_byte(obj.fetch_word()+obj.reg_x)
        elif mode == 'aby':
            return obj.read_byte(obj.fetch_word()+obj.reg_y)
        elif mode == 'zp':
            return obj.read_byte(obj.fetch_byte())
        elif mode == 'zpx':
            return obj.read_byte(obj.fetch_byte()+obj.reg_x)
        elif mode == 'zpy':
            return obj.read_byte(obj.fetch_byte()+obj.reg_y)
        elif mode == 'inx':
            return obj.read_word(obj.read_word(obj.fetch_byte() + obj.reg_x))
        elif mode == 'iny':
            return obj.read_word(obj.read_word(obj.fetch_byte() + obj.reg_y))

    def put(self, obj, mode):
        if mode == 'abs':
            return obj.fetch_word()
        if mode == 'abx':
            return obj.fetch_word()+obj.reg_x
        if mode == 'aby':
            return obj.fetch_word()+obj.reg_y
        elif mode == 'zp':
            return obj.fetch_byte()
        elif mode == 'zpx':
            return obj.fetch_byte()+obj.reg_x
        elif mode == 'zpy':
            return obj.fetch_byte()+obj.reg_y
        elif mode == 'inx':
            return obj.read_word(obj.fetch_byte() + obj.reg_x)
        elif mode == 'iny':
            return obj.read_word(obj.fetch_byte() + obj.reg_y)

    ''' 
        Instructions 
        Split into sections    
    '''

    ''' Section 1: Load and store '''

    def lda(self, obj, mode):
        ''' Load register A '''
        obj.reg_a = self.get(obj, mode)
        obj.flag_z = bool(not obj.reg_a)
        obj.flag_n = bool(int(format(obj.reg_a, '08b')[-8]))

    def ldx(self, obj, mode):
        ''' Load register X '''
        obj.reg_x = self.get(obj, mode)
        obj.flag_z = bool(not obj.reg_x)
        obj.flag_n = bool(int(format(obj.reg_x, '08b')[-8]))

    def ldy(self, obj, mode):
        ''' Load register Y '''
        obj.reg_y = self.get(obj, mode)
        obj.flag_z = bool(not obj.reg_y)
        obj.flag_n = bool(int(format(obj.reg_y, '08b')[-8]))

    def sta(self, obj, mode):
        ''' Store register A '''
        obj.write_byte(self.put(obj, mode), obj.reg_a)

    def stx(self, obj, mode):
        ''' Store register X '''
        obj.write_byte(self.put(obj, mode), obj.reg_x)

    def sty(self, obj, mode):
        ''' Store register Y '''
        obj.write_byte(self.put(obj, mode), obj.reg_y)

    ''' Section 2: Transfer '''

    def tax(self, obj, mode):
        ''' Transfer A to X '''
        obj.reg_x = obj.reg_a
        obj.flag_z = bool(not obj.reg_a)
        obj.flag_n = bool(int(format(obj.reg_a, '08b')[-8]))

    def tay(self, obj, mode):
        ''' Transfer A to Y '''
        obj.reg_y = obj.reg_a
        obj.flag_z = bool(not obj.reg_y)
        obj.flag_n = bool(int(format(obj.reg_y, '08b')[-8]))

    def tsx(self, obj, mode):
        ''' Transfer stack pointer to X '''
        obj.reg_x = obj.stack_pointer
        obj.flag_z = bool(not obj.reg_x)
        obj.flag_n = bool(int(format(obj.reg_x, '08b')[-8]))

    def txa(self, obj, mode):
        ''' Transfer X to A '''
        obj.reg_a = obj.reg_x
        obj.flag_z = bool(not obj.reg_a)
        obj.flag_n = bool(int(format(obj.reg_a, '08b')[-8]))

    def txs(self, obj, mode):
        ''' Transfer stack pointer to X '''
        obj.stack_pointer = obj.reg_x

    def tya(self, obj, mode):
        ''' Transfer Y to A '''
        obj.reg_a = obj.reg_y
        obj.flag_z = bool(not obj.reg_a)
        obj.flag_n = bool(int(format(obj.reg_a, '08b')[-8]))

    ''' Section 4: Shift '''

    def asl(self, obj, mode):
        ''' Arithmetic shift left '''
        if mode == 'acc':
            value = obj.reg_a
            self.flag_c = bool(int(format(value, '08b')[-8]))
            value = max(value << 1, 0xff)
            obj.reg_a = value
        else:
            value = self.get(obj, mode)
            self.flag_c = bool(int(format(value, '08b')[-8]))
            addr = self.put(obj, mode)
            value = max(value << 1, 0xff)
            obj.write_byte(addr, value)
        self.flag_n = bool(int(format(value, '08b')[-8]))
        self.flag_z = bool(value)

    def lsr(self, obj, mode):
        ''' Logical shift right '''
        if mode == 'acc':
            value = obj.reg_a
            self.flag_c = bool(int(format(value, '08b')[-1]))
            value = max(value >> 1, 0xff)
            obj.reg_a = value
        else:
            value = self.get(obj, mode)
            self.flag_c = bool(int(format(value, '08b')[-1]))
            addr = self.put(obj, mode)
            value = max(value >> 1, 0xff)
            obj.write_byte(addr, value)
        self.flag_n = False
        self.flag_z = bool(value)

    def rol(self, obj, mode):
        ''' Rotate bits to the left '''
        if mode == 'acc':
            value = obj.reg_a
            self.flag_c = bool(int(format(value, '08b')[-8]))
            value = max((value << 1) + int(self.flag_c), 0xff)
            obj.reg_a = value
        else:
            value = self.get(obj, mode)
            self.flag_c = bool(int(format(value, '08b')[-8]))
            addr = self.put(obj, mode)
            value = max((value << 1) + int(self.flag_c), 0xff)
            obj.write_byte(addr, value)
        self.flag_n = bool(int(format(value, '08b')[-8]))
        self.flag_z = bool(value)

    def ror(self, obj, mode):
        ''' Rotate bits to the left '''
        if mode == 'acc':
            value = obj.reg_a
            self.flag_n = bool(int(format(value, '08b')[-8]))
            self.flag_c = bool(int(format(value, '08b')[-1]))
            value = max((value >> 1) + int(self.flag_c)*0xf0, 0xff)
            obj.reg_a = value
        else:
            value = self.get(obj, mode)
            self.flag_n = bool(int(format(value, '08b')[-8]))
            self.flag_c = bool(int(format(value, '08b')[-1]))
            addr = self.put(obj, mode)
            value = max((value >> 1) + int(self.flag_c)*0xf0, 0xff)
            obj.write_byte(addr, value)
        self.flag_z = bool(value)

    ''' Section 5: Logical instructions'''

    def AND(self, obj, mode):
        ''' Logical AND with accumulator & '''
        obj.reg_a = obj.reg_a & self.get(obj, mode)
        obj.flag_z = bool(obj.reg_a)
        obj.flag_n = bool(int(format(obj.reg_a, '08b')[-8]))

    def bit(self, obj, mode):
        ''' Test bit in memory with accumulator '''
        value = self.get(obj, mode)
        obj.flag_n = bool(int(format(value, '08b')[-8]))
        obj.flag_v = bool(int(format(value, '08b')[-7]))
        obj.flag_z = bool(addr & obj.reg_a)

    def eor(self, obj, mode):
        ''' Binary Exclusive OR with accumulator ^'''
        obj.reg_a = obj.reg_a ^ self.get(obj, mode)
        obj.flag_z = bool(obj.reg_a)
        obj.flag_n = bool(int(format(obj.reg_a, '08b')[-8]))

    def ora(self, obj, mode):
        ''' Binary OR with accumulator | '''
        obj.reg_a = obj.reg_a | self.get(obj, mode)
        obj.flag_z = bool(obj.reg_a)
        obj.flag_n = bool(int(format(obj.reg_a, '08b')[-8]))

    ''' Section 6: Arithmetic instructions '''

    def adc(self, obj, mode):
        ''' Add with carry '''
        value = self.get(obj, mode)
        n = int(format(value, '08b')[-8])
        m = int(format(obj.reg_a, '08b')[-8])
        obj.reg_a = obj.reg_a + value
        if obj.reg_a > 0xff:
            obj.reg_a -= 0x100
            obj.flag_c = True
        else:
            obj.flag_c = False
        # obj.flag_v = (not m & not n & not obj.flag_c) | (m & n & ! obj.flag_c)
        obj.flag_n = bool(int(format(obj.reg_a, '08b')[-8]))

    def cmp(self, obj, mode):
        ''' Compare memory and accumulator '''
        value = self.get(obj, mode)
        obj.flag_c = obj.reg_a >= value
        obj.flag_z = bool(not (obj.reg_a - value))
        obj.flag_n = bool(int(format(obj.reg_a, '08b')[-8]))

    def cpx(self, obj, mode):
        ''' Compare Register X '''
        value = self.get(obj, mode)
        obj.flag_c = obj.reg_x >= value
        obj.flag_z = bool(not (obj.reg_x - value))
        obj.flag_n = bool(int(format(obj.reg_x, '08b')[-8]))

    def cpy(self, obj, mode):
        ''' Compare Register Y '''
        value = self.get(obj, mode)
        obj.flag_c = obj.reg_y >= value
        obj.flag_z = bool(not (obj.reg_y - value))
        obj.flag_n = bool(int(format(obj.reg_y, '08b')[-8]))

    def sbc(self, obj, mode):
        ''' Subtract with borrow '''
        value = self.get(obj, mode)
        n = int(format(value, '08b')[-8])
        m = int(format(obj.reg_a, '08b')[-8])
        obj.reg_a -= value
        obj.flag_c = obj.reg_a >= 0
        obj.flag_v = obj.reg_a >= 0x80
        obj.flag_z = bool(not obj.reg_a)
        obj.flag_n = bool(int(format(obj.reg_a, '08b')[-8]))

    ''' Section 7: Incrementing instructions '''

    def dec(self, obj, mode):
        ''' Decrement memory by 1 '''
        value = self.get(obj, mode)
        addr = self.put(obj, mode)
        value -= 1
        obj.write_byte(addr, value)
        obj.flag_z = bool(not value)
        obj.flag_n = bool(int(format(value, '08b')[-8]))

    def dex(self, obj, mode):
        ''' Increment register X '''
        obj.reg_x -= 0x01
        obj.flag_z = bool(not obj.reg_x)
        obj.flag_n = bool(int(format(obj.reg_x, '08b')[-8]))

    def dey(self, obj, mode):
        ''' Increment register Y '''
        obj.reg_y -= 0x01
        obj.flag_z = bool(not obj.reg_y)
        obj.flag_n = bool(int(format(obj.reg_y, '0b8')[-8]))

    def inc(self, obj, mode):
        ''' Increment memory by 1 '''
        value = self.get(obj, mode)
        addr = self.put(obj, mode)
        value += 1
        obj.write_byte(addr, value)
        obj.flag_z = bool(not value)
        obj.flag_n = bool(int(format(value, '08b')[-8]))

    def inx(self, obj, mode):
        ''' Increment register X '''
        obj.reg_x += 0x01
        obj.flag_z = bool(not obj.reg_x)
        obj.flag_n = bool(int(format(obj.reg_x, '08b')[-8]))

    def iny(self, obj, mode):
        ''' Increment register Y '''
        obj.reg_y += 0x01
        obj.flag_z = bool(not obj.reg_y)
        obj.flag_n = bool(int(format(obj.reg_y, '08b')[-8]))

    ''' Section 8: Control '''

    def brk(self, obj, mode):
        ''' Break - end program '''
        obj.flag_b = True

    def jmp(self, obj, mode):
        ''' Jump to address '''
        obj.program_counter = self.get(obj, mode)

    def jsr(self, obj, mode):
        ''' Jump to subroutine '''
        obj.stack_pointer -= 0x01
        obj.write_word(obj.stack_pointer+0x100, obj.program_counter+0x01)
        obj.stack_pointer -= 0x01
        obj.program_counter = obj.fetch_word()

    def rti(self, obj, mode):
        ''' To be implemented '''
        print('RTI not implemented')
        input()

    def rts(self, obj, mode):
        ''' Return from subroutine '''
        obj.stack_pointer += 0x01
        obj.program_counter = obj.read_word(obj.stack_pointer+0x100)+0x01
        obj.stack_pointer += 0x01

    ''' Section 9: Branching '''

    def bcc(self, obj, mode):
        ''' Branch on clear carry '''
        addr = obj.fetch_byte()
        if addr > 0x80:
            addr -= 0x100
        if not obj.flag_c:
            obj.program_counter += addr

    def bcs(self, obj, mode):
        ''' Branch on carry set '''
        addr = obj.fetch_byte()
        if addr > 0x80:
            addr -= 0x100
        if obj.flag_c:
            obj.program_counter += addr

    def beq(self, obj, mode):
        ''' Branch on equal (zero)'''
        addr = obj.fetch_byte()
        if addr > 0x80:
            addr -= 0x100
        if obj.flag_z:
            obj.program_counter += addr

    def bmi(self, obj, mode):
        ''' Branch on negative '''
        addr = obj.fetch_byte()
        if addr > 0x80:
            addr -= 0x100
        if obj.flag_n:
            obj.program_counter += addr

    def bne(self, obj, mode):
        ''' Branch on result not zero (not equal) '''
        addr = obj.fetch_byte()
        if addr > 0x80:
            addr -= 0x100
        if not obj.flag_z:
            obj.program_counter += addr

    def bpl(self, obj, mode):
        ''' Branch on not negative '''
        addr = obj.fetch_byte()
        if addr > 0x80:
            addr -= 0x100
        if not obj.flag_n:
            obj.program_counter += addr

    def bvc(self, obj, mode):
        ''' Branch on overflow clear '''
        addr = obj.fetch_byte()
        if addr > 0x80:
            addr -= 0x100
        if not obj.flag_v:
            obj.program_counter += addr

    def bvs(self, obj, mode):
        ''' Branch on overflow set '''
        addr = obj.fetch_byte()
        if addr > 0x80:
            addr -= 0x100
        if obj.flag_v:
            obj.program_counter += addr

    ''' Section 10: Flags & NOP'''

    def clc(self, obj, mode):
        ''' Clear carry flag '''
        obj.flag_c = False

    def cld(self, obj, mode):
        ''' Clear decimal flag '''
        obj.flag_d = False

    def cli(self, obj, mode):
        ''' Clear interupt disable '''
        obj.flag_i = False

    def clv(self, obj, mode):
        ''' Clear overflow flag '''
        obj.flag_v = False

    def sec(self, obj, mode):
        ''' Set carry flag '''
        obj.flag_c = True

    def sed(self, obj, mode):
        ''' Set decimal mode '''
        obj.flag_d = True

    def sei(self, obj, mode):
        ''' Set interupt disable '''
        obj.flag_i = True

    def nop(self, obj, mode):
        ''' No operations '''
        obj.cycles += 1
