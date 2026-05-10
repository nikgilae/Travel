import { useState } from 'react'
import './OnboardingStyle.css'

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

const STYLES = [
  { id: 'relaxed',  label: 'RELAXED',  sub: 'неспешно, без суеты',         glyph: '01' },
  { id: 'active',   label: 'ACTIVE',   sub: 'больше мест и событий',        glyph: '02' },
  { id: 'cultural', label: 'CULTURAL', sub: 'история, музеи, архитектура',  glyph: '03' },
  { id: 'food',     label: 'FOOD',     sub: 'гастро-фокус, рынки, рестораны', glyph: '04' },
  { id: 'nature',   label: 'NATURE',   sub: 'парки, природа, прогулки',     glyph: '05' },
  { id: 'night',    label: 'NIGHT',    sub: 'ночная жизнь, бары, концерты', glyph: '06' },
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
const StarIcon = () => (
  <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
    <path d="M8 1 L9 7 L15 8 L9 9 L8 15 L7 9 L1 8 L7 7 Z" fill="currentColor"/>
  </svg>
)

export default function OnboardingStyle({ city, groupType, trip, onBack, onContinue }) {
  const [selected, setSelected] = useState(new Set(['cultural']))
  const [dayNote, setDayNote]   = useState('')

  const cityName   = city?.n   ?? 'Рим'
  const cityDays   = trip?.duration ? `${trip.duration} дней` : city?.days ?? '7–10 дней'
  const groupLabel = { solo:'СОЛО', duo:'ВДВОЁМ', family:'СЕМЬЯ', friends:'ДРУЗЬЯ', group:'ГРУППА' }[groupType] ?? 'ВДВОЁМ'

  const toggle = (id) => {
    const s = new Set(selected)
    s.has(id) ? s.delete(id) : s.add(id)
    setSelected(s)
  }

  const selectedLabels = STYLES.filter(s => selected.has(s.id)).map(s => s.label).join(' · ')

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
              <div style={{ width: '50%', height: '100%', background: TR.fg }} />
            </div>
            <div style={{
              fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
              letterSpacing: '0.18em', color: TR.fg, fontWeight: 600,
            }}>03 / 06</div>
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
          <span>{cityName.toUpperCase()} · {cityDays.toUpperCase()}</span>
          <span>ЧЕРНОВИК 40%</span>
        </div>

        {/* ── Hero ── */}
        <div style={{ padding: '4px 22px 14px' }}>
          <h1 style={{
            fontFamily: 'Archivo, sans-serif', fontWeight: 900, fontSize: 56,
            lineHeight: 0.86, letterSpacing: '-0.04em', textTransform: 'uppercase',
            color: TR.fg, margin: 0,
          }}>
            В КАКОМ<br/>СТИЛЕ?
          </h1>
        </div>

        <div style={{
          padding: '0 22px 20px', fontSize: 14.5, lineHeight: 1.5,
          color: TR.fgMute, maxWidth: 310,
        }}>
          Выберите один или несколько стилей — маршрут подстроится под приоритеты.
        </div>

        {/* ── Style grid 2×3 ── */}
        <div style={{
          padding: '0 22px',
          display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10,
        }}>
          {STYLES.map(s => {
            const isSel = selected.has(s.id)
            return (
              <div
                key={s.id}
                className="tr-style-card"
                onClick={() => toggle(s.id)}
                style={{
                  padding: '16px 16px 14px', borderRadius: 14, cursor: 'pointer',
                  background: isSel ? TR.fg : TR.surface,
                  color: isSel ? TR.bg : TR.fg,
                  border: '1.5px solid ' + (isSel ? TR.fg : TR.hairline),
                  boxShadow: isSel
                    ? '0 0 0 3px ' + TR.lime + ', 4px 4px 0 0 ' + TR.fg
                    : 'none',
                  transform: isSel ? 'translate(-2px,-2px) scale(1.02)' : 'none',
                  transformOrigin: 'center',
                  transition: 'all .2s ease',
                  position: 'relative',
                }}
              >
                {/* Glyph badge */}
                <div style={{
                  display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                  width: 28, height: 28, borderRadius: 7, marginBottom: 10,
                  background: isSel ? TR.lime : 'transparent',
                  border: '1.5px solid ' + (isSel ? TR.fg : TR.hairlineSt),
                  fontFamily: 'Archivo, sans-serif', fontSize: 12, fontWeight: 900,
                  color: TR.fg,
                }}>
                  {s.glyph}
                </div>

                <div style={{
                  fontFamily: 'Archivo, sans-serif', fontSize: 16, fontWeight: 900,
                  lineHeight: 1, letterSpacing: '-0.01em', marginBottom: 5,
                }}>{s.label}</div>

                <div style={{
                  fontFamily: 'JetBrains Mono, monospace', fontSize: 9.5,
                  lineHeight: 1.4, opacity: 0.7,
                }}>{s.sub}</div>

                {isSel && (
                  <div style={{
                    position: 'absolute', top: 10, right: 10,
                    color: TR.lime,
                  }}>
                    <StarIcon />
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* ── Draft preview ── */}
        {selected.size > 0 && (
          <div style={{ padding: '18px 22px 0' }}>
            <div style={{
              padding: '12px 14px', borderRadius: 12,
              background: TR.lime, border: '1.5px solid ' + TR.fg,
              display: 'flex', gap: 10, alignItems: 'center',
            }}>
              <StarIcon />
              <div style={{ fontSize: 12, lineHeight: 1.4, flex: 1, color: TR.fg }}>
                <b style={{ fontFamily: 'Archivo, sans-serif', fontWeight: 800, letterSpacing: 0.3 }}>
                  СТИЛЬ ЗАПИСАН.
                </b>{' '}
                <span style={{ opacity: 0.75, fontFamily: 'JetBrains Mono, monospace' }}>
                  {selectedLabels}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* ── Optional day note ── */}
        <div style={{ padding: '20px 22px 0' }}>
          <div style={{
            fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
            letterSpacing: '0.22em', textTransform: 'uppercase',
            color: TR.fg, fontWeight: 600, marginBottom: 8,
          }}>
            ИДЕАЛЬНЫЙ ДЕНЬ — ОПЦИОНАЛЬНО
          </div>
          <textarea
            className="tr-notes-input"
            placeholder="«Утром кофе и прогулка, вечером — долгий ужин и бокал вина…»"
            value={dayNote}
            onChange={e => setDayNote(e.target.value)}
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
          <button onClick={onBack} style={{
            height: 60, padding: '0 22px', borderRadius: 14,
            background: 'transparent', color: TR.fg, border: '1.5px solid ' + TR.fg,
            fontFamily: 'Archivo, sans-serif', fontSize: 13, fontWeight: 800,
            letterSpacing: '0.04em', textTransform: 'uppercase', cursor: 'pointer',
          }}>Назад</button>
          <button
            className="tr-cta-btn"
            onClick={() => onContinue?.([...selected], dayNote)}
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
