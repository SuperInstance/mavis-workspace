#!/usr/bin/env python3
"""Decode Asciipocalypse's own 256x256 PNGs to raw RGB for the C# probe.
No dependencies: stdlib zlib + struct only. Unfiltered -> all five filter types."""
import struct, zlib, os, sys
SRC = sys.argv[1] if len(sys.argv) > 1 else "/tmp/axr/ASCII_FPS/Content/textures"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/tmp/tex"
os.makedirs(OUT, exist_ok=True)
def decode(path):
    d = open(path, 'rb').read()
    assert d[:8] == b'\x89PNG\r\n\x1a\n', "not a png"
    p, idat = 8, b''
    while p + 8 <= len(d):
        ln = struct.unpack('>I', d[p:p+4])[0]; t = d[p+4:p+8]; body = d[p+8:p+8+ln]
        if t == b'IHDR': w, h, bd, ct = struct.unpack('>II', body[:8]) + (body[8], body[9])
        elif t == b'IDAT': idat += body
        elif t == b'IEND': break
        p += 12 + ln                       # 4 len + 4 type + body + 4 crc
    assert bd == 8, f"bit depth {bd} unsupported"
    ch = {0: 1, 2: 3, 4: 2, 6: 4}[ct]
    raw = zlib.decompress(idat); stride = w * ch
    out = bytearray(); prev = bytearray(stride); i = 0
    for _ in range(h):
        f = raw[i]; i += 1; line = bytearray(raw[i:i+stride]); i += stride
        for x in range(stride):
            a = line[x-ch] if x >= ch else 0; b = prev[x]; c = prev[x-ch] if x >= ch else 0; v = line[x]
            if   f == 1: v += a
            elif f == 2: v += b
            elif f == 3: v += (a + b) >> 1
            elif f == 4:
                pp = a + b - c; pa, pb, pc = abs(pp-a), abs(pp-b), abs(pp-c)
                v += a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
            line[x] = v & 0xff
        out += line; prev = line
    return w, h, ch, bytes(out)
names = []
for f in sorted(os.listdir(SRC)):
    if not f.endswith('.png'): continue
    w, h, ch, px = decode(os.path.join(SRC, f)); n = f[:-4]; names.append(n)
    with open(f"{OUT}/{n}.raw", 'w') as o:
        for y in range(h):
            o.write(','.join(f"{px[(y*w+x)*ch+k]/255:.4f}" for x in range(w) for k in range(3)) + "\n")
open(f"{OUT}/../texnames.txt", 'w').write("\n".join(names))
print(f"  decoded {len(names)} real textures -> {OUT}")
