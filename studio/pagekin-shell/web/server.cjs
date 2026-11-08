/**
 * 把 Pagekin 的主进程当作 Web 服务运行。
 *
 * 依赖前提：node_modules/electron 已被替换为 web/shims/electron（见 Dockerfile）。
 * 全部 IPC 通道通过 POST /rpc 调用，主进程的 webContents.send 通过 GET /events 以 SSE 推送。
 */

'use strict'

const http = require('node:http')
const fs = require('node:fs')
const path = require('node:path')

const ROOT = path.resolve(__dirname, '..')
const DIST = path.join(ROOT, 'dist')
const PORT = Number(process.env.PORT || 5180)
const HOST = process.env.HOST || '0.0.0.0'

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.ico': 'image/x-icon',
  '.map': 'application/json; charset=utf-8',
  '.wasm': 'application/wasm',
}

/** 主进程可能返回 Buffer，转成前端可用的结构 */
function serialize(value) {
  if (value === undefined) return null
  if (Buffer.isBuffer(value)) {
    return { __buffer: true, base64: value.toString('base64') }
  }
  if (value instanceof Uint8Array) {
    return { __buffer: true, base64: Buffer.from(value).toString('base64') }
  }
  return value
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = []
    let size = 0
    req.on('data', (chunk) => {
      size += chunk.length
      if (size > 64 * 1024 * 1024) {
        reject(new Error('请求体超过 64MB'))
        req.destroy()
        return
      }
      chunks.push(chunk)
    })
    req.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')))
    req.on('error', reject)
  })
}

function sendJson(res, status, payload) {
  const body = JSON.stringify(payload)
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(body),
    'Cache-Control': 'no-store',
  })
  res.end(body)
}

function serveStatic(req, res, pathname) {
  const safe = pathname.replace(/^\/+/, '').replace(/\.\./g, '')
  let file = path.join(DIST, safe || 'index.html')
  if (!file.startsWith(DIST)) {
    res.writeHead(403).end('forbidden')
    return
  }
  if (!fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    // SPA 回退
    file = path.join(DIST, 'index.html')
  }
  if (!fs.existsSync(file)) {
    res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' })
    res.end('前端尚未构建：请先执行 vite build')
    return
  }
  const ext = path.extname(file).toLowerCase()
  // HTML 在服务端注入桥接脚本，避免改动 Pagekin 的 index.html
  if (ext === '.html') {
    let html = fs.readFileSync(file, 'utf8')
    if (!html.includes('web-bridge.js')) {
      html = html.replace('</head>', '<script src="/web-bridge.js"></script></head>')
    }
    res.writeHead(200, {
      'Content-Type': 'text/html; charset=utf-8',
      'Content-Length': Buffer.byteLength(html),
      'Cache-Control': 'no-store',
    })
    res.end(html)
    return
  }
  const stat = fs.statSync(file)
  res.writeHead(200, {
    'Content-Type': MIME[ext] || 'application/octet-stream',
    'Content-Length': stat.size,
    'Cache-Control': ext === '.html' ? 'no-store' : 'public, max-age=31536000, immutable',
  })
  fs.createReadStream(file).pipe(res)
}

async function main() {
  process.chdir(ROOT)

  // 启动主进程：它会初始化数据目录、注册全部 IPC controller
  require(path.join(ROOT, 'dist-electron', 'main.js'))

  const electron = require('electron')
  const web = electron.__web
  if (!web) {
    throw new Error('electron shim 未生效：请确认 node_modules/electron 已替换为 web/shims/electron')
  }

  // 等 controller 注册完成（whenReady 回调是异步的）
  const deadline = Date.now() + 20000
  while (web.handlers.size === 0 && Date.now() < deadline) {
    await new Promise((r) => setTimeout(r, 200))
  }
  console.log(`[web] 已注册 IPC 通道 ${web.handlers.size} 个`)
  console.log(`[web] 数据目录 ${web.dataDir}`)

  const server = http.createServer(async (req, res) => {
    const { pathname } = new URL(req.url, `http://${req.headers.host || 'localhost'}`)

    res.setHeader('Access-Control-Allow-Origin', '*')
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type')
    res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    if (req.method === 'OPTIONS') {
      res.writeHead(204).end()
      return
    }

    if (pathname === '/health') {
      sendJson(res, 200, {
        ok: true,
        channels: web.handlers.size,
        dataDir: web.dataDir,
      })
      return
    }

    if (pathname === '/web-bridge.js') {
      const bridge = path.join(__dirname, 'bridge.js')
      const body = fs.readFileSync(bridge)
      res.writeHead(200, {
        'Content-Type': 'text/javascript; charset=utf-8',
        'Content-Length': body.length,
        'Cache-Control': 'no-store',
      })
      res.end(body)
      return
    }

    if (pathname === '/events') {
      res.writeHead(200, {
        'Content-Type': 'text/event-stream; charset=utf-8',
        'Cache-Control': 'no-cache, no-transform',
        Connection: 'keep-alive',
        'X-Accel-Buffering': 'no',
      })
      res.write(': connected\n\n')
      const remove = web.addSubscriber((payload) => {
        res.write(`data: ${JSON.stringify(payload)}\n\n`)
      })
      const keepAlive = setInterval(() => res.write(': ping\n\n'), 25000)
      req.on('close', () => {
        clearInterval(keepAlive)
        remove()
      })
      return
    }

    if (pathname === '/rpc' && req.method === 'POST') {
      let parsed
      try {
        parsed = JSON.parse(await readBody(req))
      } catch (e) {
        sendJson(res, 400, { ok: false, error: `请求体解析失败: ${e.message}` })
        return
      }
      const { channel, args } = parsed || {}
      if (typeof channel !== 'string') {
        sendJson(res, 400, { ok: false, error: 'channel 缺失' })
        return
      }
      try {
        const result = await web.invokeChannel(channel, Array.isArray(args) ? args : [])
        sendJson(res, 200, { ok: true, result: serialize(result) })
      } catch (e) {
        const message = e && e.message ? e.message : String(e)
        const stack = e && e.stack ? String(e.stack).split('\n').slice(0, 6).join('\n') : ''
        console.error(`[rpc] ${channel} 失败: ${message}`)
        sendJson(res, 200, { ok: false, error: message, code: e && e.code, stack })
      }
      return
    }

    if (req.method === 'GET') {
      serveStatic(req, res, pathname)
      return
    }

    res.writeHead(405).end('method not allowed')
  })

  server.listen(PORT, HOST, () => {
    console.log(`[web] Pagekin 运行在 http://${HOST}:${PORT}`)
  })

  const shutdown = () => {
    server.close(() => process.exit(0))
    setTimeout(() => process.exit(0), 3000)
  }
  process.on('SIGTERM', shutdown)
  process.on('SIGINT', shutdown)
}

main().catch((e) => {
  console.error('[web] 启动失败:', e)
  process.exit(1)
})
