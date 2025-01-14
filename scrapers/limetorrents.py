import asyncio
import re
import time

import aiohttp
from bs4 import BeautifulSoup

from scrapers import HEADER_AIO, BaseScraper, asyncio_fix


class Limetorrent(BaseScraper):
    """`Limetorrent` scraper class"""

    def __init__(self, website, limit):
        super().__init__()
        self.url = website
        self.limit = limit

    @asyncio_fix
    async def _individual_scrap(self, session, url, obj):
        """Scrap individual torrent page for magnet, torrent, hash"""
        try:
            async with session.get(url, headers=HEADER_AIO) as res:
                html = await res.text(encoding="ISO-8859-1")
                soup = BeautifulSoup(html, "html.parser")
                try:
                    a_tag = soup.find_all("a", class_="csprite_dltorrent")
                    obj["infohash"] = re.search(
                        r"([{a-f\d,A-F\d}]{40})\b", a_tag[-1]["href"]
                    ).group(0)
                    obj["site"] = self.url
                    obj.pop("url")
                except:
                    ...
        except:
            return None

    async def _get_torrent(self, result, session, urls):
        """Get the torrent from individual torrent page"""
        tasks = []
        for idx, url in enumerate(urls):
            for obj in result["data"]:
                if obj["url"] == url:
                    task = asyncio.create_task(
                        self._individual_scrap(session, url, result["data"][idx])
                    )
                    tasks.append(task)
        await asyncio.gather(*tasks)
        return result

    def _parser(self, htmls, idx=0):
        """Parse the result from the given HTML."""
        try:
            for html in htmls:
                soup = BeautifulSoup(html, "html.parser")
                list_of_urls = []
                my_dict = {"data": []}

                for tr in soup.find_all("tr")[idx:]:
                    td = tr.find_all("td")
                    if len(td) == 0:
                        continue
                    name = td[0].get_text(strip=True)
                    url = self.url + td[0].find_all("a")[-1]["href"]
                    list_of_urls.append(url)
                    my_dict["data"].append(
                        {
                            "name": name,
                            "url": url,
                        }
                    )
                    if len(my_dict["data"]) == self.limit:
                        break
                try:
                    div = soup.find("div", class_="search_stat")
                    current_page = int(div.find("span", class_="active").text)
                    total_page = int((div.find_all("a"))[-2].text)
                    if current_page > total_page:
                        total_page = current_page
                    my_dict["current_page"] = current_page
                    my_dict["total_pages"] = total_page
                except:
                    ...
                return my_dict, list_of_urls
        except:
            return None, None

    async def parser_result(self, start_time, url, session, idx=0):
        """Parse the result from the given URL."""
        htmls = await self.get_all_results(session, url)
        result, urls = self._parser(htmls, idx)
        if result is not None:
            results = await self._get_torrent(result, session, urls)
            results["time"] = time.time() - start_time
            results["total"] = len(results["data"])
            return results
        return result

    async def search(self, query, page, limit):
        """Search torrents from `Limetorrent`."""
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            url = self.url + "/search/all/{}//{}".format(query, page)
            return await self.parser_result(start_time, url, session, idx=5)

    async def trending(self, category, page, limit):
        """Get trending torrents from `Limetorrent`."""
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            url = self.url + "/top100"
            return await self.parser_result(start_time, url, session)

    async def recent(self, category, page, limit):
        """Get recent torrents from `Limetorrent`."""
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            if not category:
                url = self.url + "/latest100"
            else:
                category = (category).capitalize()
                if category == "Apps":
                    category = "Applications"
                elif category == "Tv":
                    category = "TV-shows"
                url = self.url + "/browse-torrents/{}/date/{}/".format(category, page)
            return await self.parser_result(start_time, url, session)
