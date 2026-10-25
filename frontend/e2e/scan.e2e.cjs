// End-to-end check of the scan flow with a fake camera showing a real EAN-13.
// Chromium on Linux has no native BarcodeDetector, so this exercises the same
// ZXing fallback that iOS Safari uses. The API is mocked; no backend needed.
//
// STATUS: work in progress, not yet run to completion (see PR #1 description).
//
// Requires Playwright with Chromium and ffmpeg:
//   python3 e2e/gen_barcode.py 482000000001 /tmp/barcode.pgm        # prints 4820000000017
//   ffmpeg -loop 1 -i /tmp/barcode.pgm -t 2 -r 15 -vf format=yuv420p /tmp/barcode.y4m
//   node e2e/scan.e2e.cjs 4820000000017 /tmp/barcode.y4m /tmp <non-localhost LAN IP>
const { chromium } = require('playwright')
const { spawn } = require('child_process')
const path = require('path')

const [BARCODE, VIDEO, OUT, LAN_IP] = process.argv.slice(2)
const FRONTEND = path.resolve(__dirname, '..')

const now = new Date().toISOString()
const med = (id, name, quantity, barcode) => ({
  id, household_id: 1, name, name_norm: name.toUpperCase(), quantity, barcode,
  description: null, notes: null, drlz_link: null, drlz_instruction_link: null,
  tabletki_link: null, tags: [], created_by: 1, created_at: now, updated_at: now,
})
const meds = [med(5, 'Ibuprofen', 5, BARCODE), med(7, 'Aspirin', 2, null)]
const calls = []
let lookupDelayMs = 0

function check(condition, message) {
  if (!condition) throw new Error('ASSERTION FAILED: ' + message)
  console.log('  ✓ ' + message)
}

async function handleApi(route) {
  const request = route.request()
  const url = new URL(request.url())
  const p = url.pathname.replace(/^.*\/api\/v1/, '')
  const method = request.method()
  calls.push(`${method} ${p}${url.search}`)
  const json = (body, status = 200) => route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) })

  if (p === '/auth/me') return json({ id: 1, email: 'tester@example.com', created_at: now })
  if (p === '/households/' || p === '/households') return json([{ id: 1, name: 'Home', role: 'owner', created_at: now }])
  if (p === '/households/1/medications' && method === 'GET') return json({ medications: meds, total: meds.length, next_cursor: null, has_more: false })
  if (p === '/households/1/medications/lookup') {
    await new Promise((resolve) => setTimeout(resolve, lookupDelayMs))
    const code = url.searchParams.get('barcode').trim()
    const found = meds.find((m) => m.barcode === code) || null
    return json({ found: !!found, barcode: code, medication: found })
  }
  let m = p.match(/^\/households\/1\/medications\/(\d+)\/(increment|decrement)$/)
  if (m && method === 'POST') {
    const target = meds.find((x) => x.id === Number(m[1]))
    const amount = Number(url.searchParams.get('amount') || 1)
    target.quantity += m[2] === 'increment' ? amount : -amount
    return json(target)
  }
  m = p.match(/^\/households\/1\/medications\/(\d+)$/)
  if (m && method === 'PATCH') {
    const target = meds.find((x) => x.id === Number(m[1]))
    Object.assign(target, request.postDataJSON())
    return json(target)
  }
  return json({ detail: 'unmocked ' + p }, 404)
}

async function openScanDialog(page, origin) {
  await page.goto(origin + '/')
  await page.getByText('Home', { exact: true }).first().click()
  await page.getByRole('button', { name: 'Scan', exact: true }).click()
}

// Fast-forward CSS transitions first: the HTTPS hint is there as soon as the
// dialog opens, so without this the capture catches MUI's fade-in half done
function screenshot(page, name) {
  return page.screenshot({ path: `${OUT}/${name}.png`, animations: 'disabled' })
}

async function cameraTracks(page) {
  return page.evaluate(() => window.__tracks.map((t) => t.readyState))
}

;(async () => {
  // Run Vite's own entry point rather than `npx vite`: npx starts Vite as a
  // grandchild, so server.kill() would only stop npx and leave Vite running,
  // keeping port 3000 busy and this script's stdout pipe open (it never exits)
  const viteBin = path.join(FRONTEND, 'node_modules', 'vite', 'bin', 'vite.js')
  const server = spawn(process.execPath, [viteBin, '--port', '3000', '--strictPort', '--host', '0.0.0.0'], {
    cwd: FRONTEND, env: { ...process.env, VITE_API_URL: '' }, stdio: ['ignore', 'pipe', 'inherit'],
  })
  const serverExited = new Promise((resolve) => server.once('exit', resolve))
  await new Promise((resolve, reject) => {
    // Vite colors its banner, so strip ANSI codes before looking for the URL
    server.stdout.on('data', (d) => d.toString().replace(/\x1b\[[0-9;]*m/g, '').includes('localhost:3000') && resolve())
    server.on('exit', (code) => reject(new Error('vite exited ' + code)))
  })

  let browser
  try {
    browser = await chromium.launch({
      args: [
        '--use-fake-ui-for-media-stream',
        '--use-fake-device-for-media-stream',
        `--use-file-for-fake-video-capture=${VIDEO}`,
      ],
    })
    const context = await browser.newContext({
      viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true,
      serviceWorkers: 'block', permissions: ['camera'],
    })
    await context.addInitScript(() => {
      localStorage.setItem('access_token', 'test-token')
      localStorage.setItem('refresh_token', 'test-refresh')
      window.__tracks = []
      if (navigator.mediaDevices?.getUserMedia) {
        const original = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices)
        navigator.mediaDevices.getUserMedia = async (constraints) => {
          const stream = await original(constraints)
          window.__tracks.push(...stream.getTracks())
          return stream
        }
      }
    })
    await context.route('**/api/v1/**', handleApi)
    const page = await context.newPage()
    page.on('pageerror', (e) => console.log('  [pageerror]', e.message))

    console.log('Scenario 1: scan a known package → add / subtract')
    await openScanDialog(page, 'http://localhost:3000')
    await page.getByText('This medication is already in your inventory.').waitFor({ timeout: 20000 })
    check(!(await page.evaluate(() => 'BarcodeDetector' in window)), 'no native BarcodeDetector, so the ZXing fallback did the decoding')
    check(calls.includes(`GET /households/1/medications/lookup?barcode=${BARCODE}`), `camera decoded ${BARCODE} and looked it up`)
    const dialog = page.getByRole('dialog')
    check(await dialog.getByText('Ibuprofen').isVisible(), 'dialog shows the matched medication')
    let tracks = await cameraTracks(page)
    check(tracks.length > 0 && tracks.every((s) => s === 'ended'), `camera released after the scan (tracks: ${tracks.join(',')})`)
    await screenshot(page, '1-found')

    await dialog.getByRole('button', { name: 'Add 1' }).click()
    await dialog.getByText('6 items').waitFor()
    check(calls.includes('POST /households/1/medications/5/increment?amount=1'), 'Add 1 increments the quantity (5 → 6)')
    await dialog.getByRole('button', { name: 'Subtract 1' }).click()
    await dialog.getByText('5 items').waitFor()
    check(calls.includes('POST /households/1/medications/5/decrement?amount=1'), 'Subtract 1 decrements the quantity (6 → 5)')
    await dialog.getByRole('button', { name: 'Close', exact: true }).click()

    console.log('Scenario 2: scan an unknown package → link it to an existing medication')
    meds[0].barcode = null
    // Answer the lookup slowly, like a real network: until it arrives the
    // dialog must not offer add/subtract from the previous scan of this code
    lookupDelayMs = 1500
    await page.getByRole('button', { name: 'Scan', exact: true }).click()
    await dialog.getByText(BARCODE, { exact: true }).waitFor({ timeout: 20000 })
    check(await dialog.getByText('Looking up barcode…').isVisible() && !(await dialog.getByText('Ibuprofen').isVisible()),
      'rescanning looks the barcode up again instead of showing the previous result (Ibuprofen)')
    await page.getByText('No medication with this barcode was found').waitFor({ timeout: 20000 })
    lookupDelayMs = 0
    check(await dialog.getByRole('button', { name: 'Create new medication' }).isVisible(), 'offers to create a new medication')
    await screenshot(page, '2-not-found')
    await dialog.getByLabel('Existing medication').click()
    await page.getByRole('option', { name: 'Aspirin' }).click()
    await dialog.getByRole('button', { name: 'Link barcode' }).click()
    await dialog.getByText('This medication is already in your inventory.').waitFor()
    check(calls.includes('PATCH /households/1/medications/7'), 'Link barcode PATCHes the chosen medication')
    check(meds[1].barcode === BARCODE, 'Aspirin now carries the scanned barcode')
    check(await dialog.getByRole('heading', { name: 'Aspirin' }).isVisible(), 'dialog switches to add/subtract for Aspirin')
    tracks = await cameraTracks(page)
    check(tracks.every((s) => s === 'ended'), `no camera track left running (tracks: ${tracks.join(',')})`)
    await screenshot(page, '3-linked')

    console.log('Scenario 3: plain-HTTP origin → explains that the camera needs HTTPS')
    const insecure = await context.newPage()
    await openScanDialog(insecure, `http://${LAN_IP}:3000`)
    check(!(await insecure.evaluate(() => window.isSecureContext)), `http://${LAN_IP} is not a secure context`)
    await insecure.getByText('The camera only works when the app is opened over HTTPS').waitFor()
    check(await insecure.getByLabel('Barcode number').isVisible(), 'manual barcode entry is offered instead')
    await screenshot(insecure, '4-https-hint')

    console.log('\nALL CHECKS PASSED')
  } finally {
    try {
      await browser?.close()
    } finally {
      server.kill()
      await serverExited
    }
  }
})().catch((e) => {
  console.error(e.message)
  console.error('API calls:', calls)
  process.exit(1)
})
