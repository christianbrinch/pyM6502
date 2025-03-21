rom = bytearray([0x00] * 65536)

# Example
#rom[0x7ffc] = 0x00
#rom[0x7ffd] = 0x80
#for idx, i in enumerate([0xad, 0x00, 0x08, 0x8D, 0x00, 0xe0, 0xad, 0x01,
#                         0x08, 0x8d, 0x28, 0xe0, 0xad, 0x02, 0x08, 0x8d,
#                         0x50, 0xe0, 0xad, 0x03, 0x08, 0x8d, 0x78, 0xe0,
#                         0xad, 0x04, 0x08, 0x8d, 0xa0, 0xe0, 0xad, 0x05,
#                         0x08, 0x8d, 0xc8, 0xe0, 0xad, 0x06, 0x08, 0x8d,
#                         0xf0, 0xe0, 0xad, 0x07, 0x08, 0x8d, 0x18, 0xe0]):
#    rom[0x0000+idx]=i

for idx, i in enumerate([0xA2, 0x00, 0xA0, 0x00, 0xA9, 0xE0, 0x8D, 0x21,
                         0x00, 0xBD, 0x00, 0x08, 0x91, 0x00, 0xE8, 0xE0,
                         0x08, 0xF0, 0x0D, 0x98, 0x18, 0x69, 0x28, 0xA8,
                         0x90, 0xEF, 0xEE, 0x21, 0x00, 0x4C, 0x09, 0x00,
                         0x60, 0x00]):
    rom[0x0000+idx]=i

# Character set at 0x0800 (page 8)

# A
for idx, i in enumerate([0x00, 0x10, 0x28, 0x44, 0x44, 0x7c, 0x64, 0x64]):
    rom[0x0800+idx]=i

# B
for idx, i in enumerate([0x00, 0x78, 0x44, 0x44, 0x78, 0x64, 0x64, 0x78]):
    rom[0x0808+idx]=i

# C
for idx, i in enumerate([0x00, 0x38, 0x44, 0x40, 0x60, 0x60, 0x64, 0x38]):
    rom[0x0810+idx]=i





with open("rom.bin", "wb") as out_file:
  out_file.write(rom)
