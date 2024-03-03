from abc import ABC, abstractmethod
from typing import Optional, Union, Dict
from urllib.parse import quote

from .connector import NetworkClient
from .filters import Filters, GenreFilm, GenreCartoons, GenreAnimation, GenreSeries, ShowCategory
from .franchises import FranchisesBriefInfoBuilder
from .html_representation import PageRepresentation
from .page_representation import PosterBuilder, MovieCollectionBuilder
from .questions_asked import QuestionsBriefInfoBuilder


class BaseSingleCategory(ABC):
    _name = None

    def __new__(cls, *args, **kwargs):  # pylint: disable= W0613
        if not hasattr(cls, "connector"):
            cls.connector = NetworkClient()
        return super(BaseSingleCategory, cls).__new__(cls)

    def __init__(self):
        self._path: Dict[str, Optional[Union[str, int]]] = {"genre": '', "page": None}
        self._modifier: Dict[str, Optional[str]] = {"filter": '', "display": ''}
        self._last_page = None

    @property
    def current_page(self):
        return self._path["page"] or 1

    @current_page.setter
    def current_page(self, value):
        self.page(value)

    @property
    def last_page(self):
        return self._last_page

    def __iter__(self):
        return self

    def __next__(self):
        if self._path["page"] is None:
            self._path["page"] = 0
        self._path["page"] += 1
        if self._last_page is not None and self._path["page"] > self.last_page:
            raise StopIteration
        return self.get()

    @abstractmethod
    def get(self):
        response = PageRepresentation(self.connector.get(str(self)).text)
        if self.last_page is None:
            self._set_last_page_number(response)
        return response.page

    def page(self, n: int):
        if isinstance(n, bool) or not isinstance(n, int) or n <= 0:
            if isinstance(n, str) and n.isdigit() and n != "0":
                n = int(n)
            else:
                raise AttributeError("Attribute \"n\" must be of type \"int\" and greater than 0. "
                                     f"Received type \"{type(n).__name__}\", value: \"{n}\".")
        self._path["page"] = n
        return self

    def _set_last_page_number(self, response):
        navigation = response.page.soup.find("div", class_="b-navigation")
        if not navigation:
            self._last_page = 1
        else:
            next_page_element = navigation.find(class_="b-navigation__next")
            if next_page_element:
                self._last_page = int(next_page_element.parent.find_previous("a").string)
            else:
                self._last_page = int(navigation.find_all("span")[-1].text)

    def __str__(self):
        def separator(x, sep):
            return f"{x}{sep}" if x != '' and x is not None else ''

        name = separator(self._name, "/")
        genre = separator(self._path.get("genre"), "/")
        page = separator(self._path.get('page'), "/") if self._path.get('page') != 1 else ""

        filters = separator(self._modifier.get('filter'), "&")
        display = separator(self._modifier.get('display'), "&")
        options = f"{filters}{display}"[:-1:]
        options = f"?{options}" if len(options) > 0 and options[0] != "?" else options

        return f"{self.connector.url}/{name}{genre}{f'page/{page}' if page != '' else ''}{options}"


class BaseCategory(BaseSingleCategory, ABC):
    @abstractmethod
    def selected_category(self, genre: Optional[str]):
        if not isinstance(genre, str) and genre is not None:
            raise AttributeError("Attribute \"genre\" must be of type \"str\". Use ready-made genres filters.Genre*")
        self._path["genre"] = genre
        return self

    def filter(self, pattern: Optional[Union[Filters, str]] = Filters.LAST):
        if pattern is None:
            self._modifier["filter"] = ""
            return self
        if not isinstance(pattern, str):
            raise AttributeError(
                "Attribute \"pattern\" must be of type \"str\". Use ready-made genres in filters.Filters")
        self._modifier["filter"] = f"?filter={pattern}"
        return self

    @abstractmethod
    def find_best(self, genre: Optional[str] = None, year: Optional[int] = None):
        select_genre = genre if genre is not None else self._path.get("genre")
        return Best(self._name).select(genre=select_genre, year=year)


class Films(BaseCategory):
    _name = "films"

    def selected_category(self, genre: Optional[Union[GenreFilm, str]]):
        return super().selected_category(genre)

    def find_best(self, genre: Optional[Union[GenreFilm, str]] = None, year: Optional[int] = None):
        return super().find_best(genre=genre, year=year)

    def get(self):
        return PosterBuilder(super().get()).extract_content()


class Cartoons(BaseCategory):
    _name = "cartoons"

    def selected_category(self, genre: Optional[Union[GenreCartoons, str]]):
        return super().selected_category(genre)

    def find_best(self, genre: Optional[Union[GenreCartoons, str]] = None, year: Optional[int] = None):
        return super().find_best(genre=genre, year=year)

    def get(self):
        return PosterBuilder(super().get()).extract_content()


class Series(BaseCategory):
    _name = "series"

    def selected_category(self, genre: Optional[Union[GenreSeries, str]]):
        return super().selected_category(genre)

    def find_best(self, genre: Optional[Union[GenreSeries, str]] = None, year: int = None):
        return super().find_best(genre=genre, year=year)

    def get(self):
        return PosterBuilder(super().get()).extract_content()


class Animation(BaseCategory):
    _name = "animation"

    def selected_category(self, genre: Optional[Union[GenreAnimation, str]]):
        return super().selected_category(genre)

    def find_best(self, genre: Optional[Union[GenreAnimation, str]] = None, year: int = None):
        return super().find_best(genre=genre, year=year)

    def get(self):
        return PosterBuilder(super().get()).extract_content()


class New(BaseSingleCategory):
    _name = "new"

    def filter(self, pattern: Optional[Union[Filters, str]] = Filters.LAST):
        if pattern is None:
            self._modifier["filter"] = ""
            return self
        if not isinstance(pattern, str):
            raise AttributeError(
                "Attribute \"pattern\" must be of type \"str\". Use ready-made genres in filters.Filters")
        self._modifier["filter"] = f"?filter={pattern}"
        return self

    def show_only(self, pattern: Optional[Union[ShowCategory, int]] = ShowCategory.ALL):
        if pattern is None or pattern == ShowCategory.ALL and not isinstance(pattern, bool):
            self._modifier["display"] = ""
        elif isinstance(pattern, bool) or not isinstance(pattern, int) or pattern < 0:
            raise AttributeError("Attribute \"pattern\" must be of type \"int\". "
                                 "Use ready-made pattern in filters.ShowCategory")
        else:
            self._modifier["display"] = f"genre={pattern}"
        if not self._modifier.get("filter") and pattern is not None:
            self.filter()
        return self

    def get(self):
        return PosterBuilder(super().get()).extract_content()


class Announce(BaseSingleCategory):
    _name = "announce"

    def get(self):
        return PosterBuilder(super().get()).extract_content()


class Collections(BaseSingleCategory):
    _name = "collections"

    def get(self):
        return MovieCollectionBuilder(super().get()).extract_content()


class Search(BaseSingleCategory):
    _name = "search"

    def __init__(self):
        super().__init__()
        self._search_text = None

    def query(self, text: str):
        if not isinstance(text, str):
            raise AttributeError("Attribute \"text\" must only be of type \"str\".")
        quote_text = "+".join(quote(t) for t in text.split())
        quote_text = quote_text.replace("%2A", "*").replace("/", "%2F").replace("~", "%7E")
        self._search_text = f"?do=search&subaction=search&q={quote_text}"  # noqa
        return self

    def get(self):
        return PosterBuilder(super().get()).extract_content()

    def __str__(self):
        page = self._path.get('page')
        page = f'&page={page}' if page else ''
        text = f"{self._search_text}" if self._search_text else ''
        return f"{self.connector.url}/{self._name}/{text}{page}"


class Best(BaseSingleCategory):
    def __init__(self, name):
        super().__init__()
        self._best_params = [name, "best"]

    def select(self, genre: Optional[str] = None, year: int = None):
        if year is not None and (isinstance(year, bool) or not isinstance(year, int) or year < 1895):
            raise AttributeError("Attribute \"year\" must be of type \"int\" and greater than or equal to 1895")
        if genre is not None and not isinstance(genre, str):
            raise AttributeError("Attribute \"genre\" must be of type \"str\". Use ready-made genres in filters.Genre*")
        self._best_params = self._best_params[:2]
        if genre is not None and genre != '':
            self._best_params.append(genre)
        if year is not None and year != '':
            self._best_params.append(year)
        return self

    def get(self):
        return PosterBuilder(super().get()).extract_content()

    def __str__(self):
        page = self._path.get("page")
        page = f"page/{page}/" if page is not None and page != "" else ""
        separator = "/"
        return f"{self.connector.url}/{separator.join(map(str, self._best_params))}/{page}"


class QuestionsAsked(BaseSingleCategory):
    _name = "qa"

    def get(self):
        return QuestionsBriefInfoBuilder(super().get()).extract_content()


class Franchises(BaseSingleCategory):
    _name = "franchises"

    def get(self):
        return FranchisesBriefInfoBuilder(super().get()).extract_content()
