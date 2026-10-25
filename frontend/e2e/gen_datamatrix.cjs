// Render a DataMatrix PGM for the fake camera feed: the per-pack GS1 code on
// medicine packs, which the scanner must ignore.
// Usage: node e2e/gen_datamatrix.cjs <text> <out.pgm>
const fs = require('fs')
const { DataMatrixWriter, BarcodeFormat } = require('@zxing/library')

const [text, out] = process.argv.slice(2)
const matrix = new DataMatrixWriter().encode(text, BarcodeFormat.DATA_MATRIX, 0, 0)

const W = 640
const H = 480
const size = Math.floor(320 / Math.max(matrix.getWidth(), matrix.getHeight()))
const x0 = Math.floor((W - matrix.getWidth() * size) / 2)
const y0 = Math.floor((H - matrix.getHeight() * size) / 2)

const pixels = Buffer.alloc(W * H, 255)
for (let y = 0; y < matrix.getHeight(); y++) {
  for (let x = 0; x < matrix.getWidth(); x++) {
    if (!matrix.get(x, y)) continue
    for (let dy = 0; dy < size; dy++) {
      pixels.fill(0, (y0 + y * size + dy) * W + x0 + x * size, (y0 + y * size + dy) * W + x0 + (x + 1) * size)
    }
  }
}
fs.writeFileSync(out, Buffer.concat([Buffer.from(`P5 ${W} ${H} 255\n`), pixels]))
