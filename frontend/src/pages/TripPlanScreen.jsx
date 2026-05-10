import { useState, useEffect, useMemo } from 'react'
import './TripPlanScreen.css'

const API_BASE = 'http://localhost:8000'

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
const TABS = ['ДНИ', 'КАРТА', 'СПИСОК', 'БЮДЖЕТ']

const BUDGET_PER_DAY = { low: 50, medium: 120, high: 250 }
const BUDGET_CATS = [
  { label: 'Жильё',      pct: 40, color: '#4a7c59' },
  { label: 'Еда',        pct: 30, color: '#8a5a2a' },
  { label: 'Активности', pct: 20, color: '#5a6e9a' },
  { label: 'Транспорт',  pct: 10, color: '#6a4a8a' },
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

const StarIcon = ({ size = 18 }) => (
  <svg width={size} height={size} viewBox="0 0 16 16" fill="none">
    <path d="M8 1 L9 7 L15 8 L9 9 L8 15 L7 9 L1 8 L7 7 Z" fill="currentColor"/>
  </svg>
)

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

// ── Rhythm chart ───────────────────────────────────────────

function RhythmChart({ day, color }) {
  const gradId = `grad-${day}`
  return (
    <svg viewBox="0 0 280 62" style={{ width: '100%', height: 62, display: 'block' }}>
      <defs>
        <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.30"/>
          <stop offset="100%" stopColor={color} stopOpacity="0"/>
        </linearGradient>
      </defs>
      {[0, 1, 2, 3].map(i => (
        <line key={i}
          x1={i * 70 + 20} y1="0" x2={i * 70 + 20} y2="50"
          stroke={TR.hairlineSt} strokeWidth="1" strokeDasharray="2,3"
        />
      ))}
      <path d={CURVE_FILL} fill={`url(#${gradId})`}/>
      <path d={CURVE_PATH} fill="none" stroke={color} strokeWidth="2" strokeLinecap="round"/>
      {CURVE_DOTS.map((dot, i) => (
        <circle key={i} cx={dot.x} cy={dot.y} r={dot.peak ? 5 : 3.5}
          fill={color} stroke={TR.surface} strokeWidth="2"/>
      ))}
      {['08', '12', '16', '20'].map((h, i) => (
        <text key={h} x={i * 70 + 20} y="61" textAnchor="middle"
          fontFamily="JetBrains Mono, monospace" fontSize="8" fill={TR.fgMute}>{h}
        </text>
      ))}
    </svg>
  )
}

// ── Map tab ────────────────────────────────────────────────

function MapTab({ activeDay, setActiveDay, allPois, numDays }) {
  const [activePin, setActivePin] = useState(null)

  const bounds = useMemo(() => {
    const valid = allPois.filter(p => p.poi.lat && p.poi.lon && p.day_number)
    if (!valid.length) return null
    const lats = valid.map(p => p.poi.lat)
    const lons = valid.map(p => p.poi.lon)
    return {
      minLat: Math.min(...lats), maxLat: Math.max(...lats),
      minLon: Math.min(...lons), maxLon: Math.max(...lons),
    }
  }, [allPois])

  const pins = useMemo(() => {
    if (!bounds) return []
    const SVG_W = 252, SVG_H = 160, PAD = 20
    const latR = bounds.maxLat - bounds.minLat || 0.01
    const lonR = bounds.maxLon - bounds.minLon || 0.01
    return allPois
      .filter(p => p.poi.lat && p.poi.lon && p.day_number)
      .sort((a, b) => (a.sequence_order ?? 999) - (b.sequence_order ?? 999))
      .map(p => ({
        id: p.poi.id,
        day: p.day_number,
        name: p.poi.name,
        time: formatTime(p.planned_start_time),
        x: PAD + ((p.poi.lon - bounds.minLon) / lonR) * (SVG_W - 2 * PAD),
        y: PAD + ((bounds.maxLat - p.poi.lat) / latR) * (SVG_H - 2 * PAD),
      }))
  }, [allPois, bounds])

  const routes = useMemo(() => pins.reduce((acc, p) => {
    if (!acc[p.day]) acc[p.day] = []
    acc[p.day].push(p)
    return acc
  }, {}), [pins])

  const visiblePins = activeDay ? pins.filter(p => p.day === activeDay) : pins
  const activePinData = activePin ? pins.find(p => p.id === activePin) : null

  return (
    <div style={{ padding: '14px 22px 32px' }}>
      {/* Day filter */}
      <div style={{ display: 'flex', gap: 6, overflowX: 'auto', marginBottom: 12, paddingBottom: 2 }}>
        {[null, ...Array.from({ length: numDays }, (_, i) => i + 1)].map((d, i) => (
          <button key={i} onClick={() => { setActiveDay(d ?? 1); setActivePin(null) }} style={{
            flexShrink: 0, padding: '4px 12px',
            border: '1.5px solid ' + (d == null ? (activeDay ? TR.hairlineSt : TR.fg) : DAY_COLORS[(d - 1) % DAY_COLORS.length]),
            borderRadius: 99, fontSize: 11, fontFamily: 'JetBrains Mono, monospace',
            background: (d == null ? !activeDay : activeDay === d) ? TR.fg : 'transparent',
            color: (d == null ? !activeDay : activeDay === d) ? TR.lime : TR.fg,
            cursor: 'pointer', letterSpacing: 0.4,
          }}>
            {d == null ? 'ВСЕ' : `Д${d}`}
          </button>
        ))}
      </div>

      {/* Map SVG */}
      <div style={{
        background: '#dde8e0', borderRadius: 14,
        border: '1.5px solid ' + TR.hairlineSt, overflow: 'hidden', position: 'relative',
      }}>
        <svg viewBox="0 0 292 200" style={{ width: '100%', height: 200, display: 'block' }}>
          <rect width="292" height="200" fill="#dde8e0"/>
          {[20, 60, 100, 140, 180].map(y => (
            <line key={y} x1="0" y1={y} x2="292" y2={y + 8} stroke="#cdddd5" strokeWidth="4"/>
          ))}
          {[30, 80, 130, 180, 240].map(x => (
            <line key={x} x1={x} y1="0" x2={x + 4} y2="200" stroke="#cdddd5" strokeWidth="3"/>
          ))}

          {Object.entries(routes).map(([day, pts]) => {
            const d = parseInt(day)
            if (activeDay && activeDay !== d) return null
            const pathD = pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ')
            return <path key={day} d={pathD} fill="none"
              stroke={DAY_COLORS[(d - 1) % DAY_COLORS.length]} strokeWidth="2"
              strokeDasharray="5,3" opacity="0.7"/>
          })}

          {visiblePins.map(p => {
            const col = DAY_COLORS[(p.day - 1) % DAY_COLORS.length]
            const isActive = activePin === p.id
            return (
              <g key={p.id} onClick={() => setActivePin(isActive ? null : p.id)} style={{ cursor: 'pointer' }}>
                <circle cx={p.x} cy={p.y} r={isActive ? 10 : 7} fill={col} stroke="#fff" strokeWidth="2"/>
                <text x={p.x} y={p.y + 1} textAnchor="middle" dominantBaseline="middle"
                  fontSize="8" fill="white" fontWeight="700" fontFamily="monospace">{p.day}</text>
              </g>
            )
          })}

          {pins.length === 0 && (
            <text x="146" y="100" textAnchor="middle"
              fontFamily="JetBrains Mono, monospace" fontSize="11" fill="#7a9a8a">
              НЕТ ДАННЫХ КООРДИНАТ
            </text>
          )}
        </svg>
        <div style={{
          position: 'absolute', bottom: 8, left: 10,
          background: 'rgba(255,255,255,0.88)', borderRadius: 6, padding: '3px 8px',
          fontSize: 10, fontFamily: 'JetBrains Mono, monospace', color: TR.fgMute,
        }}>● Нажми на пин → детали</div>
      </div>

      {activePinData && (
        <div style={{
          marginTop: 12, padding: '14px 16px',
          background: TR.surface, borderRadius: 14,
          border: '1.5px solid ' + DAY_COLORS[(activePinData.day - 1) % DAY_COLORS.length],
          boxShadow: '3px 3px 0 0 ' + DAY_COLORS[(activePinData.day - 1) % DAY_COLORS.length],
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <div style={{ fontFamily: 'Archivo, sans-serif', fontWeight: 800, fontSize: 16, textTransform: 'uppercase', color: TR.fg }}>
                {activePinData.name}
              </div>
              <div style={{ fontSize: 12, color: TR.fgMute, fontFamily: 'JetBrains Mono, monospace', marginTop: 4 }}>
                ДЕНЬ {activePinData.day}{activePinData.time ? ` · ${activePinData.time}` : ''}
              </div>
            </div>
            <button onClick={() => setActivePin(null)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: TR.fgMute, fontSize: 16 }}>✕</button>
          </div>
        </div>
      )}

      <div style={{ marginTop: 12, display: 'flex', gap: 8 }}>
        <button className="tr-action-btn" style={{ flex: 1, height: 36 }}>PDF</button>
        <button className="tr-action-btn" style={{ flex: 1, height: 36 }}>ССЫЛКА</button>
        <button className="tr-action-btn tr-action-btn--primary" style={{ flex: 1, height: 36 }}>СОХРАНИТЬ</button>
      </div>
    </div>
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
  const [open, setOpen] = useState(false)

  const dailyRate = BUDGET_PER_DAY[trip?.budget ?? 'medium']
  const totalBudget = dailyRate * numDays

  const sparkVals = Array.from({ length: numDays }, (_, i) => {
    const dayPois = (poisByDay[i + 1] ?? []).length
    return Math.max(0.3, dayPois / Math.max(...Object.values(poisByDay).map(d => d.length), 1))
  })

  return (
    <div>
      <div onClick={() => setOpen(!open)} style={{
        background: TR.fg, color: TR.bg,
        padding: '12px 22px', cursor: 'pointer',
        borderBottom: '1.5px solid ' + TR.fg,
        position: 'sticky', top: 0, zIndex: 10,
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
          <span style={{ fontFamily: 'Archivo, sans-serif', fontWeight: 900, fontSize: 15, letterSpacing: '-0.01em' }}>
            ИТОГО: ~{totalBudget.toLocaleString()} €
          </span>
          <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10, opacity: 0.6 }}>
            {open ? '▲ СВЕРНУТЬ' : '▼ ДЕТАЛИ'}
          </span>
        </div>

        <svg viewBox={`0 0 ${Math.max(280, numDays * 38 + 4)} 24`} style={{ width: '100%', height: 24, display: 'block', marginBottom: 6 }}>
          {sparkVals.map((v, i) => {
            const barH = Math.round(v * 18)
            return (
              <rect key={i} x={i * 38 + 4} y={24 - barH} width={30} height={barH}
                fill={TR.lime} opacity="0.7" rx="2"/>
            )
          })}
          {sparkVals.map((_, i) => (
            <text key={i} x={i * 38 + 19} y={23} textAnchor="middle" fontSize="7"
              fontFamily="monospace" fill={TR.bg} opacity="0.5">Д{i + 1}</text>
          ))}
        </svg>

        <div style={{ display: 'flex', height: 6, borderRadius: 3, overflow: 'hidden', marginBottom: 4 }}>
          {BUDGET_CATS.map(c => (
            <div key={c.label} style={{ width: `${c.pct}%`, background: c.color }}/>
          ))}
        </div>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          {BUDGET_CATS.map(c => (
            <span key={c.label} style={{
              fontFamily: 'JetBrains Mono, monospace', fontSize: 9, opacity: 0.7, color: TR.bg,
            }}>■ {c.label} {c.pct}%</span>
          ))}
        </div>
      </div>

      {open && (
        <div style={{ background: TR.surface, padding: '16px 22px', borderBottom: '1.5px solid ' + TR.hairlineSt }}>
          <div style={{
            fontFamily: 'JetBrains Mono, monospace', fontSize: 9, letterSpacing: '0.2em',
            color: TR.fgMute, textTransform: 'uppercase', marginBottom: 14,
          }}>УРОВЕНЬ БЮДЖЕТА · {(trip?.budget ?? 'medium').toUpperCase()}</div>

          <div style={{
            fontFamily: 'JetBrains Mono, monospace', fontSize: 9, letterSpacing: '0.2em',
            color: TR.fgMute, textTransform: 'uppercase', marginBottom: 10,
          }}>РАСПРЕДЕЛЕНИЕ</div>
          {BUDGET_CATS.map(c => (
            <div key={c.label} style={{ marginBottom: 10 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                <span style={{ fontSize: 12, color: TR.fg, fontWeight: 600 }}>{c.label}</span>
                <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 11, color: TR.fg }}>
                  ~{Math.round(totalBudget * c.pct / 100)} € · {c.pct}%
                </span>
              </div>
              <div style={{ height: 6, background: TR.surface2, borderRadius: 3, overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${c.pct}%`, background: c.color, borderRadius: 3 }}/>
              </div>
            </div>
          ))}
        </div>
      )}

      <div style={{ padding: '16px 22px 32px', display: 'flex', flexDirection: 'column', gap: 10 }}>
        <div style={{
          fontFamily: 'JetBrains Mono, monospace', fontSize: 9, letterSpacing: '0.2em',
          color: TR.fgMute, textTransform: 'uppercase', marginBottom: 4,
        }}>ПО ДНЯМ</div>
        {Array.from({ length: numDays }, (_, i) => i + 1).map(d => {
          const dayPois = poisByDay[d] ?? []
          if (dayPois.length === 0) return null
          return (
            <div key={d} style={{
              background: TR.surface, borderRadius: 12,
              border: '1.5px solid ' + TR.hairline, overflow: 'hidden',
            }}>
              <div style={{
                background: TR.fg, color: TR.lime,
                padding: '8px 14px', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              }}>
                <span style={{ fontFamily: 'Archivo, sans-serif', fontWeight: 800, fontSize: 12, letterSpacing: '0.03em' }}>
                  ДЕНЬ {String(d).padStart(2, '0')}
                </span>
                <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 12, fontWeight: 700 }}>
                  ~{dailyRate} €
                </span>
              </div>
              {dayPois.map((p, j) => {
                const t = formatTime(p.planned_start_time)
                return (
                  <div key={p.poi.id} style={{
                    padding: '8px 14px', display: 'flex', justifyContent: 'space-between',
                    borderBottom: j < dayPois.length - 1 ? '1px solid ' + TR.hairline : 'none',
                    fontSize: 12, color: TR.fg,
                  }}>
                    <span>{t ? `${t} — ` : ''}{p.poi.name}</span>
                  </div>
                )
              })}
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ── Main component ─────────────────────────────────────────

export default function TripPlanScreen({ city, groupType, rhythm, onBack }) {
  const [activeTab, setActiveTab]   = useState(0)
  const [activeDay, setActiveDay]   = useState(1)
  const [trip, setTrip]             = useState(null)
  const [loading, setLoading]       = useState(() => !!localStorage.getItem('current_trip_id'))
  const [error, setError]           = useState(null)

  useEffect(() => {
    const tripId = localStorage.getItem('current_trip_id')
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
  }, [])

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

  const cityName    = city?.n    ?? trip?.city_id ?? 'Маршрут'
  const cityCode    = city?.code ?? '—'
  const rhythmLabel = rhythm === 'slow' ? 'СПОКОЙНО' : rhythm === 'intense' ? 'НАСЫЩЕННО' : 'СБАЛАНСИРОВАННО'
  const groupLabel  = { solo: 'СОЛО', duo: 'ВДВОЁМ', family: 'СЕМЬЯ', friends: 'ДРУЗЬЯ', group: 'ГРУППА' }[groupType] ?? ''
  const budgetLabel = { low: 'ЭКОНОМНО', medium: 'КОМФОРТНО', high: 'ЛЮКС' }[trip?.budget ?? 'medium']

  const dayWeekday = (d) => {
    if (trip?.start_date) {
      const date = new Date(trip.start_date)
      date.setDate(date.getDate() + d - 1)
      return WEEKDAYS[(date.getDay() + 6) % 7]
    }
    return WEEKDAYS[(d - 1) % 7]
  }

  return (
    <div className="tr-app">
      <div className="tr-phone">

        {/* ── Top bar ── */}
        <div style={{
          height: 52, padding: '0 22px',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          flexShrink: 0,
        }}>
          <button className="tr-icon-btn" onClick={onBack}
            style={{ color: TR.fg, border: '1.5px solid ' + TR.fg }}>
            <ChevronLeft />
          </button>
          <div style={{
            fontFamily: 'Archivo, sans-serif',
            fontSize: 13, fontWeight: 800, letterSpacing: '0.04em', color: TR.fg,
          }}>
            ВАШ<span style={{ color: TR.fgMute }}>·</span>МАРШРУТ
          </div>
          <div style={{ width: 38 }} />
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
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 10 }}>
            <h1 style={{
              fontFamily: 'Archivo, sans-serif',
              fontWeight: 900, fontSize: 42, lineHeight: 0.86,
              letterSpacing: '-0.04em', textTransform: 'uppercase',
              color: TR.fg, margin: 0,
            }}>
              {typeof cityName === 'string' ? cityName.toUpperCase() : 'МАРШРУТ'},<br/>
              {rhythmLabel === 'СПОКОЙНО' ? 'НЕ СПЕША' : rhythmLabel === 'НАСЫЩЕННО' ? 'АКТИВНО' : 'В РИТМЕ'}
            </h1>
            <button style={{
              width: 46, height: 46, borderRadius: '50%',
              background: TR.lime, color: TR.fg,
              border: '1.5px solid ' + TR.fg,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '2px 2px 0 0 ' + TR.fg,
              cursor: 'pointer', flexShrink: 0,
            }}>
              <StarIcon size={18} />
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
        {activeTab === 2 && <ListTab allPois={allPois} />}
        {activeTab === 3 && <BudgetTab trip={trip} poisByDay={poisByDay} numDays={numDays} />}
        {activeTab === 1 && <MapTab activeDay={activeDay} setActiveDay={setActiveDay} allPois={allPois} numDays={numDays} />}

        {activeTab === 0 && (
          <>
            {/* ── Day pills ── */}
            <div className="tr-day-scroll" style={{
              display: 'flex', gap: 4, padding: '14px 22px 4px', overflowX: 'auto',
            }}>
              {Array.from({ length: numDays }, (_, i) => i + 1).map(d => {
                const isSel = d === activeDay
                return (
                  <div key={d} onClick={() => setActiveDay(d)} style={{
                    flexShrink: 0, display: 'flex', flexDirection: 'column',
                    alignItems: 'center', gap: 5, padding: '8px 4px',
                    minWidth: 38, cursor: 'pointer',
                  }}>
                    <div style={{
                      fontFamily: 'JetBrains Mono, monospace', fontSize: 9,
                      color: TR.fgMute, letterSpacing: 0.6,
                    }}>{dayWeekday(d)}</div>
                    <div style={{
                      width: 32, height: 32, borderRadius: 8,
                      background: isSel ? TR.fg : 'transparent',
                      color: isSel ? TR.lime : TR.fg,
                      border: '1.5px solid ' + (isSel ? TR.fg : TR.hairline),
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontFamily: 'Archivo, sans-serif', fontSize: 14, fontWeight: 800,
                      boxShadow: isSel ? '2px 2px 0 0 ' + TR.fg : 'none',
                      transform: isSel ? 'translate(-1px,-1px)' : 'none',
                      transition: 'all 0.15s ease',
                    }}>
                      {String(d).padStart(2, '0')}
                    </div>
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
                      {dayPois.length > 0 ? `${dayPois.length} МЕСТ` : 'МАРШРУТ ФОРМИРУЕТСЯ'}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: 11, color: TR.fgMute, marginTop: 2 }}>
                      {dayPois.length} событий
                    </div>
                  </div>
                </div>

                <RhythmChart day={activeDay} color={color} />

                <div style={{
                  display: 'flex', justifyContent: 'space-between',
                  marginTop: 6, fontFamily: 'JetBrains Mono, monospace',
                  fontSize: 9, letterSpacing: 0.6,
                }}>
                  <span style={{ color: TR.fgMute }}>УТРО · НАЧАЛО</span>
                  <span style={{ color, fontWeight: 700 }}>↑ АКТИВНЫЙ ПЕРИОД</span>
                  <span style={{ color: TR.fgMute }}>ВЕЧЕР · ФИНАЛ</span>
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
              <div style={{ padding: '18px 22px 32px', position: 'relative' }}>
                <div style={{
                  position: 'absolute',
                  left: 22 + 46 + 12 + 6,
                  top: 24, bottom: 24,
                  width: 1, background: TR.hairlineSt,
                }} />

                {dayPois.map((p, i) => {
                  const isMain = p.poi_status === 'main'
                  const timeStr = formatTime(p.planned_start_time)

                  return (
                    <div key={p.poi.id} style={{
                      display: 'flex', gap: 12, alignItems: 'flex-start',
                      paddingBottom: i < dayPois.length - 1 ? 18 : 0,
                    }}>
                      {/* Time column */}
                      <div style={{ width: 46, flexShrink: 0, textAlign: 'right', paddingTop: 4 }}>
                        <div style={{
                          fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
                          color: TR.fg, fontWeight: 700, letterSpacing: 0.4,
                        }}>{timeStr ?? '—:—'}</div>
                        <div style={{
                          fontFamily: 'JetBrains Mono, monospace', fontSize: 9,
                          color: TR.fgMute, letterSpacing: 0.6, marginTop: 2,
                        }}>{p.poi.is_indoor ? 'ЗАКРЫТОЕ' : 'НА УЛИЦЕ'}</div>
                      </div>

                      {/* Timeline dot */}
                      <div style={{
                        width: 14, flexShrink: 0, paddingTop: 8,
                        display: 'flex', justifyContent: 'center',
                        position: 'relative', zIndex: 1,
                      }}>
                        {isMain ? (
                          <div style={{
                            width: 14, height: 14, borderRadius: '50%',
                            background: color, border: '2px solid ' + TR.bg,
                            boxShadow: '0 0 0 1.5px ' + color,
                          }} />
                        ) : (
                          <div style={{
                            width: 10, height: 10, borderRadius: '50%',
                            background: TR.bg, border: '1.8px solid ' + color,
                          }} />
                        )}
                      </div>

                      {/* POI card */}
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{
                          padding: isMain ? '12px 14px' : '6px 0',
                          background: isMain ? TR.surface : 'transparent',
                          border: isMain ? '1.5px solid ' + TR.fg : 'none',
                          borderRadius: isMain ? 12 : 0,
                          boxShadow: isMain ? '3px 3px 0 0 ' + TR.fg : 'none',
                          transform: isMain ? 'translate(-1px,-1px)' : 'none',
                        }}>
                          <div style={{
                            display: 'flex', justifyContent: 'space-between',
                            alignItems: 'baseline', gap: 8,
                          }}>
                            <div style={{
                              fontFamily: 'Archivo, sans-serif',
                              fontSize: isMain ? 18 : 15, fontWeight: 800,
                              lineHeight: 1.1, letterSpacing: '-0.02em',
                              textTransform: 'uppercase', flex: 1, color: TR.fg,
                            }}>{p.poi.name}</div>
                          </div>

                          {p.poi.description && (
                            <div style={{
                              marginTop: 4, fontSize: 13, color: TR.fgMute, lineHeight: 1.4,
                              fontStyle: isMain ? 'normal' : 'italic',
                            }}>{p.poi.description}</div>
                          )}

                          <div style={{
                            marginTop: 6, fontFamily: 'JetBrains Mono, monospace',
                            fontSize: 9, color: TR.fgMute, letterSpacing: 1,
                          }}>↳ {p.poi.is_indoor ? 'ЗАКРЫТОЕ МЕСТО' : 'НА ОТКРЫТОМ ВОЗДУХЕ'}</div>

                          {isMain && (
                            <div style={{
                              marginTop: 10, paddingTop: 10,
                              borderTop: '1px dashed ' + TR.hairlineSt,
                              display: 'flex', gap: 8,
                            }}>
                              <button className="tr-action-btn tr-action-btn--primary">ЗАМЕНИТЬ</button>
                              <button className="tr-action-btn">ДЕТАЛИ</button>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </>
        )}

      </div>
    </div>
  )
}
