from urllib.parse import urlsplit

from HDrezka.connector import SiteConnector
from HDrezka.parse_page import Films, Cartoons, Series, Animation, New, Announce, Collections, Search
from HDrezka.player import Serial, Film
from HDrezka.filters import *


__version__ = '1.0'


class HDrezka:
    def __init__(self, mirror="https://rezka.ag"):
        self._data = {"films": Films(),
                      "cartoons": Cartoons(),
                      "series": Series(),
                      "animation": Animation(),
                      "new": New(),
                      "announce": Announce(),
                      "collections": Collections(),
                      "search": Search()
                      }
        self.connector = SiteConnector(domain=urlsplit(str(mirror))[1])

    def films(self, genre=None) -> Films:
        return self._data["films"].selected_category(genre)

    def cartoons(self, genre=None) -> Cartoons:
        return self._data["cartoons"].selected_category(genre)

    def series(self, genre=None) -> Series:
        return self._data["series"].selected_category(genre)

    def animation(self, genre=None) -> Animation:
        return self._data["animation"].selected_category(genre)

    def new(self) -> New:
        return self._data["new"]

    def announce(self) -> Announce:
        return self._data["announce"]

    def collections(self) -> Collections:
        return self._data["collections"]

    def search(self, text) -> Search:
        return self._data["search"].query(text)

    def __str__(self):
        return


if __name__ == '__main__':
    rezka = HDrezka()
    print(rezka.films().selected_category(GenreFilm.COMEDY).filter(Filters.WATCHING))
    # print(rezka.get("https://rezka.ag/cartoons/fiction/27260-geroi-envella-2017.html").quality("1080p").translate("56").subtitle())
