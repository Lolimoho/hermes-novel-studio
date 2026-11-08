/**
 * Electron shim —— 让 Pagekin 的主进程代码在普通 Node 进程里运行。
 *
 * 只实现主进程实际用到的 16 个符号（见 README）。
 * 设计原则：不模拟行为，只接管边界——
 *   ipcMain.handle   → 注册表
 *   webContents.send → SSE 广播
 *   app.getPath      → 容器内固定目录
 *   dialog           → 受控目录（不弹窗）
 */

'use strict'

const { EventEmitter } = require('node:events')
const path = require('node:path')
const fs = require('node:fs')

const DATA_DIR = process.env.PAGEKIN_DATA_DIR || '/data'
const PROJECTS_DIR = process.env.PAGEKIN_PROJECTS_DIR || path.join(DATA_DIR, 'projects')

// 与 electron/main.ts 里的计算方式保持一致：APP_ROOT 是 dist-electron 的上一级。
// 启动握手会比对 sender.mainFrame.url 与 rendererUrl，两者必须完全相等。
const APP_ROOT = path.join(__dirname, '..', '..')
const RENDERER_URL =
  process.env.PAGEKIN_WEB_URL ||
  require('node:url').pathToFileURL(path.join(APP_ROOT, 'dist', 'index.html')).href

const PATHS = {
  userData: DATA_DIR,
  appData: DATA_DIR,
  sessionData: DATA_DIR,
  temp: '/tmp',
  home: DATA_DIR,
  downloads: path.join(DATA_DIR, 'downloads'),
  documents: path.join(DATA_DIR, 'documents'),
  desktop: path.join(DATA_DIR, 'desktop'),
  logs: path.join(DATA_DIR, 'logs'),
  crashDumps: path.join(DATA_DIR, 'crashDumps'),
  exe: process.execPath,
}

/** channel -> handler */
const handlers = new Map()
/** channel -> [fn] （ipcMain.on 注册的单向监听） */
const channelListeners = new Map()
/** SSE 订阅者 */
const subscribers = new Set()

function broadcast(channel, args) {
  const payload = { channel, args }
  for (const send of subscribers) {
    try {
      send(payload)
    } catch {
      /* 订阅者已断开，交由 SSE 层清理 */
    }
  }
}

function addSubscriber(send) {
  subscribers.add(send)
  return () => subscribers.delete(send)
}

let currentWindow = null

function makeEvent() {
  const sender = currentWindow ? currentWindow.webContents : null
  return {
    sender: sender || {
      id: 1,
      send: (channel, ...args) => broadcast(channel, args),
      isDestroyed: () => false,
      once: () => {},
      on: () => {},
    },
    senderFrame: sender ? sender.mainFrame : null,
    frameId: 0,
    processId: process.pid,
    reply: (channel, ...args) => broadcast(channel, args),
    returnValue: undefined,
  }
}

// ---------------------------------------------------------------- ipcMain

const ipcMain = {
  handle(channel, listener) {
    if (typeof channel !== 'string') throw new TypeError('channel must be a string')
    if (typeof listener !== 'function') throw new TypeError('listener must be a function')
    handlers.set(channel, listener)
  },
  handleOnce(channel, listener) {
    handlers.set(channel, listener)
  },
  removeHandler(channel) {
    handlers.delete(channel)
  },
  on(channel, listener) {
    if (!channelListeners.has(channel)) channelListeners.set(channel, [])
    channelListeners.get(channel).push(listener)
  },
  once(channel, listener) {
    ipcMain.on(channel, listener)
  },
  removeListener(channel, listener) {
    const list = channelListeners.get(channel)
    if (list) channelListeners.set(channel, list.filter((fn) => fn !== listener))
  },
  emit(channel, ...args) {
    for (const fn of channelListeners.get(channel) || []) fn(makeEvent(), ...args)
  },
}

/** 供 HTTP 层调用 */
async function invokeChannel(channel, args) {
  const handler = handlers.get(channel)
  if (!handler) {
    const err = new Error(`No handler registered for '${channel}'`)
    err.code = 'NO_HANDLER'
    throw err
  }
  return handler(makeEvent(), ...args)
}

// ---------------------------------------------------------------- app

const appEvents = new EventEmitter()
let readyResolved = false

const app = {
  isPackaged: false,
  getVersion: () => process.env.PAGEKIN_VERSION || '1.4.0-web',
  getName: () => 'ai-novel-writer',
  getAppPath: () => process.cwd(),
  getPath: (name) => PATHS[name] || DATA_DIR,
  setPath: (name, value) => {
    PATHS[name] = value
  },
  whenReady: () => {
    if (!readyResolved) {
      readyResolved = true
      // 主进程在 whenReady 后初始化数据目录，先确保存在
      for (const dir of [DATA_DIR, PROJECTS_DIR]) {
        try {
          fs.mkdirSync(dir, { recursive: true })
        } catch {
          /* 目录已存在或无权限，交由后续逻辑报错 */
        }
      }
    }
    return Promise.resolve()
  },
  on: (event, fn) => {
    appEvents.on(event, fn)
    return app
  },
  once: (event, fn) => {
    appEvents.once(event, fn)
    return app
  },
  off: (event, fn) => {
    appEvents.off(event, fn)
    return app
  },
  emit: (event, ...args) => appEvents.emit(event, ...args),
  quit: () => {
    // 容器里由容器编排负责生命周期，不主动退出
  },
  exit: () => {},
  relaunch: () => {},
  requestSingleInstanceLock: () => true,
  releaseSingleInstanceLock: () => {},
  setAsDefaultProtocolClient: () => true,
  removeAsDefaultProtocolClient: () => true,
  isDefaultProtocolClient: () => false,
  getLoginItemSettings: () => ({ openAtLogin: false }),
  setLoginItemSettings: () => {},
  disableHardwareAcceleration: () => {},
  commandLine: {
    appendSwitch: () => {},
    appendArgument: () => {},
    getSwitchValue: () => '',
    hasSwitch: () => false,
    removeSwitch: () => {},
  },
  getLocale: () => process.env.PAGEKIN_LOCALE || 'zh-CN',
  getSystemLocale: () => process.env.PAGEKIN_LOCALE || 'zh-CN',
  getPreferredSystemLanguages: () => ['zh-CN', 'en-US'],
  setLocale: () => {},
  getGPUFeatureStatus: () => ({}),
  setAppUserModelId: () => {},
  dock: { hide: () => {}, show: () => {}, setBadge: () => {} },
  focus: () => {},
}

// ---------------------------------------------------------------- BrowserWindow

const windows = new Set()

class WebContents extends EventEmitter {
  constructor() {
    super()
    this.id = 1
    // 启动握手会校验 sender.mainFrame.url 是否等于 rendererUrl
    this.mainFrame = { url: RENDERER_URL }
    this.session = { clearCache: async () => {}, setPermissionRequestHandler: () => {} }
  }

  send(channel, ...args) {
    broadcast(channel, args)
  }

  once(channel, fn) {
    super.once(channel, fn)
  }

  isDestroyed() {
    return false
  }

  setWindowOpenHandler() {}

  setZoomFactor() {}

  setZoomLevel() {}

  getZoomLevel() {
    return 0
  }

  openDevTools() {}

  reload() {}
}

class BrowserWindow extends EventEmitter {
  static getAllWindows() {
    return [...windows]
  }

  static getFocusedWindow() {
    return [...windows][0] || null
  }

  static fromWebContents() {
    return [...windows][0] || null
  }

  constructor(options = {}) {
    super()
    this.options = options
    this.id = windows.size + 1
    this.webContents = new WebContents()
    this.destroyed = false
    windows.add(this)
    if (!currentWindow) currentWindow = this
  }

  loadURL() {
    return Promise.resolve()
  }

  loadFile() {
    return Promise.resolve()
  }

  show() {}

  hide() {}

  focus() {}

  close() {
    this.destroyed = true
    windows.delete(this)
    if (currentWindow === this) currentWindow = null
  }

  destroy() {
    this.close()
  }

  isDestroyed() {
    return this.destroyed
  }

  isMinimized() {
    return false
  }

  maximize() {}

  unmaximize() {}

  restore() {}

  setTitle() {}

  setMenu() {}

  setMenuBarVisibility() {}

  setProgressBar() {}

  isMaximized() {
    return false
  }

  getBounds() {
    return { x: 0, y: 0, width: 1440, height: 900 }
  }

  capturePage() {
    return Promise.resolve({ toPNG: () => Buffer.alloc(0) })
  }

  setBackgroundColor() {}
}

// ---------------------------------------------------------------- 其余边界

/**
 * Web 模式没有原生文件对话框。
 * 目录选择退化为「协议目录」：优先返回已存在的项目目录，否则返回根目录供新建。
 * 真实目录浏览留待后续用 /fs 接口实现，这里先把主流程打通。
 */
const PICK_ROOT = process.env.PAGEKIN_PICK_DIR || path.join(DATA_DIR, 'projects')

function findExistingProject() {
  try {
    const entries = fs.readdirSync(PICK_ROOT, { withFileTypes: true })
    for (const entry of entries) {
      if (!entry.isDirectory()) continue
      const dir = path.join(PICK_ROOT, entry.name)
      // Pagekin 的项目数据库在 <项目>/.ai-novel/project.db
      if (fs.existsSync(path.join(dir, '.ai-novel', 'project.db'))) return dir
    }
  } catch {
    /* 目录不存在时返回根目录 */
  }
  return null
}

const dialog = {
  showOpenDialog: async (options = {}) => {
    const properties = options.properties || []
    if (properties.includes('openDirectory')) {
      // 主进程用 title 区分用途：新建要父目录，打开要具体项目目录
      const title = String(options.title || '')
      const forCreate = title.includes('保存位置') || /choose where to save/i.test(title)
      const chosen = forCreate ? PICK_ROOT : findExistingProject() || PICK_ROOT
      try {
        fs.mkdirSync(chosen, { recursive: true })
      } catch {
        /* 目录已存在 */
      }
      console.log(`[dialog] Web 模式选择目录（${forCreate ? '新建' : '打开'}）: ${chosen}`)
      return { canceled: false, filePaths: [chosen], bookmarks: [] }
    }
    // 文件选择暂不支持
    return { canceled: true, filePaths: [], bookmarks: [] }
  },
  showOpenDialogSync: () => undefined,
  showSaveDialog: async () => ({ canceled: true, filePath: undefined, bookmark: undefined }),
  showSaveDialogSync: () => undefined,
  showMessageBox: async () => ({ response: 0, checkboxChecked: false }),
  showMessageBoxSync: () => 0,
  showErrorBox: (title, content) => console.error(`[dialog] ${title}: ${content}`),
}

const shell = {
  openExternal: async () => {},
  openPath: async () => '',
  showItemInFolder: () => {},
  trashItem: async () => {},
  beep: () => {},
}

const safeStorage = {
  isEncryptionAvailable: () => true,
  encryptString: (plain) => Buffer.from(String(plain), 'utf8'),
  decryptString: (buf) => Buffer.from(buf).toString('utf8'),
  setUsePlainTextEncryption: () => {},
  getSelectedStorageBackend: () => 'basic_text',
}

function emptyImage() {
  return {
    isEmpty: () => true,
    getSize: () => ({ width: 0, height: 0 }),
    toPNG: () => Buffer.alloc(0),
    toJPEG: () => Buffer.alloc(0),
    toDataURL: () => '',
    resize: () => emptyImage(),
  }
}

const nativeImage = {
  createFromPath: () => emptyImage(),
  createFromBuffer: () => emptyImage(),
  createFromDataURL: () => emptyImage(),
  createEmpty: () => emptyImage(),
}

const screen = {
  getPrimaryDisplay: () => ({ workAreaSize: { width: 1440, height: 900 }, scaleFactor: 1 }),
  getAllDisplays: () => [{ workAreaSize: { width: 1440, height: 900 }, scaleFactor: 1 }],
  getCursorScreenPoint: () => ({ x: 0, y: 0 }),
}

const clipboard = {
  readText: () => '',
  writeText: () => {},
  readImage: () => emptyImage(),
  writeImage: () => {},
}

const Menu = {
  buildFromTemplate: () => ({ popup: () => {} }),
  setApplicationMenu: () => {},
  getApplicationMenu: () => null,
}

const globalShortcut = {
  register: () => true,
  unregister: () => {},
  unregisterAll: () => {},
}

const powerMonitor = {
  on: () => {},
  getSystemIdleTime: () => 0,
}

const protocol = {
  registerSchemesAsPrivileged: () => {},
  handle: () => {},
  unhandle: () => {},
}

module.exports = {
  app,
  ipcMain,
  BrowserWindow,
  WebContents,
  dialog,
  shell,
  safeStorage,
  nativeImage,
  screen,
  clipboard,
  Menu,
  globalShortcut,
  powerMonitor,
  protocol,
  // preload 才用，Web 下不加载 preload，这里给空实现避免导入报错
  ipcRenderer: { invoke: async () => {}, on: () => {}, once: () => {}, send: () => {} },
  contextBridge: { exposeInMainWorld: () => {} },
  webFrame: { setZoomLevel: () => {}, setZoomFactor: () => {}, getZoomLevel: () => 0 },
  // 内部给 HTTP 层用的非 Electron 接口
  __web: {
    invokeChannel,
    addSubscriber,
    handlers,
    dataDir: DATA_DIR,
    projectsDir: PROJECTS_DIR,
  },
}
