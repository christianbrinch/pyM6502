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
        obj.toggle(1, not obj.reg_a)        # toogle Z
        obj.toggle(7, obj.reg_a & 0x80)     # toogle N

    def ldx(self, obj, mode):
        ''' Load register X '''
        obj.reg_x = eval("self.get_"+mode+"(obj)")
        obj.toggle(1, not obj.reg_x)        # toogle Z
        obj.toggle(7, obj.reg_x & 0x80)     # toogle N

    def ldy(self, obj, mode):
        ''' Load register Y '''
        obj.reg_y = eval("self.get_"+mode+"(obj)")
        obj.toggle(1, not obj.reg_y)        # toogle Z
        obj.toggle(7, obj.reg_y & 0x80)     # toogle N


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
        obj.toggle(1, not obj.reg_a)        # toogle Z
        obj.toggle(7, obj.reg_a & 0x80)     # toogle N

    def tay(self, obj, mode):
        ''' Transfer A to Y '''
        obj.reg_y = obj.reg_a
        obj.toggle(1, not obj.reg_y)        # toogle Z
        obj.toggle(7, obj.reg_y & 0x80)     # toogle N

    def tsx(self, obj, mode):
        ''' Transfer stack pointer to X '''
        obj.reg_x = obj.stack_pointer
        obj.toggle(1, not obj.reg_x)        # toogle Z
        obj.toggle(7, obj.reg_x & 0x80)     # toogle N

    def txa(self, obj, mode):
        ''' Transfer X to A '''
        obj.reg_a = obj.reg_x
        obj.toggle(1, not obj.reg_a)        # toogle Z
        obj.toggle(7, obj.reg_a & 0x80)     # toogle N

    def txs(self, obj, mode):
        ''' Transfer stack pointer to X '''
        obj.stack_pointer = obj.reg_x

    def tya(self, obj, mode):
        ''' Transfer Y to A '''
        obj.reg_a = obj.reg_y
        obj.toggle(1, not obj.reg_a)        # toogle Z
        obj.toggle(7, obj.reg_a & 0x80)     # toogle N


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
            obj.toggle(0, not value)        # toogle C
            value = min(value << 1, 0xff)
            obj.reg_a = value
        else:
            value = eval("self.get_"+mode+"(obj)")
            obj.toggle(0, not value)        # toogle C
            addr = eval("self.put_"+mode+"(obj)")
            value = min(value << 1, 0xff)
            obj.write_byte(addr, value)
        obj.toggle(1, not value)        # toogle Z
        obj.toggle(7, value & 0x80)     # toogle N


    def lsr(self, obj, mode):
        ''' Logical shift right '''
        if mode == 'acc':
            value = obj.reg_a
            obj.toggle(0, value & 0x01)        # toogle C
            value = value >> 1
            obj.reg_a = value
        else:
            value = eval("self.get_"+mode+"(obj)")
            obj.toggle(0, value & 0x01)        # toogle C
            addr = eval("self.put_"+mode+"(obj)")
            value = value >> 1
            obj.write_byte(addr, value)
        obj.toggle(1, not value)        # toogle Z
        obj.toggle(7, 0x00)             # toogle N

    def rol(self, obj, mode):
        ''' Rotate bits to the left '''
        if mode == 'acc':
            value = obj.reg_a
            obj.toggle(0, value & 0x80)        # toogle C
            value = max((value << 1) + (obj.reg_p & 0x01), 0xff)
            obj.reg_a = value
        else:
            value = eval("self.get_"+mode+"(obj)")
            obj.toggle(0, value & 0x80)        # toogle C
            addr = eval("self.put_"+mode+"(obj)")
            value = max((value << 1) + (obj.reg_p & 0x01), 0xff)
            obj.write_byte(addr, value)
        obj.toggle(1, not value)        # toogle Z
        obj.toggle(7, value & 0x80)     # toogle N


    def ror(self, obj, mode):
        ''' Rotate bits to the right '''
        if mode == 'acc':
            value = obj.reg_a
            obj.toggle(0, value & 0x01)        # toogle C
            value = (value >> 1) | (obj.reg_p & 0x01) * 0x80
            obj.reg_a = value
        else:
            value = eval("self.get_"+mode+"(obj)")
            obj.toggle(0, value & 0x01)        # toogle C
            addr = eval("self.put_"+mode+"(obj)")
            value = (value >> 1) | (obj.reg_p & 0x01) * 0x80
            obj.write_byte(addr, value)
        obj.toggle(1, not value)        # toogle Z
        obj.toggle(7, value & 0x80)     # toogle N


    ''' Section 5: Logical instructions'''

    def AND(self, obj, mode):
        ''' Logical AND with accumulator & '''
        obj.reg_a = obj.reg_a & eval("self.get_"+mode+"(obj)")
        obj.toggle(1, not obj.reg_a)        # toogle Z
        obj.toggle(7, obj.reg_a & 0x80)     # toogle N


    def bit(self, obj, mode):
        ''' Test bit in memory with accumulator '''
        value = eval("self.get_"+mode+"(obj)")
        obj.toggle(6, value & 0x20)                   # toogle V
        obj.toggle(1, not (value & obj.reg_a))        # toogle Z
        obj.toggle(7, value & 0x80)                   # toogle N

    def eor(self, obj, mode):
        ''' Binary Exclusive OR with accumulator ^'''
        obj.reg_a = obj.reg_a ^ eval("self.get_"+mode+"(obj)")
        obj.toggle(1, not obj.reg_a)        # toogle Z
        obj.toggle(7, obj.reg_a & 0x80)     # toogle N

    def ora(self, obj, mode):
        ''' Binary OR with accumulator | '''
        obj.reg_a = obj.reg_a | eval("self.get_"+mode+"(obj)")
        obj.toggle(1, not obj.reg_a)        # toogle Z
        obj.toggle(7, obj.reg_a & 0x80)     # toogle N

    ''' Section 6: Arithmetic instructions '''

    def adc(self, obj, mode):
        ''' Add with carry '''
        value = eval("self.get_"+mode+"(obj)")
        result = obj.reg_a + value + (obj.reg_p & 0x01)
        M = bool(obj.reg_a & 0x80)
        N = bool(value & 0x80)
        C = bool((obj.reg_a & 0x40) & (value & 0x40))
        obj.toggle(6, (~M&~N&C) | (M&N&~C)) # toggle overflow flag

        obj.reg_a = result % 0x100

        obj.toggle(0, int(result > 0xff))   # Toggle carry
        obj.toggle(1, not obj.reg_a)        # toogle Z
        obj.toggle(7, obj.reg_a & 0x80)     # toogle N



    def cmp(self, obj, mode):
        ''' Compare memory and accumulator '''
        value = eval("self.get_"+mode+"(obj)")
        obj.toggle(0, int(obj.reg_a >= value))      # toogle C
        obj.toggle(1, not (obj.reg_a-value))        # toogle Z
        obj.toggle(7, (obj.reg_a-value) & 0x80)     # toogle N


    def cpx(self, obj, mode):
        ''' Compare Register X '''
        value = eval("self.get_"+mode+"(obj)")
        obj.toggle(0, int(obj.reg_x >= value))      # toogle C
        obj.toggle(1, not (obj.reg_x-value))        # toogle Z
        obj.toggle(7, int((obj.reg_x-value)<0))     # toogle N


    def cpy(self, obj, mode):
        ''' Compare Register Y '''
        value = eval("self.get_"+mode+"(obj)")
        obj.toggle(0, int(obj.reg_y >= value))      # toogle C
        obj.toggle(1, not (obj.reg_y-value))        # toogle Z
        obj.toggle(7, int((obj.reg_y-value)<0))     # toogle N

    def sbc(self, obj, mode):
        ''' Subtract with borrow '''
        value = eval("self.get_"+mode+"(obj)")
        result = obj.reg_a - value - (1- (obj.reg_p & 0x01))
        M = bool(obj.reg_a & 0x80)
        N = bool(value & 0x80)
        C = bool((obj.reg_a & 0x40) & (value & 0x40))
        obj.toggle(6, (~M&N&C) | (M&~N&~C)) # toggle overflow flag
        obj.reg_a = result % 0x100

        obj.toggle(0, int(result>0x00))        # toogle C
        obj.toggle(1, not obj.reg_a)           # toogle Z
        obj.toggle(7, int(obj.reg_a>0x80))     # toogle N


    ''' Section 7: Incrementing instructions '''

    def dec(self, obj, mode):
        ''' Decrement memory by 1 '''
        addr = eval("self.put_"+mode+"(obj)")
        value = obj.read_byte(addr)
        value = (value - 1) % 256
        obj.write_byte(addr, value)
        obj.toggle(1, not value)        # toogle Z
        obj.toggle(7, value & 0x80)     # toogle N


    def dex(self, obj, mode):
        ''' Decrement register X '''
        obj.reg_x -= 0x01
        if obj.reg_x < 0:
            obj.reg_x = 0xff - (obj.reg_x + 1)

        obj.toggle(1, not obj.reg_x)        # toogle Z
        obj.toggle(7, int(obj.reg_x<0))     # toogle N

    def dey(self, obj, mode):
        ''' Decrement register Y '''
        obj.reg_y -= 0x01
        if obj.reg_y < 0:
            obj.reg_y = 0xff - (obj.reg_y + 1)
        obj.toggle(1, not obj.reg_y)        # toogle Z
        obj.toggle(7, int(obj.reg_y<0))     # toogle N

    def inc(self, obj, mode):
        ''' Increment memory by 1 '''
        addr = eval("self.put_"+mode+"(obj)")
        value = obj.read_byte(addr)
        value += 0x01
        obj.write_byte(addr, value%256)
        obj.toggle(1, not value)        # toogle Z
        obj.toggle(7, value & 0x80)     # toogle N

    def inx(self, obj, mode):
        ''' Increment register X '''
        obj.reg_x = (obj.reg_x+0x01)%256
        obj.toggle(1, not obj.reg_x)        # toogle Z
        obj.toggle(7, obj.reg_x & 0x80)     # toogle N

    def iny(self, obj, mode):
        ''' Increment register Y '''
        obj.reg_y = (obj.reg_y+0x01)%256
        obj.toggle(1, not obj.reg_y)        # toogle Z
        obj.toggle(7, obj.reg_y & 0x80)     # toogle N


    ''' Section 8: Control '''

    def brk(self, obj, mode):
        ''' Break - end program '''
        obj.toggle(4,0)     # Clear B flag

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
        obj.stack_pointer += 0x01
        obj.reg_p = obj.read_byte(obj.stack_pointer+0x100)
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
        if not (obj.reg_p & 0x01):
            obj.program_counter += addr

    def bcs(self, obj, mode):
        ''' Branch on carry set '''
        addr = obj.fetch_byte()
        if addr > 0x80:
            addr -= 0x100
        if obj.reg_p & 0x01:
            obj.program_counter += addr

    def beq(self, obj, mode):
        ''' Branch on equal (zero)'''
        addr = obj.fetch_byte()
        if addr > 0x80:
            addr -= 0x100
        if obj.reg_p & 0x02:
            obj.program_counter += addr

    def bmi(self, obj, mode):
        ''' Branch on negative '''
        addr = obj.fetch_byte()
        if addr > 0x80:
            addr -= 0x100
        if obj.reg_p & 0x80:
            obj.program_counter += addr

    def bne(self, obj, mode):
        ''' Branch on result not zero (not equal) '''
        addr = obj.fetch_byte()
        if addr > 0x80:
            addr -= 0x100
        if not(obj.reg_p & 0x02):
            obj.program_counter += addr

    def bpl(self, obj, mode):
        ''' Branch on not negative '''
        addr = obj.fetch_byte()
        if addr > 0x80:
            addr -= 0x100
        if not(obj.reg_p & 0x80):
            obj.program_counter += addr

    def bvc(self, obj, mode):
        ''' Branch on overflow clear '''
        addr = obj.fetch_byte()
        if addr > 0x80:
            addr -= 0x100
        if not(obj.reg_p & 0x40):
            obj.program_counter += addr

    def bvs(self, obj, mode):
        ''' Branch on overflow set '''
        addr = obj.fetch_byte()
        if addr > 0x80:
            addr -= 0x100
        if obj.reg_p & 0x40 :
            obj.program_counter += addr

    ''' Section 10: Flags & NOP'''

    def clc(self, obj, mode):
        ''' Clear carry flag '''
        obj.cycles += 1
        obj.toggle(0,0)     # Clear C flag

    def cld(self, obj, mode):
        ''' Clear decimal flag '''
        obj.cycles += 1
        obj.toggle(3,0)     # Clear D flag

    def cli(self, obj, mode):
        ''' Clear interupt disable '''
        obj.cycles += 1
        obj.toggle(2,0)     # Clear I flag

    def clv(self, obj, mode):
        ''' Clear overflow flag '''
        obj.cycles += 1
        obj.toggle(6,0)     # Clear V flag

    def sec(self, obj, mode):
        ''' Set carry flag '''
        obj.cycles += 1
        obj.toggle(0,1)     # Set C flag

    def sed(self, obj, mode):
        ''' Set decimal mode '''
        obj.cycles += 1
        obj.toggle(3,1)     # Set D flag

    def sei(self, obj, mode):
        ''' Set interupt disable '''
        obj.cycles += 1
        obj.toggle(2,1)     # Set I flag

    def nop(self, obj, mode):
        ''' No operations '''
        obj.cycles += 1
