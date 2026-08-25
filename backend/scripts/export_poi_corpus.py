"""
Export POI corpus to text files for offline RAG retrieval analysis.

Writes one .txt file per POI (name + description + information) into
backend/eval/rag/corpus/<poi_id>.txt. Used as input for retrieval_evaluator.py
(rag-architect skill). Read-only against the DB — no writes.

Run: uv run python -m scripts.export_poi_corpus
"""

import asyncio
import logging
import shutil
from pathlib import Path

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.poi import POI
from app.services.embedding import build_poi_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CORPUS_DIR = Path(__file__).resolve().parents[1] / "eval" / "rag" / "corpus"


async def export():
    if CORPUS_DIR.exists():
        shutil.rmtree(CORPUS_DIR)
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(POI))
        pois = result.scalars().all()

        for poi in pois:
            text = build_poi_text(poi)
            if not text.strip():
                logger.warning("POI %s has no text content — skipping", poi.id)
                continue
            (CORPUS_DIR / f"{poi.id}.txt").write_text(text, encoding="utf-8")

        logger.info("Exported %d POI documents to %s", len(pois), CORPUS_DIR)


if __name__ == "__main__":
    asyncio.run(export())
