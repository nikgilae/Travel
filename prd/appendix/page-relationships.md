# Карта переходов между страницами

```
/  (Вход)
 ├─ успех, is_first_login=true  → /onboarding
 ├─ успех, is_first_login=false → /dashboard/routes
 └─ ссылка «Регистрация»        → /register

/register (Регистрация)
 ├─ успех (register + auto-login) → /onboarding  (всегда, вне зависимости от is_first_login)
 └─ ссылка «Уже есть аккаунт»      → /

/onboarding (внутренний степ-машин, 6 шагов, без общей навигации)
 Шаг 1 (Куда едем) → Шаг 2 (С кем вы) → Шаг 3 (Когда едем) → Шаг 4 (В каком стиле)
   → Шаг 5 (Бюджет) → Шаг 6 (Финальный вопрос)
 Шаг 6, кнопка «Создать маршрут»:
   POST /trips → POST /trips/{id}/generate → успех → /trip/{id}/plan (state: city, groupType, rhythm)

/dashboard/routes (Дашборд, DashboardLayout — тёмный таб-бар)
 ├─ «＋ Создать маршрут»        → /onboarding
 ├─ карточка поездки «Открыть →» → /trip/{id}/plan (state: cached city/groupType/rhythm)
 ├─ пустое состояние: «Открыть чат» → /dashboard/chat
 ├─ таб-бар: Маршруты (текущая) / Чат → /dashboard/chat / Рядом → /dashboard/nearby
 └─ «Выйти» (в профиле) → очистка localStorage → /

/dashboard/chat (Общий чат, DashboardLayout)
 └─ таб-бар → /dashboard/routes | /dashboard/nearby

/dashboard/nearby (Рядом, без tripId, DashboardLayout)
 └─ таб-бар → /dashboard/routes | /dashboard/chat
 (кнопка «В ЧАТ →» скрыта, т.к. нет контекста поездки)

/trip/:id/plan (Экран маршрута, TripLayout — светлый таб-бар)
 ├─ back-стрелка          → /dashboard/routes
 ├─ таб-бар: Маршруты(=plan) / Чат → /trip/{id}/chat / Рядом → /trip/{id}/nearby
 ├─ «ДЕТАЛИ» на точке     → открывает PlaceDetailsModal (в рамках страницы, не переход)
 └─ «ЗАМЕНИТЬ» на точке   → POST /trips/{id}/pois/swap (без перехода)

/trip/:id/chat (Чат по поездке, TripLayout)
 ├─ таб-бар → /trip/{id}/plan | /trip/{id}/nearby
 └─ принимает location.state.prefill (из NearbyPage) для предзаполнения сообщения

/trip/:id/nearby (Рядом, с tripId, TripLayout)
 ├─ таб-бар → /trip/{id}/plan | /trip/{id}/chat
 └─ карточка места «В ЧАТ →» → /trip/{id}/chat  (state.prefill = 'Добавь "{name}" в мой маршрут')

* (любой другой путь) → редирект на /
```

## Связность данных между страницами

- **`trip_meta` (localStorage, словарь по trip_id)** — заполняется на Шаге 6 онбординга (`{cityName, city, groupType, rhythm}`), читается Дашбордом (для отображения города на карточке), Экраном маршрута и Чатом по поездке — чтобы не перезапрашивать эти данные с бэкенда.
- **`current_trip_id` / `trip_display_data`** — «последний созданный слот», перезаписывается при каждом новом онбординге.
- **`tripHistoryCache` (модульный кэш в памяти, keyed by tripId)** — история сообщений WS-чата поездки; переживает переключение вкладок в рамках SPA-сессии, но теряется при полной перезагрузке страницы (история чата не хранится на бэкенде для чтения).
- **Дашборд → Экран маршрута**: при клике на карточку поездки в `location.state` передаются кэшированные `city`/`groupType`/`rhythm`, чтобы избежать лишнего запроса.
- **Рядом → Чат по поездке**: передаёт `location.state.prefill` — единственный явный межстраничный «инжект данных» через router state, не через localStorage.
