from urllib.parse import urlsplit

from HDrezka.connector import NetworkClient
from HDrezka.filters import GenreFilm, GenreSeries, GenreAnimation, GenreCartoons
from HDrezka.site_navigation import Films, Cartoons, Series, Animation, New, Announce, Collections, Search

__all__ = ["HDrezka"]


class HDrezka:
    def __init__(self, mirror="https://rezka.ag"):
        self.connector = NetworkClient(domain=urlsplit(str(mirror))[1])

    @staticmethod
    def films(genre: GenreFilm = None) -> Films:
        return Films().selected_category(genre)

    @staticmethod
    def cartoons(genre: GenreCartoons = None) -> Cartoons:
        return Cartoons().selected_category(genre)

    @staticmethod
    def series(genre: GenreSeries = None) -> Series:
        return Series().selected_category(genre)

    @staticmethod
    def animation(genre: GenreAnimation = None) -> Animation:
        return Animation().selected_category(genre)

    @staticmethod
    def new() -> New:
        return New()

    @staticmethod
    def announce() -> Announce:
        return Announce()

    @staticmethod
    def collections() -> Collections:
        return Collections()

    @staticmethod
    def search(text: str) -> Search:
        return Search().query(text)

    def __str__(self):
        return self.connector.url
