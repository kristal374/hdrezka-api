from bs4 import BeautifulSoup
from dataclasses import dataclass
import re
from HDrezka.filters import convert_genres

__all__ = ["Poster", "CollectionFilm", "MovieForm", "NewForm", "AnnounceForm", "CollectionsForm", "SearchForm"]


@dataclass
class Poster:
    id: int = None  # ID фильма
    title: str = None  # Названия фильма
    entity: str = None  # Тип видео(Фильм, Сериал и тд)
    info: str = None  # Если является сериалом, отображает информацию о вышедших сериях
    year: str = None  # Дата выхода
    country: str = None  # Страна производитель
    genre: str = None  # Жанр фильма
    img_url: str = None  # Ссылка на обложку фильма
    url: str = None  # Ссылка на страницу фильма

    def __repr__(self):
        return f"Poster(\"{self.title}\")"


@dataclass
class CollectionFilm:
    id: int = None  # ID коллекции
    title: str = None  # Названия коллекции
    amount_film: int = None  # Количество фильмов в коллекции
    img_url: str = None  # Ссылка на обложку коллекции
    url: str = None  # Ссылка на страницу коллекции

    def __repr__(self):
        return f"CollectionFilm(\"{self.title}\")"


class FormPage:
    def __init__(self, requests_response):
        self._page = requests_response
        self.soup = BeautifulSoup(self._page, "lxml")

    def extract_content(self):
        page_info = []
        for item in self.soup.find_all('div', class_="b-content__inline_item"):
            poster = Poster()
            poster.id = int(item.get("data-id"))
            poster.title = item.find("div", class_="b-content__inline_item-link").find('a').text
            poster.entity = item.find('i', class_="entity").text
            poster.info = self.extract_info(item)
            poster.year, poster.country, poster.genre = self.extract_misc(item)
            poster.img_url = item.find('img').get("src")
            poster.url = item.get("data-url")

            page_info.append(poster)
        return page_info

    @staticmethod
    def extract_info(item):
        info = item.find('span', class_="info")
        if not info:
            return
        info = "".join(i if str(i) != "<br/>" else " " for i in info.contents).replace(",", "")
        return info

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


class MovieForm(FormPage):
    pass


class NewForm(FormPage):
    pass


class AnnounceForm(FormPage):
    pass


class CollectionsForm(FormPage):
    def extract_content(self):
        collection_info = []
        for item in self.soup.find_all('div', class_="b-content__collections_item"):
            collection = CollectionFilm()
            collection.id = re.search(r"(?<=collections/)[^\-]\d*", item.get("data-url")).group(0)
            collection.title = item.find("a", class_="title").text
            collection.amount_film = item.find("div", class_="num").text
            collection.img_url = item.find("img").get("src")
            collection.url = item.get("data-url")

            collection_info.append(collection)
        return collection_info


class SearchForm(FormPage):
    pass
