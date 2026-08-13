import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import './OnboardingFinalQuestion.css'
import { useOnboarding } from '../store/onboardingStore.jsx'

const API_BASE = import.meta.env.VITE_API_URL

// Бюджет времени на ОДИН запрос (создание поездки ИЛИ генерация — таймер
// перезапускается перед каждым из них отдельно). Бэкенд укладывает саму
// AI-генерацию в свой бюджет ~40 с (AI_GENERATION_BUDGET_SECONDS); 45 с
// на клиенте оставляют небольшой запас на сеть, не обрывая честный ответ.
const ATTEMPT_BUDGET_MS = 45000

function getToken() {
  return localStorage.getItem('access_token') ?? ''
}

// ── Честные ошибки: разбор тела ответа и классификация ────────────────

/** Ошибка HTTP-запроса с распознанным человекочитаемым сообщением. */
class RequestFailedError extends Error {
  constructor(message, status, retryable) {
    super(message)
    this.name = 'RequestFailedError'
    this.status = status
    this.retryable = retryable
  }
}

const FALLBACK_MESSAGES = {
  400: 'Не хватает данных для маршрута — вернитесь на предыдущие шаги и укажите даты поездки.',
  404: 'В базе пока нет мест для этого города. Попробуйте выбрать другой город или загляните позже.',
  502: 'Сервис подбора мест сейчас недоступен. Попробуйте ещё раз.',
}

function fallbackMessage(status) {
  return FALLBACK_MESSAGES[status] ?? `Не получилось выполнить запрос (код ${status}). Попробуйте ещё раз.`
}

function kindForStatus(status) {
  if (status === 400) return 'no_dates'
  if (status === 404) return 'cold_city'
  if (status === 502) return 'ai_failure'
  return 'server_error'
}

/**
 * Достаёт человекочитаемое сообщение из тела ответа об ошибке.
 * Бэкенд отдаёт RFC7807-подобный формат `{ error_code, message, detail? }`,
 * но читаем защитно: где-то может не быть `message`, где-то `detail` —
 * либо строка, либо объект; на случай смены формата — ещё и `title`.
 *
 * `retryable`: сервер явно шлёт `true` только для 502 (сбой AI — временный).
 * Для остальных статусов по умолчанию НЕ считаем повтор осмысленным —
 * иначе кнопка «Попробовать снова» уводит в бесконечный цикл одной и той же
 * ошибки (нет дат / холодный город не чинятся повторным запросом).
 */
async function parseErrorResponse(res) {
  const body = await res.json().catch(() => null)

  let message = null
  let retryable = res.status >= 500 || res.status === 429

  if (body && typeof body === 'object') {
    if (typeof body.message === 'string' && body.message.trim()) {
      message = body.message
    } else if (typeof body.detail === 'string' && body.detail.trim()) {
      message = body.detail
    } else if (body.detail && typeof body.detail === 'object' && typeof body.detail.message === 'string') {
      message = body.detail.message
    } else if (typeof body.title === 'string' && body.title.trim()) {
      message = body.title
    }

    if (typeof body.retryable === 'boolean') {
      retryable = body.retryable
    }
  }

  return new RequestFailedError(message ?? fallbackMessage(res.status), res.status, retryable)
}

// ── Loading screen ─────────────────────────────────────────

function LoadingScreen({ cityName, onCancel }) {
  const cancelBtnRef = useRef(null)

  // Фокус на «Отменить» — иначе клавиатурный пользователь застревает
  // на элементе, которого уже нет в DOM (форма скрыта под спиннером).
  useEffect(() => {
    cancelBtnRef.current?.focus()
  }, [])

  return (
    <div className="ofq-app">
      <div
        className="ofq-phone"
        role="status"
        aria-live="polite"
        style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100svh' }}
      >
        <div aria-hidden="true" style={{
          width: 64, height: 64, borderRadius: '50%',
          border: '3px solid rgba(185,255,61,0.2)',
          borderTopColor: '#B9FF3D',
          animation: 'ofq-spin 0.9s linear infinite',
          marginBottom: 28,
        }} />
        <div style={{
          fontFamily: 'var(--font-ui)', fontWeight: 600, fontSize: 20,
          color: '#0A0B0C', letterSpacing: '-0.005em',
          marginBottom: 10, textAlign: 'center',
        }}>
          Складываю маршрут…
        </div>
        <div style={{
          fontFamily: 'var(--font-mono)', fontSize: 11,
          color: '#9097A0', letterSpacing: '0.12em', textTransform: 'uppercase',
          marginBottom: 32,
        }}>
          {cityName ? cityName : '···'}
        </div>
        <button
          type="button"
          ref={cancelBtnRef}
          onClick={onCancel}
          style={{
            background: 'none',
            border: '1px solid #E8EAEC',
            borderRadius: 10,
            padding: '10px 22px',
            fontFamily: 'var(--font-ui)', fontSize: 13, fontWeight: 500,
            color: '#5B6066', cursor: 'pointer',
            transition: 'border-color 0.12s ease, color 0.12s ease',
          }}
          onMouseEnter={e => { e.currentTarget.style.borderColor = '#C7CBD1'; e.currentTarget.style.color = '#0A0B0C' }}
          onMouseLeave={e => { e.currentTarget.style.borderColor = '#E8EAEC'; e.currentTarget.style.color = '#5B6066' }}
        >
          Отменить
        </button>
      </div>
    </div>
  )
}

// ── Error screen ────────────────────────────────────────────

function ErrorScreen({ message, retryable, kind, onRetry, onEdit, onBack }) {
  const primaryRef   = useRef(null)
  const secondaryRef = useRef(null)

  // Для «нет дат»/«холодный город» повтор с этого экрана ничего не чинит —
  // проблема в данных, заданных на предыдущих шагах. Первичное действие —
  // вернуться туда, а не долбить ту же ошибку кнопкой «Попробовать снова».
  const showBackToSettings = kind === 'no_dates' || kind === 'cold_city'
  const showRetry = !showBackToSettings && retryable

  useEffect(() => {
    (primaryRef.current ?? secondaryRef.current)?.focus()
  }, [])

  return (
    <div className="ofq-app">
      <div
        className="ofq-phone"
        role="alert"
        style={{
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          minHeight: '100svh', padding: '0 28px', boxSizing: 'border-box', textAlign: 'center',
        }}
      >
        <div aria-hidden="true" style={{
          width: 56, height: 56, borderRadius: '50%',
          background: '#FBE5E7', border: '1px solid rgba(180,51,64,0.3)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 22, fontWeight: 600, color: '#B43340',
          marginBottom: 22, fontFamily: 'var(--font-ui)',
        }}>
          !
        </div>
        <h1 style={{
          fontFamily: 'var(--font-ui)', fontWeight: 600, fontSize: 19,
          color: '#0A0B0C', letterSpacing: '-0.008em', margin: '0 0 10px',
        }}>
          Не получилось создать маршрут
        </h1>
        <div style={{
          fontFamily: 'var(--font-ui)', fontSize: 14, color: '#5B6066',
          lineHeight: 1.55, marginBottom: 28, maxWidth: 320,
        }}>
          {message}
        </div>

        {showBackToSettings && (
          <button
            type="button"
            ref={primaryRef}
            onClick={onBack}
            style={{
              width: '100%', maxWidth: 320, height: 44,
              background: '#B9FF3D',
              border: '1px solid #B9FF3D',
              borderRadius: 10,
              fontWeight: 500, fontSize: 14, letterSpacing: '-0.005em',
              color: '#0A0B0C',
              cursor: 'pointer',
              marginBottom: 14,
              fontFamily: 'var(--font-ui)',
              transition: 'background 0.12s ease',
            }}
            onMouseEnter={e => { e.currentTarget.style.background = '#A8F02C'; e.currentTarget.style.borderColor = '#A8F02C' }}
            onMouseLeave={e => { e.currentTarget.style.background = '#B9FF3D'; e.currentTarget.style.borderColor = '#B9FF3D' }}
          >
            ← Вернуться к настройкам
          </button>
        )}

        {showRetry && (
          <button
            type="button"
            ref={primaryRef}
            onClick={onRetry}
            style={{
              width: '100%', maxWidth: 320, height: 44,
              background: '#B9FF3D',
              border: '1px solid #B9FF3D',
              borderRadius: 10,
              fontWeight: 500, fontSize: 14, letterSpacing: '-0.005em',
              color: '#0A0B0C',
              cursor: 'pointer',
              marginBottom: 14,
              fontFamily: 'var(--font-ui)',
              transition: 'background 0.12s ease',
            }}
            onMouseEnter={e => { e.currentTarget.style.background = '#A8F02C'; e.currentTarget.style.borderColor = '#A8F02C' }}
            onMouseLeave={e => { e.currentTarget.style.background = '#B9FF3D'; e.currentTarget.style.borderColor = '#B9FF3D' }}
          >
            Попробовать снова
          </button>
        )}

        <button
          type="button"
          ref={secondaryRef}
          onClick={onEdit}
          style={{
            background: 'none', border: 'none', color: '#5B6066',
            fontSize: 13, cursor: 'pointer', padding: 0, fontFamily: 'inherit',
          }}
        >
          ← Изменить ответ
        </button>
      </div>
    </div>
  )
}

// ── Main component ─────────────────────────────────────────

export default function OnboardingFinalQuestion({ city, groupType, rhythm, onBack }) {
  const navigate             = useNavigate()
  const { data, update }     = useOnboarding()

  const [text, setText]     = useState('')
  const [status, setStatus] = useState('idle') // 'idle' | 'loading' | 'error'
  const [error, setError]   = useState(null)   // { message, retryable, kind }

  // Флаги/данные, которые не должны триггерить ре-рендеры и должны быть
  // видны синхронно (в т.ч. между двумя быстрыми кликами по кнопке).
  // id уже созданной поездки НЕ хранится в ref — он в onboarding-сторе
  // (data.created_trip_id), потому что ref живёт только до размонтирования
  // этого экрана, а «← Назад» → «← Изменить настройки» → «Создать маршрут»
  // размонтирует его за три клика и создал бы вторую поездку.
  const inFlightRef         = useRef(false)   // защита от двойного сабмита
  const abortControllerRef  = useRef(null)
  const budgetTimerRef      = useRef(null)
  const cancelledByUserRef  = useRef(false)
  const mountedRef          = useRef(true)

  const cityName = city?.n ?? 'город'

  // Размонтирование страницы во время генерации не должно оставлять
  // висящий запрос/таймер и не должно триггерить setState в никуда.
  // Важно: тело эффекта ОБЯЗАНО выставлять mountedRef.current = true —
  // под StrictMode (см. main.jsx) React в dev делает mount → cleanup →
  // mount, а ref между этими фазами не пересоздаётся. Без этой строки
  // ref навсегда остаётся false после первого прохода, и все ветки выхода
  // (success/error/timeout/cancel) молча умирают за проверкой mountedRef.
  useEffect(() => {
    mountedRef.current = true
    return () => {
      mountedRef.current = false
      clearBudgetTimer()
      abortControllerRef.current?.abort()
      abortControllerRef.current = null
    }
  }, [])

  function clearBudgetTimer() {
    if (budgetTimerRef.current) {
      clearTimeout(budgetTimerRef.current)
      budgetTimerRef.current = null
    }
  }

  function handleCancel() {
    if (!inFlightRef.current) return
    cancelledByUserRef.current = true
    clearBudgetTimer()
    abortControllerRef.current?.abort()
  }

  async function handleSubmit(notes) {
    // useRef, а не useState: должен сработать синхронно на второй клик,
    // даже если React ещё не успел перерисовать компонент после первого.
    if (inFlightRef.current) return
    inFlightRef.current = true

    update({ notes })
    cancelledByUserRef.current = false
    setStatus('loading')
    setError(null)

    const controller = new AbortController()
    abortControllerRef.current = controller

    // Перезапускается перед каждым из двух запросов отдельно (см. комментарий
    // у ATTEMPT_BUDGET_MS) — иначе создание поездки съедает часть бюджета,
    // отведённого на честный ответ от AI, и клиент обрывает генерацию
    // за секунды до валидного ответа при полностью рабочем сервисе.
    function startBudgetTimer() {
      clearBudgetTimer()
      budgetTimerRef.current = setTimeout(() => controller.abort(), ATTEMPT_BUDGET_MS)
    }

    let tripId = data.created_trip_id

    try {
      startBudgetTimer()

      // Поездка уже была создана в этом прохождении онбординга (успешный
      // POST /trips, но упавшая генерация) — повтор запускает только
      // /generate, второй поездки не создаём.
      if (!tripId) {
        const body = {
          country_id:        data.country_id,
          city_id:           data.city_id,
          purpose:           data.purpose           ?? 'leisure',
          budget:            data.budget            ?? 'medium',
          group_size:        data.group_size        ?? 1,
          other_information: data.other_information ?? [],
          start_date:        data.start_date        ?? null,
          end_date:          data.end_date          ?? null,
        }

        const res = await fetch(`${API_BASE}/trips`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${getToken()}`,
          },
          body: JSON.stringify(body),
          signal: controller.signal,
        })

        if (!res.ok) throw await parseErrorResponse(res)

        const trip = await res.json()
        tripId = trip.id
        update({ created_trip_id: trip.id })

        localStorage.setItem('trip_display_data', JSON.stringify({ city, groupType, rhythm }))

        let tripMeta = {}
        try {
          tripMeta = JSON.parse(localStorage.getItem('trip_meta') ?? '{}')
        } catch {
          tripMeta = {}
        }
        tripMeta[trip.id] = { cityName: city?.n ?? null, city, groupType, rhythm }
        localStorage.setItem('trip_meta', JSON.stringify(tripMeta))
      }

      startBudgetTimer()

      const genRes = await fetch(`${API_BASE}/trips/${tripId}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${getToken()}`,
        },
        body: JSON.stringify({
          interests: data.interests ?? [],
          notes: notes || null,
        }),
        signal: controller.signal,
      })

      if (!genRes.ok) throw await parseErrorResponse(genRes)

      clearBudgetTimer()
      abortControllerRef.current = null
      inFlightRef.current = false
    } catch (err) {
      clearBudgetTimer()
      abortControllerRef.current = null
      inFlightRef.current = false

      if (err && err.name === 'AbortError') {
        if (cancelledByUserRef.current) {
          // Пользователь сам нажал «Отменить» — это не ошибка,
          // просто честно возвращаемся к форме с сохранённым текстом.
          cancelledByUserRef.current = false
          if (mountedRef.current) setStatus('idle')
          return
        }
        if (mountedRef.current) {
          setError({
            message: 'Не уложились по времени — сервис отвечает слишком долго. Попробуйте ещё раз.',
            retryable: true,
            kind: 'timeout',
          })
          setStatus('error')
        }
        return
      }

      // Протухший/невалидный токен — незачем крутить пользователя по кругу
      // одной и той же 401/403, отправляем на логин.
      if (err instanceof RequestFailedError && (err.status === 401 || err.status === 403)) {
        localStorage.removeItem('access_token')
        navigate('/login', { replace: true })
        return
      }

      if (!mountedRef.current) return

      if (err instanceof RequestFailedError) {
        setError({ message: err.message, retryable: err.retryable, kind: kindForStatus(err.status) })
      } else {
        setError({
          message: 'Не удалось связаться с сервером. Проверьте подключение и попробуйте ещё раз.',
          retryable: true,
          kind: 'network',
        })
      }
      setStatus('error')
      return
    }

    // До сюда доходим только если оба запроса завершились успешно.
    // navigate() — намеренно вне try/catch: синхронное исключение при
    // навигации не должно репортиться как «не удалось связаться с сервером».
    if (!mountedRef.current) return
    localStorage.setItem('current_trip_id', tripId)
    navigate(`/trip/${tripId}/plan`, { state: { city, groupType, rhythm } })
  }

  if (status === 'loading') {
    return <LoadingScreen cityName={cityName} onCancel={handleCancel} />
  }

  if (status === 'error' && error) {
    return (
      <ErrorScreen
        message={error.message}
        retryable={error.retryable}
        kind={error.kind}
        onRetry={() => handleSubmit(text)}
        onEdit={() => { setError(null); setStatus('idle') }}
        onBack={onBack}
      />
    )
  }

  return (
    <div className="ofq-app">
      <div className="ofq-phone">

        {/* Progress bar */}
        <div style={{ padding: '20px 22px 0' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <button type="button" onClick={onBack} style={{
              background: 'none', border: 'none', color: '#5B6066',
              fontSize: 13, cursor: 'pointer', padding: 0, fontFamily: 'inherit',
            }}>← Назад</button>
            <span style={{
              fontFamily: 'var(--font-mono)', fontSize: 11, color: '#9097A0',
              letterSpacing: '0.1em',
            }}>ШАГ 5 / 5</span>
          </div>
          <div style={{ height: 4, background: '#F1F3F5', borderRadius: 2, overflow: 'hidden' }}>
            <div style={{ height: '100%', width: '100%', background: '#B9FF3D', borderRadius: 2 }} />
          </div>
        </div>

        {/* Content */}
        <div style={{ padding: '28px 22px 24px' }}>
          <div style={{
            fontFamily: 'var(--font-mono)', fontSize: 11, letterSpacing: '0.14em',
            textTransform: 'uppercase', color: '#9097A0', marginBottom: 10,
          }}>
            ПОЧТИ ГОТОВО
          </div>
          <h1 style={{
            fontSize: 26, fontWeight: 600, lineHeight: 1.2,
            letterSpacing: '-0.012em',
            color: '#0A0B0C', margin: '0 0 8px', fontFamily: 'var(--font-ui)',
          }}>
            Зачем ты едешь<br/>в {cityName}?
          </h1>
          <p style={{
            fontSize: 14, color: '#5B6066', lineHeight: 1.55, margin: '0 0 20px',
          }}>
            Чем честнее ответ — тем точнее маршрут.
          </p>

          <textarea
            value={text}
            onChange={e => setText(e.target.value)}
            placeholder="Хочу отдохнуть от работы, почувствовать другой ритм жизни…"
            rows={5}
            style={{
              width: '100%', padding: '14px 16px',
              background: '#FFFFFF',
              border: '1px solid #E8EAEC',
              borderRadius: 14, resize: 'none', outline: 'none',
              fontFamily: 'var(--font-ui)', fontSize: 14, lineHeight: 1.55,
              color: '#0A0B0C', boxSizing: 'border-box',
              transition: 'border-color 0.12s ease, box-shadow 0.12s ease',
            }}
            onFocus={e => {
              e.target.style.borderColor = '#0A0B0C'
              e.target.style.boxShadow = '0 0 0 3px rgba(185,255,61,0.45)'
            }}
            onBlur={e => {
              e.target.style.borderColor = '#E8EAEC'
              e.target.style.boxShadow = 'none'
            }}
          />

          {text.length > 0 && (
            <div style={{
              marginTop: 10, padding: '10px 14px',
              background: '#F0FFD6',
              border: '1px solid rgba(185,255,61,0.4)',
              borderRadius: 10, fontSize: 12, color: '#1B2A0A', lineHeight: 1.4,
            }}>
              ИИ учтёт твой запрос при составлении маршрута
            </div>
          )}
        </div>

        {/* Sticky CTA */}
        <div style={{
          position: 'sticky', bottom: 0,
          padding: '16px 22px 28px',
          background: 'linear-gradient(to top, #F6F7F9 75%, transparent)',
        }}>
          <button
            type="button"
            onClick={() => handleSubmit(text)}
            style={{
              width: '100%', height: 44,
              background: '#B9FF3D',
              border: '1px solid #B9FF3D',
              borderRadius: 10,
              fontWeight: 500, fontSize: 14, letterSpacing: '-0.005em',
              color: '#0A0B0C',
              cursor: 'pointer',
              transition: 'background 0.12s ease, transform 0.06s ease',
              fontFamily: 'var(--font-ui)',
            }}
            onMouseEnter={e => { e.currentTarget.style.background = '#A8F02C'; e.currentTarget.style.borderColor = '#A8F02C' }}
            onMouseLeave={e => { e.currentTarget.style.background = '#B9FF3D'; e.currentTarget.style.borderColor = '#B9FF3D' }}
          >
            Создать маршрут
          </button>
        </div>

      </div>
    </div>
  )
}
