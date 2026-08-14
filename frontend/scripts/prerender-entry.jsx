// Точка входа для статического рендера лендинга на этапе сборки.
// Собирается Vite в SSR-режиме и выполняется в Node, браузер не нужен.
import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'
import LandingPage from '../src/pages/LandingPage.jsx'

// Анимации навешивают классы через IntersectionObserver, а эффекты при
// статическом рендере не выполняются. Поэтому доводим разметку до финального
// состояния руками: ровно то же, что делает ветка prefers-reduced-motion.
function toFinalState(html) {
  return html.replace(/class="s s(\d)([^"]*)"/g, (_m, n, rest) => {
    let cls = `s s${n}${rest}`
    if (!/\bon\b/.test(cls)) cls += ' on'
    if (n === '4') {
      if (!/\btalk\b/.test(cls)) cls += ' talk'
      if (!/\bdone\b/.test(cls)) cls += ' done'
    }
    return `class="${cls}"`
  })
}

export function render() {
  const html = renderToStaticMarkup(
    <MemoryRouter initialEntries={['/']}>
      <LandingPage />
    </MemoryRouter>,
  )
  return toFinalState(html)
}
