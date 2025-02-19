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
    def get_imm(self, obj):
        return obj.fetch_byte()
    def get_abs(self, obj):
        return obj.read_byte(obj.fetch_word())
    def get_abs(self, obj):
        return obj.read_byte(obj.fetch_word())
    def get_abx(self, obj):
        return obj.read_byte(obj.fetch_word() + obj.reg_x)
    def get_aby(self, obj):
        return obj.read_byte(obj.fetch_word() + obj.reg_y)
    def get_zp(self, obj):
        return obj.read_byte(obj.fetch_byte())
    def get_zpx(self, obj):
        return obj.read_byte(obj.fetch_byte() + obj.reg_x)
    def get_zpy(self, obj):
        return obj.read_byte(obj.fetch_byte() + obj.reg_y)
    def get_inx(self, obj):
        return obj.read_byte(obj.read_word(obj.fetch_byte()) + obj.reg_x)
    def get_iny(self, obj):
        return obj.read_byte(obj.read_word(obj.fetch_byte()) + obj.reg_y)

    def put_abs(self, obj):
        return obj.fetch_word()
    def put_ind(self, obj):
        return obj.read_word(obj.fetch_word())
    def put_abx(self, obj):
        return obj.fetch_word()+obj.reg_x
    def put_aby(self, obj):
        return obj.fetch_word()+obj.reg_y
    def put_zp(self, obj):
        return obj.fetch_byte()
    def put_zpx(self, obj):
        return obj.fetch_byte()+obj.reg_x
    def put_zpy(self, obj):
        return obj.fetch_byte()+obj.reg_y
    def put_inx(self, obj):
        return obj.read_word(obj.fetch_byte()) + obj.reg_x
    def put_iny(self, obj):
        return obj.read_word(obj.fetch_byte()) + obj.reg_y

    '''
        Instructions
        Split into sections
    '''

    ''' Section 1: Load and store '''

    def lda(self, obj, mode):
        ''' Load register A '''
        obj.reg_a = eval("self.get_"+mode+"(obj)")
        obj.flag_z = bool(not obj.reg_a)
        obj.flag_n = bool(int(format(obj.reg_a, '08b')[-8]))

    def ldx(self, obj, mode):
        ''' Load register X '''
        obj.reg_x = eval("self.get_"+mode+"(obj)")
        obj.flag_z = bool(not obj.reg_x)
        obj.flag_n = bool(int(format(obj.reg_x, '08b')[-8]))

    def ldy(self, obj, mode):
        ''' Load register Y '''
        obj.reg_y = eval("self.get_"+mode+"(obj)")
        obj.flag_z = bool(not obj.reg_y)
        obj.flag_n = bool(int(format(obj.reg_y, '08b')[-8]))

    def sta(self, obj, mode):
        ''' Store register A '''
        obj.write_byte(eval("self.put_"+mode+"(obj)"), obj.reg_a)


    def stx(self, obj, mode):
        ''' Store register X '''
        obj.write_byte(eval("self.put_"+mode+"(obj)"), obj.reg_x)

    def sty(self, obj, mode):
        ''' Store register Y '''
        obj.write_byte(eval("self.put_"+mode+"(obj)"), obj.reg_y)

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

    ''' Section 3: Stack instructions'''

    def pha(self, obj, mode):
        ''' Push accumulator onto stack '''
        obj.write_byte(obj.stack_pointer+0x100, obj.reg_a)
        obj.stack_pointer -= 0x01

    def pla(self, obj, mode):
        ''' Pull accumulator onto stack '''
        obj.stack_pointer += 0x01
        obj.reg_a = obj.read_byte(obj.stack_pointer+0x100)

    ''' Section 4: Shift '''

    def asl(self, obj, mode):
        ''' Arithmetic shift left '''
        if mode == 'acc':
            value = obj.reg_a
            obj.flag_c = bool(int(format(value, '08b')[-8]))
            value = min(value << 1, 0xff)
            obj.reg_a = value
        else:
            value = eval("self.get_"+mode+"(obj)")
            obj.flag_c = bool(int(format(value, '08b')[-8]))
            addr = eval("self.put_"+mode+"(obj)")
            value = min(value << 1, 0xff)
            obj.write_byte(addr, value)
        obj.flag_n = bool(int(format(value, '08b')[-8]))
        obj.flag_z = bool(not value)

    def lsr(self, obj, mode):
        ''' Logical shift right '''
        if mode == 'acc':
            value = obj.reg_a
            obj.flag_c = bool(int(format(value, '08b')[-1]))
            value = value >> 1
            obj.reg_a = value
        else:
            value = eval("self.get_"+mode+"(obj)")
            obj.flag_c = bool(int(format(value, '08b')[-1]))
            addr = eval("self.put_"+mode+"(obj)")
            value = value >> 1
            obj.write_byte(addr, value)
        obj.flag_n = False
        obj.flag_z = bool(not value)

    def rol(self, obj, mode):
        ''' Rotate bits to the left '''
        if mode == 'acc':
            value = obj.reg_a
            obj.flag_c = bool(int(format(value, '08b')[-8]))
            value = max((value << 1) + int(obj.flag_c), 0xff)
            obj.reg_a = value
        else:
            value = eval("self.get_"+mode+"(obj)")
            obj.flag_c = bool(int(format(value, '08b')[-8]))
            addr = eval("self.put_"+mode+"(obj)")
            value = max((value << 1) + int(obj.flag_c), 0xff)
            obj.write_byte(addr, value)
        obj.flag_n = bool(int(format(value, '08b')[-8]))
        obj.flag_z = bool(value)

    def ror(self, obj, mode):
        ''' Rotate bits to the right '''
        if mode == 'acc':
            value = obj.reg_a
            obj.flag_c = bool(value & (1<<0))
            value = (value >> 1) | int(obj.flag_c) * 0x80
            obj.reg_a = value
        else:
            value = eval("self.get_"+mode+"(obj)")
            obj.flag_c = bool(value & (1<<0))
            addr = eval("self.put_"+mode+"(obj)")
            value = (value >> 1) | int(obj.flag_c) * 0x80
            obj.write_byte(addr, value)
        obj.flag_n = bool(value & 0x80)
        obj.flag_z = not bool(value)

    ''' Section 5: Logical instructions'''

    def AND(self, obj, mode):
        ''' Logical AND with accumulator & '''
        obj.reg_a = obj.reg_a & eval("self.get_"+mode+"(obj)")
        obj.flag_z = bool(obj.reg_a)
        obj.flag_n = bool(int(format(obj.reg_a, '08b')[-8]))

    def bit(self, obj, mode):
        ''' Test bit in memory with accumulator '''
        value = eval("self.get_"+mode+"(obj)")
        obj.flag_n = bool(int(format(value, '08b')[-8]))
        obj.flag_v = bool(int(format(value, '08b')[-7]))
        obj.flag_z = bool(not (value & obj.reg_a))

    def eor(self, obj, mode):
        ''' Binary Exclusive OR with accumulator ^'''
        obj.reg_a = obj.reg_a ^ eval("self.get_"+mode+"(obj)")
        obj.flag_z = bool(not obj.reg_a)
        obj.flag_n = bool(int(format(obj.reg_a, '08b')[-8]))

    def ora(self, obj, mode):
        ''' Binary OR with accumulator | '''
        obj.reg_a = obj.reg_a | eval("self.get_"+mode+"(obj)")
        obj.flag_z = bool(not obj.reg_a)
        obj.flag_n = bool(int(format(obj.reg_a, '08b')[-8]))

    ''' Section 6: Arithmetic instructions '''

    def adc(self, obj, mode):
        ''' Add with carry '''
        value = eval("self.get_"+mode+"(obj)")
        n = int(format(value, '08b')[-8])
        m = int(format(obj.reg_a, '08b')[-8])
        obj.reg_a = obj.reg_a + value
        if obj.reg_a > 0xff:
            obj.reg_a -= 0x100
            obj.flag_c = True
        else:
            obj.flag_c = False
        # obj.flag_v = (not m & not n & not obj.flag_c) | (m & n & ! obj.flag_c)
        obj.flag_z = bool(not obj.reg_a)
        obj.flag_n = bool(int(format(obj.reg_a, '08b')[-8]))

    def cmp(self, obj, mode):
        ''' Compare memory and accumulator '''
        value = eval("self.get_"+mode+"(obj)")
        obj.flag_c = obj.reg_a >= value
        obj.flag_z = bool(not (obj.reg_a - value))
        obj.flag_n = bool((obj.reg_a - value) & 0x80)
        #if obj.reg_a - value < 0:
        #    obj.flag_n = True
        #else:
        #    obj.flag_n = False

    def cpx(self, obj, mode):
        ''' Compare Register X '''
        value = eval("self.get_"+mode+"(obj)")
        obj.flag_c = obj.reg_x >= value
        obj.flag_z = bool(not (obj.reg_x - value))
        if obj.reg_x - value < 0:
            obj.flag_n = True
        else:
            obj.flag_n = False

    def cpy(self, obj, mode):
        ''' Compare Register Y '''
        value = eval("self.get_"+mode+"(obj)")
        obj.flag_c = obj.reg_y >= value
        obj.flag_z = bool(not (obj.reg_y - value))
        if obj.reg_y - value < 0:
            obj.flag_n = True
        else:
            obj.flag_n = False

    def sbc(self, obj, mode):
        ''' Subtract with borrow '''
        value = eval("self.get_"+mode+"(obj)")
        n = int(format(value, '08b')[-8])
        m = int(format(obj.reg_a, '08b')[-8])
        obj.reg_a = obj.reg_a - value - (1- int(obj.flag_c))
        if obj.reg_a >= 0:
            obj.flag_c = True
        else:
            obj.flag_c = False
            # obj.flag_v = True
            obj.reg_a += 0x100
        if obj.reg_a > 0x80:
            obj.flag_n = True
        else:
            obj.flag_n = False
        obj.flag_z = bool(not obj.reg_a)

    ''' Section 7: Incrementing instructions '''

    def dec(self, obj, mode):
        ''' Decrement memory by 1 '''
        addr = eval("self.put_"+mode+"(obj)")
        value = obj.read_byte(addr)
        value = (value - 1) % 256
        obj.write_byte(addr, value)
        obj.flag_z = bool(not value)
        obj.flag_n = obj.flag_n = bool(value & 0x80)

    def dex(self, obj, mode):
        ''' Decrement register X '''
        obj.reg_x -= 0x01
        if obj.reg_x < 0:
            obj.flag_n = True
            obj.reg_x = 0xff - (obj.reg_x + 1)
        else:
            obj.flag_n = False
        obj.flag_z = bool(not obj.reg_x)

    def dey(self, obj, mode):
        ''' Decrement register Y '''
        obj.reg_y -= 0x01
        if obj.reg_y < 0:
            obj.flag_n = True
            obj.reg_y = 0xff - (obj.reg_y + 1)
        else:
            obj.flag_n = False
        obj.flag_z = bool(not obj.reg_y)

    def inc(self, obj, mode):
        ''' Increment memory by 1 '''
        addr = eval("self.put_"+mode+"(obj)")
        value = obj.read_byte(addr)
        value += 0x01
        obj.write_byte(addr, value%256)
        obj.flag_z = bool(not value)
        obj.flag_n = bool(int(format(value, '08b')[-8]))

    def inx(self, obj, mode):
        ''' Increment register X '''
        obj.reg_x = (obj.reg_x+0x01)%256
        obj.flag_z = bool(not obj.reg_x)
        obj.flag_n = bool(int(format(obj.reg_x, '08b')[-8]))

    def iny(self, obj, mode):
        ''' Increment register Y '''
        obj.reg_y = (obj.reg_y+0x01)%256
        obj.flag_z = bool(not obj.reg_y)
        obj.flag_n = bool(int(format(obj.reg_y, '08b')[-8]))

    ''' Section 8: Control '''

    def brk(self, obj, mode):
        ''' Break - end program '''
        obj.flag_b = False

    def jmp(self, obj, mode):
        ''' Jump to address '''
        obj.program_counter = eval("self.put_"+mode+"(obj)")

    def jsr(self, obj, mode):
        ''' Jump to subroutine: 6 cycles '''
        obj.cycles += 1
        obj.stack_pointer -= 0x01
        obj.write_word(obj.stack_pointer+0x100, obj.program_counter+0x01)
        obj.stack_pointer -= 0x01
        obj.program_counter = obj.fetch_word()

    def rti(self, obj, mode):
        ''' Return from interrupt: 6 cycles '''
        obj.stack_pointer += 0x00
        status = bin(obj.read_byte(obj.stack_pointer+0x100))[2:].zfill(8)
        obj.flag_n = bool(status[0])
        obj.flag_v = bool(status[1])
        obj.flag_d = bool(status[4])
        obj.flag_i = False #bool(status[5])
        obj.flag_z = bool(status[6])
        obj.flag_c = bool(status[7])
        obj.stack_pointer += 0x01
        obj.program_counter = obj.read_word(obj.stack_pointer+0x100)
        obj.stack_pointer += 0x01


    def rts(self, obj, mode):
        ''' Return from subroutine: 6 cycles '''
        obj.cycles += 3
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
        obj.cycles += 1
        obj.flag_c = False

    def cld(self, obj, mode):
        ''' Clear decimal flag '''
        obj.cycles += 1
        obj.flag_d = False

    def cli(self, obj, mode):
        ''' Clear interupt disable '''
        obj.cycles += 1
        obj.flag_i = False

    def clv(self, obj, mode):
        ''' Clear overflow flag '''
        obj.cycles += 1
        obj.flag_v = False

    def sec(self, obj, mode):
        ''' Set carry flag '''
        obj.cycles += 1
        obj.flag_c = True

    def sed(self, obj, mode):
        ''' Set decimal mode '''
        obj.cycles += 1
        obj.flag_d = True

    def sei(self, obj, mode):
        ''' Set interupt disable '''
        obj.cycles += 1
        obj.flag_i = True

    def nop(self, obj, mode):
        ''' No operations '''
        obj.cycles += 1
