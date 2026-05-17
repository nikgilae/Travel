import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.config import settings
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/places", tags=["Places"])

GMAPS_BASE = "https://maps.googleapis.com/maps/api/place"

_http = httpx.AsyncClient(timeout=10.0)


@router.get("/find")
async def find_place(
    input: str = Query(..., description="Текстовый запрос для поиска места"),
    _user: User = Depends(get_current_user),
):
    """Найти place_id по тексту (проксирует Google Places FindPlace)."""
    resp = await _http.get(
        f"{GMAPS_BASE}/findplacefromtext/json",
        params={
            "input": input,
            "inputtype": "textquery",
            "fields": "place_id",
            "key": settings.GOOGLE_MAPS_API_KEY,
        },
    )
    resp.raise_for_status()
    data = resp.json()
    candidates = data.get("candidates", [])
    if not candidates:
        raise HTTPException(status_code=404, detail="Место не найдено в Google Maps")
    return {"place_id": candidates[0]["place_id"]}


@router.get("/details")
async def place_details(
    place_id: str = Query(..., description="Google place_id"),
    _user: User = Depends(get_current_user),
):
    """Получить детали места (проксирует Google Places Details)."""
    resp = await _http.get(
        f"{GMAPS_BASE}/details/json",
        params={
            "place_id": place_id,
            "fields": "name,rating,user_ratings_total,formatted_address,opening_hours,photos,editorial_summary",
            "key": settings.GOOGLE_MAPS_API_KEY,
        },
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("status") not in ("OK", "ZERO_RESULTS"):
        raise HTTPException(status_code=502, detail=f"Google Places ошибка: {data.get('status')}")
    return data.get("result", {})


@router.get("/photo")
async def place_photo(
    photo_reference: str = Query(...),
    maxwidth: int = Query(400, ge=1, le=1600),
    _user: User = Depends(get_current_user),
):
    """Проксирует фото из Google Places Photo API."""
    resp = await _http.get(
        f"{GMAPS_BASE}/photo",
        params={
            "photo_reference": photo_reference,
            "maxwidth": maxwidth,
            "key": settings.GOOGLE_MAPS_API_KEY,
        },
        follow_redirects=True,
    )
    resp.raise_for_status()
    content_type = resp.headers.get("content-type", "image/jpeg")
    return StreamingResponse(iter([resp.content]), media_type=content_type)
