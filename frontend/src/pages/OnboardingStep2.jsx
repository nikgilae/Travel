import { useState } from 'react'
import './OnboardingStep2.css'

const TR = {
  bg:          '#f1ede0',
  surface:     '#fbf7ea',
  surface2:    '#e8e2cf',
  fg:          '#0d2818',
  fgMute:      '#5e6e58',
  hairline:    'rgba(13,40,24,0.12)',
  hairlineSt:  'rgba(13,40,24,0.22)',
  lime:        '#b9ff3d',
  warn:        '#c8553d',
}

const OPTIONS = [
  { id: 'solo',   label: 'ОДИН',    sub: 'один на один с городом' },
  { id: 'duo',    label: 'ВДВОЁМ',  sub: 'пара или близкий друг' },
  { id: 'family', label: 'СЕМЬЯ',   sub: 'с детьми или родителями' },
  { id: 'friends',label: 'ДРУЗЬЯ',  sub: 'небольшая компания' },
  { id: 'group',  label: 'ГРУППА',  sub: '5+ человек' },
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

const CheckIcon = () => (
  <svg width="16" height="16" viewBox="0 0 14 14" fill="none">
    <path d="M3 7 L6 10 L11 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
)

export default function OnboardingStep2({ city, onContinue, onBack }) {
  const [selected, setSelected] = useState('duo')
  const [notes, setNotes] = useState('')

  const cityName = city?.n ?? 'Рим'
  const cityDays = city?.days ?? '7–10 дней'

  return (
    <div className="tr-app">
      <div className="tr-phone">

        {/* ── Top bar with progress ── */}
        <div style={{
          height: 52, padding: '0 22px',
          display: 'flex', alignItems: 'center', gap: 14,
          flexShrink: 0,
        }}>
          <button
            className="tr-icon-btn"
            onClick={onBack}
            style={{ color: TR.fg, border: '1.5px solid ' + TR.fg }}
          >
            <ChevronLeft />
          </button>
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{
              flex: 1, height: 4,
              background: TR.surface2, borderRadius: 2, overflow: 'hidden',
            }}>
              <div style={{ width: '20%', height: '100%', background: TR.fg }} />
            </div>
            <div style={{
              fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
              letterSpacing: '0.18em', color: TR.fg, fontWeight: 600,
            }}>01 / 05</div>
          </div>
        </div>

        {/* ── Ledger ── */}
        <div style={{
          margin: '8px 22px 12px',
          padding: '10px 14px',
          border: '1px solid ' + TR.hairline,
          borderRadius: 10,
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
          color: TR.fgMute, letterSpacing: 1, textTransform: 'uppercase',
        }}>
          <span>{cityName.toUpperCase()} · {cityDays.toUpperCase()}</span>
          <span>16%</span>
        </div>

        {/* ── Hero ── */}
        <div style={{ padding: '4px 22px 18px' }}>
          <h1 style={{
            fontFamily: 'Archivo, sans-serif',
            fontWeight: 900, fontSize: 56, lineHeight: 0.86,
            letterSpacing: '-0.04em', textTransform: 'uppercase',
            color: TR.fg, margin: 0,
          }}>
            С КЕМ<br/>ВЫ?
          </h1>
        </div>

        {/* ── Options ── */}
        <div style={{ padding: '0 22px', display: 'flex', flexDirection: 'column', gap: 8 }}>
          {OPTIONS.map((o, i) => {
            const isSel = o.id === selected
            return (
              <div
                key={o.id}
                className="tr-option-card"
                onClick={() => setSelected(o.id)}
                style={{
                  display: 'flex', alignItems: 'center', gap: 14,
                  padding: '16px 18px', borderRadius: 12,
                  background: isSel ? TR.fg : TR.surface,
                  color: isSel ? TR.bg : TR.fg,
                  border: '1.5px solid ' + (isSel ? TR.fg : TR.hairline),
                  boxShadow: isSel
                    ? '0 0 0 4px ' + TR.lime + ', 5px 5px 0 0 ' + TR.fg
                    : 'none',
                  transform: isSel ? 'translate(-2px,-2px) scale(1.02)' : 'none',
                  transformOrigin: 'left center',
                  transition: 'all .25s ease',
                  cursor: 'pointer',
                }}
              >
                {/* Index glyph */}
                <div style={{
                  width: 36, height: 36, flexShrink: 0, borderRadius: 8,
                  background: isSel ? TR.lime : 'transparent',
                  color: TR.fg,
                  border: '1.5px solid ' + (isSel ? TR.fg : TR.hairlineSt),
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontFamily: 'Archivo, sans-serif', fontSize: 14, fontWeight: 900,
                }}>
                  0{i + 1}
                </div>

                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{
                    fontFamily: 'Archivo, sans-serif',
                    fontSize: 22, fontWeight: 900, lineHeight: 1,
                    letterSpacing: '-0.02em',
                  }}>{o.label}</div>
                  <div style={{
                    fontSize: 12, opacity: 0.75, marginTop: 5,
                    fontFamily: 'JetBrains Mono, monospace', letterSpacing: 0.5,
                  }}>{o.sub}</div>
                </div>

                {isSel ? (
                  <div style={{
                    width: 32, height: 32, flexShrink: 0, borderRadius: '50%',
                    background: TR.lime, color: TR.fg,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    border: '1.5px solid ' + TR.fg,
                  }}>
                    <CheckIcon />
                  </div>
                ) : (
                  <div style={{
                    width: 32, height: 32, flexShrink: 0, borderRadius: '50%',
                    border: '1.5px solid ' + TR.hairlineSt,
                  }} />
                )}
              </div>
            )
          })}
        </div>

        {/* ── Optional note ── */}
        <div style={{ padding: '22px 22px 0' }}>
          <div style={{
            fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
            letterSpacing: '0.22em', textTransform: 'uppercase',
            color: TR.fg, fontWeight: 600, marginBottom: 8,
          }}>
            ПОДРОБНЕЕ — ОПЦИОНАЛЬНО
          </div>
          <textarea
            className="tr-notes-input"
            placeholder="«Едем с женой, любим долгие ужины и не любим вставать рано…»"
            value={notes}
            onChange={e => setNotes(e.target.value)}
            rows={3}
            style={{
              width: '100%', padding: '14px 16px', borderRadius: 12,
              background: TR.surface, border: '1px dashed ' + TR.hairlineSt,
              fontSize: 14, fontStyle: 'italic', color: TR.fg,
              lineHeight: 1.5, resize: 'none', outline: 'none',
              fontFamily: 'Inter, sans-serif', boxSizing: 'border-box',
            }}
          />
        </div>

        <div style={{ height: 24 }} />

        {/* ── Sticky footer ── */}
        <div style={{
          position: 'sticky', bottom: 0,
          padding: '14px 22px 22px',
          background: `linear-gradient(to top, ${TR.bg} 75%, transparent)`,
          display: 'flex', gap: 10,
        }}>
          <button
            className="tr-skip-btn"
            onClick={() => onContinue?.(null, '')}
            style={{
              height: 60, padding: '0 22px', borderRadius: 14,
              background: 'transparent', color: TR.fg, border: '1.5px solid ' + TR.fg,
              fontFamily: 'Archivo, sans-serif', fontSize: 13, fontWeight: 800,
              letterSpacing: '0.04em', textTransform: 'uppercase', cursor: 'pointer',
            }}
          >
            Пропустить
          </button>
          <button
            className="tr-cta-btn"
            onClick={() => onContinue?.(selected, notes)}
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
