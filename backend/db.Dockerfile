# Прод db-сервис (docker-compose.yml) собирает pgvector поверх PostGIS-образа —
# в отличие от голого Postgres на хосте (дев-окружение, ставится через apt),
# Alpine-репозиторий не даёт готовый postgresql-pgvector под PG15 (только под
# PG16, см. RAG-POI-PLAN.md, деплой-раздел) — собираем из исходников.
#
# Версия pgvector (v0.8.6) и версия Alpine builder-стадии (3.20, та же, что
# и в postgis/postgis:15-3.4-alpine) синхронизированы намеренно — сборка на
# другой версии Alpine рискует бинарной несовместимостью musl libc между
# стадиями. Проверено вживую: CREATE EXTENSION vector, cosine distance,
# postgis_version() — всё работает на получившемся образе.

FROM postgres:15-alpine3.20 AS pgvector-builder
RUN apk add --no-cache --virtual .build-deps git build-base
RUN git clone --branch v0.8.6 --depth 1 https://github.com/pgvector/pgvector.git /tmp/pgvector \
    && cd /tmp/pgvector \
    # with_llvm= отключает необязательную сборку LLVM bitcode (JIT для
    # расширения) — требует полного набора llvm15+clang15 ради выигрыша,
    # незаметного на масштабе проекта (единицы пользователей).
    && make OPTFLAGS="" with_llvm= \
    && make install with_llvm=

FROM postgis/postgis:15-3.4-alpine
COPY --from=pgvector-builder /usr/local/lib/postgresql/vector.so /usr/local/lib/postgresql/vector.so
COPY --from=pgvector-builder /usr/local/share/postgresql/extension/vector* /usr/local/share/postgresql/extension/
