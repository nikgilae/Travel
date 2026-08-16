#!/usr/bin/env bash
# Шаг 0: разведка перед изменениями.
#
# Ничего не меняет на сервере — только читает текущее состояние.
# Выполни на сервере 72.56.34.52 (по ssh, из-под пользователя с sudo)
# и пришли мне весь вывод целиком.
#
# Зачем: я не имею доступа к серверу и не знаю, как именно настроен
# nginx для api.tourrhythm.ru — какой путь к сертификатам, версия nginx,
# включён ли http2/HSTS, где лежат конфиги сайтов. Конфиг для фронта
# должен быть в том же стиле, а не собран наугад — иначе certbot или
# nginx -t может сломаться на несовместимости.

set -euo pipefail

echo "=== версия nginx ==="
nginx -v 2>&1 || echo "nginx не найден в PATH"

echo
echo "=== активные сайты (sites-enabled) ==="
ls -la /etc/nginx/sites-enabled/ 2>&1

echo
echo "=== все конфиги сайтов (sites-available) ==="
ls -la /etc/nginx/sites-available/ 2>&1

echo
echo "=== содержимое конфига для api.tourrhythm.ru (если найден) ==="
grep -rl "api.tourrhythm.ru" /etc/nginx/ 2>/dev/null | while read -r f; do
  echo "--- $f ---"
  cat "$f"
done

echo
echo "=== есть ли уже конфиг для tourrhythm.ru (без api) ==="
grep -rl "tourrhythm.ru" /etc/nginx/ 2>/dev/null | grep -v "api\.tourrhythm"

echo
echo "=== сертификаты certbot ==="
certbot certificates 2>&1 || echo "certbot не найден или нет доступа"

echo
echo "=== кто держит порты 80/443 ==="
ss -tlnp 2>&1 | grep -E ":80 |:443 " || sudo ss -tlnp 2>&1 | grep -E ":80 |:443 "

echo
echo "=== занятое место на диске (нужно под dist/) ==="
df -h /var/www 2>&1 || df -h /

echo
echo "=== существует ли /var/www ==="
ls -la /var/www/ 2>&1

echo
echo "=== пользователь, от которого работает nginx worker ==="
ps aux | grep "nginx: worker" | grep -v grep

echo
echo "=== firewall (ufw) ==="
ufw status 2>&1 || echo "ufw не установлен / нет прав"

echo
echo "=== версия ОС ==="
cat /etc/os-release 2>&1 | head -5

echo
echo "=== ГОТОВО. Скопируй весь вывод выше и пришли мне. ==="
