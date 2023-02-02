from abc import ABC

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

    def __str__(self):
        def separator(x, sep): return f"{x}{sep}" if x != '' and x is not None else ''

        genre = separator(self._path.get("genre"), "/")
        page = separator(self._path.get('page'), "/")

        filters = separator(self._modifier.get('filter'), "&")
        display = separator(self._modifier.get('display'), "&")
        options = f"{filters}{display}"[:-1:]

        return f"{self.name}/{genre}{f'page/{page}' if page != '' else ''}{options}"


class BaseCategory(BaseSingleCategory, ABC):
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


class Cartoons(BaseCategory, ABC):
    name = "cartoons"

    def selected_category(self, genre: GenreCartoons):
        return super(Cartoons, self).selected_category(genre)


class Series(BaseCategory, ABC):
    name = "series"

    def selected_category(self, genre: GenreSeries):
        return super(Series, self).selected_category(genre)


class Animation(BaseCategory, ABC):
    name = "animation"

    def selected_category(self, genre: GenreAnimation):
        return super(Animation, self).selected_category(genre)


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
