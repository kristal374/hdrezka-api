from typing import Optional, Union
from urllib.parse import quote_plus

from .core_navigation import PageIterator, Genre, Year, Query, BaseSiteNavigation, BaseFilmCategory
from .filters import Filters, ShowCategory, GenreAnimation, GenreFilm, GenreCartoons, GenreSeries
from .franchises import FranchisesBriefInfoBuilder
from .page_representation import PosterBuilder, MovieCollectionBuilder
from .questions_asked import QuestionsBriefInfoBuilder


class Best(BaseSiteNavigation):
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
            year: Optional[int] = None
    ):
        self._genre.genre = genre
        self._year.year = year
        return self

    def get(self):
        return PosterBuilder(super().get()).extract_content()

    def __str__(self):
        page = PageIterator.__str__(self)
        return f"{self._connector.url}/{self._category_name}/{self._name}/{self._genre}{self._year}{page}"


class Films(BaseFilmCategory):
    _name = "films"

    def selected_category(self, genre: Optional[Union[GenreFilm, str]]):
        return super().selected_category(genre)

    def find_best(self, *, genre: Optional[Union[GenreFilm, str]] = None, year: Optional[int] = None):
        return Best(self._name).select(genre=genre, year=year)


class Cartoons(BaseFilmCategory):
    _name = "cartoons"

    def selected_category(self, genre: Optional[Union[GenreCartoons, str]]):
        return super().selected_category(genre)

    def find_best(self, *, genre: Optional[Union[GenreCartoons, str]] = None, year: Optional[int] = None):
        return Best(self._name).select(genre=genre, year=year)


class Series(BaseFilmCategory):
    _name = "series"

    def selected_category(self, genre: Optional[Union[GenreSeries, str]]):
        return super().selected_category(genre)

    def find_best(self, *, genre: Optional[Union[GenreSeries, str]] = None, year: Optional[int] = None):
        return Best(self._name).select(genre=genre, year=year)


class Animation(BaseFilmCategory):
    _name = "animation"

    def selected_category(self, genre: Optional[Union[GenreAnimation, str]]):
        return super().selected_category(genre)

    def find_best(self, *, genre: Optional[Union[GenreAnimation, str]] = None, year: Optional[int] = None):
        return Best(self._name).select(genre=genre, year=year)


class New(BaseSiteNavigation):
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

    def get(self):
        return PosterBuilder(super().get()).extract_content()

    def __str__(self):
        return f"{super().__str__()}{self._query}"


class Announce(BaseSiteNavigation):
    _name = "announce"

    def get(self):
        return PosterBuilder(super().get()).extract_content()


class Collections(BaseSiteNavigation):
    _name = "collections"

    def get(self):
        return MovieCollectionBuilder(super().get()).extract_content()


class Search(BaseSiteNavigation):
    _name = "search"

    def __init__(self):
        super().__init__()
        self._search_text = None

    def query(self, text: str):
        if not isinstance(text, str):
            raise AttributeError("Attribute \"text\" must only be of type \"str\".")
        process_text = quote_plus(text).replace("%2A", "*").replace("/", "%2F").replace("~", "%7E")
        self._search_text = f"?do=search&subaction=search&q={process_text}"
        return self

    def get(self):
        return PosterBuilder(super().get()).extract_content()

    def __str__(self):
        page = f"&page={self.current_page}" if self.current_page > 1 else ""
        text = f"{self._search_text}" if self._search_text else ''
        return f"{self._connector.url}/{self._name}/{text}{page}"


class QuestionsAsked(BaseSiteNavigation):
    _name = "qa"

    def get(self):
        return QuestionsBriefInfoBuilder(super().get()).extract_content()


class Franchises(BaseSiteNavigation):
    _name = "franchises"

    def get(self):
        return FranchisesBriefInfoBuilder(super().get()).extract_content()
