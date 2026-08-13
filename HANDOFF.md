# HANDOFF — TourRhythm, волна 1, «чёрный ящик» наблюдаемости

> Этот файл — точка входа для нового чата. Прочитай его целиком, затем 3 файла-артефакта ниже, и начинай реализацию с блока «Сегодня».

## Что это и где мы

TourRhythm — MVP планировщика путешествий (React 19/Vite + FastAPI/PostgreSQL, деплой tourrhythm.ru).
Готовится **волна 1**: ~8 реальных пользователей, дедлайн 3 дня (с 2026-07-12).
Фаундер — соло вайбкодер, не программист: объясняй просто, показывай что и куда.

Ветка: `fix/qa-findings-and-vpn-proxy`.

Пройдено два ревью (office-hours + plan-eng-review). Дизайн **APPROVED**, инженерный план **CLEARED**.
Осталось: **реализовать 13 задач T1–T13**. Их разбор — ниже.

## Три файла, которые надо прочитать первым делом

1. **Дизайн-док (что и зачем строим, все решения):**
   `~/.gstack/projects/nikgilae-Travel/nazar-berest-fix-qa-findings-and-vpn-proxy-design-20260712-125753.md`
   Секция в конце «Eng Review — принятые решения» — самое важное.
2. **Список задач T1–T13 (машиночитаемый, по строке на задачу):**
   `~/.gstack/projects/nikgilae-Travel/tasks-eng-review-20260713-003416.jsonl`
3. **Тест-план (что и где тестировать):**
   `~/.gstack/projects/nikgilae-Travel/nazar-berest-fix-qa-findings-and-vpn-proxy-eng-review-test-plan-20260713-120500.md`

Плюс `TODOS.md` в корне репо — отложенное (гидрация чата, заземление чата, приватность git, PostHog).

## Что строим (одной картинкой)

«Чёрный ящик» = сервер запоминает всё, что произошло с первыми пользователями:
- **Персист чата** — модель `Message`, пишется в оба чата (REST `/chat/general` и WS `/trips/{id}/chat`), write-only, UX не меняется.
- **Event-лог** — строки JSON в существующий логгер (логин, создание трипа, generate, финализация дня, удаление POI, сообщение).
- **Видимость ошибок** — Sentry, а если недоступен из РФ — 5xx уходит в Telegram-бот фаундера.
- **Пометка** в UI чата, что диалоги сохраняются.

## Порядок реализации (СТРОГО так)

### БЛОК «Сегодня» — до всего остального (безопасность + проверка прода)
- **T2 (P1)** — Postgres закрыть: в `backend/docker-compose.yml` порт сделать `127.0.0.1:5432:5432` + реальный пароль в `.env` (сейчас торчит наружу с паролем `postgres`).
- **T10 (P2)** — дампы убрать из git: `git rm --cached backend/backup.sql travel_companion_full.sql` + добавить `*.sql` в `.gitignore`.
- **T1 (P1)** — прод-preflight: сверить реальную версию миграций на проде (`alembic current`) — в репо ДВА head'а и стамп в дампе древний; прогнать `generate` по городам двух ретро-пользователей (в «полном» дампе 0 POI, всё держится на живом Google Places).
- **T13 (P1)** — правило процесса: пользователей и ретро-сессии пускать ТОЛЬКО после деплоя №2 (иначе первые диалоги потеряются).

### БЛОК «Дни 1–2» — backend, строго по очереди (общие файлы)
- **T3 (P1)** — `alembic merge heads`, затем миграция `messages` (поле `content` nullable, индексы `(trip_id, created_at)` и `(user_id, created_at)`); прогнать на копии дампа, перед прод-миграцией — `pg_dump`.
- **T4 (P1)** — модель `Message` + `MessageRepository` + хелпер `save_messages`. ВАЖНО: сырое `user_message` писать ДО вызова агента (иначе аварийные диалоги теряются), ответы/tool — по дельте `chat_history` после `process_message`, каждая запись в try/except (сбой записи НЕ должен ронять чат).
- **T6 (P1)** — `backend/app/core/events.py`: `log_event()` + константы имён; событие `day_finalized` логировать в `TripService` (не в роутере — финализация идёт через AI-тул по WS).
- **T5 (P1)** — Sentry init + generic `Exception`-handler с отправкой в Telegram + `capture_exception` в WS-except + инструментировать существующий `SQLAlchemyError`-handler в `main.py` (он сейчас глотает ошибку молча); `SENTRY_DSN`, `TG_*` в `Settings`.
- **T12 (P2)** — `chat_agent.py` переиспользует общий `AsyncOpenAI` из `services/ai.py`, свой удалить.
- **T11 (P1)** — полный набор тестов: `test_message`, `test_chat_general`, `test_chat_ws`, `test_events`, `test_error_handlers`. Две CRITICAL-регрессии: форма ответа general-чата и обычный WS-диалог. AI мокать в одной точке.

### БЛОК «Параллельно» — независимая полоса (можно в любой момент)
- **T7 (P2)** — логи на volume в `docker-compose` (`json-file`, ротация) — переживают redeploy. Access-логи НЕ включать (в WS-URL лежит JWT-токен).
- **T8 (P2)** — ошибки фронта: `window.onerror`/`onunhandledrejection` → POST на бэкенд → Sentry/лог (UI не меняет).
- **T9 (P2)** — однострочная пометка «Диалоги сохраняются, чтобы TourRhythm становился лучше» в `frontend/src/components/ChatScreen.jsx`.

## Красные линии (не нарушать)
- Access-логи uvicorn НЕ включать — токен в query утечёт на диск.
- Гидрацию истории чата НЕ добавлять — это TODO-1, не для этой волны (правило «не менять UX»).
- Перед прод-миграцией всегда `pg_dump`.
- Записи чата/событий — best-effort: их сбой никогда не должен ронять пользовательский поток.

## Команды окружения (из CLAUDE.md)
- Backend dev: `cd backend && uv run uvicorn app.main:app --reload`
- Тесты: `cd backend && uv run pytest`
- Миграция вверх: `cd backend && uv run alembic upgrade head`
- Новая миграция: `cd backend && uv run alembic revision --autogenerate -m "add messages"`

Внимание: у пользователя VPN через `socks://`-прокси, который ломает старт бэкенда и gstack browse. Если сервер не стартует из-за прокси — см. память `vpn-socks-proxy-env`.
