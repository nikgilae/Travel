import { useEffect, useRef } from 'react'
import { useLocation } from 'react-router-dom'

import { ymHit } from '../utils/metrika'

/**
 * Отправляет в Метрику просмотр при каждой смене роута.
 *
 * Первую локацию пропускаем: её уже засчитал вызов 'init' в index.html,
 * иначе главная считалась бы дважды и отказы поехали бы вниз.
 *
 * Ничего не рендерит, монтируется внутри BrowserRouter.
 */
export default function MetrikaTracker() {
  const location = useLocation()
  const prevPath = useRef(null)

  useEffect(() => {
    const path = location.pathname + location.search
    if (prevPath.current === null) {
      prevPath.current = path
      return
    }
    if (prevPath.current === path) return

    ymHit(path, prevPath.current)
    prevPath.current = path
  }, [location])

  return null
}
