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

    def imp(self, obj, mode=None):
        return

    def acc(self, obj, mode=None):
        return obj.reg_a

    def imm(self, obj, mode=None):
        return obj.fetch_byte()

    def abs(self, obj, mode=None):
        return obj.fetch_word()

    def abx(self, obj, mode=None):
        return obj.fetch_word()+obj.reg_x

    def aby(self, obj, mode=None):
        return obj.fetch_word()+obj.reg_y

    def zp(self, obj, mode=None):
        if mode == 'write':
            return obj.fetch_byte()
        return obj.read_byte(obj.fetch_byte())

    def zpx(self, obj, mode=None):
        if mode == 'write':
            return obj.fetch_byte()+obj.reg_x
        return obj.read_byte(obj.fetch_byte()+obj.reg_x)

    def zpy(self, obj, mode=None):
        if mode == 'write':
            return obj.fetch_byte()+obj.reg_y
        return obj.read_byte(obj.fetch_byte()+obj.reg_y)

    def inx(self, obj, mode=None):
        return obj.read_word(obj.read_word(obj.fetch_byte() + obj.reg_x))

    def iny(self, obj, mode=None):
        return obj.read_word(obj.read_word(obj.fetch_byte() + obj.reg_y))

    def rel(self, obj, mode=None):
       return obj.fetch_byte() 

    ''' Check flags '''

    def check(self, obj, flag, register):
        if flag == 'carry':
            if register > 0xff:
                obj.flag_c = True
        elif flag == 'zero':
            obj.flag_z = bool(not register)
        elif flag == 'neg':
            obj.flag_n = register<0

    ''' Instructions '''

    def adc(self, obj, mode):
        ''' Add with carry '''
        obj.reg_a += eval("self."+mode+"(obj)")
        self.check(obj, 'carry', obj.reg_a)
        self.check(obj, 'zero', obj.reg_a)
        self.check(obj, 'neg', obj.reg_a)

    def AND(self, obj, mode):
        ''' Logical AND with accumulator '''
        obj.reg_a = obj.reg_a & eval("self."+mode+"(obj)")
        self.check(obj, 'zero', obj.reg_a)
        self.check(obj, 'neg', obj.reg_a)

    def asl(self, obj, mode):
        ''' Arithmetic shift left '''
        obj.reg_a = eval("self."+mode+"(obj)") << 1
        self.check(obj, 'zero', obj.reg_a)
        self.check(obj, 'neg', obj.reg_a)

    def bcc(self, obj, mode):
        ''' Branch on clear carry '''
        addr = eval("self."+mode+"(obj)")
        if not obj.flag_c:
            obj.program_counter += addr

    def bit(self, obj, mode):
        ''' Test bit in memory with accumulator '''
        addr = eval("self."+mode+"(obj)")
        obj.flag_n = bool(int(format(obj.reg_a, '#010b')[2]))
        obj.flag_v = bool(int(format(obj.reg_a, '#010b')[3]))
        obj.flag_z = addr & obj.reg_a

    def beq(self, obj, mode):
        ''' Branch on equal '''
        addr = eval("self."+mode+"(obj)")
        if obj.flag_z:
            obj.program_counter += addr  
    
    def bmi(self, obj, mode):
        ''' Branch on negative '''
        addr = eval("self."+mode+"(obj)")
        if obj.flag_n:
            obj.program_counter += addr 

    def bne(self, obj, mode):
        ''' Branch on result not zero '''
        addr = eval("self."+mode+"(obj)")
        if not obj.flag_z:
            obj.program_counter += addr

    def bpl(self, obj, mode):
        ''' Branch on not negative '''
        addr = eval("self."+mode+"(obj)")
        if not obj.flag_n:
            obj.program_counter += addr - 0x100

    def brk(self, obj, mode):
        ''' Break - end program '''
        obj.flag_b = True

    def bcs(self, obj, mode):
        ''' Branch on carry set '''
        addr = eval("self."+mode+"(obj)")
        if obj.flag_c:
            obj.program_counter += addr


    def clc(self, obj, mode):
        ''' Clear carry flag '''
        obj.flag_c = False

    def cmp(self, obj, mode):
        ''' Compare memory and accumulator '''
        addr = eval("self."+mode+"(obj)")
        obj.flag_c = obj.reg_a >= addr
        obj.flag_z = bool(not (obj.reg_a - addr))
        obj.flag_n = bool(int(format(obj.reg_a, '#010b')[2]))

    def cpx(self, obj, mode):
        ''' Compare Register X '''
        addr = eval("self."+mode+"(obj)")
        obj.flag_c = obj.reg_x >= addr
        obj.flag_z = bool(not (obj.reg_x - addr))
        obj.flag_n = bool(int(format(obj.reg_x, '#010b')[2]))

    def cpy(self, obj, mode):
        ''' Compare Register Y '''
        addr = eval("self."+mode+"(obj)")
        obj.flag_c = obj.reg_y >= addr
        obj.flag_z = bool(not (obj.reg_y - addr))
        obj.flag_n = bool(int(format(obj.reg_y, '#010b')[2]))

    def dex(self, obj, mode):
        ''' Increment register X '''
        obj.reg_x -= 0x01
        self.check(obj, 'zero', obj.reg_x)
        self.check(obj, 'neg', obj.reg_x)
    
    def inx(self, obj, mode):
        ''' Increment register X '''
        obj.reg_x += 0x01
        self.check(obj, 'zero', obj.reg_x)
        self.check(obj, 'neg', obj.reg_x)

    def jmp(self, obj, mode):
        ''' Jump to address '''
        obj.program_counter = eval("self."+mode+"(obj)")

    def jsr(self, obj, mode):
        ''' Jump to subroutine '''
        obj.stack_pointer -= 0x01
        obj.write_word(obj.stack_pointer+0x100, obj.program_counter+0x01)
        obj.stack_pointer -= 0x01
        obj.program_counter = obj.fetch_word()

    def lda(self, obj, mode):
        ''' Load register A '''
        obj.reg_a = eval("self."+mode+"(obj)")
        self.check(obj, 'zero', obj.reg_a)
        self.check(obj, 'neg', obj.reg_a)

    def ldx(self, obj, mode):
        ''' Load register X '''
        obj.reg_x = eval("self."+mode+"(obj)")
        self.check(obj, 'zero', obj.reg_x)
        self.check(obj, 'neg', obj.reg_x)

    def ldy(self, obj, mode):
        ''' Load register Y '''
        obj.reg_y = eval("self."+mode+"(obj)")
        self.check(obj, 'zero', obj.reg_y)
        self.check(obj, 'neg', obj.reg_y)

    def lsr(self, obj, mode):
        ''' Logical shift right '''
        if mode == 'acc':
            obj.reg_a = eval("self."+mode+"(obj)") >> 1
        elif mode == 'abs':
            addr = obj.fetch_word()
            obj.write_word(addr, obj.read_byte(addr) >> 1)
        elif mode == 'zp':
            addr = obj.fetch_byte()
            obj.write_byte(addr, obj.read_byte(addr) >> 1)
        else:
            print(f'unknown mode {mode}')
            input()

    def nop(self, obj, mode):
        ''' No operations '''
        obj.cycles += 1

    def ora(self, obj, mode):
        ''' Logical inclusive OR '''
        obj.reg_a = obj.reg_a | eval("self."+mode+"(obj)")
        self.check(obj, 'zero', obj.reg_a)
        self.check(obj, 'neg', obj.reg_a)

    def rol(self, obj, mode):
        ''' Rotate bits to the left '''
        addr = eval("self."+mode+"(obj)")
        bit = int(format(addr, '#010b')[2])
        obj.reg_a = obj.reg_a << 1
        obj.reg_a += bit
        self.check(obj, 'zero', obj.reg_a)
        self.check(obj, 'neg', obj.reg_a)

    def rts(self, obj, mode):
        ''' Return from subroutine '''
        obj.stack_pointer += 0x01
        obj.program_counter = obj.read_word(obj.stack_pointer+0x100)+0x01
        obj.stack_pointer += 0x01

    def sbc(self, obj, mode):
        ''' Subtract with borrow '''
        addr = eval("self."+mode+"(obj)")
        obj.reg_a -= addr


    def sec(self, obj, mode):
        ''' Set carry flag '''
        obj.flag_c = True

    def sta(self, obj, mode):
        ''' Store register A '''
        obj.write_byte(eval("self."+mode+"(obj, 'write')"), obj.reg_a)

    def tax(self, obj, mode):
        ''' Transfer A to X '''
        obj.reg_x = obj.reg_a
        self.check(obj, 'zero', obj.reg_x)
        self.check(obj, 'neg', obj.reg_x)

    def txa(self, obj, mode):
        ''' Transfer X to A '''
        obj.reg_a = obj.reg_x
        self.check(obj, 'zero', obj.reg_a)
        self.check(obj, 'neg', obj.reg_a)

    ''' Illegal instructions '''

    def rra(self, obj, mode):
        ''' Rotate right + add with carry '''
        addr = eval("self."+mode+"(obj)")
        bit = int(format(addr, '#010b')[2])
        obj.reg_a += addr << 1
        obj.reg_a += bit
        self.check(obj, 'carry', obj.reg_a)
        self.check(obj, 'zero', obj.reg_a)
        self.check(obj, 'neg', obj.reg_a)

    def slo(self, obj, mode):
        ''' Arithmetic shift left + bitwise OR '''
        addr = eval("self."+mode+"(obj)")
        obj.reg_a = obj.reg_a | (addr << 1)
