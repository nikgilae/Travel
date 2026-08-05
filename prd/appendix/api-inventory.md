# Реестр API (Backend)

> Все эндпоинты, кроме отмеченных «Нет», требуют заголовок `Authorization: Bearer <access_token>` (зависимость `get_current_user`).
> Базовый URL задаётся `VITE_API_URL` на фронте; версии API-префикса нет (маршруты монтируются без `/api/v1`).

## Аутентификация — `/auth`

| Метод | Путь | Авторизация | Запрос | Ответ | Описание |
|---|---|---|---|---|---|
| POST | `/auth/register` | Нет | `RegisterRequest {email, password}` | `TokenResponse` (201) | Регистрация; email должен быть уникален (иначе 409); пароль ≥12 симв., верхний/нижний регистр, цифра, спецсимвол |
| POST | `/auth/login` | Нет | `LoginRequest {email, password}` | `TokenResponse` (200) | Логин; при неверных email/пароле — единая ошибка 401 (без раскрытия, что именно неверно) |

`TokenResponse`: `user_id`, `access_token`, `token_type="bearer"`, `expires_in` (сек, = 180 мин), `is_first_login` (true, если у пользователя ещё нет ни одной поездки — используется фронтом для маршрутизации в онбординг vs дашборд).

## Поездки — `/trips`

| Метод | Путь | Запрос | Ответ | Описание |
|---|---|---|---|---|
| POST | `/trips` | `TripCreate` | `TripResponse` (201) | Создать поездку. Проверяет существование страны/города |
| GET | `/trips` | – | `list[TripResponse]` | Список поездок текущего пользователя |
| GET | `/trips/{trip_id}` | – | `TripWithPOIsResponse` | Поездка + все привязанные POI (отсортированы по `sequence_order`) |
| PUT | `/trips/{trip_id}` | `TripUpdate` (частичное) | `TripResponse` | Обновление полей поездки |
| DELETE | `/trips/{trip_id}` | – | 204 | Удаление (каскадно удаляет `trip_pois`) |
| POST | `/trips/{trip_id}/pois` | `TripPOICreate` | `TripPOIWithWarningsResponse` (201) | Добавить POI в поездку → в ответе сразу возвращаются `contextual_warnings` (правила этой точки) — «Core Feature» |
| DELETE | `/trips/{trip_id}/pois/{poi_id}` | – | 204 | Жёсткое удаление POI из поездки (полностью убирает строку) |
| POST | `/trips/{trip_id}/pois/swap` | `TripPOISwapRequest {promote_poi_id, demote_poi_id?}` | `TripWithPOIsResponse` | «Заменить POI» — промоутит запасную точку в основные (опционально демоутит другую) |
| POST | `/trips/{trip_id}/generate` | `TripGenerateRequest {interests, notes?}` | `TripGenerateResponse` | Запуск AI-генерации маршрута (см. ниже) |
| POST | `/trips/{trip_id}/days/{day_number}/finalize` | `TripDayFinalizeRequest {poi_ids: UUID[]}` | `TripWithPOIsResponse` | Финализировать день по явному списку точек (порядок — стартовая точка пользователя, дальше nearest-neighbor) |
| POST | `/trips/{trip_id}/days/{day_number}/finalize/auto-main` | – | `TripWithPOIsResponse` | «Сделай как ИИ предложил» — автоматически берёт все точки со статусом `main` и финализирует |

### Генерация маршрута — детальный алгоритм
`POST /trips/{trip_id}/generate`:
1. Требует, чтобы у поездки были заполнены `start_date` и `end_date` (иначе — необработанный `ValueError` → 500, известный баг).
2. `calculated_days = (end_date - start_date).days + 1`.
3. **Авто-обогащение города**: если `city.last_enriched_at` пусто или старше `ENRICH_COOLDOWN_HOURS` (по умолчанию 24 ч) — запускается сбор POI из Google Places (см. «Обогащение города» ниже); сбой обогащения не блокирует генерацию.
4. Если после этого в городе 0 точек — 404 «В нашей базе нет мест для города X…».
5. В LLM передаётся не более `MAX_POIS_FOR_AI=100` точек (случайная выборка при превышении), каждая — с привязанными правилами.
6. Промпт на русском языке требует: ≥5 POI/день, `activity_level` 1–5 на каждую точку, 3–4 «основных» + 3–4 «запасных» POI на день, без повторов точек за всю поездку, соблюдение правил (`⚠️ ОБЯЗАТЕЛЬНО` для строгих, `💡 Рекомендация` для нестрогих).
7. Ответ ИИ — строгий JSON; при ошибке парсинга JSON генерация не падает — возвращается «пустая» структура с сообщением об ошибке в `summary`.
8. Результат сохраняется в `trip_pois`: основные точки получают `sequence_order` 1,2,3…; запасные — `main_order + 100` (чтобы номера никогда не пересекались); каждая точка сохраняется в отдельном savepoint — битая запись от ИИ не рушит всю пачку; уже существующие в поездке точки пропускаются (идемпотентность).
9. `trip.ai_summary` и `trip.total_budget_estimate` берутся из ответа ИИ.

## Гео-справочник — без общего префикса (`app/api/geography.py`)

| Метод | Путь | Запрос | Ответ | Описание |
|---|---|---|---|---|
| POST | `/countries` | `CountryCreate` | `CountryResponse` (201) | Создать страну; имя уникально глобально |
| GET | `/countries` | – | `list[CountryResponse]` | Список всех стран |
| POST | `/cities` | `CityCreate` | `CityResponse` (201) | Создать город; имя уникально в рамках страны |
| GET | `/countries/{country_id}/cities` | – | `list[CityResponse]` | Города страны |
| GET | `/cities/{city_id}/context-info` | – | `CityContextResponse` | «Что нужно знать о городе»: контент города + все правила города с флагом строгости + статичный дисклеймер про актуальность правил |

## Точки интереса (POI) — `/pois`

| Метод | Путь | Запрос | Ответ | Описание |
|---|---|---|---|---|
| GET | `/pois/search` | `query`, `city_id` | `POISearchResponse` | Живой поиск через Google Places (результаты НЕ сохраняются в БД) |
| POST | `/pois` | `POICreate` | `POIResponse` (201) | Ручное создание POI (координаты → PostGIS-геометрия) |
| GET | `/pois/nearby` | `lat`, `lon`, `radius_meters (50–50000)` | `list[POIResponse]` | Геопоиск по БД через PostGIS `ST_DWithin` (метры, geography-cast) |
| GET | `/pois` | – | `list[POIResponse]` | Список всех POI |
| GET | `/pois/{poi_id}` | – | `POIResponse` | Детали одной точки |
| POST | `/pois/enrich/{city_id}` | – | `{status, message, city}` | Ручной запуск обогащения города из Google Places |

### Обогащение города («Enrich»)
20 параллельных текстовых запросов к Google Places (на русском) по категориям: достопримечательности, ист. памятники, смотровые площадки, религиозные объекты, парки, природа, пляжи, активный отдых, музеи, галереи, театры, топ-рестораны, кафе, стрит-фуд/рынки, нац. кухня, бары, ночная жизнь, сувенирные рынки, спа, зоопарки/аквариумы. Отказ одной категории не блокирует остальные (`return_exceptions=True`). Дедупликация по `google_place_id`, затем по паре `(name, city_id)`. Одна транзакция коммитится только если добавлена хотя бы одна новая точка.

## Правила — `/rules`

| Метод | Путь | Запрос | Ответ | Описание |
|---|---|---|---|---|
| POST | `/rules` | `RuleCreate {content}` | `RuleResponse` (201) | Создать переиспользуемое правило |
| POST | `/rules/countries/{country_id}` | `AttachRuleRequest {rule_id, is_strict=true}` | `{"status":"attached"}` (201) | Привязать правило к стране |
| POST | `/rules/cities/{city_id}` | `AttachRuleRequest` | `{"status":"attached"}` (201) | Привязать правило к городу |
| POST | `/rules/pois/{poi_id}` | `AttachRuleRequest` | `{"status":"attached"}` (201) | Привязать правило к точке |
| GET | `/rules` | – | `list[RuleResponse]` | Все правила |
| GET | `/rules/{rule_id}` | – | `RuleResponse` | Одно правило |

Правило — это единая переиспользуемая сущность (текст), а флаг **«строгое/рекомендация»** хранится не в самом правиле, а в конкретной привязке (страна/город/точка) — одно и то же правило может быть строгим в одной стране и рекомендацией в другой.

Точки поверхностного проявления правил в продукте:
- В промпте AI-генерации (city-level и POI-level правила).
- В ответе `POST /trips/{trip_id}/pois` — `contextual_warnings` сразу после добавления точки.
- В `GET /cities/{city_id}/context-info` — общий экран «что нужно знать о городе».
- Для правил уровня страны отдельного GET-эндпоинта нет (сервис-метод есть, роут не выставлен).

## AI-чат — `/chat`

| Метод | Путь | Авторизация | Запрос/протокол | Описание |
|---|---|---|---|---|
| POST | `/chat/general` | Bearer | `GeneralChatRequest {message, history[]}` | Свободный чат без привязки к поездке. История усекается до 20 последних сообщений. `max_tokens=600`, без function calling |
| WS | `/trips/{trip_id}/chat` | Токен в query-параметре `?token=` | Текстовые сообщения (plain text, не JSON) | Стейтфул-агент с 3 инструментами (см. ниже) |

### AI-инструменты (function calling)

| Инструмент | Параметры | Делегирует в | Поведение |
|---|---|---|---|
| `tool_update_trip_info` | `trip_id`, `user_id`, `budget?`, `purpose?` | `TripService.update` | Обновляет только непустые поля |
| `tool_auto_finalize_day` | `trip_id`, `user_id`, `day_number` | `TripService.auto_finalize_main_pois` | Тот же nearest-neighbor алгоритм, что и REST-эндпоинт |
| `tool_remove_poi_from_day` | `trip_id`, `user_id`, `poi_id` | `TripService.remove_poi_from_day` | «Мягкое» удаление — точка не стирается, а переводится в `additional`, `is_selected=False` |

Все три инструмента перехватывают исключения и возвращают `{"status":"error","error":"..."}` обратно модели — ошибка не роняет WebSocket-соединение, а обрабатывается диалогово. Правила агента: брать `poi_id` только из скрытого контекста (никогда не выдумывать), никогда не показывать пользователю сырые UUID, ссылаться на места только по названию.

## Места (Google Maps прокси) — `/places`

| Метод | Путь | Запрос | Описание |
|---|---|---|---|
| GET | `/places/find` | `input` | Найти `place_id` по текстовому описанию места (404, если ничего не найдено) |
| GET | `/places/details` | `place_id` | Детали места: рейтинг, адрес, часы работы, фото-ссылки, редакционное описание (502 при ошибке Google) |
| GET | `/places/nearby` | `lat`, `lon`, `radius (100–10000, default 1000)`, `type?` | Ближайшие места (язык ответа — русский) |
| GET | `/places/photo` | `photo_reference`, `maxwidth (1–1600, default 400)` | Стриминг бинарного изображения |

## Мониторинг

| Метод | Путь | Авторизация | Описание |
|---|---|---|---|
| POST | `/client-errors` | Нет (может происходить до логина) | Приём JS-ошибок с фронта (`onerror`/`unhandledrejection`), пересылается в Sentry |
| GET | `/health` | Нет | `SELECT 1` в БД, статус `ok`/`degraded` |

## Обработка ошибок (глобально)

| Исключение | HTTP | error_code |
|---|---|---|
| `NotFoundException` | 404 | `RESOURCE_NOT_FOUND` |
| `AlreadyExistsException` | 409 | `ALREADY_EXISTS` |
| `UnauthorizedException` | 401 | `UNAUTHORIZED` (+ заголовок `WWW-Authenticate: Bearer`) |
| `ForbiddenException` | 403 | `FORBIDDEN` (определён, но нигде не используется) |
| `RequestValidationError` (Pydantic) | 422 | `VALIDATION_FAILED` (+ массив `details[]`) |
| `SQLAlchemyError` | 500 | `DATABASE_ERROR` (+ алерт в Sentry/Telegram) |
| Прочие `Exception` | 500 | `INTERNAL_ERROR` (+ алерт в Sentry/Telegram) |
