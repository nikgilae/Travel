#!/usr/bin/env bash
# Продолжение разведки — без set -e, чтобы пустой результат одной
# команды не обрывал остальные (как это случилось в 00-recon.sh).
# Ничего не меняет, только читает.

echo "=== сертификаты certbot ==="
certbot certificates 2>&1

echo
echo "=== кто держит порты 80/443 ==="
ss -tlnp 2>&1 | grep -E ":80 |:443 "

echo
echo "=== существует ли /var/www ==="
ls -la /var/www/ 2>&1

echo
echo "=== пользователь nginx worker-процессов ==="
ps aux | grep "nginx: worker" | grep -v grep

echo
echo "=== firewall (ufw) ==="
ufw status 2>&1

echo
echo "=== версия ОС ==="
head -5 /etc/os-release 2>&1

echo
echo "=== свободное место на диске ==="
df -h / 2>&1

echo
echo "=== ГОТОВО. Пришли весь вывод. ==="
