import { useState } from 'react'
import './OnboardingStep3.css'

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

const RHYTHMS = [
  {
    id: 'slow',
    label: 'СПОКОЙНО',
    sub: '2–3 места в день · долгие паузы',
    amp: [18, 16, 22, 15, 55, 18, 14],
    dots: 1,
    hours: '~3 ч / день',
    verdict: { tone: 'mild', text: 'УВИДИТЕ МЕНЬШЕ · НО ОТДОХНЁТЕ ПОЛНОСТЬЮ' },
  },
  {
    id: 'balanced',
    label: 'СБАЛАНСИРОВАННО',
    sub: '4–5 событий · ритм работы и отдыха',
    amp: [35, 72, 48, 82, 46, 68, 38],
    dots: 3,
    hours: '~6 ч / день',
    verdict: { tone: 'good', text: '+ВРЕМЯ НА ПАУЗЫ · +ГЛАВНОЕ НЕ УПУСТИТЕ' },
  },
  {
    id: 'intense',
    label: 'НАСЫЩЕННО',
    sub: 'максимум за день · мало пауз',
    amp: [78, 88, 85, 92, 80, 90, 82],
    dots: 5,
    hours: '~10 ч / день',
    verdict: { tone: 'warn', text: 'УВИДИТЕ ВСЁ · РИСК ВЕРНУТЬСЯ УСТАВШИМ' },
  },
]

const DAYS = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']

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
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
    <path d="M8 1 L9 7 L15 8 L9 9 L8 15 L7 9 L1 8 L7 7 Z" fill="currentColor"/>
  </svg>
)

const GROUP_LABELS = {
  solo: 'СОЛО',
  duo: 'ВДВОЁМ',
  family: 'СЕМЬЯ',
  friends: 'ДРУЗЬЯ',
  group: 'ГРУППА',
}

export default function OnboardingStep3({ city, groupType, onBack, onContinue }) {
  const [selected, setSelected] = useState('balanced')

  const cityName = city?.n ?? 'Рим'
  const cityDays = city?.days ?? '7–10 дней'
  const groupLabel = GROUP_LABELS[groupType] ?? 'ВДВОЁМ'

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
          margin: '8px 22px 12px',
          padding: '10px 14px',
          border: '1px solid ' + TR.hairline,
          borderRadius: 10,
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
          color: TR.fgMute, letterSpacing: 1, textTransform: 'uppercase',
        }}>
          <span>{cityName.toUpperCase()} · {groupLabel}</span>
          <span>ЧЕРНОВИК 40%</span>
        </div>

        {/* ── Hero ── */}
        <div style={{ padding: '4px 22px 18px' }}>
          <h1 style={{
            fontFamily: 'Archivo, sans-serif',
            fontWeight: 900, fontSize: 56, lineHeight: 0.86,
            letterSpacing: '-0.04em', textTransform: 'uppercase',
            color: TR.fg, margin: 0,
          }}>
            В КАКОМ<br/>РИТМЕ?
          </h1>
        </div>

        {/* ── Sub ── */}
        <div style={{
          padding: '0 22px 18px',
          fontSize: 14.5, lineHeight: 1.5, color: TR.fgMute, maxWidth: 310,
        }}>
          Хороший отдых — не максимум точек на карте, а правильный ритм между ними.
        </div>

        {/* ── Rhythm cards ── */}
        <div style={{ padding: '0 22px', display: 'flex', flexDirection: 'column', gap: 10 }}>
          {RHYTHMS.map(r => {
            const isSel = r.id === selected
            return (
              <div
                key={r.id}
                className="tr-rhythm-card"
                onClick={() => setSelected(r.id)}
                style={{
                  padding: '18px 18px 16px', borderRadius: 14,
                  background: isSel ? TR.fg : TR.surface,
                  color: isSel ? TR.bg : TR.fg,
                  border: '1.5px solid ' + (isSel ? TR.fg : TR.hairline),
                  boxShadow: isSel
                    ? '0 0 0 4px ' + TR.lime + ', 5px 5px 0 0 ' + TR.fg
                    : 'none',
                  transform: isSel ? 'translate(-2px,-2px) scale(1.015)' : 'none',
                  transformOrigin: 'left center',
                  transition: 'all .25s ease',
                  cursor: 'pointer',
                  position: 'relative',
                }}
              >
                {/* Header row */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <div style={{
                      fontFamily: 'Archivo, sans-serif',
                      fontSize: 20, fontWeight: 900, lineHeight: 1,
                      letterSpacing: '-0.02em',
                    }}>{r.label}</div>
                    <div style={{
                      fontSize: 12, marginTop: 5, opacity: 0.75,
                      fontFamily: 'JetBrains Mono, monospace', letterSpacing: 0.3,
                    }}>{r.sub}</div>
                  </div>

                  {/* Intensity dots + hours */}
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 5 }}>
                    <div style={{ display: 'flex', gap: 3 }}>
                      {[0, 1, 2, 3, 4].map(i => (
                        <div key={i} style={{
                          width: 6, height: 14, borderRadius: 1,
                          background: i < r.dots
                            ? (isSel ? TR.lime : TR.fg)
                            : 'transparent',
                          border: '1px solid ' + (isSel ? TR.lime : TR.hairlineSt),
                          opacity: i < r.dots ? 1 : 0.6,
                        }} />
                      ))}
                    </div>
                    <div style={{
                      fontFamily: 'JetBrains Mono, monospace', fontSize: 9,
                      letterSpacing: 1, opacity: 0.6,
                    }}>{r.hours}</div>
                  </div>
                </div>

                {/* Bar chart */}
                <div style={{ marginTop: 14, height: 54, display: 'flex', alignItems: 'flex-end', gap: 5 }}>
                  {r.amp.map((v, i) => (
                    <div key={i} style={{
                      flex: 1,
                      height: (v / 100) * 100 + '%',
                      background: isSel ? TR.lime : TR.fg,
                      opacity: isSel ? 1 : 0.6,
                      borderRadius: 2,
                      minHeight: 4,
                    }} />
                  ))}
                </div>

                {/* Day labels */}
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 6 }}>
                  {DAYS.map(d => (
                    <div key={d} style={{
                      fontFamily: 'JetBrains Mono, monospace', fontSize: 9,
                      opacity: 0.5, letterSpacing: 0.5,
                    }}>{d}</div>
                  ))}
                </div>

                {/* Verdict strip */}
                <div style={{
                  marginTop: 12, paddingTop: 10,
                  borderTop: '1px dashed ' + (isSel ? 'rgba(241,237,224,0.25)' : TR.hairlineSt),
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8,
                }}>
                  <div style={{
                    fontFamily: 'JetBrains Mono, monospace', fontSize: 9,
                    letterSpacing: 1, fontWeight: 600,
                    color: isSel
                      ? TR.lime
                      : (r.verdict.tone === 'warn' ? TR.warn : TR.fgMute),
                    opacity: isSel ? 1 : 0.85,
                  }}>↳ {r.verdict.text}</div>
                  {isSel && (
                    <div style={{
                      fontFamily: 'Archivo, sans-serif', fontSize: 10, fontWeight: 800,
                      letterSpacing: '0.06em', color: TR.lime, flexShrink: 0,
                    }}>★ ВЫБРАНО</div>
                  )}
                </div>
              </div>
            )
          })}
        </div>

        {/* ── Draft preview hint ── */}
        <div style={{ padding: '18px 22px 0' }}>
          <div style={{
            padding: '12px 14px', borderRadius: 12,
            background: TR.lime, border: '1.5px solid ' + TR.fg,
            display: 'flex', gap: 10, alignItems: 'center',
          }}>
            <StarIcon />
            <div style={{ fontSize: 13, lineHeight: 1.4, flex: 1, color: TR.fg }}>
              <b style={{ fontFamily: 'Archivo, sans-serif', fontWeight: 800, letterSpacing: 0.3 }}>
                ЧЕРНОВИК НА 40%.
              </b>{' '}
              <span style={{ opacity: 0.75 }}>
                {cityName} · {cityDays} · {groupLabel.toLowerCase()} →{' '}
              </span>
              <span style={{ textDecoration: 'underline', fontWeight: 600 }}>посмотреть</span>
            </div>
          </div>
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
            className="tr-back-btn"
            onClick={onBack}
            style={{
              height: 60, padding: '0 22px', borderRadius: 14,
              background: 'transparent', color: TR.fg, border: '1.5px solid ' + TR.fg,
              fontFamily: 'Archivo, sans-serif', fontSize: 13, fontWeight: 800,
              letterSpacing: '0.04em', textTransform: 'uppercase', cursor: 'pointer',
            }}
          >
            Назад
          </button>
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
