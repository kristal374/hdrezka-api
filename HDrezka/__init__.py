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

    def films(self, genre) -> Films:
        return self._data["films"].add_category(genre)

    def cartoons(self, genre) -> Cartoons:
        return self._data["cartoons"].add_category(genre)

    def series(self, genre) -> Series:
        return self._data["series"].add_category(genre)

    def animation(self, genre) -> Animation:
        return self._data["animation"].add_category(genre)

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
    # print(rezka.films("fantasy").filter("popular"))
    # print(rezka.get("https://rezka.ag/cartoons/fiction/27260-geroi-envella-2017.html").quality("1080p").translate("56").subtitle())
