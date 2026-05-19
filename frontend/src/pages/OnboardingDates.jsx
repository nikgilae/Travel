import { useState } from 'react'
import './OnboardingDates.css'

const TR = {
  bg:         '#F6F7F9',
  surface:    '#FFFFFF',
  surface2:   '#F1F3F5',
  fg:         '#0A0B0C',
  fgMute:     '#5B6066',
  hairline:   '#E8EAEC',
  hairlineSt: '#D6D9DD',
  lime:       '#B9FF3D',
  warn:       '#B43340',
}

const MAX_DAYS = 21

const MONTH_NAMES = [
  'Январь','Февраль','Март','Апрель','Май','Июнь',
  'Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь',
]
const DAY_NAMES = ['ПН','ВТ','СР','ЧТ','ПТ','СБ','ВС']

function buildCalendar(year, month) {
  const firstDay = new Date(year, month, 1)
  const startDow = (firstDay.getDay() + 6) % 7
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const cells = []
  for (let i = 0; i < startDow; i++) cells.push(null)
  for (let d = 1; d <= daysInMonth; d++) cells.push(d)
  while (cells.length % 7 !== 0) cells.push(null)
  return cells
}

function toDate({ year, month, day }) {
  return new Date(year, month, day)
}

function daysBetween(a, b) {
  return Math.round((toDate(b) - toDate(a)) / (1000 * 60 * 60 * 24)) + 1
}

function fmtDay(d) {
  return `${d.day} ${MONTH_NAMES[d.month]}`
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
today.setHours(0, 0, 0, 0)

export default function OnboardingDates({ city, groupType, onBack, onContinue }) {
  const [viewYear, setViewYear]   = useState(today.getFullYear())
  const [viewMonth, setViewMonth] = useState(today.getMonth())
  const [startDay, setStartDay]   = useState(null) // { year, month, day }
  const [endDay, setEndDay]       = useState(null) // { year, month, day }
  const [overLimit, setOverLimit] = useState(false)

  const cityName   = city?.n ?? 'Рим'
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
    return new Date(viewYear, viewMonth, day) < today
  }

  const cellDate = (day) => ({ year: viewYear, month: viewMonth, day })

  const isStart = (day) =>
    day && startDay &&
    startDay.year === viewYear && startDay.month === viewMonth && startDay.day === day

  const isEnd = (day) =>
    day && endDay &&
    endDay.year === viewYear && endDay.month === viewMonth && endDay.day === day

  const isInRange = (day) => {
    if (!day || !startDay || !endDay) return false
    const d = new Date(viewYear, viewMonth, day)
    return d > toDate(startDay) && d < toDate(endDay)
  }

  function handleDayClick(day) {
    if (!day || isPast(day)) return
    const clicked = cellDate(day)
    setOverLimit(false)

    if (!startDay || (startDay && endDay)) {
      setStartDay(clicked)
      setEndDay(null)
      return
    }

    const clickedMs = toDate(clicked).getTime()
    const startMs   = toDate(startDay).getTime()

    if (clickedMs < startMs) {
      setStartDay(clicked)
      setEndDay(null)
      return
    }

    const duration = daysBetween(startDay, clicked)
    if (duration > MAX_DAYS) {
      setOverLimit(true)
      return
    }

    setEndDay(clicked)
  }

  const duration = startDay && endDay ? daysBetween(startDay, endDay) : null
  const canContinue = !!(startDay && endDay)

  const handleContinue = () => {
    onContinue?.({
      startDay,
      duration,
      label:    `${fmtDay(startDay)} ${startDay.year}`,
      endLabel: fmtDay(endDay),
    })
  }

  const footerLabel = () => {
    if (!startDay)         return 'Выбери дату начала'
    if (!endDay)           return 'Выбери дату окончания'
    return null
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
            style={{ color: TR.fg, border: '1px solid ' + TR.hairline }}>
            <ChevronLeft />
          </button>
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ flex: 1, height: 4, background: TR.surface2, borderRadius: 2, overflow: 'hidden' }}>
              <div style={{ width: '40%', height: '100%', background: TR.fg }} />
            </div>
            <div style={{
              fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
              letterSpacing: '0.18em', color: TR.fg, fontWeight: 600,
            }}>02 / 05</div>
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
          <span>25%</span>
        </div>

        {/* ── Hero ── */}
        <div style={{ padding: '4px 22px 14px' }}>
          <h1 style={{
            fontFamily: 'Onest, sans-serif', fontWeight: 600, fontSize: 56,
            lineHeight: 0.86, letterSpacing: '-0.04em', textTransform: 'uppercase',
            color: TR.fg, margin: 0,
          }}>
            КОГДА<br/>ЕДЕМ?
          </h1>
        </div>

        {/* ── Calendar ── */}
        <div style={{ padding: '0 22px' }}>
          <div style={{
            background: TR.surface, borderRadius: 16,
            border: '1px solid ' + TR.hairline, overflow: 'hidden',
          }}>
            {/* Month nav */}
            <div style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '14px 16px 10px',
              borderBottom: '1px solid ' + TR.hairline,
            }}>
              <button onClick={prevMonth} style={{
                width: 32, height: 32, borderRadius: 8,
                background: 'transparent', border: '1px solid ' + TR.hairlineSt,
                color: TR.fg, cursor: 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}><ChevronLeft /></button>

              <div style={{
                fontFamily: 'Onest, sans-serif', fontWeight: 600, fontSize: 15,
                letterSpacing: '-0.01em', color: TR.fg, textTransform: 'uppercase',
              }}>
                {MONTH_NAMES[viewMonth]} {viewYear}
              </div>

              <button onClick={nextMonth} style={{
                width: 32, height: 32, borderRadius: 8,
                background: 'transparent', border: '1px solid ' + TR.hairlineSt,
                color: TR.fg, cursor: 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
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
                const past    = isPast(day)
                const selStart = isStart(day)
                const selEnd   = isEnd(day)
                const inRange  = isInRange(day)
                const isEndpoint = selStart || selEnd

                return (
                  <div
                    key={idx}
                    onClick={() => handleDayClick(day)}
                    style={{
                      height: 34,
                      borderRadius: 6,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontFamily: 'Onest, sans-serif',
                      fontWeight: isEndpoint ? 900 : 600,
                      fontSize: 13,
                      background: isEndpoint
                        ? TR.lime
                        : inRange
                          ? 'rgba(185,255,61,0.20)'
                          : 'transparent',
                      color: past ? TR.hairlineSt : TR.fg,
                      border: 'none',
                      cursor: !day || past ? 'default' : 'pointer',
                      transition: 'background 0.1s',
                      opacity: !day ? 0 : 1,
                    }}
                  >
                    {day ?? ''}
                  </div>
                )
              })}
            </div>
          </div>
        </div>

        {/* ── Hint / summary ── */}
        <div style={{ padding: '14px 22px 0' }}>
          {overLimit && (
            <div style={{
              padding: '11px 14px', borderRadius: 10,
              background: 'rgba(200,85,61,0.10)', border: '1px solid ' + TR.warn,
              fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
              color: TR.warn, letterSpacing: 0.4,
            }}>
              Максимальная длина маршрута — 21 день
            </div>
          )}

          {!overLimit && startDay && !endDay && (
            <div style={{
              padding: '11px 14px', borderRadius: 10,
              background: TR.surface2, border: '1px solid ' + TR.hairline,
              fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
              color: TR.fgMute, letterSpacing: 0.4,
            }}>
              ↦ {fmtDay(startDay)} — выбери дату окончания
            </div>
          )}

          {canContinue && (
            <div style={{
              padding: '12px 14px', borderRadius: 12,
              background: TR.lime, border: '1px solid ' + TR.hairline,
              fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
              color: TR.fg, letterSpacing: 0.5,
            }}>
              ↦ {fmtDay(startDay)} — {fmtDay(endDay)} · {duration} {duration === 1 ? 'день' : duration < 5 ? 'дня' : 'дней'}
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
            background: 'transparent', color: TR.fg, border: '1px solid ' + TR.hairline,
            fontFamily: 'Onest, sans-serif', fontSize: 13, fontWeight: 500,
            letterSpacing: '-0.005em', textTransform: 'uppercase', cursor: 'pointer',
          }}>Назад</button>
          <button
            className="tr-cta-btn"
            onClick={canContinue
              ? handleContinue
              : () => onContinue?.({ startDay: null, duration: null, label: null, endLabel: null })}
            style={{
              flex: 1, height: 44, borderRadius: 10,
              background: TR.lime, color: TR.fg, border: '1px solid ' + TR.lime,
              fontFamily: 'Onest, sans-serif', fontSize: 14, fontWeight: 500,
              letterSpacing: '-0.005em',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10,
              boxShadow: 'none', cursor: 'pointer',
              opacity: canContinue ? 1 : 0.6,
            }}
          >
            {canContinue ? <>Дальше <ArrowRight /></> : footerLabel()}
          </button>
        </div>

      </div>
    </div>
  )
}
