#!/usr/bin/env bash
# Шаг 6b (позже) — ВЫПОЛНЯТЬ НА СЕРВЕРЕ, после 30-certbot.sh,
# когда www.tourrhythm.ru тоже полностью разойдётся в DNS
# (проверь через 25-check-dns.sh — оба резолвера должны показывать
# 72.56.34.52 для www).
#
# --expand расширяет уже выпущенный сертификат для tourrhythm.ru,
# добавляя www.tourrhythm.ru в тот же сертификат — не отдельный
# сертификат, не пересоздание с нуля.

set -euo pipefail

certbot --nginx -d tourrhythm.ru -d www.tourrhythm.ru --expand

echo
certbot certificates

echo
nginx -t
