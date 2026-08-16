#!/usr/bin/env bash
# Шаг 2 — ВЫПОЛНЯТЬ НА СЕРВЕРЕ, после того как:
#   1) выполнён 10-setup-dirs.sh
#   2) файл nginx-tourrhythm.ru.conf скопирован в
#      /etc/nginx/sites-available/tourrhythm.ru
#      (команда для копирования — см. в инструкции, которую я пришлю
#      отдельно, через scp с ноутбука)
#
# Что делает: включает сайт (symlink в sites-enabled), проверяет
# синтаксис (nginx -t) ДО перезагрузки — если тут ошибка, nginx -t
# провалится и НИЧЕГО не сломается, старый конфиг останется работать.
# Только если проверка прошла — делает reload.

set -euo pipefail

CONF=/etc/nginx/sites-available/tourrhythm.ru

if [ ! -f "$CONF" ]; then
    echo "ОШИБКА: $CONF не найден. Сначала скопируй туда nginx-tourrhythm.ru.conf с ноутбука:"
    echo "  scp frontend/deploy/nginx-tourrhythm.ru.conf root@72.56.34.52:/etc/nginx/sites-available/tourrhythm.ru"
    exit 1
fi

ln -sf "$CONF" /etc/nginx/sites-enabled/tourrhythm.ru

echo "=== nginx -t (проверка синтаксиса, ничего ещё не применено) ==="
nginx -t

echo
echo "=== синтаксис ок, применяю reload ==="
systemctl reload nginx

echo
echo "Готово. Сайт включён на порту 80 (HTTP, без TLS пока)."
echo "На этом этапе tourrhythm.ru ЕЩЁ НЕ доступен снаружи по этому конфигу,"
echo "потому что DNS всё ещё указывает на Vercel — это ожидаемо и безопасно,"
echo "трафик пользователей сюда пока не идёт."
echo
echo "Дальше: 30-certbot.sh — получить TLS-сертификат."
