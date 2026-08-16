#!/usr/bin/env bash
# Шаг 3 — ВЫПОЛНЯТЬ НА СЕРВЕРЕ.
#
# ⚠️ ЗАПУСКАТЬ ТОЛЬКО ПОСЛЕ того, как 25-check-dns.sh покажет ✅ для
# обоих доменов у обоих резолверов. Если запустить раньше — Let's
# Encrypt не сможет пройти HTTP-01 challenge (см. объяснение в
# 25-check-dns.sh), получишь ошибку, и это ещё не страшно само по себе,
# НО у Let's Encrypt есть rate limit на количество попыток на домен —
# лучше не гонять его вслепую, а дождаться зелёного света.
#
# Что делает: certbot сам находит server-блок для tourrhythm.ru в
# /etc/nginx/sites-available/tourrhythm.ru (мы указываем -d явно, но
# certbot также ищет совпадение по server_name), дописывает в него
# 443-блок с путями к сертификату и делает reload nginx.
# Это тот же путь, которым уже выпущен сертификат для api.tourrhythm.ru
# (мы это видели в выводе certbot certificates на шаге разведки).

set -euo pipefail

# Оба домена подтверждены чистыми по 15 точкам мира (check-host.net) —
# запрашиваем сертификат сразу на оба.
certbot --nginx -d tourrhythm.ru -d www.tourrhythm.ru

echo
echo "=== Проверка результата ==="
certbot certificates

echo
echo "=== nginx -t после правок certbot ==="
nginx -t

echo
echo "Готово. Если nginx -t зелёный — HTTPS для tourrhythm.ru и www.tourrhythm.ru настроен."
