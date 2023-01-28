from parse_page import Films, Cartoons, Series, Animation, New, Announce, Collections, Search
from player import Serial, Film

__version__ = '1.0'


class HDrezka:
    def __init__(self):
        self._data = {"films": Films(),
                      "cartoons": Cartoons(),
                      "series": Series(),
                      "animation": Animation(),
                      "new": New(),
                      "announce": Announce(),
                      "collections": Collections(),
                      "search": Search()
                      }

    def films(self, *args) -> Films:
        return self._data["films"].add(*args)

    def cartoons(self, *args):
        self._data["cartoons"].add(*args)
        return self

    def series(self, *args):
        self._data["series"].add(*args)
        return self

    def animation(self, *args):
        self._data["animation"].add(*args)
        return self

    def new(self, *args):
        self._data["new"].add(*args)
        return self

    def announce(self, *args):
        self._data["announce"].add(*args)
        return self

    def collections(self, *args):
        self._data["collections"].add(*args)
        return self

    def search(self, *args):
        return self._data["search"].add(*args)

    def __str__(self):
        return


if __name__ == '__main__':
    rezka = HDrezka()
    # print(rezka.films("fantasy").filter("popular"))
    # print(rezka.get("https://rezka.ag/cartoons/fiction/27260-geroi-envella-2017.html").quality("1080p").translate("56").subtitle())
