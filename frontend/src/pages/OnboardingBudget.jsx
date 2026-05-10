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
    price: '~30–60 €',
    priceLabel: 'В ДЕНЬ',
    desc: 'Хостелы и бюджетные отели, стритфуд и простые рестораны, общественный транспорт.',
    bars: [2, 1, 1],
  },
  {
    id: 'comfort',
    label: 'COMFORT',
    price: '~80–150 €',
    priceLabel: 'В ДЕНЬ',
    desc: 'Комфортные 3–4★ отели, рестораны со средним чеком, такси при необходимости.',
    bars: [3, 3, 2],
  },
  {
    id: 'lux',
    label: 'LUX',
    price: '200 €+',
    priceLabel: 'В ДЕНЬ',
    desc: 'Бутик-отели и апартаменты 5★, рестораны fine dining, личный гид, трансферы.',
    bars: [5, 5, 5],
  },
]

const PRIORITIES = [
  { id: 'food',      label: 'ЕДА' },
  { id: 'transport', label: 'ТРАНСПОРТ' },
  { id: 'housing',   label: 'ЖИЛЬЁ' },
  { id: 'culture',   label: 'КУЛЬТУРА' },
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

const BAR_LABELS = ['ЖИЛЬЁ', 'ЕДА', 'ТРАНСПОРТ']

export default function OnboardingBudget({ city, groupType, trip, onBack, onContinue }) {
  const [selected, setSelected]   = useState('comfort')
  const [priority, setPriority]   = useState(null)

  const cityName   = city?.n   ?? 'Рим'
  const cityDays   = trip?.duration ? `${trip.duration} дней` : city?.days ?? '7–10 дней'
  const groupLabel = { solo:'СОЛО', duo:'ВДВОЁМ', family:'СЕМЬЯ', friends:'ДРУЗЬЯ', group:'ГРУППА' }[groupType] ?? 'ВДВОЁМ'

  const selectedBudget = BUDGETS.find(b => b.id === selected)

  // Estimated total
  const midPoint = { economy: 45, comfort: 115, lux: 250 }[selected]
  const numDays  = trip?.duration ?? 7
  const estimate = (midPoint * numDays).toLocaleString('ru-RU')

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
              <div style={{ width: '83%', height: '100%', background: TR.fg }} />
            </div>
            <div style={{
              fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
              letterSpacing: '0.18em', color: TR.fg, fontWeight: 600,
            }}>05 / 06</div>
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
          <span>ЧЕРНОВИК 80%</span>
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

        <div style={{
          padding: '0 22px 20px', fontSize: 14.5, lineHeight: 1.5,
          color: TR.fgMute, maxWidth: 310,
        }}>
          Мы подберём отели, рестораны и активности под выбранный уровень.
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
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  {/* Left: label + desc */}
                  <div style={{ flex: 1, paddingRight: 14 }}>
                    <div style={{
                      fontFamily: 'Archivo, sans-serif', fontSize: 22, fontWeight: 900,
                      lineHeight: 1, letterSpacing: '-0.02em', marginBottom: 6,
                    }}>{b.label}</div>
                    <div style={{
                      fontSize: 12, lineHeight: 1.5, opacity: 0.75,
                      fontFamily: 'JetBrains Mono, monospace', letterSpacing: 0.2,
                    }}>{b.desc}</div>
                  </div>

                  {/* Right: price + bars */}
                  <div style={{ flexShrink: 0, textAlign: 'right' }}>
                    <div style={{
                      fontFamily: 'Archivo, sans-serif', fontWeight: 900, fontSize: 22,
                      lineHeight: 1, letterSpacing: '-0.02em',
                      color: isSel ? TR.lime : TR.fg,
                    }}>{b.price}</div>
                    <div style={{
                      fontFamily: 'JetBrains Mono, monospace', fontSize: 9,
                      letterSpacing: 1, opacity: 0.6, marginBottom: 8,
                    }}>{b.priceLabel}</div>

                    {/* Mini bar chart */}
                    <div style={{ display: 'flex', gap: 4, justifyContent: 'flex-end' }}>
                      {b.bars.map((v, i) => (
                        <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: 2, alignItems: 'center' }}>
                          {[5,4,3,2,1].map(level => (
                            <div key={level} style={{
                              width: 6, height: 6, borderRadius: 1,
                              background: level <= v
                                ? (isSel ? TR.lime : TR.fg)
                                : 'transparent',
                              border: '1px solid ' + (isSel ? TR.lime : TR.hairlineSt),
                              opacity: level <= v ? 1 : 0.4,
                            }}/>
                          ))}
                        </div>
                      ))}
                    </div>
                    <div style={{
                      display: 'flex', gap: 4, justifyContent: 'flex-end',
                      marginTop: 4,
                    }}>
                      {BAR_LABELS.map(l => (
                        <div key={l} style={{
                          fontFamily: 'JetBrains Mono, monospace', fontSize: 7,
                          opacity: 0.5, letterSpacing: 0.2, width: 18,
                          textAlign: 'center', lineHeight: 1.2,
                        }}>{l}</div>
                      ))}
                    </div>
                  </div>
                </div>

                {isSel && (
                  <div style={{
                    marginTop: 12, paddingTop: 10,
                    borderTop: '1px dashed rgba(241,237,224,0.25)',
                    fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
                    color: TR.lime, letterSpacing: 0.8,
                  }}>
                    ★ ВЫБРАНО · ~{estimate} € НА {numDays} ДНЕЙ
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* ── Priority chips ── */}
        <div style={{ padding: '22px 22px 0' }}>
          <div style={{
            fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
            letterSpacing: '0.22em', textTransform: 'uppercase',
            color: TR.fg, fontWeight: 600, marginBottom: 10,
          }}>
            ЧТО ВАЖНЕЕ — ОПЦИОНАЛЬНО
          </div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {PRIORITIES.map(p => {
              const isSel = p.id === priority
              return (
                <button
                  key={p.id}
                  onClick={() => setPriority(isSel ? null : p.id)}
                  style={{
                    height: 40, padding: '0 18px', borderRadius: 99,
                    background: isSel ? TR.fg : 'transparent',
                    color: isSel ? TR.lime : TR.fg,
                    border: '1.5px solid ' + (isSel ? TR.fg : TR.hairlineSt),
                    boxShadow: isSel ? '3px 3px 0 0 ' + TR.fg : 'none',
                    transform: isSel ? 'translate(-1px,-1px)' : 'none',
                    fontFamily: 'Archivo, sans-serif', fontWeight: 800, fontSize: 12,
                    letterSpacing: '0.06em', cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                >
                  {p.label}
                </button>
              )
            })}
          </div>
          {priority && (
            <div style={{
              marginTop: 12, padding: '10px 14px', borderRadius: 10,
              background: TR.surface2, border: '1px solid ' + TR.hairline,
              fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
              color: TR.fgMute, letterSpacing: 0.5,
            }}>
              ✦ ИИ увеличит долю бюджета на{' '}
              <b style={{ color: TR.fg }}>{PRIORITIES.find(p2 => p2.id === priority)?.label}</b>
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
            onClick={() => onContinue?.(selected, priority)}
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
