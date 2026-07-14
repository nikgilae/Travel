import { useState, useEffect, useRef } from 'react'
import { useLocation } from 'react-router-dom'
import './ChatScreen.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const WS_BASE  = API_BASE.replace('http', 'ws')

function getToken() { return localStorage.getItem('access_token') ?? '' }

// Persists trip chat history across tab switches for the current session
const tripHistoryCache = {}

// ── Design tokens ──────────────────────────────────────────────────────────────

const DARK = {
  bg:          '#0F1011',
  surface:     '#18191A',
  surface2:    '#212224',
  fg:          '#FFFFFF',
  fgMute:      'rgba(255,255,255,0.4)',
  hairline:    'rgba(255,255,255,0.08)',
  lime:        '#B9FF3D',
  userBubble:  '#B9FF3D',
  userText:    '#0A0B0C',
  aiBubble:    '#212224',
  aiText:      'rgba(255,255,255,0.88)',
  chipBg:      'rgba(255,255,255,0.05)',
  chipBorder:  'rgba(255,255,255,0.1)',
  chipHover:   'rgba(185,255,61,0.12)',
  inputBg:     '#18191A',
  inputBorder: 'rgba(255,255,255,0.1)',
  statusOn:    '#1E7A4B',
  statusWait:  '#B86A00',
  statusOff:   '#B43340',
}

const LIGHT = {
  bg:          '#F6F7F9',
  surface:     '#FFFFFF',
  surface2:    '#F1F3F5',
  fg:          '#0A0B0C',
  fgMute:      '#5B6066',
  hairline:    '#E8EAEC',
  lime:        '#B9FF3D',
  userBubble:  '#B9FF3D',
  userText:    '#0A0B0C',
  aiBubble:    '#FFFFFF',
  aiText:      '#0A0B0C',
  chipBg:      '#F1F3F5',
  chipBorder:  '#E8EAEC',
  chipHover:   'rgba(185,255,61,0.18)',
  inputBg:     '#FFFFFF',
  inputBorder: '#E8EAEC',
  statusOn:    '#1E7A4B',
  statusWait:  '#B86A00',
  statusOff:   '#B43340',
}

// ── Suggestion chips ───────────────────────────────────────────────────────────

const CHIPS = {
  general: ['Куда поехать в мае?', 'Нужна ли виза в Турцию?', 'Бюджет на неделю в Италии'],
  trip:    ['Добавь ресторан на день 2', 'Убери последнее место из дня 3', 'Какая погода будет?'],
  live:    ['Что поесть рядом?', 'Я устал, сократи план', 'Как добраться до следующего места?'],
}

// ── Helpers ────────────────────────────────────────────────────────────────────

function fmtTime(date) {
  return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
}

let _msgCounter = 0
function mkId() { return ++_msgCounter + '-' + Date.now() }

// ── Icons ──────────────────────────────────────────────────────────────────────

const SendIcon = () => (
  <svg width="17" height="17" viewBox="0 0 17 17" fill="none">
    <path d="M8.5 13.5V3.5M4 8L8.5 3.5L13 8"
      stroke="currentColor" strokeWidth="1.8"
      strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
)

const BotIcon = ({ color }) => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
    <path d="M13.5 9.5a2 2 0 0 1-2 2H4.5L2.5 14V4a2 2 0 0 1 2-2h7a2 2 0 0 1 2 2z"
      fill={color}/>
    <circle cx="6" cy="7.5" r="1" fill="rgba(0,0,0,0.35)"/>
    <circle cx="10" cy="7.5" r="1" fill="rgba(0,0,0,0.35)"/>
  </svg>
)

// ── Sub-components ─────────────────────────────────────────────────────────────

function MessageBubble({ msg, T }) {
  const isUser   = msg.sender === 'user'
  const isSystem = msg.sender === 'system'

  return (
    <div style={{
      display: 'flex', flexDirection: 'column',
      alignItems: isUser ? 'flex-end' : 'flex-start',
      gap: 3, maxWidth: '100%',
    }}>
      <div style={{
        maxWidth: '82%', padding: '10px 13px',
        borderRadius: isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
        background: isSystem
          ? 'rgba(200,85,61,0.1)'
          : isUser ? T.userBubble : T.aiBubble,
        color: isSystem ? '#c8553d'
          : isUser ? T.userText : T.aiText,
        fontSize: 14, lineHeight: 1.55,
        border: isSystem
          ? '1px solid rgba(200,85,61,0.22)'
          : `1px solid ${T.hairline}`,
        fontFamily: isSystem ? 'JetBrains Mono, monospace' : 'Onest, sans-serif',
        wordBreak: 'break-word',
        whiteSpace: 'pre-wrap',
      }}>
        {msg.text}
      </div>
      {msg.timestamp && (
        <span style={{
          fontSize: 9, color: T.fgMute,
          fontFamily: 'JetBrains Mono, monospace',
          paddingLeft: isUser ? 0 : 4,
          paddingRight: isUser ? 4 : 0,
        }}>
          {fmtTime(msg.timestamp)}
        </span>
      )}
    </div>
  )
}

function TypingIndicator({ T }) {
  return (
    <div style={{ display: 'flex', alignItems: 'flex-start' }}>
      <div style={{
        padding: '11px 14px',
        background: T.aiBubble, border: `1px solid ${T.hairline}`,
        borderRadius: '16px 16px 16px 4px',
        display: 'flex', gap: 5, alignItems: 'center',
      }}>
        {[0, 1, 2].map(i => (
          <div
            key={i}
            className="chat-dot"
            style={{
              background: T.fgMute,
              animationDelay: `${i * 0.18}s`,
            }}
          />
        ))}
      </div>
    </div>
  )
}

// ── Main component ─────────────────────────────────────────────────────────────

export default function ChatScreen({ mode, tripId, cityName, live = false }) {
  const T        = mode === 'general' ? DARK : LIGHT
  const chips    = CHIPS[mode === 'general' ? 'general' : live ? 'live' : 'trip']
  const location = useLocation()

  // ── History (trip mode persisted in module cache) ──
  const getInitialMessages = () => {
    if (mode === 'trip' && tripId) {
      if (!tripHistoryCache[tripId]) tripHistoryCache[tripId] = []
      return tripHistoryCache[tripId]
    }
    return []
  }

  const [messages,    setMessages]    = useState(getInitialMessages)
  // Pre-fill input from location.state.prefill (e.g. navigated from NearbyPage)
  const [input,       setInput]       = useState(location.state?.prefill ?? '')
  const [typing,      setTyping]      = useState(false)
  const [connected,   setConnected]   = useState(mode === 'general')
  const [reconnectIn, setReconnectIn] = useState(null)

  const bottomRef         = useRef(null)
  const wsRef             = useRef(null)
  const reconnectAttempts = useRef(0)
  const reconnectTimer    = useRef(null)
  const countdownTimer    = useRef(null)
  const typingTimeoutRef  = useRef(null)
  const firstMsgRef       = useRef(false)
  const MAX_RECONNECT     = 5

  // Sync trip messages to module cache
  useEffect(() => {
    if (mode === 'trip' && tripId) {
      tripHistoryCache[tripId] = messages
    }
  }, [messages, mode, tripId])

  // Safety timeout: if typing stays true for 30s, force-clear it
  useEffect(() => {
    if (typing) {
      typingTimeoutRef.current = setTimeout(() => {
        setTyping(false)
        addMsg('system', 'Нет ответа от сервера. Попробуй ещё раз.')
      }, 30000)
    } else {
      clearTimeout(typingTimeoutRef.current)
    }
    return () => clearTimeout(typingTimeoutRef.current)
  }, [typing])

  // Auto-scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, typing])

  function addMsg(sender, text) {
    setMessages(prev => [...prev, {
      id: mkId(), sender, text, timestamp: new Date(),
    }])
  }

  // ── WebSocket (trip mode) ──────────────────────────
  useEffect(() => {
    if (mode !== 'trip') return

    function connect() {
      const ws = new WebSocket(
        `${WS_BASE}/trips/${tripId}/chat?token=${encodeURIComponent(getToken())}`
      )
      wsRef.current = ws

      ws.onopen = () => {
        reconnectAttempts.current = 0
        firstMsgRef.current = false
        clearTimeout(reconnectTimer.current)
        clearInterval(countdownTimer.current)
        setConnected(true)
        setReconnectIn(null)
      }

      ws.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data)
          setTyping(false)
          // Skip auth error noise — user will see the offline indicator
          if (data.sender === 'system' && data.text?.includes('токен')) return
          // Backend always sends a welcome greeting as the very first message.
          // Skip it if the user already has history (re-entering chat or reconnecting).
          if (!firstMsgRef.current) {
            firstMsgRef.current = true
            const hasHistory = (tripHistoryCache[tripId]?.length ?? 0) > 0
            if (hasHistory) return
          }
          addMsg(data.sender === 'ai' ? 'ai' : 'system', data.text)
        } catch { /* malformed JSON — ignore */ }
      }

      ws.onclose = () => {
        setConnected(false)
        setTyping(false)
        if (reconnectAttempts.current < MAX_RECONNECT) {
          reconnectAttempts.current++
          let secs = 3
          setReconnectIn(secs)
          clearInterval(countdownTimer.current)
          countdownTimer.current = setInterval(() => {
            secs--
            setReconnectIn(secs > 0 ? secs : null)
            if (secs <= 0) clearInterval(countdownTimer.current)
          }, 1000)
          reconnectTimer.current = setTimeout(connect, 3000)
        }
      }

      ws.onerror = () => ws.close()
    }

    connect()

    return () => {
      clearTimeout(reconnectTimer.current)
      clearInterval(countdownTimer.current)
      wsRef.current?.close()
    }
  }, [mode, tripId])

  // ── Send ───────────────────────────────────────────
  async function sendMessage(text) {
    const msg = text.trim()
    if (!msg || typing) return
    setInput('')
    addMsg('user', msg)
    setTyping(true)

    if (mode === 'general') {
      try {
        const history = messages.map(m => ({
          role:    m.sender === 'user' ? 'user' : 'assistant',
          content: m.text,
        }))
        const res = await fetch(`${API_BASE}/chat/general`, {
          method:  'POST',
          headers: {
            'Content-Type':  'application/json',
            'Authorization': `Bearer ${getToken()}`,
          },
          body: JSON.stringify({ message: msg, history }),
        })
        if (!res.ok) throw new Error(`${res.status}`)
        const data = await res.json()
        addMsg('ai', data.reply)
      } catch (e) {
        addMsg('system', `Ошибка связи: ${e.message}`)
      } finally {
        setTyping(false)
      }
    } else {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(msg)
      } else {
        setTyping(false)
        addMsg('system', 'Нет соединения. Переподключение...')
      }
    }
  }

  function handleSubmit(e) {
    e.preventDefault()
    sendMessage(input)
  }

  // ── Derived labels ─────────────────────────────────
  const headerTitle = mode === 'general'
    ? 'TourRhythm AI'
    : cityName ? `AI · ${cityName.toUpperCase()}` : 'AI · МАРШРУТ'

  const headerSub = mode === 'general'
    ? 'Помощник по путешествиям'
    : live ? 'В поездке — активный агент' : 'Агент маршрута'

  const statusDot = connected ? T.statusOn : reconnectIn ? T.statusWait : T.statusOff
  const statusLabel = connected ? 'ОНЛАЙН' : reconnectIn ? `${reconnectIn}с` : 'ОФЛАЙН'

  // ── Render ─────────────────────────────────────────
  return (
    <div style={{
      display: 'flex', flexDirection: 'column',
      /* Fill the scroll container on desktop (flex: 1 works now that phone has explicit height).
         On mobile it falls back to 100svh minus the 64px tab bar. */
      height: '100%',
      minHeight: 'calc(100svh - 64px)',
      background: T.bg, overflow: 'hidden',
    }}>
      {/* Header */}
      <div style={{
        padding: '13px 18px 11px',
        borderBottom: `1px solid ${T.hairline}`,
        display: 'flex', alignItems: 'center', gap: 11,
        flexShrink: 0,
      }}>
        <div style={{
          width: 36, height: 36, borderRadius: '50%',
          background: T.lime,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          flexShrink: 0,
        }}>
          <BotIcon color="#0A0B0C" />
        </div>

        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{
            fontFamily: 'Onest, sans-serif', fontWeight: 600,
            fontSize: 13, letterSpacing: '-0.01em',
            color: T.fg, textTransform: 'uppercase',
          }}>{headerTitle}</div>
          <div style={{
            fontSize: 10, color: T.fgMute,
            fontFamily: 'JetBrains Mono, monospace', marginTop: 1,
          }}>{headerSub}</div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 5, flexShrink: 0 }}>
          <div style={{
            width: 7, height: 7, borderRadius: '50%',
            background: statusDot,
          }} />
          <span style={{
            fontSize: 9, color: T.fgMute,
            fontFamily: 'JetBrains Mono, monospace',
          }}>{statusLabel}</span>
        </div>
      </div>

      {/* Messages */}
      <div
        className="chat-messages"
        style={{
          flex: 1, overflowY: 'auto',
          padding: '14px 16px 8px',
          display: 'flex', flexDirection: 'column', gap: 10,
        }}
      >
        {messages.length === 0 && (
          <div style={{
            flex: 1, display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center',
            padding: '48px 0', gap: 8, pointerEvents: 'none',
          }}>
            <div style={{
              fontFamily: 'Onest, sans-serif', fontWeight: 600,
              fontSize: 17, letterSpacing: '-0.02em',
              textTransform: 'uppercase', color: T.fg, opacity: 0.18,
            }}>Начни диалог</div>
            <div style={{
              fontSize: 11, color: T.fgMute, textAlign: 'center',
              fontFamily: 'JetBrains Mono, monospace', lineHeight: 1.6,
              maxWidth: 220, opacity: 0.7,
            }}>
              {mode === 'general'
                ? 'Спрашивай о любой стране, городе или бюджете'
                : 'Агент знает твой маршрут и может его изменить'}
            </div>
          </div>
        )}

        {messages.map(msg => (
          <MessageBubble key={msg.id} msg={msg} T={T} />
        ))}

        {typing && <TypingIndicator T={T} />}

        <div ref={bottomRef} />
      </div>

      {/* Chips */}
      <div
        className="chat-chips"
        style={{
          display: 'flex', gap: 6, overflowX: 'auto',
          padding: '8px 16px 6px', flexShrink: 0,
        }}
      >
        {chips.map(chip => (
          <button
            key={chip}
            onClick={() => sendMessage(chip)}
            disabled={typing}
            style={{
              flexShrink: 0, padding: '6px 12px',
              background: T.chipBg, border: `1px solid ${T.chipBorder}`,
              borderRadius: 99, cursor: typing ? 'default' : 'pointer',
              fontFamily: 'JetBrains Mono, monospace',
              fontSize: 10, color: T.fgMute,
              whiteSpace: 'nowrap', opacity: typing ? 0.4 : 1,
              transition: 'background 0.14s, border-color 0.14s',
            }}
            onMouseEnter={e => {
              if (!typing) {
                e.currentTarget.style.background     = T.chipHover
                e.currentTarget.style.borderColor    = T.lime
              }
            }}
            onMouseLeave={e => {
              e.currentTarget.style.background  = T.chipBg
              e.currentTarget.style.borderColor = T.chipBorder
            }}
          >
            {chip}
          </button>
        ))}
      </div>

      {/* Input bar */}
      <form
        onSubmit={handleSubmit}
        style={{
          display: 'flex', gap: 10, alignItems: 'flex-end',
          padding: '8px 16px 8px',
          borderTop: `1px solid ${T.hairline}`,
          flexShrink: 0, background: T.bg,
        }}
      >
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder={mode === 'general' ? 'Задай вопрос…' : 'Напиши агенту…'}
          disabled={typing}
          style={{
            flex: 1, height: 42,
            background: T.inputBg,
            border: `1.5px solid ${T.inputBorder}`,
            borderRadius: 12,
            padding: '0 14px',
            fontFamily: 'Onest, sans-serif',
            fontSize: 14, color: T.fg,
            outline: 'none',
            transition: 'border-color 0.14s',
          }}
          onFocus={e  => { e.currentTarget.style.borderColor = T.lime }}
          onBlur={e   => { e.currentTarget.style.borderColor = T.inputBorder }}
        />
        <button
          type="submit"
          disabled={!input.trim() || typing}
          style={{
            width: 42, height: 42, borderRadius: '50%',
            flexShrink: 0, border: 'none',
            background: input.trim() && !typing ? T.lime : T.surface,
            color: T.fg,
            cursor: input.trim() && !typing ? 'pointer' : 'default',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            transition: 'background 0.14s',
          }}
        >
          <SendIcon />
        </button>
      </form>

      {/* Privacy & Trust: честная пометка о сохранении диалогов (волна 1). */}
      <div style={{
        flexShrink: 0, background: T.bg,
        padding: '0 16px 10px', textAlign: 'center',
      }}>
        <span style={{
          fontSize: 9, color: T.fgMute,
          fontFamily: 'JetBrains Mono, monospace', letterSpacing: '0.02em',
        }}>
          Диалоги сохраняются, чтобы TourRhythm становился лучше
        </span>
      </div>
    </div>
  )
}
