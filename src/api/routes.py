from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List

from src.parsers.marathonbet_parser import MarathonbetParser
from src.storage.mongo_storage import MongoStorage
from src.utils.functions import date_to_millis, millis_to_date
import logging

router = APIRouter()
storage = MongoStorage()
logging.basicConfig(level=logging.INFO)

def daterange(start_date: datetime, end_date: datetime):
    for n in range((end_date - start_date).days + 1):
        yield start_date + timedelta(n)

@router.get("/events/by-range")
async def get_events_by_range(
    from_date: str = Query(..., description="Start date in YYYY.MM.DD format"),
    to_date: str = Query(..., description="End date in YYYY.MM.DD format"),
):
    """
    Returns events for the given date range.
    Automatically adds only missing days (does not reparse existing ones).
    """
    try:
        from_dt = datetime.strptime(from_date, "%Y.%m.%d")
        to_dt = datetime.strptime(to_date, "%Y.%m.%d")

        # Step 1: create full list of dates
        all_dates = [(from_dt + timedelta(days=i)).strftime("%Y.%m.%d")
                     for i in range((to_dt - from_dt).days + 1)]

        missing_dates = []

        # Step 2: check each date for presence in DB
        for day in all_dates:
            start_ts = date_to_millis(day + " 00:00:00")
            end_ts = date_to_millis(day + " 23:59:59")

            exists = await storage.collection.find_one({
                "timestamp": {"$gte": start_ts, "$lte": end_ts}
            })

            if not exists:
                missing_dates.append(day)

        if missing_dates:
            logging.info(f"[api] Missing {len(missing_dates)} days. Fetching: {missing_dates}")
            async with MarathonbetParser() as parser:
                for day in missing_dates:
                    try:
                        new_data = await parser.fetch_data(day, day)
                        await storage.save_events(new_data)
                    except Exception as inner:
                        logging.warning(f"[api] Failed to fetch data for {day}: {inner}")

        # Step 3: final fetch
        from_ts = date_to_millis(from_date + " 00:00:00")
        to_ts = date_to_millis(to_date + " 23:59:59")

        query = {"timestamp": {"$gte": from_ts, "$lte": to_ts}}
        cursor = storage.collection.find(query)
        events = [doc async for doc in cursor]

        # Format timestamp
        for event in events:
            if "timestamp" in event:
                event["date"] = millis_to_date(event["timestamp"])
                del event["timestamp"]

        return {
            "from": from_date,
            "to": to_date,
            "total": len(events),
            "events": events
        }

    except Exception as e:
        logging.exception("[api] Error in /events/by-range")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/events/by-hours")
async def get_events_by_hours(
    hours_back: int = Query(..., ge=1, le=240, description="Кількість годин назад від поточного моменту")
):
    """
    Returns events that happened within the last `hours_back` hours.
    """
    try:
        now = datetime.now(timezone.utc)
        from_dt = now - timedelta(hours=hours_back)

        from_ts = int(from_dt.timestamp() * 1000)
        to_ts = int(now.timestamp() * 1000)

        query = {
            "timestamp": {"$gte": from_ts, "$lte": to_ts}
        }

        cursor = storage.collection.find(query)
        events = [doc async for doc in cursor]

        if not events:
            logging.info(f"[api] No events found in the last {hours_back} hours. Triggering update...")
            async with MarathonbetParser() as parser:
                from_str = from_dt.strftime("%Y.%m.%d")
                to_str = now.strftime("%Y.%m.%d")
                new_data = await parser.fetch_data(from_str, to_str)
                await storage.save_events(new_data)

            # Retry fetch after update
            cursor = storage.collection.find(query)
            events = [doc async for doc in cursor]

        for event in events:
            if "timestamp" in event:
                event["date"] = millis_to_date(event["timestamp"])
                del event["timestamp"]

        return {
            "from": from_dt.isoformat(),
            "to": now.isoformat(),
            "total": len(events),
            "events": events
        }

    except Exception as e:
        logging.exception("[api] Error in /events/by-hours")
        raise HTTPException(status_code=400, detail=str(e))
