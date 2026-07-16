#!/usr/bin/env bash
#
# Переносит данные из локальной БД (контейнер travel_db) в БД на сервере.
#
# Предполагается, что на сервере уже подняты контейнеры (docker compose up -d)
# и alembic-миграции применены entrypoint.sh — этот скрипт переносит только
# ДАННЫЕ поверх уже существующей схемы, чтобы схемой на сервере продолжал
# управлять alembic, а не замороженный дамп.
#
# Использование:
#   ./scripts/migrate_to_server.sh <ssh-host> <remote-path-to-backend>
#
# Пример:
#   ./scripts/migrate_to_server.sh deploy@1.2.3.4 /srv/tourry/backend
#
# Требования:
#   - локальный docker-compose с сервисом db (container_name: travel_db) запущен
#   - на сервере уже запущен docker compose (тот же container_name: travel_db)
#   - ssh-доступ на сервер настроен (ключи, а не пароль)

set -euo pipefail

SSH_HOST="${1:?Использование: $0 <ssh-host> <remote-path-to-backend>}"
REMOTE_PATH="${2:?Использование: $0 <ssh-host> <remote-path-to-backend>}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$BACKEND_DIR/.env"

if [[ ! -f "$ENV_FILE" ]]; then
    echo "Не найден $ENV_FILE" >&2
    exit 1
fi

# Берём POSTGRES_USER/POSTGRES_DB из локального .env
# shellcheck disable=SC1090
set -a
source "$ENV_FILE"
set +a

POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-travel_companion}"

DUMP_NAME="migrate_$(date +%Y%m%d_%H%M%S).dump"
LOCAL_DUMP_PATH="/tmp/$DUMP_NAME"

echo "==> Снимаю дамп данных из локального travel_db ($POSTGRES_DB)..."
docker exec -t travel_db pg_dump \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB" \
    --data-only \
    -F c \
    -f "/tmp/$DUMP_NAME"
docker cp "travel_db:/tmp/$DUMP_NAME" "$LOCAL_DUMP_PATH"
docker exec -t travel_db rm -f "/tmp/$DUMP_NAME"

echo "==> Копирую дамп на сервер ($SSH_HOST:$REMOTE_PATH)..."
scp "$LOCAL_DUMP_PATH" "$SSH_HOST:$REMOTE_PATH/$DUMP_NAME"

echo "==> Восстанавливаю данные в travel_db на сервере..."
ssh "$SSH_HOST" bash -s <<EOF
set -euo pipefail
cd "$REMOTE_PATH"
docker cp "$DUMP_NAME" travel_db:/tmp/$DUMP_NAME
docker exec -t travel_db pg_restore \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB" \
    --data-only \
    --disable-triggers \
    "/tmp/$DUMP_NAME"
docker exec -t travel_db rm -f "/tmp/$DUMP_NAME"
rm -f "$REMOTE_PATH/$DUMP_NAME"
EOF

rm -f "$LOCAL_DUMP_PATH"

echo "==> Готово. Данные перенесены в travel_db на $SSH_HOST."
