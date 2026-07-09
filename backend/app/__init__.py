"""Инициализация пакета приложения.

Выполняется раньше любого подмодуля, а значит — раньше, чем создаётся первый
httpx-клиент (OpenAI в app.services.ai / app.services.chat_agent, Google Maps в
app.api.places и app.core.maps). Именно поэтому нормализация прокси живёт здесь.

Проблема: некоторые прокси-клиенты (v2ray/clash в режиме прокси, типичный кейс
при работе через VPN) экспортируют ALL_PROXY со схемой `socks://`, которую httpx
не понимает и падает с "Unknown scheme for proxy URL" уже на конструкции клиента.
Так как OpenAI-клиент создаётся на уровне модуля, это роняет импорт всего
приложения — сервер не стартует.

Решение: переписываем `socks://` в поддерживаемую httpx форму `socks5h://`
(суффикс `h` = резолвить DNS на стороне прокси, что нужно для гео-заблокированных
хостов). Если прокси не задан (VPN выключен) — нормализовывать нечего, клиенты
идут напрямую. Итог: бэкенд стартует и с VPN, и без него.
"""
import os

_PROXY_ENV_VARS = (
    "ALL_PROXY", "all_proxy",
    "HTTP_PROXY", "http_proxy",
    "HTTPS_PROXY", "https_proxy",
)


def _normalize_proxy_env() -> None:
    for var in _PROXY_ENV_VARS:
        value = os.environ.get(var)
        if value and value.startswith("socks://"):
            os.environ[var] = "socks5h://" + value[len("socks://"):]


_normalize_proxy_env()
