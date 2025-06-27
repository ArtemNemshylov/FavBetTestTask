"""
Parser for fetching finished events from Marathonbet API.
"""

import logging
from typing import List, Dict

from src.parsers.base_parser import BaseAiohttpParser
from src.utils.functions import date_to_millis
from src.configs.headers import MARATHONBET_HEADERS as HEADERS

logger = logging.getLogger(__name__)


class MarathonbetParser(BaseAiohttpParser):
    """
    Asynchronous parser for finished sports events from Marathonbet API.
    """

    API_URL = "https://www.marathonbet.com/en/react/unionresults/results"

    @staticmethod
    def build_payload(from_date: str, to_date: str) -> dict:
        return {
            "sportIds": [],
            "interval": {
                "from": date_to_millis(from_date),
                "to": date_to_millis(to_date + " 23:59:59")
            },
            "searchWords": "",
            "resultTab": "FINISHED",
            "pageIndex": 0,
            "categoriesPerPage": 999999999,
            "collapsedSports": False,
            "excludeSportIds": [],
            "startPageNumber": 0,
            "countPagesToLoad": 1
        }

    async def fetch_data(self, from_date: str, to_date: str) -> List[Dict]:
        """
        Fetches and parses finished events from Marathonbet API for the given date range.

        :param from_date: Start date in 'YYYY.MM.DD' format
        :param to_date: End date in 'YYYY.MM.DD' format
        :return: List of dicts representing events
        """
        payload = self.build_payload(from_date, to_date)
        logger.info(f"[marathonbet] Fetching data from {from_date} to {to_date}")

        try:
            raw = await self.post(self.API_URL, payload, headers=HEADERS)
        except Exception as e:
            logger.exception(f"[marathonbet] Failed to fetch data: {e}")
            return []

        results = []

        for sport in raw.get("sports", []):
            sport_name = sport.get("name", "")
            for tournament in sport.get("childs", []):
                tournament_name = tournament.get("name", "")
                for event in tournament.get("childs", []):
                    scores = event.get("scores") or []
                    score_value = scores[0]["value"] if scores and isinstance(scores[0], dict) else None

                    event_data = {
                        "sport": sport_name,
                        "tournament": tournament_name,
                        "event": event.get("name"),
                        "timestamp": event.get("date"),
                        "score": score_value,
                        "comment": event.get("comment", "")
                    }
                    results.append(event_data)

        return results
