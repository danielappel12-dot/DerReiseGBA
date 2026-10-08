#!/usr/bin/env python3
"""gbafix.py - minimal GBA ROM header fixer.

Computes the header complement checksum (byte 0xBD), pads the ROM to a
multiple of 4 bytes and sets the fixed 0x96 byte.

It deliberately does NOT embed the Nintendo boot logo (0x04-0x9F).  Real
hardware (and the real BIOS) requires that logo; the devkitPro `gbafix` tool
inserts it.  The Makefile prefers devkitPro's `gbafix` when it is on PATH and
only falls back to this script (which is enough for every emulator and for
flash carts that patch the header themselves).
"""
import sys


def main(path):
    with open(path, "rb") as f:
        rom = bytearray(f.read())
    while len(rom) % 4:
        rom.append(0xFF)
    rom[0xB2] = 0x96
    rom[0xB3] = 0x00
    rom[0xB4] = 0x00
    chk = 0
    for b in rom[0xA0:0xBD]:
        chk = (chk - b) & 0xFF
    chk = (chk - 0x19) & 0xFF
    rom[0xBD] = chk
    with open(path, "wb") as f:
        f.write(rom)
    print("gbafix.py: %s fixed (%d bytes, checksum 0x%02X)" % (path, len(rom), chk))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: gbafix.py ROM.gba")
    main(sys.argv[1])
