import { useState } from 'react'
import './OnboardingDates.css'

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

const DURATION_OPTS = [3, 5, 7, 10, 14, 21]

const MONTH_NAMES = [
  'Январь','Февраль','Март','Апрель','Май','Июнь',
  'Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь',
]
const DAY_NAMES = ['ПН','ВТ','СР','ЧТ','ПТ','СБ','ВС']

function buildCalendar(year, month) {
  const firstDay = new Date(year, month, 1)
  // Monday-first: 0=Mon…6=Sun
  const startDow = (firstDay.getDay() + 6) % 7
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const cells = []
  for (let i = 0; i < startDow; i++) cells.push(null)
  for (let d = 1; d <= daysInMonth; d++) cells.push(d)
  while (cells.length % 7 !== 0) cells.push(null)
  return cells
}

const ChevronLeft = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
    <path d="M10 3 L5 8 L10 13" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
)
const ChevronRight = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
    <path d="M6 3 L11 8 L6 13" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
)
const ArrowRight = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
    <path d="M3 8 H13 M9 4 L13 8 L9 12" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
)

const today = new Date()

export default function OnboardingDates({ city, groupType, onBack, onContinue }) {
  const [viewYear, setViewYear]   = useState(today.getFullYear())
  const [viewMonth, setViewMonth] = useState(today.getMonth())
  const [startDay, setStartDay]   = useState(null) // { year, month, day }
  const [duration, setDuration]   = useState(7)

  const cityName  = city?.n  ?? 'Рим'
  const groupLabel = { solo:'СОЛО', duo:'ВДВОЁМ', family:'СЕМЬЯ', friends:'ДРУЗЬЯ', group:'ГРУППА' }[groupType] ?? 'ВДВОЁМ'

  const cells = buildCalendar(viewYear, viewMonth)

  const prevMonth = () => {
    if (viewMonth === 0) { setViewMonth(11); setViewYear(y => y - 1) }
    else setViewMonth(m => m - 1)
  }
  const nextMonth = () => {
    if (viewMonth === 11) { setViewMonth(0); setViewYear(y => y + 1) }
    else setViewMonth(m => m + 1)
  }

  const isPast = (day) => {
    if (!day) return false
    const d = new Date(viewYear, viewMonth, day)
    d.setHours(0,0,0,0)
    const t = new Date(); t.setHours(0,0,0,0)
    return d < t
  }

  const isSel = (day) =>
    day && startDay &&
    startDay.year === viewYear &&
    startDay.month === viewMonth &&
    startDay.day === day

  const isInRange = (day) => {
    if (!day || !startDay) return false
    const d = new Date(viewYear, viewMonth, day)
    const s = new Date(startDay.year, startDay.month, startDay.day)
    const e = new Date(s); e.setDate(e.getDate() + duration - 1)
    return d > s && d <= e
  }

  const endDateLabel = () => {
    if (!startDay) return null
    const s = new Date(startDay.year, startDay.month, startDay.day)
    s.setDate(s.getDate() + duration - 1)
    return `${s.getDate()} ${MONTH_NAMES[s.getMonth()]}`
  }

  const startLabel = startDay
    ? `${startDay.day} ${MONTH_NAMES[startDay.month]} ${startDay.year}`
    : null

  const canContinue = !!startDay

  const handleContinue = () => {
    onContinue?.({
      startDay,
      duration,
      label: startLabel,
      endLabel: endDateLabel(),
    })
  }

  return (
    <div className="tr-app">
      <div className="tr-phone">

        {/* ── Top bar ── */}
        <div style={{
          height: 52, padding: '0 22px',
          display: 'flex', alignItems: 'center', gap: 14, flexShrink: 0,
        }}>
          <button className="tr-icon-btn" onClick={onBack}
            style={{ color: TR.fg, border: '1.5px solid ' + TR.fg }}>
            <ChevronLeft />
          </button>
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ flex: 1, height: 4, background: TR.surface2, borderRadius: 2, overflow: 'hidden' }}>
              <div style={{ width: '33%', height: '100%', background: TR.fg }} />
            </div>
            <div style={{
              fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
              letterSpacing: '0.18em', color: TR.fg, fontWeight: 600,
            }}>02 / 06</div>
          </div>
        </div>

        {/* ── Ledger ── */}
        <div style={{
          margin: '8px 22px 12px', padding: '10px 14px',
          border: '1px solid ' + TR.hairline, borderRadius: 10,
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
          color: TR.fgMute, letterSpacing: 1, textTransform: 'uppercase',
        }}>
          <span>{cityName.toUpperCase()} · {groupLabel}</span>
          <span>ЧЕРНОВИК 25%</span>
        </div>

        {/* ── Hero ── */}
        <div style={{ padding: '4px 22px 14px' }}>
          <h1 style={{
            fontFamily: 'Archivo, sans-serif', fontWeight: 900, fontSize: 56,
            lineHeight: 0.86, letterSpacing: '-0.04em', textTransform: 'uppercase',
            color: TR.fg, margin: 0,
          }}>
            КОГДА<br/>ЕДЕМ?
          </h1>
        </div>

        <div style={{
          padding: '0 22px 20px', fontSize: 14.5, lineHeight: 1.5,
          color: TR.fgMute, maxWidth: 300,
        }}>
          Выберите дату вылета — подберём открытые музеи, рынки и фестивали.
        </div>

        {/* ── Calendar ── */}
        <div style={{ padding: '0 22px' }}>
          <div style={{
            background: TR.surface, borderRadius: 16,
            border: '1.5px solid ' + TR.hairline, overflow: 'hidden',
          }}>
            {/* Month nav */}
            <div style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '14px 16px 10px',
              borderBottom: '1px solid ' + TR.hairline,
            }}>
              <button onClick={prevMonth} style={{
                width: 32, height: 32, borderRadius: 8,
                background: 'transparent', border: '1.5px solid ' + TR.hairlineSt,
                color: TR.fg, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}><ChevronLeft /></button>

              <div style={{
                fontFamily: 'Archivo, sans-serif', fontWeight: 900, fontSize: 15,
                letterSpacing: '-0.01em', color: TR.fg, textTransform: 'uppercase',
              }}>
                {MONTH_NAMES[viewMonth]} {viewYear}
              </div>

              <button onClick={nextMonth} style={{
                width: 32, height: 32, borderRadius: 8,
                background: 'transparent', border: '1.5px solid ' + TR.hairlineSt,
                color: TR.fg, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}><ChevronRight /></button>
            </div>

            {/* Day headers */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', padding: '8px 10px 4px' }}>
              {DAY_NAMES.map(d => (
                <div key={d} style={{
                  textAlign: 'center', fontFamily: 'JetBrains Mono, monospace',
                  fontSize: 9, color: TR.fgMute, letterSpacing: 1, padding: '2px 0',
                }}>{d}</div>
              ))}
            </div>

            {/* Day grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', padding: '0 10px 12px', gap: 2 }}>
              {cells.map((day, idx) => {
                const past = isPast(day)
                const sel  = isSel(day)
                const inRange = isInRange(day)
                return (
                  <div key={idx} onClick={() => {
                    if (!day || past) return
                    setStartDay({ year: viewYear, month: viewMonth, day })
                  }} style={{
                    height: 34, borderRadius: 8,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontFamily: 'Archivo, sans-serif', fontWeight: sel ? 900 : 600,
                    fontSize: 13,
                    background: sel ? TR.fg : inRange ? 'rgba(185,255,61,0.22)' : 'transparent',
                    color: sel ? TR.lime : past ? TR.hairlineSt : TR.fg,
                    border: sel ? '1.5px solid ' + TR.fg : 'none',
                    cursor: !day || past ? 'default' : 'pointer',
                    transition: 'background 0.1s',
                  }}>
                    {day ?? ''}
                  </div>
                )
              })}
            </div>
          </div>
        </div>

        {/* ── Duration ── */}
        <div style={{ padding: '20px 22px 0' }}>
          <div style={{
            fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
            letterSpacing: '0.22em', textTransform: 'uppercase',
            color: TR.fg, fontWeight: 600, marginBottom: 10,
          }}>КОЛИЧЕСТВО ДНЕЙ</div>

          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {DURATION_OPTS.map(n => {
              const sel = n === duration
              return (
                <button key={n} onClick={() => setDuration(n)} style={{
                  height: 44, minWidth: 56, padding: '0 14px',
                  borderRadius: 10, cursor: 'pointer',
                  background: sel ? TR.fg : TR.surface,
                  color: sel ? TR.lime : TR.fg,
                  border: '1.5px solid ' + (sel ? TR.fg : TR.hairlineSt),
                  boxShadow: sel ? '3px 3px 0 0 ' + TR.fg : 'none',
                  transform: sel ? 'translate(-1px,-1px)' : 'none',
                  fontFamily: 'Archivo, sans-serif', fontWeight: 900, fontSize: 15,
                  transition: 'all 0.15s ease',
                }}>
                  {n}
                </button>
              )
            })}
          </div>

          {startDay && (
            <div style={{
              marginTop: 14, padding: '12px 14px', borderRadius: 12,
              background: TR.lime, border: '1.5px solid ' + TR.fg,
              fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
              color: TR.fg, letterSpacing: 0.5,
            }}>
              ↦ {startLabel} — {endDateLabel()} · {duration} {duration === 1 ? 'день' : duration < 5 ? 'дня' : 'дней'}
            </div>
          )}
        </div>

        <div style={{ height: 24 }} />

        {/* ── Sticky footer ── */}
        <div style={{
          position: 'sticky', bottom: 0,
          padding: '14px 22px 22px',
          background: `linear-gradient(to top, ${TR.bg} 75%, transparent)`,
          display: 'flex', gap: 10,
        }}>
          <button onClick={onBack} style={{
            height: 60, padding: '0 22px', borderRadius: 14,
            background: 'transparent', color: TR.fg, border: '1.5px solid ' + TR.fg,
            fontFamily: 'Archivo, sans-serif', fontSize: 13, fontWeight: 800,
            letterSpacing: '0.04em', textTransform: 'uppercase', cursor: 'pointer',
          }}>Назад</button>
          <button
            className="tr-cta-btn"
            onClick={canContinue ? handleContinue : () => onContinue?.({ startDay: null, duration, label: null, endLabel: null })}
            style={{
              flex: 1, height: 60, borderRadius: 14,
              background: TR.lime, color: TR.fg, border: '2px solid ' + TR.fg,
              fontFamily: 'Archivo, sans-serif', fontSize: 15, fontWeight: 800,
              letterSpacing: '0.04em', textTransform: 'uppercase',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10,
              boxShadow: '4px 4px 0 0 ' + TR.fg, cursor: 'pointer',
              opacity: canContinue ? 1 : 0.6,
            }}
          >
            {canContinue ? <>Дальше <ArrowRight /></> : 'Выбери дату'}
          </button>
        </div>

      </div>
    </div>
  )
}
