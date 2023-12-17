from urllib.parse import urlsplit

from HDrezka.connector import NetworkClient
from HDrezka.parse_page import Films, Cartoons, Series, Animation, New, Announce, Collections, Search
from HDrezka.filters import *

__all__ = ["HDrezka", "Films", "Cartoons", "Series", "Animation", "New", "Announce", "Collections", "Search",
           'GenreFilm', 'GenreCartoons', 'GenreSeries', 'GenreAnimation', 'Filters', 'ShowCategory', 'NetworkClient']


class HDrezka:
    def __init__(self, mirror="https://rezka.ag"):
        self.connector = NetworkClient(domain=urlsplit(str(mirror))[1])

    @staticmethod
    def films(genre=None) -> Films:
        return Films().selected_category(genre)

    @staticmethod
    def cartoons(genre=None) -> Cartoons:
        return Cartoons().selected_category(genre)

    @staticmethod
    def series(genre=None) -> Series:
        return Series().selected_category(genre)

    @staticmethod
    def animation(genre=None) -> Animation:
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
    def search(text) -> Search:
        return Search().query(text)

    def __str__(self):
        return self.connector.url
