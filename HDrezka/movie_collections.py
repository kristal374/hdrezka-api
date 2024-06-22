from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Union, List, Iterator

from .connector import NetworkClient
from .core_navigation import Query, PageIterator, BaseSiteNavigation
from .exceptions import EmptyPage
from .filters import Filters
from .html_representation import PageRepresentation
from .movie_posters import Poster, PosterBuilder


class CollectionIterator(BaseSiteNavigation[List[Poster]]):
    def __init__(self, collection_url: str):
        super().__init__()
        self.collection_url = collection_url
        self._query = Query()

    def filter(self, pattern: Optional[Union[Filters, str]] = Filters.LAST):
        self._query.filter(pattern)
        return self

    def get(self) -> List[Poster]:
        return PosterBuilder(super().get()).extract_content()

    def __str__(self):
        return f"{self.collection_url.rstrip('/')}/{PageIterator.__str__(self)}{self._query}"


@dataclass
class CollectionBriefInfo:
    id: int = None  # идентификатор коллекции
    title: str = None  # название коллекции
    url: str = None  # ссылка на коллекцию

    def get(self, custom_filter: Optional[Union[Filters, str]] = None) -> List[Poster]:
        filter_param = Query().filter(custom_filter)
        return PosterBuilder(NetworkClient().get(f"{self.url}{filter_param}").text).extract_content()

    def __iter__(self) -> Iterator[List[Poster]]:
        return CollectionIterator(self.url)

    def __repr__(self):
        return f"<CollectionBriefInfo({self.title})>"


@dataclass
class MovieCollection:
    id: int = None  # ID коллекции
    title: str = None  # Названия коллекции
    amount_film: Optional[int] = None  # Количество фильмов в коллекции
    img_url: str = None  # Ссылка на обложку коллекции
    url: str = None  # Ссылка на страницу коллекции

    def get(self, custom_filter: Optional[Union[Filters, str]] = None) -> List[Poster]:
        filter_param = Query().filter(custom_filter)
        return PosterBuilder(NetworkClient().get(f"{self.url}{filter_param}").text).extract_content()

    def __iter__(self) -> Iterator[List[Poster]]:
        return CollectionIterator(self.url)

    def __repr__(self):
        return f'MovieCollection("{self.title}")'


class MovieCollectionBuilder(PageRepresentation):
    def extract_content(self):
        collection_info = []
        for item in self.page.soup.find_all("div", class_="b-content__collections_item"):
            collection = MovieCollection()
            collection.id = int(re.search(r"(?<=collections/)[^\-]\d*", item.get("data-url")).group(0))
            collection.title = item.find("a", class_="title").text
            collection.amount_film = int(item.find("div", class_="num").text)
            collection.img_url = item.find("img").get("src")
            collection.url = item.get("data-url")

            collection_info.append(collection)

        if not collection_info:
            raise EmptyPage("No Collections found on the page")
        return collection_info
