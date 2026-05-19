# Берем легкий официальный образ Python
FROM python:3.12-slim

# Устанавливаем системные пакеты (нужны для компиляции драйвера базы данных)
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Копируем быстрый пакетный менеджер uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Создаем рабочую папку
WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости системно (виртуальное окружение в докере не нужно)
RUN uv pip install --system --no-cache -r pyproject.toml

# Копируем весь остальной код
COPY . .

# Запускаем FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]