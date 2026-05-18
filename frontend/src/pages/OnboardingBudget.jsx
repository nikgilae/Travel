import { useState } from 'react'
import './OnboardingBudget.css'

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

const BUDGETS = [
  {
    id: 'economy',
    label: 'ECONOMY',
    desc: 'Хостелы и бюджетные отели, стритфуд, общественный транспорт.',
  },
  {
    id: 'comfort',
    label: 'COMFORT',
    desc: 'Комфортные 3–4★ отели, рестораны со средним чеком, такси.',
  },
  {
    id: 'lux',
    label: 'LUX',
    desc: 'Бутик-отели и апартаменты 5★, fine dining, личный гид, трансферы.',
  },
]

const ChevronLeft = () => (
  <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
    <path d="M11.5 4 L6.5 9 L11.5 14" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
)
const ArrowRight = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
    <path d="M3 8 H13 M9 4 L13 8 L9 12" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
)

export default function OnboardingBudget({ city, groupType, trip, onBack, onContinue }) {
  const [selected, setSelected] = useState('comfort')

  const cityName = city?.n ?? 'Рим'
  const numDays  = trip?.duration ?? 7

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
              <div style={{ width: '80%', height: '100%', background: TR.fg }} />
            </div>
            <div style={{
              fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
              letterSpacing: '0.18em', color: TR.fg, fontWeight: 600,
            }}>04 / 05</div>
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
          <span>{cityName.toUpperCase()} · {numDays} ДНЕЙ</span>
          <span>80%</span>
        </div>

        {/* ── Hero ── */}
        <div style={{ padding: '4px 22px 14px' }}>
          <h1 style={{
            fontFamily: 'Archivo, sans-serif', fontWeight: 900, fontSize: 56,
            lineHeight: 0.86, letterSpacing: '-0.04em', textTransform: 'uppercase',
            color: TR.fg, margin: 0,
          }}>
            КАКОЙ<br/>БЮДЖЕТ?
          </h1>
        </div>

        {/* ── Budget cards ── */}
        <div style={{ padding: '0 22px', display: 'flex', flexDirection: 'column', gap: 10 }}>
          {BUDGETS.map(b => {
            const isSel = b.id === selected
            return (
              <div
                key={b.id}
                className="tr-budget-card"
                onClick={() => setSelected(b.id)}
                style={{
                  padding: '18px 18px 16px', borderRadius: 14, cursor: 'pointer',
                  background: isSel ? TR.fg : TR.surface,
                  color: isSel ? TR.bg : TR.fg,
                  border: '1.5px solid ' + (isSel ? TR.fg : TR.hairline),
                  boxShadow: isSel
                    ? '0 0 0 4px ' + TR.lime + ', 5px 5px 0 0 ' + TR.fg
                    : 'none',
                  transform: isSel ? 'translate(-2px,-2px) scale(1.015)' : 'none',
                  transformOrigin: 'left center',
                  transition: 'all .25s ease',
                }}
              >
                <div style={{
                  fontFamily: 'Archivo, sans-serif', fontSize: 22, fontWeight: 900,
                  lineHeight: 1, letterSpacing: '-0.02em', marginBottom: 8,
                }}>{b.label}</div>
                <div style={{
                  fontSize: 12, lineHeight: 1.5, opacity: 0.75,
                  fontFamily: 'JetBrains Mono, monospace', letterSpacing: 0.2,
                }}>{b.desc}</div>
              </div>
            )
          })}
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
            onClick={() => onContinue?.(selected)}
            style={{
              flex: 1, height: 60, borderRadius: 14,
              background: TR.lime, color: TR.fg, border: '2px solid ' + TR.fg,
              fontFamily: 'Archivo, sans-serif', fontSize: 15, fontWeight: 800,
              letterSpacing: '0.04em', textTransform: 'uppercase',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10,
              boxShadow: '4px 4px 0 0 ' + TR.fg, cursor: 'pointer',
            }}
          >
            Дальше <ArrowRight />
          </button>
        </div>

      </div>
    </div>
  )
}
