class BaseExp:
    name = None

    def add(self, *args):
        return self

    def get_link(self):
        raise NotImplementedError

    def filter(self, *args):
        raise NotImplementedError

    def __str__(self):
        return f"{self.name}/"




class Films(BaseExp):
    name = "films"

    def filter(self, *args):
        ...
class Cartoons(BaseExp):
    name = "cartoons"
    ...
class Series(BaseExp):
    name = "series"
    ...
class Animation(BaseExp):
    name = "animation"
    ...
class New(BaseExp):
    name = "new"
    ...
class Announce(BaseExp):
    name = "announce"
    ...
class Collections(BaseExp):
    name = "collections"
    ...
class Search(BaseExp):
    name = "search"
    ...

class PageInfo:
    def __init__(self):
        self.name = None
        self.original_name = None
        self.rates = None
        self.on_the_lists = None
        self.tagline = None
        self.release = None
        self.country = None
        self.producer = None
        self.genre = None
        self.age = None
        self.time = None
        self.playlist = None
        self.cast = None
        self.title = None

