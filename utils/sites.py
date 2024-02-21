from typing import ClassVar, Dict, List, Optional, Union

import aiohttp
from pydantic import BaseModel

from scrapers import *
from utils.logger import logger


class SiteInfo(BaseModel):
    """Base Model for Site Info"""

    website: str
    search_by_category: bool = False
    categories: Optional[List[str]] = []
    limit: int = 10
    scraper_module: Optional[str] = None
    scraper_class: Optional[str] = None

    async def search(self, query: str, page: int, limit: int):
        """Search for torrents."""
        scraper_instance = self.get_scraper_instance()
        try:
            return await scraper_instance.search(query, page, limit)
        except Exception as e:
            return {"error": str(e)}

    async def search_by_category(
        self, query: str, category: str, page: int, limit: int
    ):
        """Search for torrents by category."""
        scraper_instance = self.get_scraper_instance()
        if scraper_instance and hasattr(scraper_instance, "category"):
            return await scraper_instance.category(query, category, page, limit)

    def get_scraper_instance(self):
        """Returns an instance of the scraper class."""
        if self.scraper_module and self.scraper_class:
            module = __import__(self.scraper_module, fromlist=[self.scraper_class])
            scraper_cls = getattr(module, self.scraper_class)
            return scraper_cls(website=self.website, limit=self.limit)
        return None

    async def get_proxy_site(self) -> str:
        """Asynchronously checks each proxy URL and returns the first accessible one."""
        async with aiohttp.ClientSession() as session:
            for proxy_url in self.proxy_urls:
                try:
                    async with session.get(proxy_url, timeout=5) as response:
                        if response.status == 200:
                            logger.debug(f"Using proxy: {proxy_url}")
                            return proxy_url
                except Exception as e:
                    logger.debug(f"Proxy check failed for {proxy_url}: {e}")
        return self.website


class X1337(SiteInfo):
    """`1337x.to` Site Info"""

    website: str = "https://1337xx.to"
    search_by_category: bool = True
    categories: List[str] = ["anime", "music", "games", "tv", "documentaries", "movies"]
    scraper_module: str = "scrapers.x1337"
    scraper_class: str = "X1337"


class Apibay(SiteInfo):
    """`Apibay` Site Info"""

    website: str = "https://apibay.org"
    scraper_module: str = "scrapers.apibay"
    scraper_class: str = "Apibay"


class Torlock(SiteInfo):
    """`Torlock.com` Site Info"""

    website: str = "https://torlock2.com"
    search_by_category: bool = False
    categories: List[str] = [
        "anime",
        "music",
        "games",
        "tv",
        "documentaries",
        "movies",
        "books",
    ]
    scraper_module: str = "scrapers.torlock"
    scraper_class: str = "Torlock"


class NyaaSi(SiteInfo):
    """`Nyaa.si` Site Info"""

    website: str = "https://nyaa.si"
    scraper_module: str = "scrapers.nyaa"
    scraper_class: str = "NyaaSi"
    proxy_urls: ClassVar[List[str]] = [
        "https://nyaa.si",
        "https://nyaadotsi.netlify.app",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        asyncio.run(self.set_proxy_site())

    async def set_proxy_site(self):
        self.website = await self.get_proxy_site()

    async def get_proxy_site(self) -> str:
        """Asynchronously checks each proxy URL and returns the first accessible one."""
        async with aiohttp.ClientSession() as session:
            for proxy_url in self.proxy_urls:
                try:
                    async with session.get(proxy_url, timeout=5) as response:
                        if response.status == 200:
                            return proxy_url
                except Exception:
                    pass
        return self.website


class Yts(SiteInfo):
    """`Yts.mx` Site Info"""

    website: str = "https://yts.mx"
    scraper_module: str = "scrapers.yts"
    scraper_class: str = "Yts"


class Sites(BaseModel):
    """Sites Model for all available sites."""

    apibay: Apibay = Apibay()
    nyaa: NyaaSi = NyaaSi()
    torlock: Torlock = Torlock()
    x1337: X1337 = X1337()
    yts: Yts = Yts()

    def __getitem__(self, key: str):
        """Returns a site instance by name."""
        return getattr(self, key, None)

    def __eq__(self, other):
        """Check if two Sites instances are equal."""
        return self.__dict__ == other.__dict__

    def __contains__(self, key: str) -> bool:
        """Check if a site exists in the Sites object."""
        return hasattr(self, key)

    def __len__(self) -> int:
        """Returns the number of site instances with search methods."""
        count = 0
        for site_instance in self.values():
            if hasattr(site_instance, "search"):
                count += 1
        return count

    def keys(self) -> List[str]:
        """Returns a list of all site names (keys)."""
        return [key for key in self.__dict__ if not key.startswith("_")]

    def values(self) -> List[SiteInfo]:
        """Returns a list of all site instances."""
        return [getattr(self, key) for key in self.keys()]

    def get(self, key: str, default=None):
        """Retrieve a site instance by key, with an optional default."""
        return getattr(self, key, default)

    def set(self, key: str, value: SiteInfo):
        """Set or update a site instance by key."""
        if not isinstance(value, SiteInfo):
            raise ValueError(
                f"Value must be an instance of SiteInfo, got {type(value)}"
            )
        setattr(self, key, value)

    def get_scraper(self, key: str):
        """Returns the scraper instance associated with the given site key."""
        site_info = getattr(self, key, None)
        return site_info.get_scraper_instance() if site_info else None

    def items(self) -> Dict[str, Union[str, SiteInfo]]:
        """Returns a dictionary containing site names and corresponding SiteInfo instances."""
        return [
            (site_name, getattr(self, site_name))
            for site_name in self.__annotations__.keys()
        ]

    def search(self, site: Optional[str], query: str, page: int, limit: int):
        """Returns search results for the given site and query."""
        if site:
            site_instance = getattr(self, site, None)
            if site_instance:
                return site_instance.search(query, page, limit)
            else:
                return None
        else:
            results = {}
            for site_instance in self.values():
                result = site_instance.search(query, page, limit)
                if result:
                    results[site_instance.website] = result
            return results


sites = Sites()
