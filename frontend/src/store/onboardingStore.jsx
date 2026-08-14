import { createContext, useContext, useState } from 'react'

const INITIAL = {
  country_id:        null,
  city_id:           null,
  purpose:           'leisure', // "leisure" | "business" | "education" | "other"
  budget:            'medium',  // "low" | "medium" | "high"
  group_size:        1,
  other_information: ['balanced'], // default rhythm
  start_date:        null,      // "2026-06-01"
  end_date:          null,
  interests:         [],        // for /generate
  notes:             '',        // final open question — for /generate
  created_trip_id:   null,      // id поездки, уже созданной в текущем прохождении
                                 // онбординга (T5, "честные ошибки") — повтор после
                                 // сбоя генерации не должен создавать вторую поездку;
                                 // сбрасывается в null при смене city_id/country_id/дат
                                 // (см. App.jsx), иначе после смены города переиспользуется
                                 // старая поездка.
}

const OnboardingContext = createContext(null)

export function OnboardingProvider({ children }) {
  const [data, setData] = useState(INITIAL)

  function update(patch) {
    setData(prev => ({ ...prev, ...patch }))
  }

  function reset() {
    setData(INITIAL)
  }

  return (
    <OnboardingContext.Provider value={{ data, update, reset }}>
      {children}
    </OnboardingContext.Provider>
  )
}

export function useOnboarding() {
  const ctx = useContext(OnboardingContext)
  if (!ctx) throw new Error('useOnboarding must be used inside OnboardingProvider')
  return ctx
}
