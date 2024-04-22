from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Union, Optional, List, TYPE_CHECKING

from bs4.element import NavigableString

from . import movie_page_descriptor
from . import person
from .connector import NetworkClient
from .exceptions import EmptyPage
from .filters import convert_genres
from .html_representation import PageRepresentation
from .person import PersonBriefInfo
from .trailer import TrailerBuilder

if TYPE_CHECKING:
    from .movie_page_descriptor import MovieDetails
    from .movie_page_descriptor import CustomString, Rating

__all__ = ["PosterBuilder", "Poster"]


@dataclass
class Poster:
    id: int = None  # ID фильма
    title: str = None  # Названия фильма
    entity: str = None  # Тип видео(Фильм, Сериал и тд)
    rates: Optional[float] = None  # Рейтинг видео(присутствует в категории Best)
    status: Optional[str] = None  # Если является сериалом, отображает информацию о вышедших сериях
    year: str = None  # Дата выхода
    country: Optional[str] = None  # Страна производитель
    genre: str = None  # Жанр фильма
    trailer: TrailerBuilder = None  # объект трейлера
    img_url: str = None  # Ссылка на обложку фильма
    url: str = None  # Ссылка на страницу фильма

    def get(self):
        return movie_page_descriptor.MovieDetailsBuilder(NetworkClient().get(self.url).text).extract_content()

    def quick_content(self):
        connector = NetworkClient()
        url = f"{connector.url}/engine/ajax/quick_content.php"
        extended_info = connector.post(url, data={'id': self.id, 'is_touch': "1"}).text
        return PosterExtendedInfoBuilder(extended_info).extract_content()

    def __repr__(self):
        return f"Poster(\"{self.title}\")"


@dataclass
class PosterExtendedInfo:
    id: int = None
    title: str = None
    entity: str = None
    description: Optional[str] = None
    age_restrictions: Optional[str] = None
    genre: List[CustomString] = None
    directors: List[PersonBriefInfo] = None
    actors: List[PersonBriefInfo] = None
    rates: List[Rating] = None
    url: str = None

    def get(self) -> MovieDetails:
        return movie_page_descriptor.MovieDetailsBuilder(NetworkClient().get(self.url).text).extract_content()

    def __repr__(self):
        return f"PosterExtendedInfo(\"{self.title}\")"


class PosterExtendedInfoBuilder(PageRepresentation):
    def extract_content(self) -> PosterExtendedInfo:
        poster_info = PosterExtendedInfo()
        poster_info.url = self.page.soup.find("div", class_="b-content__bubble_title").a.get("href").strip()
        poster_info.id = int(re.search(r"/(\d*)-", poster_info.url).group(1))
        poster_info.title = self.page.soup.find('div', class_='b-content__bubble_title').text.strip()
        poster_info.entity = self.page.soup.find('i', class_='entity').text.strip()
        poster_info.description = self.extract_description()
        poster_info.age_restrictions = self.extract_age_restriction()
        poster_info.genre = self.extract_genre()
        poster_info.directors = self.extract_person(string='Режиссер:')
        poster_info.actors = self.extract_person(string='В ролях:')
        poster_info.rates = self.extract_ratings()

        return poster_info

    def extract_description(self) -> Optional[str]:
        result_string = None
        for item in self.page.soup.find_all('div', class_='b-content__bubble_text'):
            if len(item.contents) == 1 and isinstance(item.contents[0], NavigableString):
                result_string = item.contents[0].strip()
        return result_string

    def extract_age_restriction(self) -> Optional[str]:
        age_restriction = self.page.soup.find('span', string='Возрастное ограничение:')
        if age_restriction is None:
            return age_restriction
        return age_restriction.find_next_sibling().text.strip()

    def extract_genre(self) -> List[CustomString]:
        genres = self.page.soup.find('span', string='Жанр:')
        result_string = []
        for item in genres.parent.find_all("a"):
            genre = item.text.strip()
            url = item.get("href")
            result_string.append(movie_page_descriptor.CustomString(genre, url))
        return result_string

    def extract_person(self, string) -> List[Union[PersonBriefInfo, str]]:
        person_obj = self.page.soup.find('span', string=string).parent
        process_person = list(filter(lambda x: str(x) not in ("\n", " ", "", ", ", ",", " и "), person_obj))
        if isinstance(process_person[1], NavigableString):
            iterable_obj = re.split(', | и ', process_person[1].strip())
        else:
            iterable_obj = process_person[1:]
        result_list: List[Union[PersonBriefInfo, str]] = []
        for item in iterable_obj:
            if not isinstance(item, str):
                result_list.append(
                    person.PersonBriefInfo(
                        id=int(item.get("data-id").strip()),
                        film_id=int(item.get("data-pid").strip()),
                        name=item.a.span.text.strip(),
                        url=item.a.get("href").strip(),
                    )
                )
            else:
                result_list.append(item)
        return result_list

    def extract_ratings(self) -> List[Rating]:
        ratings = self.page.soup.find(class_='b-content__bubble_rates')
        result_list = []
        if ratings:
            for item in ratings.find_all("span"):
                rate = movie_page_descriptor.Rating()
                rate.name = item.next.strip()[:-1]
                rate.rates = float(item.find("b").text.strip())
                rate.votes = int(item.find("i").text.strip()[1:-1].replace(" ", ""))
                result_list.append(rate)

        rating_rezka = self.page.soup.find('div', class_='b-content__bubble_rating')
        if rating_rezka:
            rate = movie_page_descriptor.Rating()
            rate.name = 'HDrezka'
            rate.rates = float(rating_rezka.b.text.strip())
            rate.votes = int(re.search(r"\((.*?)\)", rating_rezka.text.strip()).group(1))
            result_list.append(rate)
        return result_list


class PosterBuilder(PageRepresentation):
    def extract_content(self):
        page_info = []
        for item in self.page.soup.find_all('div', class_="b-content__inline_item"):
            poster = Poster()
            poster.id = int(item.get("data-id"))
            poster.title = item.find("div", class_="b-content__inline_item-link").find('a').text
            poster.entity = item.find("i", class_="entity").next.text.strip() or None
            poster.rates = self.extract_rates(item)
            poster.status = self.extract_info(item)
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
        return TrailerBuilder(int(trailer.get("data-id"))) if trailer else None

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
