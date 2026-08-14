/**
 * Пререндер лендинга на этапе сборки, без браузера.
 *
 * Лендинг это React-компонент, поэтому его можно превратить в HTML прямо в
 * Node через renderToStaticMarkup. Прошлая версия скрипта поднимала настоящий
 * Chromium и снимала страницу с него: это требовало 115 МБ браузера в каждой
 * сборке и роняло деплой, когда загрузка не проходила.
 *
 * Здесь ничего не качается и результат детерминированный, поэтому проверки
 * жёсткие: если текста нет, сборка падает и пустая страница в прод не уезжает.
 *
 * Запускается после `vite build`, правит dist/index.html.
 */

import path from 'node:path'
import { readFile, writeFile, rm } from 'node:fs/promises'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { build } from 'vite'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.join(__dirname, '..')
const DIST_DIR = path.join(ROOT, 'dist')
const INDEX_HTML = path.join(DIST_DIR, 'index.html')
const TMP_DIR = path.join(ROOT, '.prerender-tmp')
const ENTRY = path.join(__dirname, 'prerender-entry.jsx')

const ROOT_PLACEHOLDER = '<div id="root"></div>'
const REQUIRED_PHRASE = 'Что ты будешь делать в поездке каждый день?'
const MIN_VISIBLE_CHARS = 500

function log(m) { console.log(`[prerender] ${m}`) }
function fail(m) { console.error(`[prerender] ${m}`); process.exit(1) }

/** Грубо оценить объём видимого текста: без тегов, скриптов и стилей. */
function visibleTextLength(html) {
  const stripped = html
    .replace(/<(script|style)\b[\s\S]*?<\/\1>/gi, ' ')
    .replace(/<[^>]+>/g, ' ')
  return stripped.replace(/\s+/g, ' ').trim()
}

async function buildEntry() {
  await build({
    root: ROOT,
    logLevel: 'error',
    build: {
      ssr: ENTRY,
      outDir: TMP_DIR,
      emptyOutDir: true,
      copyPublicDir: false,
      minify: false,
      rollupOptions: { output: { entryFileNames: 'entry.mjs', format: 'es' } },
    },
  })
  return path.join(TMP_DIR, 'entry.mjs')
}

async function main() {
  const original = await readFile(INDEX_HTML, 'utf8').catch(() =>
    fail(`не найден ${INDEX_HTML} — похоже, "vite build" не отработал перед этим шагом`),
  )
  if (!original.includes(ROOT_PLACEHOLDER)) {
    fail(`в ${INDEX_HTML} не найден маркер ${ROOT_PLACEHOLDER} — разметка index.html изменилась`)
  }

  let entryFile
  try {
    entryFile = await buildEntry()
  } catch (err) {
    fail(`не удалось собрать точку входа: ${err && err.message ? err.message : err}`)
  }

  let markup
  try {
    const mod = await import(pathToFileURL(entryFile).href)
    if (typeof mod.render !== 'function') fail('в собранной точке входа нет функции render')
    markup = mod.render()
  } catch (err) {
    fail(`рендер упал: ${err && err.stack ? err.stack : err}`)
  } finally {
    await rm(TMP_DIR, { recursive: true, force: true })
  }

  if (!markup || !markup.trim()) fail('рендер вернул пустую разметку')

  const text = visibleTextLength(markup)
  if (text.length < MIN_VISIBLE_CHARS) {
    fail(`видимого текста слишком мало: ${text.length} символов, нужно больше ${MIN_VISIBLE_CHARS}`)
  }
  if (!text.includes(REQUIRED_PHRASE)) {
    fail(`в отрендеренном тексте нет обязательной фразы: «${REQUIRED_PHRASE}»`)
  }

  const updated = original.replace(ROOT_PLACEHOLDER, `<div id="root">${markup}</div>`)
  if (updated === original) fail('не удалось подставить разметку в index.html')

  await writeFile(INDEX_HTML, updated, 'utf8')
  log(`готово: ${text.length} символов видимого текста в #root, браузер не понадобился`)
}

main().catch((err) => fail(err && err.stack ? err.stack : String(err)))
