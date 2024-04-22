from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, TYPE_CHECKING

from . import movie_page_descriptor
from .connector import NetworkClient
from .html_representation import PageRepresentation

if TYPE_CHECKING:
    from .movie_page_descriptor import MovieDetails


@dataclass
class Franchise:
    title: str  # Название фильма
    year: str  # год выпуска фильма
    rating: str  # рейтинг фильма
    url: str  # ссылка на фильм

    def get(self) -> MovieDetails:
        return movie_page_descriptor.MovieDetailsBuilder(NetworkClient().get(self.url).text).extract_content()

    def __repr__(self):
        return f"<Franchise({self.title})>"


class FranchisesBuilder(PageRepresentation):
    def extract_content(self) -> List[Franchise]:
        result_lst = []
        for item in self.page.soup.find_all("div", class_="b-post__partcontent_item"):
            url = item.find("div", class_="title").a
            base_url = self.page.soup.find("meta", property="og:url").get("content").strip()
            result_lst.append(
                Franchise(
                    title=item.find("div", class_="title").text.strip(),
                    url=url.get("href") if url else base_url,
                    year=item.find("div", class_="year").text.strip(),
                    rating=item.find("div", class_="rating").text.strip(),
                )
            )
        return result_lst


@dataclass
class FranchiseBriefInfo:
    id: int
    title: str
    amount_film: int
    img_url: str
    url: str

    def get(self):
        return FranchisesBuilder(NetworkClient().get(self.url).text).extract_content()

    def __repr__(self):
        return f"<FranchiseBriefInfo({self.title})>"


class FranchisesBriefInfoBuilder(PageRepresentation):
    def extract_content(self) -> List[FranchiseBriefInfo]:
        result_list = []
        content = self.page.soup.find("div", class_="b-content__collections_list clearfix")
        for item in content.find_all("div", class_="b-content__collections_item"):
            url = item.find("div", class_="title-layer").a.get("href").strip()
            result_list.append(
                FranchiseBriefInfo(
                    id=int(re.search(r"/(\d+)-", url)[1]),
                    title=item.find("div", class_="title-layer").text.strip(),
                    amount_film=int(item.find("div", class_="num").text),
                    img_url=item.img.get("src").strip(),
                    url=url,
                )
            )
        return result_list
