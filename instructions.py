"""MOS-6502 instruction set"""

__author__ = "Christian Brinch"
__copyright__ = "Copyright 2023"
__credits__ = ["Christian Brinch"]
__license__ = "AFL 3.0"
__version__ = "1.0"
__maintainer__ = "Christian Brinch"
__email__ = "brinch.c@gmail.com"


class Set:
    def __init__(self):
        self.addressing = {
            "acc": self.acc,
            "imm": self.imm,
            "ind": self.ind,
            "zp": self.zp,
            "zpx": self.zpx,
            "abs": self.abs,
            "abx": self.abx,
            "aby": self.aby,
            "idx": self.idx,
            "idy": self.idy,
        }

    """Addressing modes"""

    def acc(self, obj):
        return None, obj.reg_a

    def imm(self, obj):
        addr = obj.program_counter
        return addr, obj.fetch_byte()

    def ind(self, obj):
        addr = obj.read_word(obj.fetch_word())
        return addr, None

    def zp(self, obj):
        addr = obj.fetch_byte()
        return addr, obj.read_byte(addr)

    def zpx(self, obj):
        addr = obj.fetch_byte() + obj.reg_x
        return addr, obj.read_byte(addr)

    def abs(self, obj):
        addr = obj.fetch_word()
        return addr, obj.read_byte(addr)

    def abx(self, obj):
        addr = obj.fetch_word() + obj.reg_x
        return addr, obj.read_byte(addr)

    def aby(self, obj):
        addr = obj.fetch_word() + obj.reg_y
        return addr, obj.read_byte(addr)

    def idx(self, obj):
        addr = obj.read_byte(obj.fetch_byte() + obj.reg_x)
        return addr, obj.read_byte(addr)

    def idy(self, obj):
        addr = obj.read_word(obj.fetch_byte()) + obj.reg_y
        return addr, obj.read_byte(addr)

    """
        Instructions
        Split into sections
    """

    """ Section 1: Load and store """

    def lda(self, obj, mode):
        """Load register A"""
        _, value = self.addressing[mode](obj)
        p = obj.reg_p  # operate on a local variable (fast)
        p = (p & ~0x82) | ((not value) * 0x02) | (value & 0x80)  # Toggle Z and N
        obj.reg_p = p  # write to register
        obj.reg_a = value

    def ldx(self, obj, mode):
        """Load register X"""
        _, value = self.addressing[mode](obj)
        p = obj.reg_p
        p = (p & ~0x82) | ((not value) * 0x02) | (value & 0x80)  # Toggle Z and N
        obj.reg_p = p
        obj.reg_x = value

    def ldy(self, obj, mode):
        """Load register Y"""
        _, value = self.addressing[mode](obj)
        p = obj.reg_p
        p = (p & ~0x82) | ((not value) * 0x02) | (value & 0x80)  # Toggle Z and N
        obj.reg_p = p
        obj.reg_y = value

    def sta(self, obj, mode):
        """Store register A"""
        addr, _ = self.addressing[mode](obj)
        obj.write_byte(addr, obj.reg_a)

    def stx(self, obj, mode):
        """Store register X"""
        addr, _ = self.addressing[mode](obj)
        obj.write_byte(addr, obj.reg_x)

    def sty(self, obj, mode):
        """Store register Y"""
        addr, _ = self.addressing[mode](obj)
        obj.write_byte(addr, obj.reg_y)

    """ Section 2: Transfer """

    def tax(self, obj, mode):
        """Transfer A to X"""
        value = obj.reg_a
        p = obj.reg_p
        p = (p & ~0x82) | ((not value) * 0x02) | (value & 0x80)  # Toggle Z and N
        obj.reg_p = p
        obj.reg_x = value

    def tay(self, obj, mode):
        """Transfer A to Y"""
        value = obj.reg_a
        p = obj.reg_p
        p = (p & ~0x82) | ((not value) * 0x02) | (value & 0x80)  # Toggle Z and N
        obj.reg_p = p
        obj.reg_y = value

    def tsx(self, obj, mode):
        """Transfer stack pointer to X"""
        value = obj.stack_pointer
        p = obj.reg_p
        p = (p & ~0x82) | ((not value) * 0x02) | (value & 0x80)  # Toggle Z and N
        obj.reg_p = p
        obj.reg_x = value

    def txa(self, obj, mode):
        """Transfer X to A"""
        value = obj.reg_x
        p = obj.reg_p
        p = (p & ~0x82) | ((not value) * 0x02) | (value & 0x80)  # Toggle Z and N
        obj.reg_p = p
        obj.reg_a = value

    def txs(self, obj, mode):
        """Transfer stack pointer to X"""
        obj.stack_pointer = obj.reg_x

    def tya(self, obj, mode):
        """Transfer Y to A"""
        value = obj.reg_y
        p = obj.reg_p
        p = (p & ~0x82) | ((not value) * 0x02) | (value & 0x80)  # Toggle Z and N
        obj.reg_p = p
        obj.reg_a = value

    """ Section 3: Stack instructions"""

    def pha(self, obj, mode):
        """Push accumulator onto stack"""
        obj.write_byte(obj.stack_pointer + 0x100, obj.reg_a)
        obj.stack_pointer -= 0x01

    def pla(self, obj, mode):
        """Pull accumulator onto stack"""
        obj.stack_pointer += 0x01
        obj.reg_a = obj.read_byte(obj.stack_pointer + 0x100)

    """ Section 4: Shift """

    def asl(self, obj, mode):
        """Arithmetic shift left"""
        addr, value = self.addressing[mode](obj)
        p = obj.reg_p
        p = (p & ~0x01) | (value & 0x80) >> 7  # toggle C
        value = (value << 1) & 0xFF
        p = (p & ~0x82) | ((not value) * 0x02) | (value & 0x80)  # Toggle Z and N
        obj.reg_p = p
        if mode == "acc":
            obj.reg_a = value
        else:
            obj.write_byte(addr, value)

    def lsr(self, obj, mode):
        """Logical shift right"""
        addr, value = self.addressing[mode](obj)
        p = obj.reg_p
        p = (p & ~0x01) | (value & 0x80) >> 7  # toggle C
        value = value >> 1
        p = (p & ~0x82) | ((not value) * 0x02) | (value & 0x80)  # Toggle Z and N
        obj.reg_p = p
        if mode == "acc":
            obj.reg_a = value
        else:
            obj.write_byte(addr, value)

    def rol(self, obj, mode):
        """Rotate bits to the left"""
        addr, value = self.addressing[mode](obj)
        p = obj.reg_p
        p = (p & ~0x01) | (value & 0x80) >> 7  # toggle C
        value = ((value << 1) & 0xFF) + (p & 0x00)
        p = (p & ~0x82) | ((not value) * 0x02) | (value & 0x80)  # Toggle Z and N
        obj.reg_p = p
        if mode == "acc":
            obj.reg_a = value
        else:
            obj.write_byte(addr, value)

    def ror(self, obj, mode):
        """Rotate bits to the right"""
        addr, value = self.addressing[mode](obj)
        p = obj.reg_p
        carry = p & 0x01  # Hold carry
        p = (p & ~0x01) | (value & 0x80) >> 7  # toggle C
        value = (value >> 1) | carry * 0x80
        p = (p & ~0x82) | ((not value) * 0x02) | (value & 0x80)  # Toggle Z and N
        obj.reg_p = p
        if mode == "acc":
            obj.reg_a = value
        else:
            obj.write_byte(addr, value)

    """ Section 5: Logical instructions"""

    def AND(self, obj, mode):
        """Logical AND with accumulator &"""
        _, value = self.addressing[mode](obj)
        a = obj.reg_a & value
        p = obj.reg_p
        p = (p & ~0x82) | ((a == 0) << 1) | (a & 0x80)
        obj.reg_p = p
        obj.reg_a = a

    def bit(self, obj, mode):
        """Test bit in memory with accumulator"""
        _, value = self.addressing[mode](obj)
        a = obj.reg_a  # use local variables for speed
        p = obj.reg_p
        p = (
            p & ~0xC2  # clear N (0x80), V (0x40), Z (0x02)
            | (value & 0xC0)  # copy bits 7 and 6 into N and V
            | (((a & value) == 0) << 1)  # set Z
        )
        obj.reg_p = p

    def eor(self, obj, mode):
        """Binary Exclusive OR with accumulator ^"""
        _, value = self.addressing[mode](obj)
        a = obj.reg_a ^ value
        p = obj.reg_p
        p = (p & ~0x82) | ((a == 0) << 1) | (a & 0x80)
        obj.reg_p = p
        obj.reg_a = a

    def ora(self, obj, mode):
        """Binary OR with accumulator |"""
        _, value = self.addressing[mode](obj)
        a = obj.reg_a | value
        p = obj.reg_p
        p = (p & ~0x82) | ((a == 0) << 1) | (a & 0x80)
        obj.reg_p = p
        obj.reg_a = a

    """ Section 6: Arithmetic instructions """

    def adc(self, obj, mode):
        """Add with carry"""
        _, value = self.addressing[mode](obj)

        a = obj.reg_a
        c = obj.reg_p & 0x01

        result = a + value + c
        r = result & 0xFF

        p = obj.reg_p
        p = (
            p & ~0xC3  # clear N, V, Z, C
            | (result > 0xFF)  # C
            | ((r == 0) << 1)  # Z
            | (r & 0x80)  # N
            | (((~(a ^ value) & (a ^ r)) & 0x80) >> 1)  # V
        )

        obj.reg_a = r
        obj.reg_p = p

    def cmp(self, obj, mode):
        """Compare memory and accumulator"""
        _, value = self.addressing[mode](obj)
        a = obj.reg_a
        diff = (a - value) & 0xFF
        p = obj.reg_p
        p = (
            p & ~0x83  # clear C (0x01), Z (0x02), N (0x80)
            | (a >= value)  # set C
            | ((diff == 0) << 1)  # set Z
            | (diff & 0x80)  # set N
        )
        obj.reg_p = p

    def cpx(self, obj, mode):
        """Compare Register X"""
        _, value = self.addressing[mode](obj)
        x = obj.reg_x
        diff = (x - value) & 0xFF
        p = obj.reg_p
        p = (
            p & ~0x83  # clear C (0x01), Z (0x02), N (0x80)
            | (x >= value)  # set C
            | ((diff == 0) << 1)  # set Z
            | (diff & 0x80)  # set N
        )
        obj.reg_p = p

    def cpy(self, obj, mode):
        """Compare Register Y"""
        _, value = self.addressing[mode](obj)
        y = obj.reg_y
        diff = (y - value) & 0xFF
        p = obj.reg_p
        p = (
            p & ~0x83  # clear C (0x01), Z (0x02), N (0x80)
            | (y >= value)  # set C
            | ((diff == 0) << 1)  # set Z
            | (diff & 0x80)  # set N
        )
        obj.reg_p = p

    def sbc(self, obj, mode):
        """Subtract with borrow"""
        _, value = self.addressing[mode](obj)

        a = obj.reg_a
        c = obj.reg_p & 0x01

        result = a - value - (1 - c)
        r = result & 0xFF

        p = obj.reg_p
        p = (
            p & ~0xC3  # clear N, V, Z, C
            | (result >= 0)  # C (no borrow)
            | ((r == 0) << 1)  # Z
            | (r & 0x80)  # N
            | (((a ^ r) & (a ^ value) & 0x80) >> 1)  # V
        )

        obj.reg_a = r
        obj.reg_p = p

    """ Section 7: Incrementing instructions """

    def dec(self, obj, mode):
        """Decrement memory by 1"""
        addr, value = self.addressing[mode](obj)
        value -= 0x01
        obj.write_byte(addr, value & 0xFF)
        p = obj.reg_p
        p = (p & ~0x82) | ((not value) * 0x02) | (value & 0x80)  # Toggle Z and N
        obj.reg_p = p

    def dex(self, obj, mode):
        """Decrement register X"""
        value = (obj.reg_x - 0x01) & 0xFF
        p = obj.reg_p
        p = (p & ~0x82) | ((not value) * 0x02) | (value & 0x80)  # Toggle Z and N
        obj.reg_p = p
        obj.reg_x = value

    def dey(self, obj, mode):
        """Decrement register Y"""
        value = (obj.reg_y - 0x01) & 0xFF
        p = obj.reg_p
        p = (p & ~0x82) | ((not value) * 0x02) | (value & 0x80)  # Toggle Z and N
        obj.reg_p = p
        obj.reg_y = value

    def inc(self, obj, mode):
        """Increment memory by 1"""
        addr, value = self.addressing[mode](obj)
        value += 0x01
        obj.write_byte(addr, value & 0xFF)
        p = obj.reg_p
        p = (p & ~0x82) | ((not value) * 0x02) | (value & 0x80)  # Toggle Z and N
        obj.reg_p = p

    def inx(self, obj, mode):
        """Increment register X"""
        value = (obj.reg_x + 0x01) & 0xFF
        p = obj.reg_p
        p = (p & ~0x82) | ((not value) * 0x02) | (value & 0x80)  # Toggle Z and N
        obj.reg_p = p
        obj.reg_x = value

    def iny(self, obj, mode):
        """Increment register Y"""
        value = (obj.reg_y + 0x01) & 0xFF
        p = obj.reg_p
        p = (p & ~0x82) | ((not value) * 0x02) | (value & 0x80)  # Toggle Z and N
        obj.reg_p = p
        obj.reg_y = value

    """ Section 8: Control """

    def brk(self, obj, mode):
        """Break - end program"""
        obj.reg_p &= ~0x16  # Clear B flag

    def jmp(self, obj, mode):
        """Jump to address"""
        obj.program_counter, _ = self.addressing[mode](obj)

    def jsr(self, obj, mode):
        """Jump to subroutine"""
        obj.stack_pointer -= 0x01
        obj.write_word(obj.stack_pointer + 0x100, obj.program_counter + 0x01)
        obj.stack_pointer -= 0x01
        obj.program_counter = obj.fetch_word()

    def rti(self, obj, mode):
        """Return from interrupt"""
        obj.stack_pointer += 0x01
        obj.reg_p = obj.read_byte(obj.stack_pointer + 0x100)
        obj.stack_pointer += 0x01
        obj.program_counter = obj.read_word(obj.stack_pointer + 0x100)
        obj.stack_pointer += 0x01

    def rts(self, obj, mode):
        """Return from subroutine"""
        obj.stack_pointer += 0x01
        obj.program_counter = obj.read_word(obj.stack_pointer + 0x100) + 0x01
        obj.stack_pointer += 0x01

    """ Section 9: Branching """

    def bcc(self, obj, mode):
        """Branch on clear carry"""
        addr = obj.fetch_byte()
        addr = addr - 0x100 if addr & 0x80 else addr
        if not (obj.reg_p & 0x01):
            obj.program_counter += addr

    def bcs(self, obj, mode):
        """Branch on carry set"""
        addr = obj.fetch_byte()
        addr = addr - 0x100 if addr & 0x80 else addr
        if obj.reg_p & 0x01:
            obj.program_counter += addr

    def beq(self, obj, mode):
        """Branch on equal (zero)"""
        addr = obj.fetch_byte()
        addr = addr - 0x100 if addr & 0x80 else addr
        if obj.reg_p & 0x02:
            obj.program_counter += addr

    def bmi(self, obj, mode):
        """Branch on negative"""
        addr = obj.fetch_byte()
        addr = addr - 0x100 if addr & 0x80 else addr
        if obj.reg_p & 0x80:
            obj.program_counter += addr

    def bne(self, obj, mode):
        """Branch on result not zero (not equal)"""
        addr = obj.fetch_byte()
        addr = addr - 0x100 if addr & 0x80 else addr
        if not (obj.reg_p & 0x02):
            obj.program_counter += addr

    def bpl(self, obj, mode):
        """Branch on not negative"""
        addr = obj.fetch_byte()
        addr = addr - 0x100 if addr & 0x80 else addr
        if not (obj.reg_p & 0x80):
            obj.program_counter += addr

    def bvc(self, obj, mode):
        """Branch on overflow clear"""
        addr = obj.fetch_byte()
        addr = addr - 0x100 if addr & 0x80 else addr
        if not (obj.reg_p & 0x40):
            obj.program_counter += addr

    def bvs(self, obj, mode):
        """Branch on overflow set"""
        addr = obj.fetch_byte()
        addr = addr - 0x100 if addr & 0x80 else addr
        if obj.reg_p & 0x40:
            obj.program_counter += addr

    """ Section 10: Flags & NOP"""

    def clc(self, obj, mode):
        """Clear carry flag"""
        obj.reg_p &= ~0x01  # Clear C flag

    def cld(self, obj, mode):
        """Clear decimal flag"""
        obj.reg_p &= ~0x08  # Clear D flag

    def cli(self, obj, mode):
        """Clear interupt disable"""
        obj.reg_p &= ~0x04  # Clear I flag

    def clv(self, obj, mode):
        """Clear overflow flag"""
        obj.reg_p &= ~0x40  # Clear V flag

    def sec(self, obj, mode):
        """Set carry flag"""
        obj.reg_p |= 0x01  # Set C flag

    def sed(self, obj, mode):
        """Set decimal mode"""
        obj.reg_p |= 0x08  # Set D flag

    def sei(self, obj, mode):
        """Set interupt disable"""
        obj.reg_p |= 0x04  # Set I flag

    def nop(self, obj, mode):
        """No operations"""

    """ Section 11: Illegal instructions """

    def slo(self, obj, mode):
        """No operations"""

    def php(self, obj, mode):
        """No operations"""

    def rla(self, obj, mode):
        """No operations"""

    def plp(self, obj, mode):
        """No operations"""

    def isb(self, obj, mode):
        """No operations"""

    def sre(self, obj, mode):
        """No operations"""

    def rra(self, obj, mode):
        """No operations"""

    def sax(self, obj, mode):
        """No operations"""

    def lax(self, obj, mode):
        """No operations"""

    def dcp(self, obj, mode):
        """No operations"""

    def cdp(self, obj, mode):
        """No operations"""
