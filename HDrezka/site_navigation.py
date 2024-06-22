from __future__ import annotations

from abc import abstractmethod, ABC
from typing import Optional, Union, List
from urllib.parse import quote_plus

from .core_navigation import PageIterator, Genre, Year, Query, BaseSiteNavigation
from .filters import (
    Filters,
    ShowCategory,
    GenreAnimation,
    GenreFilm,
    GenreCartoons,
    GenreSeries,
)
from .franchises import FranchisesBriefInfoBuilder, FranchiseBriefInfo
from .movie_collections import MovieCollectionBuilder, MovieCollection
from .movie_posters import PosterBuilder, Poster
from .questions_asked import QuestionsBriefInfoBuilder, QuestionBriefInfo


class BaseMovieCategory(BaseSiteNavigation[List[Poster]], ABC):
    """
    :class: BaseMovieCategory

    This class represents a base movie category for site navigation and search.
    """

    def __init__(self):
        super().__init__()
        self._genre = Genre()
        self._query = Query()

    @abstractmethod
    def selected_category(self, genre: Optional[Union[GenreFilm, GenreSeries, GenreCartoons, GenreAnimation, str]]):
        self._genre.genre = genre
        return self

    def filter(self, pattern: Optional[Union[Filters, str]] = Filters.LAST):
        self._query.filter(pattern)
        return self

    @abstractmethod
    def find_best(self):
        ...

    def get(self) -> List[Poster]:
        return PosterBuilder(super().get()).extract_content()

    def __str__(self):
        name = f"{self._name}/" if self._name else ""
        return f"{self._connector.url}/{name}{self._genre}{PageIterator.__str__(self)}{self._query}"


class Best(BaseSiteNavigation[List[Poster]]):
    _name = "best"

    def __init__(self, name: str):
        super().__init__()
        self._category_name = name
        self._genre = Genre()
        self._year = Year()

    def select(
        self,
        *,
        genre: Optional[Union[GenreFilm, GenreSeries, GenreCartoons, GenreAnimation, str]] = None,
        year: Optional[int] = None,
    ):
        self._genre.genre = genre
        self._year.year = year
        return self

    def get(self) -> List[Poster]:
        return PosterBuilder(super().get()).extract_content()

    def __str__(self):
        page = PageIterator.__str__(self)
        return f"{self._connector.url}/{self._category_name}/{self._name}/{self._genre}{self._year}{page}"


class Films(BaseMovieCategory):
    _name = "films"

    def selected_category(self, genre: Optional[Union[GenreFilm, str]]):  # type: ignore[override]
        return super().selected_category(genre)

    def find_best(
        self,
        *,
        genre: Optional[Union[GenreFilm, str]] = None,
        year: Optional[int] = None,
    ):
        return Best(self._name).select(genre=genre, year=year)


class Cartoons(BaseMovieCategory):
    _name = "cartoons"

    def selected_category(self, genre: Optional[Union[GenreCartoons, str]]):  # type: ignore[override]
        return super().selected_category(genre)

    def find_best(
        self,
        *,
        genre: Optional[Union[GenreCartoons, str]] = None,
        year: Optional[int] = None,
    ):
        return Best(self._name).select(genre=genre, year=year)


class Series(BaseMovieCategory):
    _name = "series"

    def selected_category(self, genre: Optional[Union[GenreSeries, str]]):  # type: ignore[override]
        return super().selected_category(genre)

    def find_best(
        self,
        *,
        genre: Optional[Union[GenreSeries, str]] = None,
        year: Optional[int] = None,
    ):
        return Best(self._name).select(genre=genre, year=year)


class Animation(BaseMovieCategory):
    _name = "animation"

    def selected_category(self, genre: Optional[Union[GenreAnimation, str]]):  # type: ignore[override]
        return super().selected_category(genre)

    def find_best(
        self,
        *,
        genre: Optional[Union[GenreAnimation, str]] = None,
        year: Optional[int] = None,
    ):
        return Best(self._name).select(genre=genre, year=year)


class New(BaseSiteNavigation[List[Poster]]):
    _name = "new"

    def __init__(self):
        super().__init__()
        self._query = Query()

    def filter(self, pattern: Optional[Union[Filters, str]] = Filters.LAST):
        self._query.filter(pattern)
        return self

    def show_only(self, pattern: Optional[Union[ShowCategory, int]] = ShowCategory.ALL):
        self._query.show_only(pattern)
        return self

    def get(self) -> List[Poster]:
        return PosterBuilder(super().get()).extract_content()

    def __str__(self):
        return f"{super().__str__()}{self._query}"


class Announce(BaseSiteNavigation[List[Poster]]):
    _name = "announce"

    def get(self) -> List[Poster]:
        return PosterBuilder(super().get()).extract_content()


class Collections(BaseSiteNavigation[List[MovieCollection]]):
    _name = "collections"

    def get(self) -> List[MovieCollection]:
        return MovieCollectionBuilder(super().get()).extract_content()


class Search(BaseSiteNavigation[List[Poster]]):
    _name = "search"

    def __init__(self):
        super().__init__()
        self._search_text = None

    def query(self, text: str):
        if not isinstance(text, str):
            raise AttributeError('Attribute "text" must only be of type "str".')
        process_text = quote_plus(text).replace("%2A", "*").replace("/", "%2F").replace("~", "%7E")
        self._search_text = f"?do=search&subaction=search&q={process_text}"
        return self

    def get(self) -> List[Poster]:
        return PosterBuilder(super().get()).extract_content()

    def __str__(self):
        page = f"&page={self.current_page}" if self.current_page > 1 else ""
        text = f"{self._search_text}" if self._search_text else ""
        return f"{self._connector.url}/{self._name}/{text}{page}"


class QuestionsAsked(BaseSiteNavigation[List[QuestionBriefInfo]]):
    _name = "qa"

    def get(self) -> List[QuestionBriefInfo]:
        return QuestionsBriefInfoBuilder(super().get()).extract_content()


class Franchises(BaseSiteNavigation[List[FranchiseBriefInfo]]):
    _name = "franchises"

    def get(self) -> List[FranchiseBriefInfo]:
        return FranchisesBriefInfoBuilder(super().get()).extract_content()
