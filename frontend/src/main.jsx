import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { OnboardingProvider } from './store/onboardingStore.jsx'
import { installErrorReporter } from './utils/errorReporter.js'

// Глобальные ловушки ошибок фронта → бэкенд (T8). Ставим до рендера.
installErrorReporter()

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <OnboardingProvider>
      <App />
    </OnboardingProvider>
  </StrictMode>,
)
