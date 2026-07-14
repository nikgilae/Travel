import json
import logging
import uuid

from app.core import events


def _capture(caplog):
    """Достаёт JSON-полезную нагрузку из последней записи логгера событий."""
    for rec in reversed(caplog.records):
        if rec.name == "app.core.events":
            # формат: 'event {json}'
            msg = rec.getMessage()
            return json.loads(msg.split("event ", 1)[1])
    return None


class TestLogEvent:

    def test_emits_core_fields(self, caplog):
        uid, tid = uuid.uuid4(), uuid.uuid4()
        with caplog.at_level(logging.INFO, logger="app.core.events"):
            events.log_event(events.EVENT_TRIP_CREATED, user_id=uid, trip_id=tid)
        payload = _capture(caplog)
        assert payload["event"] == "trip_created"
        assert payload["user_id"] == str(uid)
        assert payload["trip_id"] == str(tid)
        assert "ts" in payload

    def test_includes_extra_fields(self, caplog):
        with caplog.at_level(logging.INFO, logger="app.core.events"):
            events.log_event(events.EVENT_DAY_FINALIZED, user_id=uuid.uuid4(),
                             trip_id=uuid.uuid4(), day_number=3)
        payload = _capture(caplog)
        assert payload["event"] == "day_finalized"
        assert payload["day_number"] == 3

    def test_none_ids_serialize_as_null(self, caplog):
        with caplog.at_level(logging.INFO, logger="app.core.events"):
            events.log_event(events.EVENT_CHAT_MESSAGE, user_id=uuid.uuid4(),
                             trip_id=None, channel="general")
        payload = _capture(caplog)
        assert payload["trip_id"] is None
        assert payload["channel"] == "general"

    def test_never_raises_on_bad_extra(self, caplog):
        """Несериализуемое значение не должно ронять запрос — default=str спасает."""
        class Weird:
            def __str__(self): return "weird"
        # не должно бросить
        events.log_event(events.EVENT_LOGIN, user_id=uuid.uuid4(), obj=Weird())

    def test_event_name_constants_present(self):
        assert events.EVENT_LOGIN == "login"
        assert events.EVENT_TRIP_CREATED == "trip_created"
        assert events.EVENT_GENERATE == "generate"
        assert events.EVENT_DAY_FINALIZED == "day_finalized"
        assert events.EVENT_POI_REMOVED == "poi_removed"
        assert events.EVENT_CHAT_MESSAGE == "chat_message"
