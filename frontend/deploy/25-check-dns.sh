#!/usr/bin/env bash
# Можно выполнять И на сервере, И на ноутбуке — просто проверка DNS.
#
# ЗАЧЕМ ЭТОТ ШАГ ОБЯЗАТЕЛЕН перед certbot (30-certbot.sh):
# certbot по умолчанию использует HTTP-01 challenge — Let's Encrypt
# сам ходит на http://tourrhythm.ru/.well-known/... с СВОИХ серверов
# и смотрит, куда резолвится домен. Если DNS ещё указывает на Vercel,
# запрос Let's Encrypt попадёт на Vercel, а не на наш nginx — выпуск
# сертификата ГАРАНТИРОВАННО провалится. Поэтому нельзя просто
# "попробовать certbot и посмотреть" — нужно дождаться, пока публичные
# резолверы реально видят новый IP, и только потом запускать certbot.

set -euo pipefail

EXPECTED_IP="72.56.34.52"

echo "Ожидаемый IP сервера: $EXPECTED_IP"
echo

for domain in tourrhythm.ru www.tourrhythm.ru; do
    echo "=== $domain через 8.8.8.8 (Google) ==="
    got=$(dig @8.8.8.8 +short "$domain" A | tr '\n' ' ')
    echo "  -> $got"

    echo "=== $domain через 1.1.1.1 (Cloudflare) ==="
    got2=$(dig @1.1.1.1 +short "$domain" A | tr '\n' ' ')
    echo "  -> $got2"

    # Важно: сравниваем ВСЕ строки ответа, а не последнюю — если
    # записей несколько (например, старая Vercel-запись ещё не
    # удалена), tail -1 показал бы только одну и создал ложное "чисто".
    if [ "$got" = "$EXPECTED_IP " ] && [ "$got2" = "$EXPECTED_IP " ]; then
        echo "  ✅ $domain — ровно одна A-запись, указывает на наш сервер, у обоих резолверов."
    else
        echo "  ⏳ $domain ещё не чист (либо не тот IP, либо больше одной записи) — certbot запускать рано."
    fi
    echo
done
