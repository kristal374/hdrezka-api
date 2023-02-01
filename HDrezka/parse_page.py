from filters import *


class BaseSingleCategory:
    name = None

    def get(self):
        raise NotImplementedError

    def __str__(self):
        return f"{self.name}/"


class BaseCategory(BaseSingleCategory):
    def __init__(self):
        self._params = None
        self._filter_pattern = None

    def selected_category(self, genre):
        self._params = genre
        return self

    def filter(self, pattern: Filters):
        self._filter_pattern = f"?filter={pattern}"
        return self

    def __str__(self):
        separator = "/"
        return f"{self.name}/" + separator.join([i for i in self.__dict__.values() if i is not None])


class Films(BaseCategory):
    name = "films"

    def selected_category(self, genre: GenreFilm):
        return super(Films, self).selected_category(genre)


class Cartoons(BaseCategory):
    name = "cartoons"

    def selected_category(self, genre: GenreCartoons):
        return super(Cartoons, self).selected_category(genre)


class Series(BaseCategory):
    name = "series"

    def selected_category(self, genre: GenreSeries):
        return super(Series, self).selected_category(genre)


class Animation(BaseCategory):
    name = "animation"

    def selected_category(self, genre: GenreAnimation):
        return super(Animation, self).selected_category(genre)


class New(BaseSingleCategory):
    name = "new"
    def __init__(self):
        self._filter_pattern = None

    def filter(self, pattern):
        self._filter_pattern = f"?filter={pattern}"
        return self
    def __str__(self):
        separator = "/"
        return f"{self.name}/" + separator.join([i for i in self.__dict__.values() if i is not None])

class Announce(BaseSingleCategory):
    name = "announce"
    ...
class Collections(BaseSingleCategory):
    name = "collections"
    ...
class Search(BaseSingleCategory):
    name = "search"
    ...
    "https://rezka.ag/search/?do=search&subaction=search&q=дракон&page=2"

    def query(self, text):
        pass

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
