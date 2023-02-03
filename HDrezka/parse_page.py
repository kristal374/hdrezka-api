from abc import ABC, abstractmethod

from HDrezka.filters import *


class BaseSingleCategory:
    name = None

    def __init__(self):
        self._path = {"genre": '', "page": ''}
        self._modifier = {"filter": '', "display": ''}

    def get(self):
        raise NotImplementedError

    def page(self, n):
        self._path["page"] = n
        return self

    @abstractmethod
    def find_best(self, *, genre=None, year: int = None):
        select_genre = genre if genre is not None else self._path.get("genre")
        return Best(self.name).select(genre=select_genre, year=year)

    def __str__(self):
        def separator(x, sep): return f"{x}{sep}" if x != '' and x is not None else ''

        genre = separator(self._path.get("genre"), "/")
        page = separator(self._path.get('page'), "/")

        filters = separator(self._modifier.get('filter'), "&")
        display = separator(self._modifier.get('display'), "&")
        options = f"{filters}{display}"[:-1:]

        return f"{self.name}/{genre}{f'page/{page}' if page != '' else ''}{options}"


class BaseCategory(BaseSingleCategory, ABC):
    @abstractmethod
    def selected_category(self, genre):
        self._path["genre"] = genre
        return self

    def filter(self, pattern: Filters = Filters.LAST):
        self._modifier["filter"] = f"?filter={pattern}"
        return self


class Films(BaseCategory, ABC):
    name = "films"

    def selected_category(self, genre: GenreFilm):
        return super(Films, self).selected_category(genre)

    def find_best(self, *, genre: GenreFilm = None, year: int = None):
        return super(Films, self).find_best(genre=genre, year=year)


class Cartoons(BaseCategory, ABC):
    name = "cartoons"

    def selected_category(self, genre: GenreCartoons):
        return super(Cartoons, self).selected_category(genre)

    def find_best(self, *, genre: GenreCartoons = None, year: int = None):
        return super(Cartoons, self).find_best(genre=genre, year=year)


class Series(BaseCategory, ABC):
    name = "series"

    def selected_category(self, genre: GenreSeries):
        return super(Series, self).selected_category(genre)

    def find_best(self, *, genre: GenreSeries = None, year: int = None):
        return super(Series, self).find_best(genre=genre, year=year)


class Animation(BaseCategory, ABC):
    name = "animation"

    def selected_category(self, genre: GenreAnimation):
        return super(Animation, self).selected_category(genre)

    def find_best(self, *, genre: GenreAnimation = None, year: int = None):
        return super(Animation, self).find_best(genre=genre, year=year)


class New(BaseSingleCategory, ABC):
    name = "new"

    def filter(self, pattern: Filters = Filters.LAST):
        self._modifier["filter"] = f"?filter={pattern}"
        return self

    def show_only(self, pattern: ShowCategory = ShowCategory.ALL):
        self._modifier["display"] = f"genre={pattern}"
        return self


class Announce(BaseSingleCategory, ABC):
    name = "announce"


class Collections(BaseSingleCategory, ABC):
    name = "collections"


class Search(BaseSingleCategory, ABC):
    name = "search"

    def __init__(self):
        super().__init__()
        self._search_text = None

    def query(self, text: str):
        self._search_text = f"?do=search&subaction=search&q={text.replace(' ', '+')}"
        return self

    def __str__(self):
        page = self._path.get('page')
        return f"{self.name}/{self._search_text}&{f'page={page}&' if page else ''}"[:-1:]


class Best(BaseSingleCategory, ABC):
    def __init__(self, name):
        super().__init__()
        self._best_params = [name, "best"]

    def select(self, *, genre=None, year: int = None):
        if genre is not None and genre != '':
            self._best_params.append(genre)
        elif year is not None and year != '':
            self._best_params.append(year)
        else:
            raise AttributeError('Either "genre" or "year" must always be specified.')
        return self

    def __str__(self):
        page = self._path.get("page")
        page = f"/page/{page}/" if page is not None and page != "" else ""
        separator = "/"
        return separator.join(map(str, self._best_params)) + page

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
