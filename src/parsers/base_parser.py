"""
Base parser class using aiohttp for making async HTTP requests.

Provides:
- Context-managed session opening/closing
- GET and POST request helpers with JSON response handling
- Pluggable timeout
- Structured logging

To use: inherit and implement the `fetch_data()` method.

Example:
    async with MyParser() as parser:
        data = await parser.fetch_data("2024-06-01", "2024-06-02")
"""

import aiohttp
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union

logger = logging.getLogger(__name__)


class BaseAiohttpParser(ABC):
    """
    Abstract base class for parsers using aiohttp session.
    """

    def __init__(self, timeout: int = 30):
        """
        Initializes the parser with optional request timeout.

        :param timeout: Request timeout in seconds (default: 30)
        """
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """
        Asynchronous context manager entry. Opens aiohttp session.
        """
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Asynchronous context manager exit. Closes aiohttp session.
        """
        if self.session:
            await self.session.close()

    async def close(self):
        """
        Manually closes aiohttp session, if open.
        """
        if self.session:
            await self.session.close()

    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Union[Dict[str, Any], list]:
        """
        Sends a GET request to the given URL and returns the parsed JSON response.

        :param url: URL to send the GET request to
        :param params: Optional query parameters
        :param headers: Optional request headers
        :return: Parsed JSON data as dict or list
        """
        logger.debug(f"GET {url} with params={params}")
        async with self.session.get(url, params=params, headers=headers) as response:
            response.raise_for_status()
            return await response.json()

    async def post(
        self,
        url: str,
        payload: Any,
        headers: Optional[Dict[str, str]] = None,
    ) -> Union[Dict[str, Any], list]:
        """
        Sends a POST request with JSON payload and returns the parsed JSON response.

        :param url: URL to send the POST request to
        :param payload: Payload to be sent as JSON
        :param headers: Optional request headers
        :return: Parsed JSON data as dict or list
        """
        logger.debug(f"POST {url} with payload={payload}")
        async with self.session.post(url, json=payload, headers=headers) as response:
            response.raise_for_status()
            return await response.json()

    @abstractmethod
    async def fetch_data(self, *args, **kwargs) -> list:
        """
        Abstract method to be implemented by subclasses to fetch and return structured data.

        :return: List of parsed structured data (dicts)
        """
        pass
