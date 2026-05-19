import { useState, useEffect, useMemo, useCallback } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import './TripPlanScreen.css'
import TripMap from '../components/TripMap'

const API_BASE = 'http://localhost:8000'
const GMAPS_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY

function getToken() { return localStorage.getItem('access_token') ?? '' }

function formatTime(dt) {
  if (!dt) return null
  try { return new Date(dt).toTimeString().slice(0, 5) }
  catch { return null }
}

function calcNumDays(startDate, endDate) {
  if (startDate && endDate) {
    const diff = Math.round((new Date(endDate) - new Date(startDate)) / 86400000) + 1
    return Math.max(1, diff)
  }
  return 7
}

const TR = {
  bg:         '#f1ede0',
  surface:    '#fbf7ea',
  surface2:   '#e8e2cf',
  fg:         '#0d2818',
  fgMute:     '#5e6e58',
  hairline:   'rgba(13,40,24,0.12)',
  hairlineSt: 'rgba(13,40,24,0.22)',
  lime:       '#b9ff3d',
  warn:       '#c8553d',
}

const DAY_COLORS = [
  '#c8553d', '#4a7c59', '#5a6e9a', '#8a5a2a', '#6a4a8a', '#3a7a6a', '#7a5a3a',
]

const WEEKDAYS = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
const WEEKDAYS_FULL = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
const MONTHS_FULL = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
const TABS = ['ДНИ', 'КАРТА', 'БЮДЖЕТ']

const BUDGET_PER_DAY = { low: 4000, medium: 10000, high: 22000 }
const BUDGET_CATS = [
  { icon: '🏨', label: 'Жильё',          pct: 40 },
  { icon: '🍽', label: 'Еда',             pct: 30 },
  { icon: '🎫', label: 'Входные билеты',  pct: 20 },
  { icon: '🚇', label: 'Транспорт',       pct: 10 },
]

const CURVE_PATH = 'M0,45 C20,42 30,42 40,38 C50,30 60,15 80,12 C100,9 120,18 140,28 C160,38 175,40 195,30 C215,20 230,18 250,22 C265,25 275,30 280,35'
const CURVE_FILL = 'M0,45 C20,42 30,42 40,38 C50,30 60,15 80,12 C100,9 120,18 140,28 C160,38 175,40 195,30 C215,20 230,18 250,22 C265,25 275,30 280,35 L280,55 L0,55 Z'
const CURVE_DOTS = [
  { x: 8,   y: 43, peak: false },
  { x: 80,  y: 12, peak: true  },
  { x: 140, y: 28, peak: false },
  { x: 230, y: 18, peak: false },
]

// ── Icons ──────────────────────────────────────────────────

const ChevronLeft = () => (
  <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
    <path d="M11.5 4 L6.5 9 L11.5 14" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
)

const ShareIcon = () => (
  <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
    <circle cx="14" cy="4" r="2" stroke="currentColor" strokeWidth="1.5"/>
    <circle cx="4" cy="9" r="2" stroke="currentColor" strokeWidth="1.5"/>
    <circle cx="14" cy="14" r="2" stroke="currentColor" strokeWidth="1.5"/>
    <path d="M6 8 L12 5M6 10 L12 13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
  </svg>
)

const TrashIcon = () => (
  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
    <path d="M2 4h10M5 4V2.5h4V4M5.5 6.5v4M8.5 6.5v4M3 4l.8 7.2A1 1 0 0 0 4.8 12h4.4a1 1 0 0 0 1-.8L11 4" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
)

const CheckIcon = () => (
  <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
    <path d="M2 7 L5.5 10.5 L11 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
)

const InfoIcon = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
    <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="1.4"/>
    <line x1="8" y1="7.5" x2="8" y2="11.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
    <circle cx="8" cy="4.8" r="0.75" fill="currentColor"/>
  </svg>
)

// ── Toast ──────────────────────────────────────────────────

function Toast({ message, onDone }) {
  useEffect(() => {
    const t = setTimeout(onDone, 2200)
    return () => clearTimeout(t)
  }, [onDone])
  return (
    <div style={{
      position: 'fixed', bottom: 80, left: '50%', transform: 'translateX(-50%)',
      zIndex: 2000, pointerEvents: 'none',
      background: TR.fg, color: TR.lime,
      padding: '10px 18px', borderRadius: 99,
      fontFamily: 'Archivo, sans-serif', fontWeight: 800, fontSize: 12,
      letterSpacing: '0.05em', whiteSpace: 'nowrap',
      boxShadow: '0 4px 16px rgba(13,40,24,0.25)',
      animation: 'tr-toast-in 0.18s ease',
    }}>
      {message}
    </div>
  )
}

// ── Confirm modal ──────────────────────────────────────────

function ConfirmModal({ title, body, onConfirm, onCancel, loading, confirmLabel = 'УДАЛИТЬ', loadingLabel, confirmColor = TR.warn, confirmTextColor = '#fff' }) {
  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 1100,
      display: 'flex', flexDirection: 'column', justifyContent: 'flex-end',
      background: 'rgba(13,40,24,0.5)',
    }} onClick={onCancel}>
      <div style={{
        background: TR.bg, borderRadius: '20px 20px 0 0',
        border: '1.5px solid ' + TR.fg, borderBottom: 'none',
        padding: '24px 22px 32px',
      }} onClick={e => e.stopPropagation()}>
        <div style={{
          fontFamily: 'Archivo, sans-serif', fontWeight: 900, fontSize: 18,
          letterSpacing: '-0.02em', color: TR.fg, textTransform: 'uppercase',
          marginBottom: 10,
        }}>{title}</div>
        {body && (
          <div style={{ fontSize: 14, color: TR.fgMute, lineHeight: 1.5, marginBottom: 20 }}>
            {body}
          </div>
        )}
        <div style={{ display: 'flex', gap: 10 }}>
          <button onClick={onCancel} style={{
            flex: 1, height: 46,
            background: 'transparent', border: '1.5px solid ' + TR.hairlineSt,
            borderRadius: 12, cursor: 'pointer',
            fontFamily: 'Archivo, sans-serif', fontWeight: 800, fontSize: 13,
            letterSpacing: '0.04em', color: TR.fg,
          }}>ОТМЕНА</button>
          <button onClick={onConfirm} disabled={loading} style={{
            flex: 1, height: 46,
            background: confirmColor, border: '1.5px solid ' + TR.fg,
            borderRadius: 12, cursor: loading ? 'wait' : 'pointer',
            fontFamily: 'Archivo, sans-serif', fontWeight: 800, fontSize: 13,
            letterSpacing: '0.04em', color: confirmTextColor,
            boxShadow: '2px 2px 0 0 ' + TR.fg,
            opacity: loading ? 0.6 : 1,
          }}>{loading ? (loadingLabel ?? confirmLabel + '…') : confirmLabel}</button>
        </div>
      </div>
    </div>
  )
}

// ── Skeleton ───────────────────────────────────────────────

function Shimmer({ w = '100%', h = 16, r = 6, style = {} }) {
  return (
    <div className="tr-shimmer" style={{ width: w, height: h, borderRadius: r, ...style }} />
  )
}

function SkeletonDay() {
  return (
    <div style={{ padding: '18px 22px 24px' }}>
      {[0, 1, 2].map(i => (
        <div key={i} style={{ display: 'flex', gap: 12, marginBottom: 22 }}>
          <div style={{ width: 46, flexShrink: 0 }}>
            <Shimmer w={46} h={13} style={{ marginBottom: 6 }} />
            <Shimmer w={34} h={10} />
          </div>
          <div style={{ width: 14, flexShrink: 0, paddingTop: 3 }}>
            <Shimmer w={10} h={10} r={99} style={{ margin: '0 auto' }} />
          </div>
          <div style={{ flex: 1 }}>
            <Shimmer w="65%" h={18} style={{ marginBottom: 8 }} />
            <Shimmer w="88%" h={13} style={{ marginBottom: 6 }} />
            <Shimmer w={56} h={10} />
          </div>
        </div>
      ))}
    </div>
  )
}

// ── Place Details Modal ────────────────────────────────────

function PlaceDetailsModal({ poi, cityName, onClose }) {
  const [details, setDetails] = useState(null)
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState(null)

  useEffect(() => {
    const headers = { Authorization: `Bearer ${getToken()}` }

    async function load() {
      try {
        let placeId = poi.google_place_id
        if (!placeId) {
          const query = `${poi.name} ${cityName ?? ''}`
          const findRes = await fetch(`${API_BASE}/places/find?input=${encodeURIComponent(query)}`, { headers })
          if (!findRes.ok) { setErr('Место не найдено в Google Maps'); setLoading(false); return }
          const findData = await findRes.json()
          placeId = findData.place_id
        }
        if (!placeId) { setErr('Место не найдено в Google Maps'); setLoading(false); return }

        const detailRes = await fetch(`${API_BASE}/places/details?place_id=${placeId}`, { headers })
        if (!detailRes.ok) { setErr('Не удалось загрузить детали'); setLoading(false); return }
        setDetails(await detailRes.json())
      } catch (e) {
        setErr(e.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [poi, cityName])

  const [photoBlob, setPhotoBlob] = useState(null)
  useEffect(() => {
    if (!details?.photos?.[0]?.photo_reference) return
    const ref = details.photos[0].photo_reference
    fetch(`${API_BASE}/places/photo?photo_reference=${encodeURIComponent(ref)}&maxwidth=400`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    })
      .then(r => r.ok ? r.blob() : null)
      .then(blob => blob && setPhotoBlob(URL.createObjectURL(blob)))
  }, [details])

  const todayHours = (() => {
    const periods = details?.opening_hours?.weekday_text
    if (!periods) return null
    const day = new Date().getDay()
    const idx = day === 0 ? 6 : day - 1
    return periods[idx] ?? null
  })()

  const mapsUrl = details?.formatted_address
    ? `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(details.formatted_address)}`
    : `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(poi.name)}`

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 1000,
      display: 'flex', flexDirection: 'column', justifyContent: 'flex-end',
      background: 'rgba(13,40,24,0.5)',
    }} onClick={onClose}>
      <div style={{
        background: TR.bg, borderRadius: '20px 20px 0 0',
        maxHeight: '80vh', overflowY: 'auto',
        border: '1.5px solid ' + TR.fg,
        borderBottom: 'none',
      }} onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div style={{ padding: '16px 22px 12px', borderBottom: '1px solid ' + TR.hairline, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ fontFamily: 'Archivo, sans-serif', fontWeight: 800, fontSize: 16, letterSpacing: '-0.02em', color: TR.fg, textTransform: 'uppercase' }}>
            {poi.name}
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: 20, color: TR.fgMute, lineHeight: 1 }}>×</button>
        </div>

        <div style={{ padding: '0 0 32px' }}>
          {loading && (
            <div style={{ padding: '32px 22px', textAlign: 'center', fontFamily: 'JetBrains Mono, monospace', fontSize: 11, color: TR.fgMute, letterSpacing: 1 }}>
              ЗАГРУЖАЕМ ДАННЫЕ…
            </div>
          )}
          {err && (
            <div style={{ padding: '20px 22px', fontSize: 13, color: TR.warn }}>
              {err}
            </div>
          )}
          {details && (
            <>
              {photoBlob && (
                <img src={photoBlob} alt={poi.name} style={{ width: '100%', height: 180, objectFit: 'cover', display: 'block' }} />
              )}
              <div style={{ padding: '16px 22px 0' }}>
                {details.rating && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                    <span style={{ background: TR.lime, color: TR.fg, fontFamily: 'JetBrains Mono, monospace', fontSize: 13, fontWeight: 700, padding: '3px 8px', borderRadius: 6 }}>
                      ★ {details.rating}
                    </span>
                    {details.user_ratings_total && (
                      <span style={{ fontSize: 12, color: TR.fgMute, fontFamily: 'JetBrains Mono, monospace' }}>
                        {details.user_ratings_total.toLocaleString()} отзывов
                      </span>
                    )}
                  </div>
                )}
                {details.formatted_address && (
                  <div style={{ fontSize: 13, color: TR.fgMute, marginBottom: 10, lineHeight: 1.4 }}>
                    📍 {details.formatted_address}
                  </div>
                )}
                {todayHours && (
                  <div style={{ fontSize: 12, color: TR.fg, fontFamily: 'JetBrains Mono, monospace', marginBottom: 12, padding: '6px 10px', background: TR.surface, borderRadius: 8 }}>
                    🕐 {todayHours}
                  </div>
                )}
                {details.editorial_summary?.overview && (
                  <div style={{ fontSize: 13, color: TR.fg, lineHeight: 1.6, marginBottom: 14, fontStyle: 'italic' }}>
                    {details.editorial_summary.overview}
                  </div>
                )}
                <a href={mapsUrl} target="_blank" rel="noreferrer" style={{
                  display: 'block', padding: '11px 0', textAlign: 'center',
                  background: TR.fg, color: TR.lime,
                  borderRadius: 10, fontFamily: 'Archivo, sans-serif',
                  fontWeight: 800, fontSize: 13, letterSpacing: '0.05em',
                  textDecoration: 'none',
                }}>
                  ОТКРЫТЬ В GOOGLE MAPS
                </a>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

// ── Rhythm chart ───────────────────────────────────────────

const T_START = 8, T_END = 21
const Y_TOP = 8, Y_BOT = 50

function txTime(hours) {
  return 5 + (hours - T_START) / (T_END - T_START) * 270
}
function tyLevel(level) {
  return Y_TOP + (5 - level) / 4 * (Y_BOT - Y_TOP)
}

function parseHHMM(t) {
  if (!t) return null
  const parts = t.split(':')
  const h = parseInt(parts[0], 10)
  const m = parseInt(parts[1] ?? '0', 10)
  return isNaN(h) || isNaN(m) ? null : h + m / 60
}

function catmullRomSVGPath(pts) {
  if (pts.length < 2) return ''
  const p = [pts[0], ...pts, pts[pts.length - 1]]
  const f = n => n.toFixed(2)
  let d = `M${f(pts[0].x)},${f(pts[0].y)}`
  for (let i = 0; i < pts.length - 1; i++) {
    const [p0, p1, p2, p3] = [p[i], p[i + 1], p[i + 2], p[i + 3]]
    d += ` C${f(p1.x + (p2.x - p0.x) / 6)},${f(p1.y + (p2.y - p0.y) / 6)} ${f(p2.x - (p3.x - p1.x) / 6)},${f(p2.y - (p3.y - p1.y) / 6)} ${f(p2.x)},${f(p2.y)}`
  }
  return d
}

function RhythmChart({ day, color, pois }) {
  const gradId = `grad-${day}`

  const pts = (pois ?? [])
    .filter(p => p.poi_status === 'main' && p.start_time && p.activity_level != null)
    .map(p => {
      const t = parseHHMM(p.start_time)
      return t !== null ? { x: txTime(t), y: tyLevel(p.activity_level), level: p.activity_level } : null
    })
    .filter(Boolean)
    .sort((a, b) => a.x - b.x)

  const hasReal = pts.length >= 2
  const linePath = hasReal ? catmullRomSVGPath(pts) : CURVE_PATH
  const fillPath = hasReal
    ? `${linePath} L${pts[pts.length - 1].x.toFixed(2)},${Y_BOT} L${pts[0].x.toFixed(2)},${Y_BOT} Z`
    : CURVE_FILL

  const gridHours = [8, 12, 16, 20]

  return (
    <svg viewBox="0 0 280 62" style={{ width: '100%', height: 62, display: 'block' }}>
      <defs>
        <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.30"/>
          <stop offset="100%" stopColor={color} stopOpacity="0"/>
        </linearGradient>
      </defs>
      {gridHours.map(h => (
        <line key={h} x1={txTime(h)} y1="0" x2={txTime(h)} y2="50"
          stroke={TR.hairlineSt} strokeWidth="1" strokeDasharray="2,3"/>
      ))}
      <path d={fillPath} fill={`url(#${gradId})`}/>
      <path d={linePath} fill="none" stroke={color} strokeWidth="2"
        strokeLinecap="round" strokeLinejoin="round"/>
      {hasReal
        ? pts.map((pt, i) => (
            <circle key={i} cx={pt.x} cy={pt.y} r={pt.level >= 4 ? 5 : 3.5}
              fill={color} stroke={TR.surface} strokeWidth="2"/>
          ))
        : CURVE_DOTS.map((dot, i) => (
            <circle key={i} cx={dot.x} cy={dot.y} r={dot.peak ? 5 : 3.5}
              fill={color} stroke={TR.surface} strokeWidth="2"/>
          ))
      }
      {gridHours.map(h => (
        <text key={h} x={txTime(h)} y="61" textAnchor="middle"
          fontFamily="JetBrains Mono, monospace" fontSize="8" fill={TR.fgMute}>
          {String(h).padStart(2, '0')}
        </text>
      ))}
    </svg>
  )
}


// ── List tab ───────────────────────────────────────────────

function ListTab({ allPois }) {
  const [filterDay, setFilterDay] = useState(null)
  const [selected, setSelected] = useState(new Set())

  const sorted = useMemo(() => {
    return [...allPois]
      .filter(p => p.day_number != null)
      .sort((a, b) => {
        if (a.day_number !== b.day_number) return a.day_number - b.day_number
        return (a.sequence_order ?? 999) - (b.sequence_order ?? 999)
      })
  }, [allPois])

  const days = useMemo(() => [...new Set(sorted.map(p => p.day_number))], [sorted])

  const filtered = filterDay != null ? sorted.filter(p => p.day_number === filterDay) : sorted

  const toggleAll = () => {
    if (selected.size === filtered.length) setSelected(new Set())
    else setSelected(new Set(filtered.map(p => p.poi.id)))
  }

  const toggle = id => {
    const s = new Set(selected)
    s.has(id) ? s.delete(id) : s.add(id)
    setSelected(s)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', gap: 6, overflowX: 'auto', padding: '12px 22px 8px' }}>
        {[null, ...days].map((d, i) => (
          <button key={i} onClick={() => setFilterDay(d ?? null)} style={{
            flexShrink: 0, padding: '5px 12px',
            border: '1.5px solid ' + TR.hairlineSt,
            borderRadius: 99, fontSize: 10,
            fontFamily: 'Archivo, sans-serif', fontWeight: 800, letterSpacing: '0.05em',
            background: filterDay === (d ?? null) ? TR.fg : 'transparent',
            color: filterDay === (d ?? null) ? TR.lime : TR.fg,
            cursor: 'pointer',
          }}>
            {d == null ? 'ВСЕ' : `ДЕНЬ ${d}`}
          </button>
        ))}
      </div>

      <div style={{
        padding: '6px 22px 8px', display: 'flex', alignItems: 'center', gap: 10,
        borderBottom: '1px solid ' + TR.hairline,
      }}>
        <input type="checkbox"
          checked={selected.size === filtered.length && filtered.length > 0}
          onChange={toggleAll}
          style={{ accentColor: TR.fg, width: 14, height: 14 }}
        />
        <span style={{ fontSize: 11, color: TR.fgMute, fontFamily: 'JetBrains Mono, monospace' }}>
          ВЫБРАТЬ ВСЕ ({filtered.length})
        </span>
        {selected.size > 0 && (
          <div style={{ marginLeft: 'auto', display: 'flex', gap: 6 }}>
            <button className="tr-action-btn tr-action-btn--primary" style={{ height: 26 }}>ОСТАВИТЬ 👍</button>
            <button className="tr-action-btn" style={{ height: 26 }}>УБРАТЬ 👎</button>
          </div>
        )}
      </div>

      <div>
        {filtered.length === 0 && (
          <div style={{
            padding: '32px 22px', textAlign: 'center',
            fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
            color: TR.fgMute, letterSpacing: 1,
          }}>МАРШРУТ ФОРМИРУЕТСЯ…</div>
        )}
        {filtered.map((p, i) => {
          const timeStr = formatTime(p.planned_start_time)
          return (
            <div key={p.poi.id} style={{
              display: 'flex', alignItems: 'center', gap: 10,
              padding: '10px 22px',
              borderBottom: i < filtered.length - 1 ? '1px solid ' + TR.hairline : 'none',
              background: selected.has(p.poi.id) ? 'rgba(185,255,61,0.08)' : 'transparent',
              transition: 'background 0.1s',
            }}>
              <input type="checkbox" checked={selected.has(p.poi.id)} onChange={() => toggle(p.poi.id)}
                style={{ accentColor: TR.fg, flexShrink: 0, width: 14, height: 14 }}/>
              <div style={{
                width: 8, height: 8, borderRadius: '50%', flexShrink: 0,
                background: DAY_COLORS[(p.day_number - 1) % DAY_COLORS.length],
              }}/>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{
                  fontFamily: 'Archivo, sans-serif', fontWeight: 800, fontSize: 13,
                  textTransform: 'uppercase', letterSpacing: '-0.01em',
                  overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                  color: TR.fg,
                }}>{p.poi.name}</div>
                <div style={{ fontSize: 10, color: TR.fgMute, fontFamily: 'JetBrains Mono, monospace', marginTop: 2 }}>
                  Д{p.day_number}{timeStr ? ` · ${timeStr}` : ''}
                </div>
              </div>
              <span style={{
                fontSize: 9, padding: '3px 8px',
                background: TR.surface2, borderRadius: 99,
                fontFamily: 'JetBrains Mono, monospace', color: TR.fgMute,
                flexShrink: 0,
              }}>{p.poi.is_indoor ? 'ЗАКРЫТОЕ' : 'НА УЛИЦЕ'}</span>
            </div>
          )
        })}
      </div>

      <div style={{
        padding: '12px 22px', borderTop: '1.5px solid ' + TR.hairlineSt,
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        background: TR.surface,
      }}>
        <span style={{ fontSize: 11, color: TR.fgMute, fontFamily: 'JetBrains Mono, monospace' }}>
          {filtered.length} ПОЗИЦИЙ
        </span>
        <span style={{ fontSize: 11, color: TR.fgMute, fontFamily: 'JetBrains Mono, monospace' }}>
          {filtered.filter(p => p.poi_status === 'main').length} ОСНОВНЫХ
        </span>
      </div>
    </div>
  )
}

// ── Budget tab ─────────────────────────────────────────────

function BudgetTab({ trip, poisByDay, numDays }) {
  const [openDay, setOpenDay] = useState(null)

  const dailyRate   = BUDGET_PER_DAY[trip?.budget ?? 'medium']
  const totalBudget = dailyRate * numDays
  const budgetLabel = { low: 'ECONOMY', medium: 'COMFORT', high: 'LUX' }[trip?.budget ?? 'medium']
  const totalPois   = Object.values(poisByDay).reduce((sum, d) => sum + d.length, 0)

  const getDayDate = (d) => {
    if (!trip?.start_date) return null
    const date = new Date(trip.start_date)
    date.setDate(date.getDate() + d - 1)
    return date
  }

  const formatDayLabel = (d) => {
    const date = getDayDate(d)
    if (!date) return null
    const wd = WEEKDAYS[(date.getDay() + 6) % 7]
    return `${wd}, ${date.getDate()} ${MONTHS_FULL[date.getMonth()]}`
  }

  if (totalPois === 0) {
    return (
      <div style={{ padding: '52px 22px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14 }}>
        <div style={{ fontSize: 36 }}>💸</div>
        <div style={{
          fontFamily: 'Archivo, sans-serif', fontWeight: 800, fontSize: 14,
          textTransform: 'uppercase', letterSpacing: '0.02em', color: TR.fg, textAlign: 'center',
        }}>Нет данных по бюджету</div>
        <div style={{
          fontFamily: 'JetBrains Mono, monospace', fontSize: 11, color: TR.fgMute,
          textAlign: 'center', lineHeight: 1.65, letterSpacing: 0.2, maxWidth: 270,
        }}>
          Бюджет рассчитывается на основе выбранных мест. Добавь места в маршрут чтобы увидеть примерную стоимость.
        </div>
      </div>
    )
  }

  return (
    <div style={{ padding: '16px 22px 48px', display: 'flex', flexDirection: 'column', gap: 12 }}>

      {/* ── Block 1: Total ── */}
      <div style={{
        background: TR.surface, borderRadius: 16,
        border: '1.5px solid ' + TR.hairline,
        padding: '20px 20px 18px',
        boxShadow: '0 1px 4px rgba(13,40,24,0.06)',
      }}>
        <div style={{
          fontFamily: 'JetBrains Mono, monospace', fontSize: 9,
          letterSpacing: '0.22em', color: TR.fgMute,
          textTransform: 'uppercase', marginBottom: 10,
        }}>ИТОГО НА ПОЕЗДКУ</div>

        <div style={{
          fontFamily: 'Archivo, sans-serif', fontWeight: 900, fontSize: 38,
          lineHeight: 1, letterSpacing: '-0.03em', color: TR.fg, marginBottom: 12,
        }}>
          ₽{totalBudget.toLocaleString('ru-RU')}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
          <span style={{
            background: TR.fg, color: TR.lime,
            fontFamily: 'Archivo, sans-serif', fontWeight: 800,
            fontSize: 10, letterSpacing: '0.08em',
            padding: '3px 9px', borderRadius: 6,
          }}>{budgetLabel}</span>
          <span style={{
            fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
            color: TR.fgMute, letterSpacing: 0.4,
          }}>{numDays} дней · {totalPois} мест</span>
        </div>
      </div>

      {/* ── Block 2: Categories ── */}
      <div style={{
        background: TR.surface, borderRadius: 16,
        border: '1.5px solid ' + TR.hairline,
        overflow: 'hidden',
        boxShadow: '0 1px 4px rgba(13,40,24,0.06)',
      }}>
        <div style={{ padding: '14px 20px 10px', borderBottom: '1px solid rgba(13,40,24,0.08)' }}>
          <div style={{
            fontFamily: 'JetBrains Mono, monospace', fontSize: 9,
            letterSpacing: '0.22em', color: TR.fgMute, textTransform: 'uppercase',
          }}>ПО КАТЕГОРИЯМ</div>
        </div>
        {BUDGET_CATS.map((cat, i) => (
          <div key={cat.label} style={{
            padding: '12px 20px',
            display: 'flex', alignItems: 'center', gap: 12,
            borderBottom: i < BUDGET_CATS.length - 1 ? '1px solid rgba(13,40,24,0.06)' : 'none',
          }}>
            <span style={{ fontSize: 17, lineHeight: 1, flexShrink: 0 }}>{cat.icon}</span>
            <span style={{
              flex: 1,
              fontFamily: 'Archivo, sans-serif', fontWeight: 600, fontSize: 13, color: TR.fg,
            }}>{cat.label}</span>
            <span style={{
              fontFamily: 'JetBrains Mono, monospace', fontSize: 12, color: TR.fg, fontWeight: 600,
            }}>~₽{Math.round(totalBudget * cat.pct / 100).toLocaleString('ru-RU')}</span>
          </div>
        ))}
      </div>

      {/* ── Block 3: Per day ── */}
      <div style={{
        background: TR.surface, borderRadius: 16,
        border: '1.5px solid ' + TR.hairline,
        overflow: 'hidden',
        boxShadow: '0 1px 4px rgba(13,40,24,0.06)',
      }}>
        <div style={{ padding: '14px 20px 10px', borderBottom: '1px solid rgba(13,40,24,0.08)' }}>
          <div style={{
            fontFamily: 'JetBrains Mono, monospace', fontSize: 9,
            letterSpacing: '0.22em', color: TR.fgMute, textTransform: 'uppercase',
          }}>ПО ДНЯМ</div>
        </div>

        {Array.from({ length: numDays }, (_, i) => i + 1).map((d, idx) => {
          const dayPois = poisByDay[d] ?? []
          const isOpen  = openDay === d
          const label   = formatDayLabel(d)
          const isLast  = idx === numDays - 1

          return (
            <div key={d}>
              <div
                onClick={() => setOpenDay(isOpen ? null : d)}
                style={{
                  padding: '13px 20px',
                  display: 'flex', alignItems: 'center', gap: 10,
                  cursor: dayPois.length > 0 ? 'pointer' : 'default',
                  borderBottom: !isLast || isOpen ? '1px solid rgba(13,40,24,0.06)' : 'none',
                  transition: 'background 0.12s',
                }}
                onMouseEnter={e => { if (dayPois.length > 0) e.currentTarget.style.background = 'rgba(13,40,24,0.03)' }}
                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
              >
                <div style={{ flex: 1, display: 'flex', alignItems: 'baseline', gap: 8, flexWrap: 'wrap' }}>
                  <span style={{
                    fontFamily: 'Archivo, sans-serif', fontWeight: 700,
                    fontSize: 13, color: TR.fg,
                  }}>День {d}</span>
                  {label && (
                    <span style={{
                      fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
                      color: TR.fgMute, letterSpacing: 0.2,
                    }}>{label}</span>
                  )}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
                  <span style={{
                    fontFamily: 'JetBrains Mono, monospace', fontSize: 12,
                    color: TR.fg, fontWeight: 600,
                  }}>~₽{dailyRate.toLocaleString('ru-RU')}</span>
                  {dayPois.length > 0 && (
                    <span style={{ fontSize: 8, color: TR.fgMute, lineHeight: 1 }}>
                      {isOpen ? '▲' : '▼'}
                    </span>
                  )}
                </div>
              </div>

              {isOpen && dayPois.length > 0 && (
                <div style={{ borderBottom: !isLast ? '1px solid rgba(13,40,24,0.06)' : 'none' }}>
                  {dayPois.map((p) => (
                    <div key={p.poi.id} style={{
                      padding: '9px 20px 9px 38px',
                      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                      borderTop: '1px solid rgba(13,40,24,0.05)',
                      background: 'rgba(13,40,24,0.02)',
                      gap: 10,
                    }}>
                      <span style={{ fontSize: 12, color: TR.fg, lineHeight: 1.3, flex: 1 }}>
                        {p.poi.name}
                      </span>
                      {p.budget_estimate && (
                        <span style={{
                          fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
                          color: TR.fgMute, flexShrink: 0,
                        }}>{p.budget_estimate}</span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ── Summary bottom sheet ───────────────────────────────────

function SummarySheet({ trip, onClose }) {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const raf = requestAnimationFrame(() => setVisible(true))
    return () => cancelAnimationFrame(raf)
  }, [])

  function close() {
    setVisible(false)
    setTimeout(onClose, 290)
  }

  return (
    <div
      onClick={close}
      style={{
        position: 'fixed', inset: 0, zIndex: 1100,
        display: 'flex', flexDirection: 'column', justifyContent: 'flex-end',
        background: visible ? 'rgba(13,40,24,0.4)' : 'rgba(13,40,24,0)',
        transition: 'background 0.25s ease',
      }}
    >
      <div
        onClick={e => e.stopPropagation()}
        style={{
          background: TR.bg,
          borderRadius: '16px 16px 0 0',
          maxHeight: '70vh', overflowY: 'auto',
          transform: visible ? 'translateY(0)' : 'translateY(100%)',
          transition: 'transform 0.28s cubic-bezier(0.32,0.72,0,1)',
          paddingBottom: 40,
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'center', paddingTop: 12, paddingBottom: 6 }}>
          <div style={{ width: 32, height: 4, borderRadius: 2, background: 'rgba(13,40,24,0.18)' }} />
        </div>

        <div style={{
          padding: '8px 22px 14px',
          borderBottom: '1px solid ' + TR.hairline,
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        }}>
          <div style={{
            fontFamily: 'Archivo, sans-serif', fontWeight: 900, fontSize: 16,
            letterSpacing: '-0.02em', color: TR.fg, textTransform: 'uppercase',
          }}>О маршруте</div>
          <button onClick={close} style={{
            background: 'none', border: 'none', cursor: 'pointer',
            fontSize: 20, color: TR.fgMute, lineHeight: 1, padding: 0,
          }}>×</button>
        </div>

        <div style={{ padding: '18px 22px' }}>
          {trip?.ai_summary ? (
            <div style={{ fontSize: 14, color: TR.fg, lineHeight: 1.65 }}>
              {trip.ai_summary}
            </div>
          ) : (
            <div style={{ fontSize: 13, color: TR.fgMute, fontFamily: 'JetBrains Mono, monospace' }}>
              Саммари недоступно
            </div>
          )}
          {trip?.total_budget_estimate && (
            <div style={{
              marginTop: 14, fontSize: 12, color: TR.fgMute,
              fontFamily: 'JetBrains Mono, monospace',
              padding: '8px 12px', background: TR.surface, borderRadius: 8,
            }}>
              Общий бюджет: {trip.total_budget_estimate}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// ── Main component ─────────────────────────────────────────

export default function TripPlanScreen() {
  const { id: tripId } = useParams()
  const navigate = useNavigate()
  const location = useLocation()

  const locState = location.state ?? {}
  const tripMeta = JSON.parse(localStorage.getItem('trip_meta') ?? '{}')
  const meta = tripMeta[tripId]
  const city      = locState.city      ?? meta?.city      ?? null
  const groupType = locState.groupType ?? meta?.groupType ?? null
  const rhythm    = locState.rhythm    ?? meta?.rhythm    ?? null

  const [activeTab, setActiveTab]   = useState(0)
  const [activeDay, setActiveDay]   = useState(1)

  useEffect(() => {
    if (activeTab === 1) setActiveDay(1)
  }, [activeTab])
  const [trip, setTrip]             = useState(null)
  const [loading, setLoading]       = useState(!!tripId)
  const [error, setError]           = useState(null)
  const [detailsPoi, setDetailsPoi]       = useState(null)
  const [replacingPoiId, setReplacingPoiId] = useState(null)

  // delete POI
  const [confirmDelete, setConfirmDelete] = useState(null) // { poiId, poiName }
  const [deleting, setDeleting]           = useState(false)

  // finalize day
  const [finalizedDays, setFinalizedDays] = useState(new Set())
  const [finalizingDay, setFinalizingDay] = useState(null)
  const [preFinalizePois, setPreFinalizePois] = useState({}) // { dayNum: pois[] }
  const [confirmUnfinalize, setConfirmUnfinalize] = useState(null) // dayNum

  // summary sheet
  const [showSummary, setShowSummary] = useState(false)

  // promoting alternative to main
  const [promotingPoiId, setPromotingPoiId] = useState(null)

  // share toast
  const [toast, setToast] = useState(null)

  const showToast = useCallback((msg) => {
    setToast(msg)
  }, [])

  async function handleDeletePoi() {
    if (!confirmDelete) return
    setDeleting(true)
    try {
      const res = await fetch(`${API_BASE}/trips/${tripId}/pois/${confirmDelete.poiId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${getToken()}` },
      })
      if (!res.ok) throw new Error(`Ошибка (${res.status})`)
      setTrip(prev => ({
        ...prev,
        pois: prev.pois.filter(p => p.poi.id !== confirmDelete.poiId),
      }))
      setConfirmDelete(null)
    } catch (e) {
      setError(e.message)
    } finally {
      setDeleting(false)
    }
  }

  async function handleFinalizeDay(dayNum) {
    const snapshotPois = trip?.pois ? [...trip.pois] : []
    setFinalizingDay(dayNum)
    try {
      console.log(`[finalize] POST /trips/${tripId}/days/${dayNum}/finalize/auto-main`)
      const res = await fetch(`${API_BASE}/trips/${tripId}/days/${dayNum}/finalize/auto-main`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${getToken()}` },
      })
      const body = await res.json()
      console.log('[finalize] response:', res.status, body)
      if (!res.ok) {
        showToast(`ОШИБКА: ${body?.detail ?? res.status}`)
        return
      }
      setPreFinalizePois(prev => ({ ...prev, [dayNum]: snapshotPois }))
      setTrip(body)
      setFinalizedDays(prev => new Set([...prev, dayNum]))
      showToast(`МАРШРУТ ДНЯ ${dayNum} УТВЕРЖДЁН ✓`)
    } catch (e) {
      console.error('[finalize] error:', e)
      showToast(`ОШИБКА: ${e.message}`)
    } finally {
      setFinalizingDay(null)
    }
  }

  function handleUnfinalizeDay(dayNum) {
    const original = preFinalizePois[dayNum]
    if (original) {
      setTrip(prev => ({ ...prev, pois: original }))
    }
    setFinalizedDays(prev => { const s = new Set(prev); s.delete(dayNum); return s })
    setPreFinalizePois(prev => { const n = { ...prev }; delete n[dayNum]; return n })
    setConfirmUnfinalize(null)
    showToast(`ДЕНЬ ${dayNum} ОТКРЫТ ДЛЯ РЕДАКТИРОВАНИЯ`)
  }

  async function handleSwapPoi(promotePoiId, demotePoiId = null) {
    setPromotingPoiId(promotePoiId)
    try {
      const res = await fetch(`${API_BASE}/trips/${tripId}/pois/swap`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${getToken()}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          promote_poi_id: promotePoiId,
          demote_poi_id: demotePoiId ?? null,
        }),
      })
      if (!res.ok) {
        const body = await res.json()
        showToast(`ОШИБКА: ${body?.detail ?? res.status}`)
        return
      }
      const updatedTrip = await res.json()
      setTrip(updatedTrip)
      setReplacingPoiId(null)
      showToast(demotePoiId ? 'МЕСТО ЗАМЕНЕНО ✓' : 'МЕСТО ДОБАВЛЕНО ✓')
    } catch (e) {
      showToast(`ОШИБКА: ${e.message}`)
    } finally {
      setPromotingPoiId(null)
    }
  }

  function handleShare() {
    const url = window.location.href
    navigator.clipboard.writeText(url).then(() => {
      showToast('ССЫЛКА СКОПИРОВАНА ✓')
    }).catch(() => {
      showToast('СКОПИРУЙ URL ВРУЧНУЮ')
    })
  }

  useEffect(() => {
    if (!tripId) { return }

    fetch(`${API_BASE}/trips/${tripId}`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    })
      .then(r => {
        if (!r.ok) throw new Error(`Ошибка загрузки (${r.status})`)
        return r.json()
      })
      .then(data => { setTrip(data); setLoading(false) })
      .catch(err => { setError(err.message); setLoading(false) })
  }, [tripId])

  const poisByDay = useMemo(() => {
    if (!trip?.pois) return {}
    return [...trip.pois]
      .filter(p => p.day_number != null)
      .sort((a, b) => (a.sequence_order ?? 999) - (b.sequence_order ?? 999))
      .reduce((acc, p) => {
        const d = p.day_number
        if (!acc[d]) acc[d] = []
        acc[d].push(p)
        return acc
      }, {})
  }, [trip])

  const numDays = useMemo(() => {
    if (trip?.start_date && trip?.end_date) return calcNumDays(trip.start_date, trip.end_date)
    const maxDay = Math.max(...Object.keys(poisByDay).map(Number), 1)
    return maxDay
  }, [trip, poisByDay])

  const allPois   = trip?.pois ?? []
  const dayPois   = poisByDay[activeDay] ?? []
  const color     = DAY_COLORS[(activeDay - 1) % DAY_COLORS.length]

  // Map gets all pois but additional ones are filtered out for finalized days
  const mapPois = useMemo(() => {
    return allPois.filter(p => {
      if (p.poi_status === 'additional' && finalizedDays.has(p.day_number)) return false
      return true
    })
  }, [allPois, finalizedDays])

  const cityName    = city?.n    ?? trip?.city_id ?? 'Маршрут'
  const cityCode    = city?.code ?? '—'
  const rhythmLabel = rhythm === 'slow' ? 'СПОКОЙНО' : rhythm === 'intense' ? 'НАСЫЩЕННО' : 'СБАЛАНСИРОВАННО'
  const groupLabel  = { solo: 'СОЛО', duo: 'ВДВОЁМ', family: 'СЕМЬЯ', friends: 'ДРУЗЬЯ', group: 'ГРУППА' }[groupType] ?? ''
  const budgetLabel = { low: 'ЭКОНОМНО', medium: 'КОМФОРТНО', high: 'ЛЮКС' }[trip?.budget ?? 'medium']

  const getDayDate = (d) => {
    if (!trip?.start_date) return null
    const date = new Date(trip.start_date)
    date.setDate(date.getDate() + d - 1)
    return date
  }

  const isDayToday = (d) => {
    const date = getDayDate(d)
    if (!date) return false
    const now = new Date()
    return date.getDate() === now.getDate() &&
      date.getMonth() === now.getMonth() &&
      date.getFullYear() === now.getFullYear()
  }

  const dayWeekday = (d) => {
    const date = getDayDate(d)
    if (date) return WEEKDAYS[(date.getDay() + 6) % 7]
    return WEEKDAYS[(d - 1) % 7]
  }

  const dayTooltip = (d) => {
    const date = getDayDate(d)
    if (!date) return undefined
    return `${WEEKDAYS_FULL[(date.getDay() + 6) % 7]}, ${date.getDate()} ${MONTHS_FULL[date.getMonth()]}`
  }

  return (
    <>

        {/* ── Top bar ── */}
        <div style={{
          height: 52, padding: '0 22px',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          flexShrink: 0,
        }}>
          <button className="tr-icon-btn"
            onClick={() => navigate('/dashboard/routes')}
            style={{ color: TR.fg, border: '1.5px solid ' + TR.fg }}>
            <ChevronLeft />
          </button>
          <div style={{
            fontFamily: 'Archivo, sans-serif',
            fontSize: 13, fontWeight: 800, letterSpacing: '0.04em', color: TR.fg,
          }}>
            ВАШ<span style={{ color: TR.fgMute }}>·</span>МАРШРУТ
          </div>
          <button className="tr-icon-btn"
            onClick={handleShare}
            title="Поделиться маршрутом"
            style={{ color: TR.fg, border: '1.5px solid ' + TR.hairlineSt }}>
            <ShareIcon />
          </button>
        </div>

        {/* ── Trip header ── */}
        <div style={{ padding: '4px 22px 14px' }}>
          <div style={{
            fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
            letterSpacing: '0.22em', color: TR.fgMute, marginBottom: 6,
            textTransform: 'uppercase',
          }}>
            {cityCode !== '—' ? `${cityCode} · ` : ''}{numDays} ДНЕЙ
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
            <h1 style={{
              fontFamily: 'Archivo, sans-serif',
              fontWeight: 900, fontSize: 42, lineHeight: 0.86,
              letterSpacing: '-0.04em', textTransform: 'uppercase',
              color: TR.fg, margin: 0, flex: 1,
            }}>
              {typeof cityName === 'string' ? cityName.toUpperCase() : 'МАРШРУТ'},<br/>
              {rhythmLabel === 'СПОКОЙНО' ? 'НЕ СПЕША' : rhythmLabel === 'НАСЫЩЕННО' ? 'АКТИВНО' : 'В РИТМЕ'}
            </h1>
            <button
              onClick={() => setShowSummary(true)}
              title="О маршруте"
              style={{
                flexShrink: 0, marginTop: 4,
                width: 22, height: 22, borderRadius: '50%',
                background: 'transparent',
                border: '1px solid ' + TR.fgMute,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                cursor: 'pointer', color: TR.fgMute,
                transition: 'border-color 0.15s, color 0.15s',
              }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = TR.fg; e.currentTarget.style.color = TR.fg }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = TR.fgMute; e.currentTarget.style.color = TR.fgMute }}
            >
              <InfoIcon />
            </button>
          </div>
          <div style={{
            marginTop: 10, display: 'flex', gap: 8, flexWrap: 'wrap',
            fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
            color: TR.fg, letterSpacing: 0.6,
          }}>
            {[groupLabel, rhythmLabel, budgetLabel].filter(Boolean).map(tag => (
              <span key={tag} style={{
                padding: '4px 10px',
                background: TR.surface, border: '1px solid ' + TR.hairline,
                borderRadius: 99,
              }}>{tag}</span>
            ))}
          </div>
        </div>

        {/* ── Tabs ── */}
        <div style={{
          margin: '0 22px', padding: 4,
          background: TR.surface2, borderRadius: 12,
          display: 'flex', gap: 2,
          border: '1px solid ' + TR.hairline,
        }}>
          {TABS.map((tab, i) => (
            <button key={tab} onClick={() => setActiveTab(i)} style={{
              flex: 1, height: 36,
              background: activeTab === i ? TR.bg : 'transparent',
              color: TR.fg, border: 'none', borderRadius: 9,
              fontFamily: 'Archivo, sans-serif',
              fontSize: 11, fontWeight: activeTab === i ? 800 : 600,
              letterSpacing: '0.06em',
              boxShadow: activeTab === i ? '0 1px 3px rgba(13,40,24,0.12)' : 'none',
              cursor: 'pointer', transition: 'all 0.15s ease',
            }}>{tab}</button>
          ))}
        </div>

        {/* ── Error ── */}
        {error && (
          <div style={{
            margin: '16px 22px', padding: '14px 16px',
            background: 'rgba(200,85,61,0.1)', border: '1.5px solid rgba(200,85,61,0.3)',
            borderRadius: 12, fontSize: 13, color: TR.warn,
          }}>
            {error}
          </div>
        )}

        {/* ── Tab content ── */}
        {activeTab === 2 && <BudgetTab trip={trip} poisByDay={poisByDay} numDays={numDays} />}
        {activeTab === 1 && (
          <TripMap
            allPois={mapPois}
            numDays={numDays}
            activeDay={activeDay}
            setActiveDay={setActiveDay}
            cityName={city?.n ?? null}
            finalizedDays={finalizedDays}
          />
        )}

        {activeTab === 0 && (
          <>
            {/* ── Day pills ── */}
            <div className="tr-day-scroll" style={{
              display: 'flex', gap: 4, padding: '14px 22px 4px', overflowX: 'auto',
            }}>
              {Array.from({ length: numDays }, (_, i) => i + 1).map(d => {
                const isSel = d === activeDay
                const dayDate = getDayDate(d)
                const isToday = isDayToday(d)
                const dateNum = dayDate ? dayDate.getDate() : d
                return (
                  <div key={d} onClick={() => setActiveDay(d)} title={dayTooltip(d)} style={{
                    flexShrink: 0, display: 'flex', flexDirection: 'column',
                    alignItems: 'center', gap: 4, padding: '8px 4px 6px',
                    minWidth: 44, cursor: 'pointer',
                  }}>
                    <div style={{
                      fontFamily: 'JetBrains Mono, monospace', fontSize: 9,
                      color: isSel ? TR.fg : TR.fgMute,
                      letterSpacing: 0.8, textTransform: 'uppercase',
                      fontWeight: isToday ? 700 : 400,
                    }}>{dayWeekday(d)}</div>
                    <div style={{
                      width: 34, height: 34, borderRadius: 9,
                      background: isSel ? TR.fg : 'transparent',
                      color: isSel ? TR.lime : TR.fg,
                      border: '1.5px solid ' + (isSel ? TR.fg : TR.hairline),
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontFamily: 'Archivo, sans-serif', fontSize: 15, fontWeight: 800,
                      boxShadow: isSel ? '2px 2px 0 0 ' + TR.fg : 'none',
                      transform: isSel ? 'translate(-1px,-1px)' : 'none',
                      transition: 'all 0.15s ease',
                    }}>
                      {dateNum}
                    </div>
                    <div style={{
                      width: 5, height: 5, borderRadius: '50%',
                      background: isToday ? TR.lime : 'transparent',
                      border: isToday ? '1.5px solid ' + TR.fg : 'none',
                      flexShrink: 0,
                      transition: 'background 0.15s',
                    }} />
                  </div>
                )
              })}
            </div>

            {/* ── Day rhythm chart ── */}
            <div style={{ padding: '4px 22px 0' }}>
              <div style={{
                padding: '14px 16px', background: TR.surface, borderRadius: 14,
                border: '1.5px solid ' + TR.hairline,
              }}>
                <div style={{
                  display: 'flex', justifyContent: 'space-between',
                  alignItems: 'baseline', marginBottom: 10,
                }}>
                  <div>
                    <div style={{
                      fontFamily: 'JetBrains Mono, monospace', fontSize: 9,
                      letterSpacing: '0.22em', color: TR.fgMute, textTransform: 'uppercase',
                    }}>ДЕНЬ {String(activeDay).padStart(2, '0')} · РИТМ</div>
                    <div style={{
                      fontFamily: 'Archivo, sans-serif',
                      fontSize: 18, fontWeight: 800, lineHeight: 1.05,
                      letterSpacing: '-0.02em', color: TR.fg, marginTop: 4,
                    }}>
                      {(() => {
                        const mainCount = dayPois.filter(p => p.poi_status === 'main').length
                        return mainCount > 0 ? `${mainCount} МЕСТ` : 'МАРШРУТ ФОРМИРУЕТСЯ'
                      })()}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: 11, color: TR.fgMute, marginTop: 2 }}>
                      {dayPois.filter(p => p.poi_status === 'main').length} событий
                    </div>
                  </div>
                </div>

                <RhythmChart day={activeDay} color={color} pois={dayPois} />

                <div style={{
                  display: 'flex', justifyContent: 'space-between',
                  marginTop: 6, fontFamily: 'JetBrains Mono, monospace',
                  fontSize: 9, letterSpacing: 0.6,
                }}>
                  <span style={{ color: TR.fgMute }}>УТРО · НАЧАЛО</span>
                  <span style={{ color, fontWeight: 700 }}>↑ АКТИВНЫЙ ПЕРИОД</span>
                  <span style={{ color: TR.fgMute }}>ВЕЧЕР · ФИНАЛ</span>
                </div>

                <div style={{ marginTop: 12 }}>
                  {finalizedDays.has(activeDay) ? (
                    <button
                      onClick={() => setConfirmUnfinalize(activeDay)}
                      style={{
                        width: '100%', height: 36,
                        background: TR.fg, border: '1.5px solid ' + TR.fg,
                        borderRadius: 10, cursor: 'pointer',
                        fontFamily: 'Archivo, sans-serif', fontWeight: 800, fontSize: 11,
                        letterSpacing: '0.05em', color: TR.lime,
                        display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
                        boxShadow: '2px 2px 0 0 rgba(13,40,24,0.3)',
                        transition: 'opacity 0.15s',
                      }}
                      onMouseEnter={e => e.currentTarget.style.opacity = '0.8'}
                      onMouseLeave={e => e.currentTarget.style.opacity = '1'}
                    >
                      <CheckIcon /> МАРШРУТ ФИНАЛИЗИРОВАН
                    </button>
                  ) : (
                    <button
                      onClick={() => handleFinalizeDay(activeDay)}
                      disabled={finalizingDay === activeDay}
                      style={{
                        width: '100%', height: 36,
                        background: 'transparent',
                        border: '1.5px solid ' + TR.hairlineSt,
                        borderRadius: 10, cursor: finalizingDay === activeDay ? 'wait' : 'pointer',
                        fontFamily: 'Archivo, sans-serif', fontWeight: 800, fontSize: 11,
                        letterSpacing: '0.05em', color: TR.fg,
                        opacity: finalizingDay === activeDay ? 0.5 : 1,
                        transition: 'border-color 0.15s',
                      }}
                      onMouseEnter={e => { if (finalizingDay !== activeDay) e.currentTarget.style.borderColor = TR.fg }}
                      onMouseLeave={e => e.currentTarget.style.borderColor = TR.hairlineSt}
                    >
                      {finalizingDay === activeDay ? 'ФИНАЛИЗИРУЕМ…' : 'ФИНАЛИЗИРОВАТЬ ПЛАН ДНЯ'}
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* ── POI timeline ── */}
            {loading ? (
              <SkeletonDay />
            ) : dayPois.length === 0 ? (
              <div style={{
                padding: '32px 22px', textAlign: 'center',
                fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
                color: TR.fgMute, letterSpacing: 1,
              }}>
                ДЕНЬ {String(activeDay).padStart(2, '0')} — НЕТ МЕСТ
              </div>
            ) : (
              <div style={{ padding: '18px 22px 32px' }}>
                {(() => {
                  const isFinalized = finalizedDays.has(activeDay)
                  const altPois  = isFinalized ? [] : dayPois.filter(p => p.poi_status === 'additional')
                  const mainPois = dayPois.filter(p => p.poi_status === 'main')
                  // Dot column center X, relative to each zone's wrapper (no outer padding here)
                  const DOT_X = 46 + 12 + 6  // 64px
                  return (
                    <>
                      {/* ── ZONE 1: Main POIs — lime vertical line ── */}
                      <div style={{ position: 'relative' }}>
                        {mainPois.length > 1 && (
                          <div style={{
                            position: 'absolute', left: DOT_X, top: 20, bottom: 8,
                            width: 1, background: '#b8ff4f', opacity: 0.6,
                            pointerEvents: 'none',
                          }} />
                        )}

                        {mainPois.map((p, i) => {
                          const startT = p.start_time ?? formatTime(p.planned_start_time)
                          const endT   = p.end_time ?? null
                          const isReplacing = !isFinalized && replacingPoiId === p.poi.id

                          return (
                            <div key={p.poi.id} style={{
                              paddingBottom: i < mainPois.length - 1 ? 18 : 0,
                            }}>
                              <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
                                {/* Time column */}
                                <div style={{ width: 46, flexShrink: 0, textAlign: 'right', paddingTop: 4 }}>
                                  <div style={{
                                    fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
                                    color: '#4d7a00', fontWeight: 700, letterSpacing: 0.4,
                                  }}>{startT ?? '—:—'}</div>
                                  {endT && (
                                    <div style={{
                                      fontFamily: 'JetBrains Mono, monospace', fontSize: 9,
                                      color: TR.fgMute, letterSpacing: 0.4, marginTop: 2,
                                    }}>{endT}</div>
                                  )}
                                </div>

                                {/* Lime dot */}
                                <div style={{
                                  width: 14, flexShrink: 0, paddingTop: 8,
                                  display: 'flex', justifyContent: 'center',
                                  position: 'relative', zIndex: 1,
                                }}>
                                  <div style={{
                                    width: 14, height: 14, borderRadius: '50%',
                                    background: '#b8ff4f', border: '2px solid ' + TR.bg,
                                    boxShadow: '0 0 0 1.5px #b8ff4f',
                                  }} />
                                </div>

                                {/* POI card */}
                                <div style={{ flex: 1, minWidth: 0 }}>
                                  <div style={{
                                    padding: '12px 14px',
                                    background: TR.surface,
                                    border: '1.5px solid ' + TR.fg,
                                    borderRadius: 12,
                                    boxShadow: '3px 3px 0 0 ' + TR.fg,
                                    transform: 'translate(-1px,-1px)',
                                  }}>
                                    <div style={{
                                      display: 'flex', justifyContent: 'space-between',
                                      alignItems: 'flex-start', gap: 8,
                                    }}>
                                      <div style={{
                                        fontFamily: 'Archivo, sans-serif',
                                        fontSize: 18, fontWeight: 800,
                                        lineHeight: 1.1, letterSpacing: '-0.02em',
                                        textTransform: 'uppercase', flex: 1, color: TR.fg,
                                      }}>{p.poi.name}</div>
                                      {p.budget_estimate && (
                                        <div style={{
                                          flexShrink: 0, fontFamily: 'JetBrains Mono, monospace',
                                          fontSize: 10, color: TR.fgMute,
                                          background: TR.surface2, padding: '2px 7px',
                                          borderRadius: 6, whiteSpace: 'nowrap',
                                        }}>💰 {p.budget_estimate}</div>
                                      )}
                                    </div>

                                    {p.ai_tip && (
                                      <div style={{
                                        marginTop: 6, fontSize: 12, color: TR.fgMute,
                                        lineHeight: 1.5, fontStyle: 'italic',
                                      }}>💡 {p.ai_tip}</div>
                                    )}

                                    {!p.ai_tip && p.poi.description && (
                                      <div style={{
                                        marginTop: 4, fontSize: 13, color: TR.fgMute, lineHeight: 1.4,
                                      }}>{p.poi.description}</div>
                                    )}

                                    <div style={{
                                      marginTop: 10, paddingTop: 10,
                                      borderTop: '1px dashed ' + TR.hairlineSt,
                                      display: 'flex', gap: 8, alignItems: 'center',
                                    }}>
                                      {!isFinalized && (
                                        <button
                                          className={`tr-action-btn${isReplacing ? ' tr-action-btn--primary' : ''}`}
                                          style={{ color: TR.fg }}
                                          onClick={() => setReplacingPoiId(isReplacing ? null : p.poi.id)}
                                        >
                                          {isReplacing ? 'ЗАКРЫТЬ ✕' : 'ЗАМЕНИТЬ'}
                                        </button>
                                      )}
                                      <button className="tr-action-btn" onClick={() => setDetailsPoi(p.poi)}>ДЕТАЛИ</button>
                                      <button
                                        onClick={() => setConfirmDelete({ poiId: p.poi.id, poiName: p.poi.name })}
                                        title="Удалить место"
                                        style={{
                                          marginLeft: 'auto',
                                          width: 28, height: 28, borderRadius: '50%',
                                          background: 'transparent', border: '1px solid ' + TR.hairline,
                                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                                          cursor: 'pointer', color: TR.fgMute,
                                          transition: 'border-color 0.15s, color 0.15s',
                                        }}
                                        onMouseEnter={e => { e.currentTarget.style.borderColor = TR.warn; e.currentTarget.style.color = TR.warn }}
                                        onMouseLeave={e => { e.currentTarget.style.borderColor = TR.hairline; e.currentTarget.style.color = TR.fgMute }}
                                      >
                                        <TrashIcon />
                                      </button>
                                    </div>
                                  </div>
                                </div>
                              </div>

                              {/* Replace strip — horizontal scroll of alt cards */}
                              {isReplacing && (
                                <div style={{ marginTop: 10, marginLeft: 46 + 12 + 14 + 12 }}>
                                  {altPois.length === 0 ? (
                                    <div style={{
                                      padding: '10px 14px', fontSize: 12, color: TR.fgMute,
                                      fontFamily: 'JetBrains Mono, monospace', letterSpacing: 0.6,
                                    }}>НЕТ АЛЬТЕРНАТИВ</div>
                                  ) : (
                                    <div style={{ display: 'flex', gap: 10, overflowX: 'auto', paddingBottom: 6 }}>
                                      {altPois.map(alt => {
                                        const isPromoting = promotingPoiId === alt.poi.id
                                        return (
                                          <div
                                            key={alt.poi.id}
                                            onClick={() => !isPromoting && handleSwapPoi(alt.poi.id, p.poi.id)}
                                            style={{
                                              flexShrink: 0, width: 160,
                                              background: TR.surface,
                                              border: '1.5px solid ' + TR.hairlineSt,
                                              borderRadius: 12, padding: '10px 12px',
                                              cursor: isPromoting ? 'wait' : 'pointer',
                                              opacity: isPromoting ? 0.5 : 1,
                                              transition: 'border-color 0.15s, opacity 0.15s',
                                            }}
                                            onMouseEnter={e => { if (!isPromoting) e.currentTarget.style.borderColor = TR.lime }}
                                            onMouseLeave={e => e.currentTarget.style.borderColor = TR.hairlineSt}
                                          >
                                            <div style={{
                                              fontFamily: 'Archivo, sans-serif', fontWeight: 800,
                                              fontSize: 13, letterSpacing: '-0.01em',
                                              textTransform: 'uppercase', color: TR.fg,
                                              lineHeight: 1.2, marginBottom: 6,
                                              overflow: 'hidden', display: '-webkit-box',
                                              WebkitLineClamp: 2, WebkitBoxOrient: 'vertical',
                                            }}>{alt.poi.name}</div>
                                            {alt.start_time && (
                                              <div style={{
                                                fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
                                                color: '#4d7a00', fontWeight: 700, marginBottom: 4,
                                              }}>{alt.start_time}{alt.end_time ? ` — ${alt.end_time}` : ''}</div>
                                            )}
                                            {alt.budget_estimate && (
                                              <div style={{
                                                fontSize: 10, color: TR.fgMute,
                                                fontFamily: 'JetBrains Mono, monospace',
                                                marginBottom: 4,
                                              }}>💰 {alt.budget_estimate}</div>
                                            )}
                                            {alt.ai_tip && (
                                              <div style={{
                                                fontSize: 11, color: TR.fgMute,
                                                lineHeight: 1.4, fontStyle: 'italic',
                                                overflow: 'hidden', display: '-webkit-box',
                                                WebkitLineClamp: 3, WebkitBoxOrient: 'vertical',
                                              }}>💡 {alt.ai_tip}</div>
                                            )}
                                            <div style={{
                                              marginTop: 8, fontSize: 10,
                                              fontFamily: 'JetBrains Mono, monospace',
                                              color: TR.fg, fontWeight: 700, letterSpacing: 0.5,
                                            }}>
                                              {isPromoting ? 'ЗАМЕНЯЕМ…' : '↩ ЗАМЕНИТЬ'}
                                            </div>
                                          </div>
                                        )
                                      })}
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          )
                        })}
                      </div>

                      {/* ── ZONE 2: Alternative POIs (hidden when finalized) ── */}
                      {!isFinalized && altPois.length > 0 && (
                        <>
                          {/* Divider separating main from alternatives */}
                          <div style={{
                            display: 'flex', alignItems: 'center', gap: 10,
                            margin: mainPois.length > 0 ? '20px 0 16px' : '0 0 16px',
                          }}>
                            <div style={{ flex: 1, height: 1, background: TR.hairlineSt }} />
                            <span style={{
                              fontFamily: 'JetBrains Mono, monospace', fontSize: 9,
                              letterSpacing: '0.18em', color: TR.fgMute, textTransform: 'uppercase',
                            }}>ЗАПАСНЫЕ ВАРИАНТЫ</span>
                            <div style={{ flex: 1, height: 1, background: TR.hairlineSt }} />
                          </div>

                          {/* Alt POIs as timeline rows with hollow grey pins */}
                          <div style={{ position: 'relative' }}>
                            {/* Grey dashed vertical line for Zone 2 */}
                            {altPois.length > 1 && (
                              <div style={{
                                position: 'absolute', left: DOT_X, top: 20, bottom: 8,
                                width: 0, borderLeft: '1.5px dashed rgba(13,40,24,0.18)',
                                pointerEvents: 'none',
                              }} />
                            )}

                            {altPois.map((alt, i) => {
                              const isPromoting = promotingPoiId === alt.poi.id
                              return (
                                <div key={alt.poi.id} style={{
                                  paddingBottom: i < altPois.length - 1 ? 14 : 0,
                                  opacity: isPromoting ? 0.5 : 1,
                                  transition: 'opacity 0.15s',
                                }}>
                                  <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
                                    {/* Empty time column */}
                                    <div style={{ width: 46, flexShrink: 0, textAlign: 'right', paddingTop: 6 }}>
                                      <div style={{
                                        fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
                                        color: 'rgba(13,40,24,0.25)', letterSpacing: 0.4,
                                      }}>—</div>
                                    </div>

                                    {/* Hollow grey pin */}
                                    <div style={{
                                      width: 14, flexShrink: 0, paddingTop: 8,
                                      display: 'flex', justifyContent: 'center',
                                      position: 'relative', zIndex: 1,
                                    }}>
                                      <div style={{
                                        width: 12, height: 12, borderRadius: '50%',
                                        background: TR.bg,
                                        border: '1.5px solid rgba(13,40,24,0.28)',
                                      }} />
                                    </div>

                                    {/* Alt POI card — muted, dashed border, no shadow */}
                                    <div style={{ flex: 1, minWidth: 0 }}>
                                      <div style={{
                                        padding: '10px 14px',
                                        background: 'rgba(13,40,24,0.03)',
                                        border: '1.5px dashed rgba(13,40,24,0.22)',
                                        borderRadius: 12,
                                      }}>
                                        <div style={{
                                          display: 'flex', justifyContent: 'space-between',
                                          alignItems: 'flex-start', gap: 8,
                                        }}>
                                          <div style={{
                                            fontFamily: 'Archivo, sans-serif',
                                            fontSize: 15, fontWeight: 700,
                                            lineHeight: 1.15, letterSpacing: '-0.015em',
                                            textTransform: 'uppercase', flex: 1,
                                            color: 'rgba(13,40,24,0.55)',
                                          }}>{alt.poi.name}</div>
                                          {alt.budget_estimate && (
                                            <div style={{
                                              flexShrink: 0, fontFamily: 'JetBrains Mono, monospace',
                                              fontSize: 10, color: 'rgba(13,40,24,0.4)',
                                              whiteSpace: 'nowrap',
                                            }}>{alt.budget_estimate}</div>
                                          )}
                                        </div>

                                        {alt.ai_tip && (
                                          <div style={{
                                            marginTop: 5, fontSize: 11,
                                            color: 'rgba(13,40,24,0.45)',
                                            lineHeight: 1.45, fontStyle: 'italic',
                                          }}>{alt.ai_tip}</div>
                                        )}

                                        <div style={{ marginTop: 10, display: 'flex', justifyContent: 'flex-end' }}>
                                          <button
                                            onClick={() => !isPromoting && handleSwapPoi(alt.poi.id, null)}
                                            disabled={isPromoting}
                                            style={{
                                              padding: '4px 12px',
                                              background: 'transparent',
                                              border: '1.5px solid ' + TR.lime,
                                              borderRadius: 99,
                                              cursor: isPromoting ? 'wait' : 'pointer',
                                              fontFamily: 'Archivo, sans-serif',
                                              fontWeight: 800, fontSize: 10,
                                              letterSpacing: '0.04em', color: TR.fg,
                                              transition: 'background 0.15s',
                                            }}
                                            onMouseEnter={e => { if (!isPromoting) e.currentTarget.style.background = TR.lime }}
                                            onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                                          >
                                            {isPromoting ? '…' : '+ ДОБАВИТЬ'}
                                          </button>
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              )
                            })}
                          </div>
                        </>
                      )}
                    </>
                  )
                })()}
              </div>
            )}
          </>
        )}

      {showSummary && (
        <SummarySheet trip={trip} onClose={() => setShowSummary(false)} />
      )}

      {detailsPoi && (
        <PlaceDetailsModal
          poi={detailsPoi}
          cityName={cityName}
          onClose={() => setDetailsPoi(null)}
        />
      )}

      {confirmDelete && (
        <ConfirmModal
          title="Удалить место?"
          body={`«${confirmDelete.poiName}» будет удалено из дня ${activeDay}.`}
          loading={deleting}
          loadingLabel="УДАЛЯЕМ…"
          onConfirm={handleDeletePoi}
          onCancel={() => setConfirmDelete(null)}
        />
      )}

      {confirmUnfinalize != null && (
        <ConfirmModal
          title="Вернуть к редактированию?"
          body={`День ${confirmUnfinalize} будет открыт для изменений. Запасные места вернутся в список.`}
          loading={false}
          confirmLabel="ВЕРНУТЬ"
          confirmColor={TR.fg}
          confirmTextColor={TR.lime}
          onConfirm={() => handleUnfinalizeDay(confirmUnfinalize)}
          onCancel={() => setConfirmUnfinalize(null)}
        />
      )}

      {toast && (
        <Toast message={toast} onDone={() => setToast(null)} />
      )}
    </>
  )
}
