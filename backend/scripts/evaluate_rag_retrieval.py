"""
Оценка retrieval-качества pgvector embedding-поиска (Итерация 3,
RAG-POI-PLAN.md) на реалистичном k (40/100 — MAX_POIS_FOR_AI fast/normal)
против random-baseline. Прод-код не трогает: corpus-wide (без city_id)
запрос собран прямо здесь, отдельно от POIRepository.get_relevant_for_trip
(которая фильтрует по городу — другая область охвата, не подходит для
сравнения с ground truth Итерации 0, размеченным по всему корпусу).

Основной прогон — queries_production_shape.json (байт-в-байт как строит
query_text TripAIService._select_city_pois: interests-теги без синонимов +
notes). Вторичный — queries.json (Итерация 0, TF-IDF-раздутые синонимами
запросы) для контекста. Go/no-go — по основному прогону.

Run: uv run python -m scripts.evaluate_rag_retrieval
"""

import asyncio
import json
import logging
import random
from pathlib import Path

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.poi import POI
from app.services.embedding import get_embedding

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EVAL_DIR = Path(__file__).resolve().parents[1] / "eval" / "rag"
K_VALUES = [40, 100]
RANDOM_REPEATS = 20
RANDOM_SEED = 42
QUALITATIVE_ONLY_TAGS = ("relaxed", "active")


def load_json(name: str) -> dict:
    with open(EVAL_DIR / name, encoding="utf-8") as f:
        return json.load(f)


def _relevant_ids_for(query_id: str, ground_truth: dict) -> set[str]:
    """
    ground_truth.json размечен по тегу (cultural_1/cultural_2 — идентичные
    списки), не по конкретному варианту запроса. Оба стиля запросов
    (queries_production_shape.json: cultural_tag_only/cultural_with_notes;
    queries.json: cultural_1/cultural_2) сводятся к одному ключу по тегу.
    """
    tag = query_id.split("_")[0]
    return set(ground_truth.get(f"{tag}_1", []))


def precision_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float:
    top_k = retrieved_ids[:k]
    return len(set(top_k) & relevant_ids) / len(top_k) if top_k else 0.0


def recall_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float:
    if not relevant_ids:
        return 0.0
    return len(set(retrieved_ids[:k]) & relevant_ids) / len(relevant_ids)


def reciprocal_rank(retrieved_ids: list[str], relevant_ids: set[str]) -> float:
    for i, doc_id in enumerate(retrieved_ids):
        if doc_id in relevant_ids:
            return 1.0 / (i + 1)
    return 0.0


def _safe_mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


async def get_all_poi_ids_with_embedding(session) -> list[str]:
    result = await session.execute(select(POI.id).where(POI.embedding.isnot(None)))
    return [str(poi_id) for poi_id in result.scalars().all()]


async def retrieve_cosine(session, query_embedding: list[float], k: int) -> list[str]:
    result = await session.execute(
        select(POI)
        .where(POI.embedding.isnot(None))
        .order_by(POI.embedding.cosine_distance(query_embedding), POI.id)
        .limit(k)
    )
    return [str(poi.id) for poi in result.scalars().all()]


async def evaluate_query_set(session, queries, ground_truth, all_poi_ids, label) -> dict:
    max_k = max(K_VALUES)
    per_query: dict[str, dict] = {}

    for q in queries:
        qid, qtext = q["id"], q["query"]
        relevant_ids = _relevant_ids_for(qid, ground_truth)
        if not relevant_ids:
            continue  # relaxed/active — качественная проверка отдельно, не здесь

        embedding = await get_embedding(qtext)
        retrieved = await retrieve_cosine(session, embedding, max_k)

        per_query[qid] = {
            "query": qtext,
            "relevant_count": len(relevant_ids),
            "metrics": {
                **{f"precision@{k}": precision_at_k(retrieved, relevant_ids, k) for k in K_VALUES},
                **{f"recall@{k}": recall_at_k(retrieved, relevant_ids, k) for k in K_VALUES},
                "mrr": reciprocal_rank(retrieved, relevant_ids),
            },
        }

    random.seed(RANDOM_SEED)
    for qid, data in per_query.items():
        relevant_ids = _relevant_ids_for(qid, ground_truth)
        precisions = {k: [] for k in K_VALUES}
        recalls = {k: [] for k in K_VALUES}
        mrrs = []
        for _ in range(RANDOM_REPEATS):
            sample = random.sample(all_poi_ids, max_k)
            for k in K_VALUES:
                precisions[k].append(precision_at_k(sample, relevant_ids, k))
                recalls[k].append(recall_at_k(sample, relevant_ids, k))
            mrrs.append(reciprocal_rank(sample, relevant_ids))
        data["baseline"] = {
            **{f"precision@{k}": _safe_mean(precisions[k]) for k in K_VALUES},
            **{f"recall@{k}": _safe_mean(recalls[k]) for k in K_VALUES},
            "mrr": _safe_mean(mrrs),
        }

    aggregate = {
        **{f"mean_precision@{k}": _safe_mean([d["metrics"][f"precision@{k}"] for d in per_query.values()]) for k in K_VALUES},
        **{f"mean_recall@{k}": _safe_mean([d["metrics"][f"recall@{k}"] for d in per_query.values()]) for k in K_VALUES},
        **{f"mean_baseline_recall@{k}": _safe_mean([d["baseline"][f"recall@{k}"] for d in per_query.values()]) for k in K_VALUES},
        "mean_mrr": _safe_mean([d["metrics"]["mrr"] for d in per_query.values()]),
        "mean_baseline_mrr": _safe_mean([d["baseline"]["mrr"] for d in per_query.values()]),
    }

    logger.info("[%s] агрегаты: %s", label, aggregate)
    return {"label": label, "per_query": per_query, "aggregate": aggregate}


async def qualitative_check(session, queries, label) -> dict:
    """relaxed/active — нет ground truth, сохраняем топ-10 для ручного просмотра."""
    results = {}
    for q in queries:
        qid, qtext = q["id"], q["query"]
        embedding = await get_embedding(qtext)
        retrieved = await session.execute(
            select(POI)
            .where(POI.embedding.isnot(None))
            .order_by(POI.embedding.cosine_distance(embedding), POI.id)
            .limit(10)
        )
        pois = retrieved.scalars().all()
        results[qid] = {
            "query": qtext,
            "top_10": [{"name": p.name, "description": p.description} for p in pois],
        }
    logger.info("[%s] качественная проверка сохранена для %d запросов", label, len(results))
    return results


async def main():
    ground_truth = {
        k: v for k, v in load_json("ground_truth.json").items() if not k.startswith("_")
    }
    production_queries = load_json("queries_production_shape.json")["queries"]
    tfidf_queries = load_json("queries.json")["queries"]

    async with AsyncSessionLocal() as session:
        all_poi_ids = await get_all_poi_ids_with_embedding(session)
        logger.info("Корпус: %d POI с embedding", len(all_poi_ids))

        production_result = await evaluate_query_set(
            session, production_queries, ground_truth, all_poi_ids, "production_shape"
        )
        tfidf_result = await evaluate_query_set(
            session, tfidf_queries, ground_truth, all_poi_ids, "tfidf_style_iteration0"
        )

        qualitative_queries = [
            q for q in production_queries if q["id"].startswith(QUALITATIVE_ONLY_TAGS)
        ]
        qualitative = await qualitative_check(session, qualitative_queries, "relaxed_active")

    output = {
        "corpus_size": len(all_poi_ids),
        "k_values": K_VALUES,
        "random_repeats": RANDOM_REPEATS,
        "random_seed": RANDOM_SEED,
        "production_shape": production_result,
        "tfidf_style_iteration0": tfidf_result,
        "qualitative_relaxed_active": qualitative,
    }

    out_path = EVAL_DIR / "iteration3-results.json"
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Результаты сохранены в %s", out_path)


if __name__ == "__main__":
    asyncio.run(main())
