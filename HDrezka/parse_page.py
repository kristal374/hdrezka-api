from abc import ABC, abstractmethod
from requests import exceptions
from urllib.parse import quote

from HDrezka.connector import SiteConnector
from HDrezka.filters import *
from HDrezka.page_representation import MovieForm, NewForm, AnnounceForm, CollectionsForm, SearchForm


class BaseSingleCategory(ABC):
    _name = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "connector"):
            cls.connector = SiteConnector()
        return super(BaseSingleCategory, cls).__new__(cls)

    def __init__(self):
        self._path = {"genre": '', "page": ''}
        self._modifier = {"filter": '', "display": ''}

    @abstractmethod
    def get(self):
        try:
            response = self.connector.session.get(self.__str__())
        except exceptions.ConnectionError:
            raise exceptions.ConnectionError(
                f"Failed to establish a new connection. Max retries exceeded with url: {self}") from None
        return response.text

    def page(self, n):
        self._path["page"] = n
        return self

    @abstractmethod
    def find_best(self, *, genre=None, year: int = None):
        select_genre = genre if genre is not None else self._path.get("genre")
        return Best(self._name).select(genre=select_genre, year=year)

    def __str__(self):
        def separator(x, sep): return f"{x}{sep}" if x != '' and x is not None else ''

        genre = separator(self._path.get("genre"), "/")
        page = separator(self._path.get('page'), "/")

        filters = separator(self._modifier.get('filter'), "&")
        display = separator(self._modifier.get('display'), "&")
        options = f"{filters}{display}"[:-1:]

        return f"{self.connector.url}/{self._name}/{genre}{f'page/{page}' if page != '' else ''}{options}"


class BaseCategory(BaseSingleCategory, ABC):
    @abstractmethod
    def selected_category(self, genre):
        self._path["genre"] = genre
        return self

    def filter(self, pattern: Filters = Filters.LAST):
        self._modifier["filter"] = f"?filter={pattern}"
        return self


class Films(BaseCategory):
    _name = "films"

    def selected_category(self, genre: GenreFilm):
        return super(Films, self).selected_category(genre)

    def find_best(self, *, genre: GenreFilm = None, year: int = None):
        return super(Films, self).find_best(genre=genre, year=year)

    def get(self):
        return MovieForm(super(Films, self).get()).extract_content()


class Cartoons(BaseCategory):
    _name = "cartoons"

    def selected_category(self, genre: GenreCartoons):
        return super(Cartoons, self).selected_category(genre)

    def find_best(self, *, genre: GenreCartoons = None, year: int = None):
        return super(Cartoons, self).find_best(genre=genre, year=year)

    def get(self):
        return MovieForm(super(Cartoons, self).get()).extract_content()


class Series(BaseCategory):
    _name = "series"

    def selected_category(self, genre: GenreSeries):
        return super(Series, self).selected_category(genre)

    def find_best(self, *, genre: GenreSeries = None, year: int = None):
        return super(Series, self).find_best(genre=genre, year=year)

    def get(self):
        return MovieForm(super(Series, self).get()).extract_content()


class Animation(BaseCategory):
    _name = "animation"

    def selected_category(self, genre: GenreAnimation):
        return super(Animation, self).selected_category(genre)

    def find_best(self, *, genre: GenreAnimation = None, year: int = None):
        return super(Animation, self).find_best(genre=genre, year=year)

    def get(self):
        return MovieForm(super(Animation, self).get()).extract_content()


class New(BaseSingleCategory):
    _name = "new"

    def filter(self, pattern: Filters = Filters.LAST):
        self._modifier["filter"] = f"?filter={pattern}"
        return self

    def show_only(self, pattern: ShowCategory = ShowCategory.ALL):
        self._modifier["display"] = f"genre={pattern}"
        return self

    def get(self):
        return NewForm(super(New, self).get()).extract_content()


class Announce(BaseSingleCategory):
    _name = "announce"

    def get(self):
        return AnnounceForm(super(Announce, self).get()).extract_content()


class Collections(BaseSingleCategory):
    _name = "collections"

    def get(self):
        return CollectionsForm(super(Collections, self).get()).extract_content()


class Search(BaseSingleCategory):
    _name = "search"

    def __init__(self):
        super().__init__()
        self._search_text = None

    def query(self, text: str):
        quote_text = quote(text)
        self._search_text = f"?do=search&subaction=search&q={quote_text}"  # noqa
        return self

    def get(self):
        return SearchForm(super(Search, self).get()).extract_content()

    def __str__(self):
        page = self._path.get('page')
        return f"{self.connector.url}/{self._name}/{self._search_text}&{f'page={page}&' if page else ''}"[:-1:]


class Best(BaseSingleCategory):
    def __init__(self, name):
        super().__init__()
        self._best_params = [name, "best"]

    def select(self, *, genre=None, year: int = None):
        self._best_params = self._best_params[:2]
        if genre is not None and genre != '':
            self._best_params.append(genre)
        if year is not None and year != '':
            self._best_params.append(year)
        return self

    def get(self):
        return MovieForm(super(Best, self).get()).extract_content()

    def __str__(self):
        page = self._path.get("page")
        page = f"page/{page}/" if page is not None and page != "" else ""
        separator = "/"
        return f"{self.connector.url}/{separator.join(map(str, self._best_params))}/{page}"

# class PageInfo:
#     def __init__(self):
#         self.name = None
#         self.original_name = None
#         self.rates = None
#         self.on_the_lists = None
#         self.tagline = None
#         self.release = None
#         self.country = None
#         self.producer = None
#         self.genre = None
#         self.age = None
#         self.time = None
#         self.playlist = None
#         self.cast = None
#         self.title = None
#
