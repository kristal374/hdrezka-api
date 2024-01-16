import re
from dataclasses import dataclass
from typing import Union, Optional, List, TYPE_CHECKING

from HDrezka.connector import NetworkClient
from HDrezka.exceptions import EmptyPage
from HDrezka.filters import convert_genres
from HDrezka.html_representation import PageRepresentation
from HDrezka.movie_page_descriptor import MovieDetailsBuilder
from HDrezka.trailer import TrailerBuilder

if TYPE_CHECKING:
    from HDrezka.filters import Filters

__all__ = ["PosterBuilder", "MovieCollectionBuilder", "MovieCollection", "Poster"]


@dataclass
class Poster:
    id: int = None  # ID фильма
    title: str = None  # Названия фильма
    entity: str = None  # Тип видео(Фильм, Сериал и тд)
    rates: Optional[float] = None  # Рейтинг видео(присутствует в категории Best)
    info: Optional[str] = None  # Если является сериалом, отображает информацию о вышедших сериях
    year: str = None  # Дата выхода
    country: Optional[str] = None  # Страна производитель
    genre: str = None  # Жанр фильма
    trailer: TrailerBuilder = None  # объект трейлера
    img_url: str = None  # Ссылка на обложку фильма
    url: str = None  # Ссылка на страницу фильма

    def get(self):
        return MovieDetailsBuilder(NetworkClient().get(self.url).text).extract_content()

    def __repr__(self):
        return f"Poster(\"{self.title}\")"


@dataclass
class MovieCollection:
    id: int = None  # ID коллекции
    title: str = None  # Названия коллекции
    amount_film: int = None  # Количество фильмов в коллекции
    img_url: str = None  # Ссылка на обложку коллекции
    url: str = None  # Ссылка на страницу коллекции

    def get(self, custom_filter: Optional[Union["Filters", str]] = None) -> List["Poster"]:
        filter_param = f"?filter={custom_filter}" if custom_filter else ""
        return PosterBuilder(NetworkClient().get(f"{self.url}{filter_param}").text).extract_content()

    def __repr__(self):
        return f"CollectionFilm(\"{self.title}\")"


class PosterBuilder(PageRepresentation):
    def extract_content(self):
        page_info = []
        for item in self.page.soup.find_all('div', class_="b-content__inline_item"):
            poster = Poster()
            poster.id = int(item.get("data-id"))
            poster.title = item.find("div", class_="b-content__inline_item-link").find('a').text
            poster.entity = item.find("i", class_="entity").next.strip()
            poster.rates = self.extract_rates(item)
            poster.info = self.extract_info(item)
            poster.year, poster.country, poster.genre = self.extract_misc(item)
            poster.trailer = self.extract_trailer(item)
            poster.img_url = item.find('img').get("src")
            poster.url = item.get("data-url")

            page_info.append(poster)
        if not page_info:
            raise EmptyPage("No Posters were found on the page")
        return page_info

    @staticmethod
    def extract_rates(item):
        rates = item.find("i", class_="b-category-bestrating")
        if rates is None:
            return rates
        return float(rates.text[1:-1]) if rates.text != "(—)" else None

    @staticmethod
    def extract_info(item):
        info = item.find('span', class_="info")
        if not info:
            return None
        info = "".join(i if str(i) != "<br/>" else " " for i in info.contents).replace(",", "")
        return info

    @staticmethod
    def extract_trailer(item) -> Union[TrailerBuilder, None]:
        trailer = item.find("i", class_="trailer")
        return TrailerBuilder(trailer.get("data-id")) if trailer else None

    @staticmethod
    def extract_misc(item):
        raw_data = item.find("div", class_="b-content__inline_item-link").find('div').text
        parsed_info = re.match(r"(\d{4}\s?-\s?[.\d]*|\d{4}),?\s?([^,]*),?\s?([^,]*)", raw_data)
        if not parsed_info:
            return (None,) * 3
        misc = tuple((None, i)[i != ""] for i in parsed_info.groups())
        if convert_genres(misc[1]):
            return misc[0:1] + misc[:0:-1]
        return misc


class MovieCollectionBuilder(PageRepresentation):
    def extract_content(self):
        collection_info = []
        for item in self.page.soup.find_all('div', class_="b-content__collections_item"):
            collection = MovieCollection()
            collection.id = int(re.search(r"(?<=collections/)[^\-]\d*", item.get("data-url")).group(0))
            collection.title = item.find("a", class_="title").text
            collection.amount_film = int(item.find("div", class_="num").text)
            collection.img_url = item.find("img").get("src")
            collection.url = item.get("data-url")

            collection_info.append(collection)

        if not collection_info:
            raise EmptyPage("No Collections found on the page")
        return collection_info
