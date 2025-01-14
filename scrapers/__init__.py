import asyncio
import os
from typing import List

import aiohttp
from pydantic import BaseModel

from routers import asyncio_fix
from utils.logger import logger
from utils.realdebrid import realdebrid

HTTP_PROXY = os.environ.get("HTTP_PROXY", None)
HEADER_AIO = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67",
    "Cookie": "fencekey=8e5j3p61b3k0a9b0e44c5bbcecafaa5a2",
}


class BaseScraper:
    """Scraper class for scraping html"""

    def __init__(self):
        self.time = 0
        self.total = 0

    @asyncio_fix
    async def _get_html(self, session, url):
        try:
            async with session.get(url, headers=HEADER_AIO, proxy=HTTP_PROXY) as r:
                return await r.text()
        except:
            return None

    async def get_all_results(self, session, url):
        """Get all results from url"""
        return await asyncio.gather(asyncio.create_task(self._get_html(session, url)))


class Torrent(BaseModel):
    """Torrent model for storing torrent information."""

    title: str
    infohash: str
    site: str


class Torrents(BaseModel):
    """Torrents model for storing a list of Torrent objects."""

    query: str
    torrents: List[Torrent]
