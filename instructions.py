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

    def imp(self):
        return

    def acc(self, obj):
        return obj.reg_a

    def imm(self, obj):
        return obj.fetch_byte()

    def abs(self, obj):
        return obj.fetch_word()

    def abx(self, obj):
        return obj.fetch_word()+obj.reg_x

    def aby(self, obj):
        return obj.fetch_word()+obj.reg_y

    def zp(self, obj):
        return obj.fetch_byte()

    def zpx(self, obj):
        return obj.fetch_byte()+obj.reg_x

    def zpy(self, obj):
        return obj.fetch_byte()+obj.reg_y

    def inx(self, obj):
        obj.fetch_byte()
        return obj.fetch_byte + obj.reg_x

    def iny(self, obj):
        obj.fetch_byte()
        return obj.fetch_byte + obj.reg_y

    def rel(self, obj):
        obj.fetch_byte()
        return obj.fetch_byte()

    ''' Check flags '''

    def check(self, flag, register):
        if flag == 'carry':
            if register > 0xff:
                obj.flag_c = True
        elif flag == 'zero':
            self.flag_z = bool(not register)
        elif flag == 'neg':
            self.flag_z = bool(not register)

    ''' Instructions '''

    def adc(self, obj, mode):
        ''' Add with carry '''
        obj.reg_a += eval("self."+mode+"(obj)")
        self.check('carry', obj.reg_a)
        self.check('zero', obj.reg_a)
        self.check('neg', obj.reg_a)

    def AND(self, obj, mode):
        ''' Logical AND with accumulator '''
        obj.reg_a = obj.reg_a & eval("self."+mode+"(obj)")
        self.check('zero', obj.reg_a)
        self.check('neg', obj.reg_a)

    def asl(self, obj, mode):
        ''' Arithmetic shift left '''
        obj.reg_a = eval("self."+mode+"(obj)") << 1
        self.check('zero', obj.reg_a)
        self.check('neg', obj.reg_a)

    def beq(self, obj, mode):
        ''' Branch on equal '''
        if obj.flag_z:
            obj.program_counter += eval("self."+mode+"(obj)")

    def bne(self, obj, mode):
        ''' Branch on negative '''
        if obj.flag_n:
            obj.program_counter += eval("self."+mode+"(obj)")

    def brk(self, obj, mode):
        ''' Break - end program '''
        obj.flag_b = True

    def clc(self, obj, mode):
        ''' Clear carry flag '''
        obj.flag_c = False

    def cmp(self, obj, mode):
        ''' Compare memory and accumulator '''
        addr = eval("self."+mode+"(obj)")
        obj.flag_c = obj.reg_a >= addr
        obj.flag_z = bool(not (obj.reg_a - addr))
        obj.flag_n = bool(int(format(obj.reg_a, '#010b')[2]))

    def inx(self, obj, mode):
        ''' Increment register X '''
        obj.reg_x += 0x01
        self.check('zero', obj.reg_x)
        self.check('neg', obj.reg_x)

    def jsr(self, obj, mode):
        ''' Jump to subroutine '''
        obj.stack_pointer -= 0x01
        obj.write_word(obj.stack_pointer+0x100, obj.program_counter+0x01)
        obj.stack_pointer -= 0x01
        obj.program_counter = obj.fetch_word()

    def lda(self, obj, mode):
        ''' Load register A '''
        obj.reg_a = eval("self."+mode+"(obj)")
        self.check('zero', obj.reg_a)
        self.check('neg', obj.reg_a)

    def nop(self, obj, mode):
        ''' No operations '''
        obj.cycles += 1

    def ora(self, obj, mode):
        ''' Logical inclusive OR '''
        obj.reg_a = obj.reg_a | eval("self."+mode+"(obj)")
        self.check('zero', obj.reg_a)
        self.check('neg', obj.reg_a)

    def rol(self, obj, mode):
        ''' Rotate bits to the left '''
        addr = eval("self."+mode+"(obj)")
        bit = int(format(addr, '#010b')[2])
        obj.reg_a = obj.reg_a << 1
        obj.reg_a += bit
        self.check('zero', obj.reg_a)
        self.check('neg', obj.reg_a)

    def rts(self, obj, mode):
        ''' Return from subroutine '''
        obj.stack_pointer += 0x01
        obj.program_counter = obj.read_word(obj.stack_pointer+0x100)+0x01
        obj.stack_pointer += 0x01

    def sec(self, obj, mode):
        ''' Set carry flag '''
        obj.flag_c = True

    def sta(self, obj, mode):
        ''' Store register A '''
        obj.write_byte(eval("self."+mode+"(obj)"), obj.reg_a)

    def tax(self, obj, mode):
        ''' Transfer A to X '''
        obj.reg_x = obj.reg_a
        self.check('zero', obj.reg_x)
        self.check('neg', obj.reg_x)

    ''' Illegal instructions '''

    def rra(self, obj, mode):
        ''' Rotate right + add with carry '''
        addr = eval("self."+mode+"(obj)")
        bit = int(format(addr, '#010b')[2])
        obj.reg_a += addr << 1
        obj.reg_a += bit
        self.check('carry', obj.reg_a)
        self.check('zero', obj.reg_a)
        self.check('neg', obj.reg_a)

    def slo(self, obj, mode):
        ''' Arithmetic shift left + bitwise OR '''
        addr = eval("self."+mode+"(obj)")
        obj.reg_a = obj.reg_a | (addr << 1)
