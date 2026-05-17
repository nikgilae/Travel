import { useState } from 'react'

const TR = {
  bg: '#f1ede0', fg: '#0d2818', fgMute: '#5e6e58', lime: '#b9ff3d',
  surface: '#fbf7ea', surface2: '#e8e2cf', hairline: 'rgba(13,40,24,0.12)',
}

const FILTERS = ['Всё', 'Еда', 'Музеи', 'Парки', 'Кафе', 'Магазины']

const PinIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
    <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"
      stroke={TR.fgMute} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    <circle cx="12" cy="9" r="2.5" stroke={TR.fgMute} strokeWidth="1.5"/>
  </svg>
)

export default function NearbyPage() {
  const [filter, setFilter] = useState('Всё')

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0 }}>

      {/* Header */}
      <div style={{ padding: '20px 22px 14px', borderBottom: `1px solid ${TR.hairline}` }}>
        <div style={{
          fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
          letterSpacing: '0.2em', color: TR.fgMute,
          textTransform: 'uppercase', marginBottom: 6,
        }}>
          РЯДОМ С ВАМИ
        </div>
        <div style={{
          fontFamily: 'Archivo, sans-serif', fontWeight: 900,
          fontSize: 28, letterSpacing: '-0.03em', color: TR.fg,
          textTransform: 'uppercase', lineHeight: 1,
        }}>
          Что рядом?
        </div>
      </div>

      {/* Filter chips */}
      <div style={{
        display: 'flex', gap: 6, overflowX: 'auto',
        padding: '12px 22px', scrollbarWidth: 'none',
      }}>
        {FILTERS.map(f => (
          <button key={f} onClick={() => setFilter(f)} style={{
            flexShrink: 0,
            padding: '6px 14px',
            borderRadius: 99,
            border: `1.5px solid ${filter === f ? TR.fg : TR.hairline}`,
            background: filter === f ? TR.fg : 'transparent',
            color: filter === f ? TR.lime : TR.fg,
            fontFamily: 'Archivo, sans-serif',
            fontWeight: 700, fontSize: 11,
            letterSpacing: '0.05em', cursor: 'pointer',
          }}>
            {f.toUpperCase()}
          </button>
        ))}
      </div>

      {/* Placeholder state */}
      <div style={{
        flex: 1, display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
        padding: '40px 28px', gap: 16,
      }}>
        <PinIcon />
        <div style={{ textAlign: 'center' }}>
          <div style={{
            fontFamily: 'Archivo, sans-serif', fontWeight: 800,
            fontSize: 16, textTransform: 'uppercase', color: TR.fg, marginBottom: 8,
          }}>
            Геолокация не включена
          </div>
          <div style={{
            fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
            color: TR.fgMute, lineHeight: 1.6, maxWidth: 240,
          }}>
            Разрешите доступ к геолокации, чтобы увидеть места рядом с вами
          </div>
        </div>
        <button style={{
          padding: '11px 24px',
          background: TR.lime, color: TR.fg,
          border: `1.5px solid ${TR.fg}`,
          borderRadius: 10,
          fontFamily: 'Archivo, sans-serif',
          fontWeight: 800, fontSize: 12,
          letterSpacing: '0.05em', cursor: 'pointer',
          boxShadow: `2px 2px 0 0 ${TR.fg}`,
        }}>
          РАЗРЕШИТЬ ГЕОЛОКАЦИЮ
        </button>
        <div style={{
          padding: '8px 14px',
          background: TR.surface2,
          border: `1px solid ${TR.hairline}`,
          borderRadius: 8,
          fontFamily: 'JetBrains Mono, monospace',
          fontSize: 10, color: TR.fgMute, letterSpacing: '0.06em',
        }}>
          NEARBY · COMING SOON
        </div>
      </div>

    </div>
  )
}
