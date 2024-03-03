from __future__ import annotations

import dataclasses
import re
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from urllib.parse import urlsplit, urljoin

from . import franchises
from . import html_representation, page_representation, movie_page_descriptor, questions_asked, person
from .connector import NetworkClient
from .filters import GenreFilm, GenreSeries, GenreAnimation, GenreCartoons
from .site_navigation import Animation
from .site_navigation import Announce
from .site_navigation import BaseSingleCategory
from .site_navigation import Cartoons
from .site_navigation import Collections
from .site_navigation import Films
from .site_navigation import New
from .site_navigation import QuestionsAsked
from .site_navigation import Search
from .site_navigation import Series
from .utility import convert_string_into_datetime
from .utility import get_url_type, URLsType

if TYPE_CHECKING:
    from .page_representation import Poster, MovieCollection

__all__ = ["HDrezka", "MainPage"]


class HDrezka(BaseSingleCategory):
    def __init__(self, mirror="https://rezka.ag"):
        super().__init__()
        self.connector = NetworkClient(domain=urlsplit(str(mirror))[1])

    @staticmethod
    def films(genre: Optional[GenreFilm] = None) -> Films:
        return Films().selected_category(genre)

    @staticmethod
    def cartoons(genre: Optional[GenreCartoons] = None) -> Cartoons:
        return Cartoons().selected_category(genre)

    @staticmethod
    def series(genre: Optional[GenreSeries] = None) -> Series:
        return Series().selected_category(genre)

    @staticmethod
    def animation(genre: Optional[GenreAnimation] = None) -> Animation:
        return Animation().selected_category(genre)

    @staticmethod
    def new() -> New:
        return New()

    @staticmethod
    def announce() -> Announce:
        return Announce()

    @staticmethod
    def collections() -> Collections:
        return Collections()

    @staticmethod
    def search(text: str) -> Search:
        return Search().query(text)

    @staticmethod
    def questions_asked() -> QuestionsAsked:
        return QuestionsAsked()

    def get(self, url: Optional[str] = None):  # pylint: disable = R0911
        if url is not None:
            response = self.connector.get(url).text
            url_type = get_url_type(url)
            if url_type == URLsType.main:
                return MainPageBuilder(response).extract_content()
            if url_type == URLsType.movie:
                return movie_page_descriptor.MovieDetailsBuilder(response).extract_content()
            if url_type == URLsType.collections:
                return page_representation.MovieCollectionBuilder(response).extract_content()
            if url_type == URLsType.qa_info:
                return questions_asked.QuestionsBuilder(response).extract_content()
            if url_type == URLsType.qa:
                return questions_asked.QuestionsBriefInfoBuilder(response).extract_content()
            if url_type == URLsType.franchises_info:
                return franchises.FranchisesBuilder(response).extract_content()
            if url_type == URLsType.franchises:
                return franchises.FranchisesBriefInfoBuilder(response).extract_content()
            if url_type == URLsType.person_info:
                return person.PersonBuilder(response).extract_content()
            if url_type == URLsType.poster:
                return page_representation.PosterBuilder(response).extract_content()
            raise AttributeError("Incorrect url")

        if self.current_page == 1 and not any(self._modifier.values()):
            return MainPageBuilder(super().get()).extract_content()
        return page_representation.PosterBuilder(super().get()).extract_content()


@dataclasses.dataclass
class Release:
    title: str  # Название фильма
    season: str  # Номер сезона, пример: "1-2 сезон"
    episode: str  # Номер эпизода, пример: "1-4 серия"/"12 серия"
    translator: str  # Название озвучки
    url: str  # ссылка на фильм

    def __repr__(self):
        return f"<Release({self.title})>"


@dataclasses.dataclass
class DayReleases:
    date: datetime  # дата в которую были выложены данные релизы
    releases: List[Release]  # список с релизами этого дня

    def __iter__(self):
        return iter(self.releases)

    def __repr__(self):
        return f"DayReleases({self.date})"


@dataclasses.dataclass
class MainPage:
    best_news: List[Poster] = None  # лучшие новинки за последнее время
    posters: List[Poster] = None  # список постеров с
    recommended_collections: List[MovieCollection] = None
    updates: List[DayReleases] = None

    def __iter__(self):
        return iter(self.posters)

    def __repr__(self):
        return "<MainPage>"


class MainPageBuilder(html_representation.PageRepresentation):
    def extract_content(self):
        best_news_block = self.page.soup.find("div", id="newest-slider")
        poster_block = self.page.soup.find("div", class_="b-content__inline_items")

        main_page = MainPage()
        main_page.best_news = page_representation.PosterBuilder(best_news_block).extract_content()
        main_page.posters = page_representation.PosterBuilder(poster_block).extract_content()
        main_page.recommended_collections = self.extract_collections()
        main_page.updates = self.extract_updates()
        return main_page

    def __extract_base_url(self):
        page_url = urlsplit(self.page.soup.find('meta', property='og:url').get("content"))
        return f"{page_url.scheme}://{page_url.netloc}/"

    def extract_collections(self):
        result_list = []
        collections = self.page.soup.find("div", class_="b-collections__newest")
        base_url = self.__extract_base_url()
        for collection_obj in collections.find_all("a"):
            collection = page_representation.MovieCollection()
            collection.id = int(re.search(r"(?<=collections/)[^\-]\d*", collection_obj.get("href")).group(0))
            collection.title = collection_obj.span.text.strip()
            collection.img_url = collection_obj.img.get("src")
            collection.url = urljoin(base_url, collection_obj.get("href"))
            result_list.append(collection)
        return result_list

    def extract_updates(self):
        result_list = []
        base_url = self.__extract_base_url()
        updates_block = self.page.soup.find("div", class_="b-content__inline_sidebar")
        for day_block in updates_block.find_all("div", class_="b-seriesupdate__block"):
            release_list = []
            for item in day_block.find("ul", class_="b-seriesupdate__block_list"):
                cell = item.find(class_="cell-2")
                release_list.append(
                    Release(
                        title=item.a.string.strip(),
                        season=item.find(class_="season").string.strip()[1:-1],
                        episode=cell.next.strip(),
                        translator=cell.i.string.strip()[1:-1] if cell.i else None,
                        url=urljoin(base_url, item.a.get("href"))
                    )
                )
            day_obj = day_block.find("div", class_="b-seriesupdate__block_date")
            date = day_obj.small.string.strip()[1:-1] if day_obj.small else day_obj.next.string.strip()
            result_list.append(
                DayReleases(
                    date=convert_string_into_datetime(date),
                    releases=release_list
                )
            )

        return result_list
