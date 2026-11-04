from __future__ import annotations

import pytest

from tests import BARE_EVENT_TEMPLATE
from vdirsyncer.storage.singlefile import SingleFileStorage

from . import StorageTests


@pytest.mark.asyncio
async def test_list_with_calendar_uid(tmp_path):
    events = [BARE_EVENT_TEMPLATE.format(r=i, uid=f"event-{i}") for i in range(2)]
    raw = "\n".join(
        ["BEGIN:VCALENDAR", "VERSION:2.0", "UID:calendar-uid", *events, "END:VCALENDAR"]
    )
    path = tmp_path / "calendar.ics"
    path.write_text(raw, encoding="utf-8")
    storage = SingleFileStorage(path=str(path))

    entries = {href: etag async for href, etag in storage.list()}

    assert set(entries) == {"event-0", "event-1"}
    for href, etag in entries.items():
        item, actual_etag = await storage.get(href)
        assert item.uid == href
        assert item.parsed["UID"] == "calendar-uid"
        assert actual_etag == etag


class TestSingleFileStorage(StorageTests):
    storage_class = SingleFileStorage
    supports_metadata = False

    @pytest.fixture
    def get_storage_args(self, tmpdir):
        async def inner(collection="test"):
            rv = {"path": str(tmpdir.join("%s.txt")), "collection": collection}
            if collection is not None:
                rv = await self.storage_class.create_collection(**rv)
            return rv

        return inner
