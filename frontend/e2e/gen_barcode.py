"""Render an EAN-13 barcode PGM for the fake camera feed. Usage: gen_barcode.py <12 digits> <out.pgm>"""
import sys

L = ["0001101", "0011001", "0010011", "0111101", "0100011", "0110001", "0101111", "0111011", "0110111", "0001011"]
G = ["0100111", "0110011", "0011011", "0100001", "0011101", "0111001", "0000101", "0010001", "0001001", "0010111"]
R = ["1110010", "1100110", "1101100", "1000010", "1011100", "1001110", "1010000", "1000100", "1001000", "1110100"]
PARITY = ["LLLLLL", "LLGLGG", "LLGGLG", "LLGGGL", "LGLLGG", "LGGLLG", "LGGGLL", "LGLGLG", "LGLGGL", "LGGLGL"]


def ean13(digits12: str) -> str:
    total = sum(int(d) * (3 if i % 2 else 1) for i, d in enumerate(digits12))
    code = digits12 + str((10 - total % 10) % 10)
    first, left, right = int(code[0]), code[1:7], code[7:]
    bits = "101"
    bits += "".join((L if p == "L" else G)[int(d)] for p, d in zip(PARITY[first], left))
    bits += "01010" + "".join(R[int(d)] for d in right) + "101"
    return code, bits


code, bits = ean13(sys.argv[1])
W, H, module, bar_height = 640, 480, 5, 220
x0 = (W - len(bits) * module) // 2
y0 = (H - bar_height) // 2
row_with_bars = bytes(
    0 if x0 <= x < x0 + len(bits) * module and bits[(x - x0) // module] == "1" else 255
    for x in range(W)
)
blank_row = bytes([255]) * W
with open(sys.argv[2], "wb") as f:
    f.write(b"P5 %d %d 255\n" % (W, H))
    for y in range(H):
        f.write(row_with_bars if y0 <= y < y0 + bar_height else blank_row)
print(code)
