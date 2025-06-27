"""
Async MongoDB storage for Marathonbet events.
"""

import hashlib
import logging
from typing import List, Dict
from motor.motor_asyncio import AsyncIOMotorClient

from src.utils.functions import date_to_millis

logger = logging.getLogger(__name__)


class MongoStorage:
    def __init__(self, mongo_uri="mongodb://mongo:27017", db_name="marathonbet", collection_name="events"):
        self.client = AsyncIOMotorClient(mongo_uri)
        self.collection = self.client[db_name][collection_name]

    @staticmethod
    def _generate_id(event: Dict) -> str:
        raw = f"{event['sport']}|{event['tournament']}|{event['event']}|{event['timestamp']}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    async def save_events(self, events: List[Dict]) -> int:
        """
        Insert only new events (by _id hash).
        """
        for event in events:
            event["_id"] = self._generate_id(event)

        try:
            result = await self.collection.insert_many(events, ordered=False)
            added = len(result.inserted_ids)
        except Exception as e:
            # В Mongo insert_many із ordered=False просто скипає дублі
            added = 0
            logger.warning(f"[mongo] Some events may already exist. Details: {e}")

        logger.info(f"[mongo] Inserted {added} new events out of {len(events)}")
        return added

    async def get_events_by_date(self, date_str: str):
        """
        Returns events for a given day (UTC), specified as 'YYYY.MM.DD'
        """
        start_ts = date_to_millis(date_str + " 00:00:00")
        end_ts = date_to_millis(date_str + " 23:59:59")

        cursor = self.collection.find({
            "timestamp": {
                "$gte": start_ts,
                "$lte": end_ts
            }
        })

        return [doc async for doc in cursor]

    async def get_all_events(self):
        cursor = self.collection.find()
        return [doc async for doc in cursor]

    async def get_events_by_query(self, query: dict) -> List[Dict]:
        cursor = self.collection.find(query)
        return [doc async for doc in cursor]

