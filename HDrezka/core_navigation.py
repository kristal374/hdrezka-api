from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Union, TypeVar, Generic

from .connector import NetworkClient
from .filters import (
    Filters,
    ShowCategory,
    GenreFilm,
    GenreSeries,
    GenreCartoons,
    GenreAnimation,
)
from .html_representation import PageRepresentation

IteratorResponse = TypeVar("IteratorResponse")


class PageIterator(ABC, Generic[IteratorResponse]):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_connector"):
            cls._connector = NetworkClient()
        return super().__new__(cls)

    def __init__(self):
        self._page = 1
        self._last_page = None

    @property
    def current_page(self):
        return self._page

    @current_page.setter
    def current_page(self, value: int):
        self.page(value)

    @property
    def last_page(self):
        return self._last_page or 1

    @last_page.setter
    def last_page(self, value: int):
        if not isinstance(value, int) or value <= 0:
            raise AttributeError(
                'Attribute last page must be of type "int" and greater than 0.'
                f'Received type "{type(value).__name__}" with value "{value}".'
            )
        self._last_page = value

    @staticmethod
    def _get_last_page_number(response):
        navigation = response.page.soup.find("div", class_="b-navigation")
        if not navigation:
            return 1
        next_page_element = navigation.find(class_="b-navigation__next")
        if next_page_element:
            return int(next_page_element.parent.find_previous("a").string)
        return int(navigation.find_all("span")[-1].text)

    def page(self, num: int):
        if isinstance(num, bool) or not isinstance(num, int) or num <= 0:
            if isinstance(num, str) and num.isdigit() and num != "0":
                num = int(num)
            else:
                raise AttributeError(
                    'Attribute "num" must be of type "int" and greater than 0. '
                    f'Received type "{type(num).__name__}", value: "{num}".'
                )
        self._page = num
        return self

    def __iter__(self):
        return self

    def __next__(self) -> IteratorResponse:
        if self._last_page is not None and self.current_page > self.last_page:
            raise StopIteration
        result = self.get()
        self.current_page += 1
        return result

    @abstractmethod
    def get(self) -> IteratorResponse:
        ...

    def __str__(self):
        return f"page/{self.current_page}/" if self.current_page > 1 else ""


class Query:
    def __init__(self):
        self._params = {"filter": Filters.LAST.value, "genre": ShowCategory.ALL.value}

    def filter(self, pattern: Optional[Union[Filters, str]] = ShowCategory.ALL):
        if pattern is None:
            self._params["filter"] = Filters.LAST.value
        elif isinstance(pattern, Filters):
            self._params["filter"] = pattern.value
        elif isinstance(pattern, str):
            self._params["filter"] = pattern
        else:
            raise AttributeError('Attribute "pattern" must be of type "str". Use ready-made genres in filters.Filters')
        return self

    def show_only(self, pattern: Optional[Union[ShowCategory, int]] = ShowCategory.ALL):
        if pattern is None:
            self._params["genre"] = ShowCategory.ALL.value
        elif isinstance(pattern, ShowCategory):
            self._params["genre"] = pattern.value
        elif not isinstance(pattern, bool) and isinstance(pattern, int) and pattern >= 0:
            self._params["genre"] = pattern
        else:
            raise AttributeError(
                'Attribute "pattern" must be of type "ShowCategory" or "int". '
                "Use ready-made pattern in filters.ShowCategory"
            )
        return self

    def __str__(self):
        genre = f'genre={self._params["genre"]}' if self._params["genre"] != ShowCategory.ALL.value else ""
        custom_filter = ""
        if self._params["filter"] != Filters.LAST.value or genre != "":
            custom_filter = f'filter={self._params["filter"]}'
        return f'?{"&".join([i for i in (custom_filter, genre) if i != ""])}'.rstrip("?")


class Genre:
    def __init__(self):
        self._genre: Optional[str] = None

    @property
    def genre(self):
        return self._genre

    @genre.setter
    def genre(
        self,
        value: Optional[Union[GenreFilm, GenreSeries, GenreCartoons, GenreAnimation, str]] = None,
    ):
        if isinstance(value, (GenreFilm, GenreSeries, GenreCartoons, GenreAnimation)):
            self._genre = value.value
        elif value is None or isinstance(value, str):
            self._genre = value
        else:
            raise AttributeError('Attribute "value" must be of type "str". Use ready-made genres filters.Genre*')

    def __str__(self):
        return f"{self._genre}/" if self._genre is not None else ""


class Year:
    def __init__(self):
        self._year: Optional[int] = None

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value: Optional[int] = None):
        if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value < 1895):
            raise AttributeError('Attribute "year" must be of type "int" and greater than or equal to 1895')
        self._year = value

    def __str__(self):
        return f"{self._year}/" if self._year is not None else ""


class Country:
    def __init__(self):
        self._country: Optional[str] = None

    @property
    def country(self):
        return self._country

    @country.setter
    def country(self, value: Optional[int] = None):
        if value is None or not isinstance(value, str):
            raise AttributeError('Attribute "value" must be of type "str".')
        self._country = value

    def __str__(self):
        return f"country/{self._country}/" if self._country is not None else ""


class BaseSiteNavigation(PageIterator[IteratorResponse]):
    _name: Optional[str] = None

    @abstractmethod
    def get(self):
        response = PageRepresentation(self._connector.get(str(self)).text)
        if self.last_page == 1:
            self.last_page = self._get_last_page_number(response)
        return response.page

    def __str__(self):
        name = f"{self._name}/" if self._name else ""
        return f"{self._connector.url}/{name}{PageIterator.__str__(self)}"
