Работаем над Tourry (frontend: React 19 + Vite, backend: FastAPI + PostgreSQL — см. CLAUDE.md). Три связанных пункта, пройди их через product-translator → chief-architect → (гейт подтверждения) → implementation-engineer → reviewer.

## Пункт 1 — БАГ, не новая фича: неверное определение "первого входа"

Файлы:
- backend/app/services/auth.py (метод login) — is_first_login = (now - user.created_at) < 5 минут
- frontend/src/pages/LoginPage.jsx:23 — const destination = data.is_first_login ? '/onboarding' : '/dashboard/routes'
- frontend/src/pages/RegisterPage.jsx:80 — после регистрации всегда navigate('/onboarding')

Проблема: если онбординг занимает больше 5 минут, при повторном логине is_first_login становится false, и пользователь без единого маршрута попадает на /dashboard/routes вместо /onboarding.

Goal: is_first_login должен отражать реальный факт "у пользователя есть хотя бы один trip", а не время с момента регистрации.

Constraints: не трогать пароль/JWT-логику; не менять контракт /auth/register (там is_first_login=true всегда корректен).

Acceptance criteria:
- пользователь без trips после логина всегда попадает на /onboarding, независимо от времени, прошедшего с регистрации
- пользователь с хотя бы одним trip после логина попадает на /dashboard/routes
- существующие тесты auth не сломаны, добавлен тест на новый кейс (логин с trips / без trips после >5 минут)

## Пункт 2 — тривиальный фикс: убрать декоративную кнопку

Файл: frontend/src/pages/OnboardingStep1.jsx
- IconDots определён на строках 86-92
- Кнопка с этой иконкой — строки 520-528, в top bar, БЕЗ onClick (ничего не делает)

Goal: убрать кнопку и неиспользуемый IconDots из OnboardingStep1.jsx. На OnboardingStep2.jsx такой кнопки нет — не трогать.

Acceptance criteria: верстка top bar остаётся валидной (проверить, не завязана ли на кнопку flex-раскладка — сейчас justify-content: space-between с тремя элементами, после удаления решить, чем заменить третий элемент, чтобы заголовок не съехал по центру).

Это можно сразу отдать implementation-engineer, минуя chief-architect — изменение локальное и не архитектурное.

## Пункт 3 — вопрос архитектору, НЕ инструкция к реализации

Контекст: токен уже хранится в localStorage (frontend/src/utils/authToken.js), но ACCESS_TOKEN_EXPIRE_MINUTES=60 в backend/app/config.py, и refresh-токена в системе нет (backend/app/core/security.py — только access-токен). Поэтому пользователя каждый час всё равно выбрасывает на логин, вне зависимости от localStorage.

Вопрос для chief-architect: стоит ли сейчас реализовывать долгоживущую сессию (refresh-токен), и если да — какой вариант хранения (localStorage vs httpOnly cookie), какие tradeoffs по безопасности (XSS-риск при localStorage) и объём работ на бэке (новый эндпоинт /auth/refresh, ротация refresh-токенов, изменение CORS при переходе на cookie). Нужна рекомендация: делать сейчас или отложить, и если делать — то как.

Не приступай к реализации пункта 3, пока chief-architect не даст рекомендацию и (если решение архитектурное) пока я явно не подтвержу вариант.
