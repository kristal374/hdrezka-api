from __future__ import annotations

import datetime
import re
from dataclasses import dataclass
from typing import List, TYPE_CHECKING, Optional

from . import movie_page_descriptor
from .connector import NetworkClient
from .html_representation import PageRepresentation
from .utility import convert_string_into_datetime

if TYPE_CHECKING:
    from .movie_page_descriptor import MovieDetails


@dataclass
class FranchiseItem:
    num: int  # номер во франшизе
    title: str  # Название фильма
    year: datetime.datetime  # год выпуска фильма
    rating: Optional[float]  # рейтинг фильма
    url: str  # ссылка на фильм

    def get(self) -> MovieDetails:
        return movie_page_descriptor.MovieDetailsBuilder(NetworkClient().get(self.url).text).extract_content()

    def __repr__(self):
        return f"<FranchiseItem({self.title})>"


@dataclass
class Franchise:
    id: int  # идентификатор
    title: str  # Название фильма
    img_url: str  # изображение
    items_list: List[FranchiseItem]  # Список фильмов данной франшизы
    url: str  # ссылка на фильм

    def __repr__(self):
        return f"<Franchise({self.title})>"


class FranchiseBuilder(PageRepresentation):
    def extract_content(self) -> Franchise:
        url = self.page.soup.find("meta", property="og:url").get("content").strip()
        image = self.page.soup.find("img")
        return Franchise(
            id=int(re.search(r"/(\d*)-", url).group(1)),
            title=image.get("data-caption-title").strip(),
            img_url=image.parent.get("href").strip(),
            items_list=[self.extract_franchise_item(item)
                        for item in self.page.soup.find_all("div", class_="b-post__partcontent_item")[::-1]],
            url=url,
        )

    @staticmethod
    def extract_franchise_item(item) -> FranchiseItem:
        rating = item.find("div", class_="rating").text.strip()
        return FranchiseItem(
            num=int(item.find("div", class_="num").text.strip()),
            title=item.find("div", class_="title").text.strip(),
            year=convert_string_into_datetime(item.find("div", class_="year").text.strip()),
            rating=float(rating) if rating != '—' else None,
            url=item.get("data-url"),
        )


@dataclass
class FranchiseBriefInfo:
    id: int
    title: str
    items_list: List[FranchiseItem]  # Список фильмов данной франшизы
    url: str

    def get(self):
        return FranchiseBuilder(NetworkClient().get(self.url).text).extract_content()

    def __repr__(self):
        return f"<FranchiseBriefInfo({self.title})>"


class FranchiseBriefInfoBuilder(PageRepresentation):
    def extract_content(self) -> Optional[FranchiseBriefInfo]:
        url = self.page.soup.find(class_="b-post__franchise_link_title")
        if url is None:
            return None
        return FranchiseBriefInfo(
            id=int(re.search(r"/(\d*)-", url.get("href").strip()).group(1)),
            title=self.page.soup.find(class_="b-post__franchise_link_title").text.strip(),
            items_list=[FranchiseBuilder.extract_franchise_item(item)
                        for item in self.page.soup.find_all("div", class_="b-post__partcontent_item")[::-1]],
            url=url.get("href").strip(),
        )


@dataclass
class FranchiseBanner:
    id: int
    title: str
    amount_film: int
    img_url: str
    url: str

    def get(self):
        return FranchiseBuilder(NetworkClient().get(self.url).text).extract_content()

    def __repr__(self):
        return f"<FranchiseBanner({self.title})>"


class FranchiseBannerBuilder(PageRepresentation):
    def extract_content(self) -> List[FranchiseBanner]:
        content = self.page.soup.find("div", class_="b-content__collections_list clearfix")
        return [FranchiseBanner(
            id=int(re.search(r"/(\d+)-", item.find("div", class_="title-layer").a.get("href").strip())[1]),
            title=item.find("div", class_="title-layer").text.strip(),
            amount_film=int(item.find("div", class_="num").text),
            img_url=item.img.get("src").strip(),
            url=item.find("div", class_="title-layer").a.get("href").strip(),
        ) for item in content.find_all("div", class_="b-content__collections_item")]
