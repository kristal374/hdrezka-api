from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Optional, List, TYPE_CHECKING, Union

from . import movie_posters
from .connector import NetworkClient
from .exceptions import ServiceUnavailable, PageNotFound
from .html_representation import PageRepresentation

if TYPE_CHECKING:
    from .movie_posters import Poster


@dataclass
class PersonBriefInfo:
    name: str  # имя человека
    id: Optional[int] = None  # идентификатор человека
    film_id: Optional[int] = None  # идентификатор фильма
    url: Optional[str] = None  # ссылка на полную информацию о человеке
    img_url: Optional[str] = None  # ссылка на изображение
    job: Optional[str] = None  # роль в фильме

    def get(self) -> Person:
        if self.url is None:
            raise PageNotFound("No correct URL was found for the request")
        return PersonBuilder(NetworkClient().get(self.url).text).extract_content()

    def quick_content(self) -> PersonExtendedInfo:
        if self.id is None:
            raise PageNotFound("This person does not have an ID")
        connector = NetworkClient()
        url = f"{connector.url}/ajax/person_info/"
        response = connector.post(url, data={'id': self.id, 'pid': self.film_id or 1})
        if response.status_code == 200:
            return PersonExtendedInfoBuilder(response.json()).extract_content()
        raise ServiceUnavailable("Service is temporarily unavailable")

    def __repr__(self):
        return f"<PersonBriefInfo({self.name})>"


@dataclass
class PersonExtendedInfo:
    id: int  # ID персоны
    name: str  # Имя Фамилия
    original_name: Optional[str]  # Имя в оригинале
    person_height: Optional[str]  # Рост человека(Может быть всегда None)
    birthday: Optional[str]  # День рождения
    birthplace: Optional[str]  # Место рождения
    age: Optional[str]  # Текущий возраст(если человек умер равно None)
    death_day: Optional[str]  # День смерти
    death_place: Optional[str]  # Место смерти
    age_full: Optional[str]  # Возраст в котором умер человек
    stats: Optional[str]  # Информация о количестве фильмов/сериалов/МФ/аниме с участием этого человека на сайте
    careers: str  # Роли которые исполнял человек
    gender: str  # Пол человека
    image_count: int  # Количество фото с этим человеком на сайте
    image: str  # Основное фото человека
    url: str  # ссылка на основную страницу с информацией о человеке

    def get(self):
        if self.url is None:
            raise PageNotFound("No correct URL was found for the request")
        return PersonBuilder(NetworkClient(self.url).text).extract_content()

    def __repr__(self):
        return f"<PersonExtendedInfo({self.name})>"


class PersonExtendedInfoBuilder:
    def __init__(self, server_response: Dict[str, Union[str, int, None]]):
        self._server_response = server_response

    def extract_content(self) -> PersonExtendedInfo:
        return PersonExtendedInfo(
            id=int(re.search(r"/(\d*)-", self._server_response.get("link")).group(1)),
            name=self._server_response.get("name"),
            original_name=self._server_response.get("name_alt") or None,
            person_height=self._server_response.get("person_height") or None,
            birthday=self._server_response.get("birthday") or None,
            birthplace=self._server_response.get("birthplace") or None,
            age=self._server_response.get("age") or None,
            death_day=self._server_response.get("deathday") or None,
            death_place=self._server_response.get("deathplace") or None,
            age_full=self._server_response.get("agefull") or None,
            stats=self._server_response.get("stats") or None,
            careers=self._server_response.get("careers"),
            gender=self._server_response.get("gender"),
            image_count=int(self._server_response.get("photos_count")),
            image=self._server_response.get("photo"),
            url=self._server_response.get("link")
        )


@dataclass
class Person:
    id: int  # ID персоны
    name: str  # Имя Фамилия
    original_name: Optional[str]  # Имя в оригинале
    person_height: Optional[str]  # Рост человека
    careers: str  # Роли которые исполнял человек
    birthday: Optional[str]  # День рождения
    birthplace: Optional[str]  # Место рождения
    age: Optional[str]  # Текущий возраст(если человек умер равно None)
    death_day: Optional[str]  # День смерти
    death_place: Optional[str]  # Место смерти
    age_full: Optional[str]  # Возраст в котором умер человек
    image: str  # Основное фото человека
    gallery: Optional[List[str]]  # Гелерия фото с этим человеком на сайте
    stats: Dict[str, List["Poster"]]  # Информация о должности и соответствующих ей фильмах
    url: str  # ссылка на основную страницу с информацией о человеке

    def __repr__(self):
        return f"<Person({self.name})>"


class PersonBuilder(PageRepresentation):
    def extract_content(self) -> Person:
        info_table = self.extract_infotable()
        return Person(
            id=int(re.search(r"/(\d*)-", self.page.soup.find('meta', property='og:url').get("content")).group(1)),
            name=self.extract_localize_name(),
            original_name=self.extract_original_name(),
            person_height=info_table.get("person_height"),
            careers=info_table.get("careers"),
            birthday=info_table.get("birthday"),
            birthplace=info_table.get("birthplace"),
            age=info_table.get("age"),
            death_day=info_table.get("death_day"),
            death_place=info_table.get("death_place"),
            age_full=info_table.get("age_full"),
            image=self.extract_image(),
            gallery=info_table.get("gallery"),
            stats=self.extract_stats(),
            url=self.page.soup.find("meta", property="og:url").get("content")
        )

    def extract_localize_name(self):
        title_obj = self.page.soup.find("div", class_="b-post__title")
        return title_obj.find("span", itemprop="name").text.strip()

    def extract_original_name(self):
        title_obj = self.page.soup.find("div", class_="b-post__title")
        original_name = title_obj.find("span", itemprop="alternativeHeadline")
        if original_name is None:
            return original_name
        return original_name.text.strip()

    def extract_image(self):
        infotable = self.page.soup.find("div", class_="b-post__infotable clearfix")
        infotable_left = infotable.find(class_="b-post__infotable_left")
        return infotable_left.find("img").get("src")

    def extract_stats(self):
        result = {}
        all_careers = self.page.soup.find_all("div", class_="b-person__career")
        for item in all_careers:
            result[item.find("h2").text.strip().lower()] = movie_posters.PosterBuilder(item).extract_content()
        return result

    def extract_infotable(self):
        infotable_right = self.page.soup.find("div", class_="b-post__infotable_right_inner")
        info = infotable_right.find("table", class_="b-post__info")

        result = {}
        for k in info.find_all("tr"):
            item = k.find_all("td")
            key = item[0].text.strip()
            if key == "Карьера:":
                result["careers"] = [i.text.strip() for i in item[1].find_all("a")]
            elif key == "Дата рождения:":
                result["birthday"], result["age"] = self.extract_date_and_age(item[1])
            elif key == "Место рождения:":
                result["birthplace"] = item[1].text.strip()
            elif key == "Дата смерти:":
                result["death_day"], result["age_full"] = self.extract_date_and_age(item[1])
            elif key == "Место смерти:":
                result["death_place"] = item[1].text.strip()
            elif key == "Рост:":
                result["person_height"] = item[1].text.strip()
            elif item[0].find("div", class_="b-person__gallery_holder"):
                result["gallery"] = [i["href"] for i in item[0].find_all("a")]
            else:
                raise TypeError(item)  # pragma: NO COVER
        return result

    @staticmethod
    def extract_date_and_age(data):
        age = re.search(r"\(.*?\)", data.text)
        return data.find("time").get("datetime"), age[0].strip()[1:-1] if age else None
