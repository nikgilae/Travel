#!/usr/bin/env bash
# ВЫПОЛНЯТЬ НА НОУТБУКЕ, из папки frontend/ (или откуда угодно — путь
# ниже вычисляется относительно расположения самого скрипта).
#
#   frontend/deploy/deploy.sh
#
# Что делает, по шагам:
#   1. Собирает фронт локально (npm run build -> frontend/dist/)
#   2. Заливает dist/ на сервер В НОВУЮ папку releases/<таймстемп>
#      (старые релизы это НЕ трогает — если заливка оборвётся на
#      середине, сайт продолжит отдавать предыдущий рабочий релиз,
#      потому что символическая ссылка current ещё не переключена)
#   3. Только после того как ВСЕ файлы успешно долетели — одной
#      atomic-командой на сервере переключает current -> новый релиз
#   4. Оставляет 5 последних релизов для быстрого отката, старые чистит
#
# Откат на предыдущую версию без пересборки:
#   ssh root@$SERVER "ls -1 $REMOTE_BASE/releases"   # посмотреть какие есть
#   ssh root@$SERVER "ln -sfn $REMOTE_BASE/releases/<нужный> $REMOTE_BASE/current"

set -euo pipefail

SERVER="root@72.56.34.52"
REMOTE_BASE="/var/www/tourrhythm.ru"
KEEP_RELEASES=5

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$(dirname "$SCRIPT_DIR")"          # frontend/
RELEASE_ID="$(date +%Y%m%d-%H%M%S)"

echo "=== 1/4: сборка (npm run build) ==="
cd "$FRONTEND_DIR"
npm run build

if [ ! -f "dist/index.html" ]; then
    echo "ОШИБКА: dist/index.html не появился после сборки. Останов, ничего не заливаю."
    exit 1
fi

echo
echo "=== 2/4: заливка в releases/$RELEASE_ID (старый релиз пока активен, сайт не трогаем) ==="
ssh "$SERVER" "mkdir -p $REMOTE_BASE/releases/$RELEASE_ID"
rsync -az --delete "dist/" "$SERVER:$REMOTE_BASE/releases/$RELEASE_ID/"

echo
echo "=== 3/4: права + атомарное переключение current -> $RELEASE_ID ==="
# nginx-воркеры работают под www-data — им нужно право читать залитые
# файлы. rsync заливал от root, поэтому явно отдаём владение.
ssh "$SERVER" "chown -R www-data:www-data $REMOTE_BASE/releases/$RELEASE_ID && ln -sfn $REMOTE_BASE/releases/$RELEASE_ID $REMOTE_BASE/current && chown -h www-data:www-data $REMOTE_BASE/current"

echo
echo "=== 4/4: чистка старых релизов (оставляю последние $KEEP_RELEASES) ==="
ssh "$SERVER" "cd $REMOTE_BASE/releases && ls -1t | tail -n +$((KEEP_RELEASES + 1)) | xargs -r rm -rf"

echo
echo "Готово. Активный релиз: $RELEASE_ID"
echo "Список релизов на сервере:"
ssh "$SERVER" "ls -1t $REMOTE_BASE/releases"
