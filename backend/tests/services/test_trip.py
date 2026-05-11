import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.trip import TripService
from app.core.exceptions import NotFoundException, AlreadyExistsException


class TestTripService:

    def setup_method(self):
        """Создать моки перед каждым тестом."""
        self.mock_session = AsyncMock()
        self.service = TripService(self.mock_session)
        self.service.trip_repo = AsyncMock()
        self.service.trip_poi_repo = AsyncMock()
        self.service.poi_repo = AsyncMock()
        self.service.poi_rule_repo = AsyncMock()
        self.service.country_repo = AsyncMock()
        self.service.city_repo = AsyncMock()

    async def test_create_trip_country_not_found(self):
        """Создание поездки с несуществующей страной — выбрасывает NotFoundException."""
        self.service.country_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundException, match="Country not found"):
            await self.service.create(
                user_id=uuid.uuid4(),
                country_id=uuid.uuid4(),
                city_id=uuid.uuid4(),
                purpose="leisure",
                budget="medium",
                group_size=1,
                other_information=None,
                start_date=None,
                end_date=None,
            )

        self.service.trip_repo.create.assert_not_called()
        
    async def test_create_trip_city_not_found(self):
        """Создание поездки с несуществующим городом — выбрасывает NotFoundException."""
        self.service.country_repo.get_by_id.return_value = MagicMock()
        self.service.city_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundException, match="City not found"):
            await self.service.create(
                user_id=uuid.uuid4(),
                country_id=uuid.uuid4(),
                city_id=uuid.uuid4(),
                purpose="leisure",
                budget="medium",
                group_size=1,
                other_information=None,
                start_date=None,
                end_date=None,
            )

        self.service.trip_repo.create.assert_not_called()

    async def test_add_poi_already_in_trip(self):
        """Добавление POI который уже в маршруте — выбрасывает AlreadyExistsException."""
        self.service.trip_repo.get_by_user_and_id.return_value = MagicMock()
        self.service.poi_repo.get_by_id.return_value = MagicMock()
        self.service.trip_poi_repo.get_by_trip_and_poi.return_value = MagicMock()

        with pytest.raises(AlreadyExistsException, match="POI already in this trip"):
            await self.service.add_poi(
                trip_id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                poi_id=uuid.uuid4(),
                sequence_order=1.0,
                planned_start_time=None,
            )