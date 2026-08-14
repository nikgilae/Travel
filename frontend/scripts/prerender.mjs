#!/usr/bin/env node
// Пост-шаг сборки (запускается после `vite build`, см. package.json → "build").
//
// SPA-лендинг рендерится в готовый dist/index.html, чтобы поисковики и AI-боты
// (Яндекс/Google/GPTBot/PerplexityBot/...) видели текст, а не пустой <div id="root">.
// Никакого SSR-сервера и переезда на Next/Remix — это разовый шаг сборки:
//   1) поднимаем собранный dist/ статикой на локальном порту,
//   2) открываем "/" в headless Chromium (эмулируем prefers-reduced-motion: reduce,
//      чтобы анимации лендинга сразу показали финальное состояние — см. LandingPage.jsx),
//   3) забираем innerHTML #root и записываем его обратно в dist/index.html.
//
// Playwright намеренно не используется (в node_modules его нет и ставить не надо).
// Управляем локальным Chromium-бинарём напрямую по Chrome DevTools Protocol —
// поверх сырого WebSocket, написанного на голых node:net + node:crypto,
// потому что в Node 20 нет глобального WebSocket-клиента.
//
// Клиентский React после этого работает как и раньше: main.jsx вызывает
// createRoot(...).render(...), а не hydrateRoot — React просто перерисует
// содержимое #root при маунте, это ожидаемо и безопасно.

import { createServer } from 'node:http'
import { readFile, writeFile, mkdtemp, rm } from 'node:fs/promises'
import path from 'node:path'
import os from 'node:os'
import { fileURLToPath } from 'node:url'
import { spawn } from 'node:child_process'
import { randomBytes, createHash } from 'node:crypto'
import net from 'node:net'
import { EventEmitter } from 'node:events'
import http from 'node:http'
import { readdirSync, existsSync } from 'node:fs'
const __dirname = path.dirname(fileURLToPath(import.meta.url))
const DIST_DIR = path.join(__dirname, '..', 'dist')
const INDEX_HTML = path.join(DIST_DIR, 'index.html')
const ROOT_PLACEHOLDER = '<div id="root"></div>'



function findChromePath() {
  if (process.env.PRERENDER_CHROME_PATH) return process.env.PRERENDER_CHROME_PATH

  const cacheDirs = [
    process.env.PLAYWRIGHT_BROWSERS_PATH,
    path.join(os.homedir(), '.cache', 'ms-playwright'),
  ].filter(Boolean)

  for (const dir of cacheDirs) {
    if (!existsSync(dir)) continue
    const chromiumFolders = readdirSync(dir)
      .filter((name) => name.startsWith('chromium-') && !name.includes('headless'))
      .sort()
      .reverse() // берём самую свежую версию

    for (const folder of chromiumFolders) {
      const candidate = path.join(dir, folder, 'chrome-linux64', 'chrome')
      if (existsSync(candidate)) return candidate
    }
  }

  fail(
    'не найден бинарник Chromium ни в PRERENDER_CHROME_PATH, ни в кеше Playwright — ' +
      'убедитесь, что перед этим шагом выполнен "npx playwright install chromium"'
  )
}

const CHROME_PATH = findChromePath()
const REQUIRED_PHRASE = 'Что ты будешь делать в поездке каждый день?'
const MIN_VISIBLE_CHARS = 500

const NAV_TIMEOUT_MS = 15000 // ждать появления финальной разметки в #root
const CHROME_STARTUP_TIMEOUT_MS = 15000
const WATCHDOG_MS = 60000 // общий предохранитель на весь скрипт

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.mjs': 'application/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.woff2': 'font/woff2',
  '.woff': 'font/woff',
  '.json': 'application/json; charset=utf-8',
  '.ico': 'image/x-icon',
  '.txt': 'text/plain; charset=utf-8',
  '.xml': 'application/xml; charset=utf-8',
}

function fail(message) {
  console.error(`[prerender] ${message}`)
  process.exit(1)
}

function log(message) {
  console.log(`[prerender] ${message}`)
}

// ───────────────────────── статика ─────────────────────────

function startStaticServer(rootDir) {
  return new Promise((resolve, reject) => {
    const server = createServer(async (req, res) => {
      try {
        const urlPath = decodeURIComponent((req.url || '/').split('?')[0])
        const safeSuffix = path.normalize(urlPath).replace(/^(\.\.[/\\])+/, '')
        let filePath = path.join(rootDir, safeSuffix)
        if (!filePath.startsWith(rootDir)) {
          res.writeHead(403)
          res.end()
          return
        }
        if (urlPath.endsWith('/')) filePath = path.join(filePath, 'index.html')

        let data
        try {
          data = await readFile(filePath)
        } catch {
          // SPA-фолбэк: любой путь без расширения отдаём как index.html
          if (!path.extname(filePath)) {
            filePath = path.join(rootDir, 'index.html')
            data = await readFile(filePath)
          } else {
            res.writeHead(404)
            res.end('Not found')
            return
          }
        }
        const ext = path.extname(filePath)
        res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream' })
        res.end(data)
      } catch (err) {
        res.writeHead(500)
        res.end(String(err))
      }
    })
    server.on('error', reject)
    server.listen(0, '127.0.0.1', () => resolve(server))
  })
}

// ───────────────────── сырой WebSocket-клиент ─────────────────────
// Минимальный клиент под нужды CDP: текстовые JSON-фреймы, немаскированные
// фреймы от сервера, маскированные — от клиента (как требует RFC 6455).

function wsConnect(wsUrl) {
  return new Promise((resolve, reject) => {
    const u = new URL(wsUrl)
    const port = u.port || 80
    const socket = net.connect(Number(port), u.hostname)
    const emitter = new EventEmitter()

    let buf = Buffer.alloc(0)
    let handshakeDone = false
    let fragBuf = Buffer.alloc(0)
    const key = randomBytes(16).toString('base64')
    const expectedAccept = createHash('sha1')
      .update(key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11')
      .digest('base64')

    socket.once('connect', () => {
      const req =
        `GET ${u.pathname}${u.search} HTTP/1.1\r\n` +
        `Host: ${u.host}\r\n` +
        `Upgrade: websocket\r\n` +
        `Connection: Upgrade\r\n` +
        `Sec-WebSocket-Key: ${key}\r\n` +
        `Sec-WebSocket-Version: 13\r\n\r\n`
      socket.write(req)
    })

    socket.on('error', (err) => {
      if (!handshakeDone) reject(err)
      emitter.emit('error', err)
    })

    socket.on('close', () => emitter.emit('close'))

    socket.on('data', (chunk) => {
      buf = Buffer.concat([buf, chunk])

      if (!handshakeDone) {
        const headerEnd = buf.indexOf('\r\n\r\n')
        if (headerEnd === -1) return
        const header = buf.slice(0, headerEnd).toString('utf8')
        if (!/^HTTP\/1\.1 101/i.test(header)) {
          reject(new Error('WebSocket handshake failed:\n' + header))
          socket.destroy()
          return
        }
        if (!header.includes(expectedAccept)) {
          reject(new Error('WebSocket handshake: unexpected Sec-WebSocket-Accept'))
          socket.destroy()
          return
        }
        handshakeDone = true
        buf = buf.slice(headerEnd + 4)
        resolve({ send: sendFrame, close: () => socket.end(), on: (...a) => emitter.on(...a) })
      }

      // Разбор фреймов (может прийти несколько за один TCP-чанк).
      while (true) {
        if (buf.length < 2) break
        const b0 = buf[0]
        const b1 = buf[1]
        const fin = (b0 & 0x80) !== 0
        const opcode = b0 & 0x0f
        let len = b1 & 0x7f
        let offset = 2
        if (len === 126) {
          if (buf.length < 4) break
          len = buf.readUInt16BE(2)
          offset = 4
        } else if (len === 127) {
          if (buf.length < 10) break
          len = Number(buf.readBigUInt64BE(2))
          offset = 10
        }
        if (buf.length < offset + len) break
        const payload = buf.slice(offset, offset + len)
        buf = buf.slice(offset + len)

        if (opcode === 0x8) {
          emitter.emit('close')
          socket.end()
          return
        }
        if (opcode === 0x1 || opcode === 0x0) {
          fragBuf = Buffer.concat([fragBuf, payload])
          if (fin) {
            const msg = fragBuf
            fragBuf = Buffer.alloc(0)
            emitter.emit('message', msg.toString('utf8'))
          }
        }
        // ping (0x9) / pong (0xa) — CDP их не использует, игнорируем
      }
    })

    function sendFrame(str) {
      const payloadBuf = Buffer.from(str, 'utf8')
      const maskKey = randomBytes(4)
      const masked = Buffer.alloc(payloadBuf.length)
      for (let i = 0; i < payloadBuf.length; i++) masked[i] = payloadBuf[i] ^ maskKey[i % 4]

      let header
      if (payloadBuf.length < 126) {
        header = Buffer.alloc(2)
        header[0] = 0x81
        header[1] = 0x80 | payloadBuf.length
      } else if (payloadBuf.length < 65536) {
        header = Buffer.alloc(4)
        header[0] = 0x81
        header[1] = 0x80 | 126
        header.writeUInt16BE(payloadBuf.length, 2)
      } else {
        header = Buffer.alloc(10)
        header[0] = 0x81
        header[1] = 0x80 | 127
        header.writeBigUInt64BE(BigInt(payloadBuf.length), 2)
      }
      socket.write(Buffer.concat([header, maskKey, masked]))
    }
  })
}

// Тонкая обвязка над WS-соединением: request/response по id + события по method.
class CDPSession {
  constructor(ws) {
    this.ws = ws
    this._nextId = 1
    this._pending = new Map()
    this._emitter = new EventEmitter()
    ws.on('message', (raw) => {
      let msg
      try {
        msg = JSON.parse(raw)
      } catch {
        return
      }
      if (msg.id !== undefined && this._pending.has(msg.id)) {
        const { resolve, reject } = this._pending.get(msg.id)
        this._pending.delete(msg.id)
        if (msg.error) reject(new Error(msg.error.message))
        else resolve(msg.result)
      } else if (msg.method) {
        this._emitter.emit(msg.method, msg.params)
      }
    })
  }

  send(method, params = {}) {
    const id = this._nextId++
    this.ws.send(JSON.stringify({ id, method, params }))
    return new Promise((resolve, reject) => {
      this._pending.set(id, { resolve, reject })
    })
  }

  once(method, fn) {
    this._emitter.once(method, fn)
  }
}

function httpGetJson(url) {
  return new Promise((resolve, reject) => {
    http
      .get(url, (res) => {
        let data = ''
        res.on('data', (c) => (data += c))
        res.on('end', () => {
          try {
            resolve(JSON.parse(data))
          } catch (err) {
            reject(err)
          }
        })
      })
      .on('error', reject)
  })
}

// ───────────────────────── Chrome ─────────────────────────

function launchChrome(userDataDir) {
  return new Promise((resolve, reject) => {
    const args = [
      '--headless=new',
      '--no-sandbox',
      '--disable-gpu',
      '--disable-dev-shm-usage',
      '--disable-extensions',
      '--disable-background-networking',
      '--disable-sync',
      '--no-first-run',
      '--hide-scrollbars',
      '--mute-audio',
      '--no-proxy-server', // локальный сервер не должен уезжать в системный/VPN-прокси
      `--user-data-dir=${userDataDir}`,
      '--window-size=1400,2000',
      '--remote-debugging-port=0',
      'about:blank',
    ]
    const proc = spawn(CHROME_PATH, args, { stdio: ['ignore', 'ignore', 'pipe'] })

    let stderrBuf = ''
    let settled = false
    const timer = setTimeout(() => {
      if (settled) return
      settled = true
      reject(new Error('Chrome не поднялся за отведённое время (DevTools listening line не найдена)'))
    }, CHROME_STARTUP_TIMEOUT_MS)

    proc.on('error', (err) => {
      if (settled) return
      settled = true
      clearTimeout(timer)
      reject(err)
    })

    proc.on('exit', (code) => {
      if (settled) return
      settled = true
      clearTimeout(timer)
      reject(new Error(`Chrome неожиданно завершился (код ${code}) до старта DevTools:\n${stderrBuf}`))
    })

    proc.stderr.on('data', (chunk) => {
      stderrBuf += chunk.toString('utf8')
      const m = stderrBuf.match(/DevTools listening on (ws:\/\/[^\s]+)/)
      if (m && !settled) {
        settled = true
        clearTimeout(timer)
        resolve({ proc, browserWsUrl: m[1] })
      }
    })
  })
}

// ───────────────────────── основной сценарий ─────────────────────────

async function main() {
  const originalHtml = await readFile(INDEX_HTML, 'utf8').catch(() => {
    fail(`не найден ${INDEX_HTML} — похоже, "vite build" не отработал перед этим шагом`)
  })
  if (!originalHtml.includes(ROOT_PLACEHOLDER)) {
    fail(`в ${INDEX_HTML} не найден ожидаемый маркер ${ROOT_PLACEHOLDER} — верстка index.html изменилась, скрипт нужно поправить`)
  }

  const staticServer = await startStaticServer(DIST_DIR)
  const staticPort = staticServer.address().port
  log(`статика dist/ поднята на http://127.0.0.1:${staticPort}/`)

  const userDataDir = await mkdtemp(path.join(os.tmpdir(), 'tourrhythm-prerender-'))
  let chromeProc = null
  let renderedHTML = null

  try {
    const { proc, browserWsUrl } = await launchChrome(userDataDir)
    chromeProc = proc
    log('Chrome запущен, DevTools доступен')

    const versionUrl = new URL(browserWsUrl)
    const listUrl = `http://${versionUrl.host}/json/list`
    const targets = await httpGetJson(listUrl)
    let target = targets.find((t) => t.type === 'page')
    if (!target) {
      target = await httpGetJson(`http://${versionUrl.host}/json/new?about:blank`)
    }

    const ws = await wsConnect(target.webSocketDebuggerUrl)
    const cdp = new CDPSession(ws)

    await cdp.send('Page.enable')
    await cdp.send('Runtime.enable')
    // Финальное состояние анимаций лендинга без ожидания IntersectionObserver —
    // см. ветку `calm` в LandingPage.jsx.
    await cdp.send('Emulation.setEmulatedMedia', {
      features: [{ name: 'prefers-reduced-motion', value: 'reduce' }],
    })

    await cdp.send('Page.navigate', { url: `http://127.0.0.1:${staticPort}/` })

    // Не полагаемся на Page.loadEventFired: на странице есть внешний скрипт
    // (Google Maps), который может зависнуть на прокси/VPN окружении и никак
    // не влияет на содержимое #root. Вместо этого поллим сам DOM.
    const deadline = Date.now() + NAV_TIMEOUT_MS
    let ready = false
    while (Date.now() < deadline) {
      const evalResult = await cdp.send('Runtime.evaluate', {
        expression: `(() => {
          var root = document.getElementById('root');
          if (!root) return false;
          var all = root.querySelectorAll('.s');
          if (!all.length) return false;
          for (var i = 0; i < all.length; i++) {
            if (!all[i].classList.contains('on')) return false;
          }
          return true;
        })()`,
        returnByValue: true,
      })
      if (evalResult && evalResult.result && evalResult.result.value === true) {
        ready = true
        break
      }
      await new Promise((r) => setTimeout(r, 150))
    }

    if (!ready) {
      fail('за отведённое время лендинг не дорисовался в #root (секции .s не получили класс .on)')
    }

    const htmlResult = await cdp.send('Runtime.evaluate', {
      expression: `(() => { var r = document.getElementById('root'); return r ? r.innerHTML : ''; })()`,
      returnByValue: true,
    })
    renderedHTML = htmlResult && htmlResult.result ? htmlResult.result.value : ''
  } finally {
    if (chromeProc) {
      try {
        chromeProc.kill('SIGKILL')
      } catch {
        /* уже мёртв — не страшно */
      }
    }
    await new Promise((resolve) => staticServer.close(resolve))
    await rm(userDataDir, { recursive: true, force: true }).catch(() => {})
  }

  if (!renderedHTML || !renderedHTML.trim()) {
    fail('#root оказался пустым после рендера — пререндер не удался')
  }

  const visibleText = renderedHTML
    .replace(/<[^>]*>/g, ' ')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\s+/g, ' ')
    .trim()

  log(`видимого текста в #root: ${visibleText.length} символов`)

  if (visibleText.length <= MIN_VISIBLE_CHARS) {
    fail(`видимого текста в #root слишком мало: ${visibleText.length} символов (нужно больше ${MIN_VISIBLE_CHARS})`)
  }
  if (!visibleText.includes(REQUIRED_PHRASE)) {
    fail(`в отрендеренном тексте не найдена обязательная фраза: «${REQUIRED_PHRASE}»`)
  }

  const patchedHtml = originalHtml.replace(ROOT_PLACEHOLDER, `<div id="root">${renderedHTML}</div>`)
  if (patchedHtml === originalHtml) {
    fail('не удалось подставить отрендеренную разметку в index.html (replace не сработал)')
  }

  await writeFile(INDEX_HTML, patchedHtml, 'utf8')
  log(`готово: ${INDEX_HTML} обновлён, #root теперь содержит статичную разметку лендинга`)
}

const watchdog = setTimeout(() => {
  console.error(`[prerender] превышен общий таймаут ${WATCHDOG_MS}мс — принудительное завершение`)
  process.exit(1)
}, WATCHDOG_MS)
watchdog.unref()

main()
  .then(() => process.exit(0))
  .catch((err) => {
    fail(err && err.stack ? err.stack : String(err))
  })
