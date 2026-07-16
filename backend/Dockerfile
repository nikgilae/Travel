# Берем легкий официальный образ Python
FROM python:3.12-slim

# Логи сразу летят в stdout без буферизации, .pyc не засоряют образ
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Устанавливаем системные пакеты (нужны для компиляции драйвера базы данных)
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем быстрый пакетный менеджер uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Создаем рабочую папку
WORKDIR /app

# Устанавливаем зависимости строго по uv.lock (воспроизводимая сборка), отдельным
# слоем от кода — пересобирается только когда меняются зависимости.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Копируем весь остальной код
COPY . .

# Доустанавливаем сам проект (без зависимостей — они уже есть в venv выше)
RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

# Непривилегированный пользователь для запуска приложения
RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Проверка живости сервера через собственный /health эндпоинт
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)" || exit 1

# Применяем миграции и запускаем FastAPI
ENTRYPOINT ["./entrypoint.sh"]
