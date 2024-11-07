from __future__ import annotations

import base64
import datetime
import re
from dataclasses import dataclass, field
from typing import List, Optional, Union, TYPE_CHECKING
from urllib.parse import unquote

from . import franchise
from . import movie_collections
from . import movie_posters
from .comments import CommentsIterator
from .connector import NetworkClient
from .html_representation import PageRepresentation
from .person import PersonBriefInfo
from .player import PlayerBuilder, Serial, Film
from .questions_asked import QuestionsBannerBuilder
from .trailer import TrailerBuilder
from .utility import convert_string_into_datetime

if TYPE_CHECKING:
    from .movie_posters import Poster
    from .franchise import FranchiseBriefInfo
    from .questions_asked import QuestionBanner
    from .movie_collections import CollectionBriefInfo


@dataclass
class Rating:
    name: str = None  # Имя сайта представляющего оценку
    rates: float = None  # Оценка от 1 до 10
    votes: int = None  # Количество голосовавших
    source: Optional[str] = None

    def __repr__(self):
        return f"<Rating( {self.name}: {self.rates}({self.votes}) )>"


@dataclass
class TopLists:
    title: str = None  # Название подборки
    place: str = None  # Занятое место в подборке
    url: str = None  # ссылка на подборку

    def get(self) -> List[Poster]:
        return movie_posters.PosterBuilder(NetworkClient().get(self.url).text).extract_content()

    def __repr__(self):
        return f"<TopLists({self.title} - {self.place})>"


@dataclass
class EpisodeOverview:
    season: int = None  # Номер сезона и серии текущего эпизода
    episode: int = None  # Номер сезона и серии текущего эпизода
    localize_title: Optional[str] = None  # Локализированное название эпизода
    original_title: Optional[str] = None  # Название в оригинале
    release_date: Union[datetime.datetime, datetime.date, None] = None  # Дата выхода эпизода
    exists_episode: Union[bool, str] = None  # Вышел ли эпизод или время до его выхода

    def __repr__(self):
        title = self.localize_title if isinstance(self.localize_title, str) else ""
        return f'<{EpisodeOverview.__name__}({self.season} Season {self.episode} Episode - "{title}")>'


class CustomString(str):
    url: str

    def __new__(cls, value, url):
        instance = super().__new__(cls, value)
        instance.url = url
        instance.__dict__ = {"value": instance, "url": instance.url}
        return instance

    def get(self) -> List[Poster]:
        return movie_posters.PosterBuilder(NetworkClient().get(self.url).text).extract_content()


@dataclass
class InfoTable:
    rates: List[Optional[Rating]] = field(default_factory=list)  # Рейтинг
    on_the_lists: Optional[List[TopLists]] = None  # Входит в списки
    tagline: Optional[str] = None  # Слоган фильма
    release: CustomString = None  # Дата выхода
    country: List[CustomString] = None  # Страна производитель
    producer: Optional[List[PersonBriefInfo]] = None  # Режиссёры
    genre: List[CustomString] = None  # Жанры
    quality: str = None  # В качестве
    translate: Optional[List[str]] = None  # В переводе
    age_restrictions: Optional[str] = None  # Возрастное ограничение
    duration: str = None  # Продолжительность
    collections: List[CollectionBriefInfo] = None  # Из серии
    cast: Optional[List[PersonBriefInfo]] = None  # В ролях

    def __repr__(self):
        return "<InfoTable>"


@dataclass
class MovieDetails:
    id: int = None  # Идентификатор фильма
    title: str = None  # Название фильма
    url: str = None  # Ссылка на страницу
    original_title: Optional[str] = None  # Название фильма на английском(зачастую)
    status: Optional[str] = None  # Статус проекта(завершён или номер сезона и серии)
    img_url: str = None  # Промо-постер
    trailer: Optional[TrailerBuilder] = None  # наличие трейлера
    info_table: InfoTable = None  # Таблица с краткой информацией по фильму
    description: Optional[str] = None  # Описание фильма
    player: Optional[Union[Serial, Film]] = None  # Объект либо фильма, либо сериала
    comments_count: Optional[int] = None  # TODO check
    franchise: Optional[FranchiseBriefInfo] = None  # Фильмы из того же цикла(Приквелы, Сиквелы и тд)
    recommendations: List[Poster] = None  # Список рекомендованных к просмотру фильмов
    schedule_block: Optional[List[EpisodeOverview]] = None  # Список выхода серий
    questions_asked: List[QuestionBanner] = None  # Часто задаваемые вопросы
    comment: CommentsIterator = None  # Комментарии к данному фильму

    def __repr__(self):
        return f"<MovieDetails({self.title})>"


class InfoTableBuilder(PageRepresentation):
    def extract_content(self):
        info = self.page.soup.find("table", class_="b-post__info")
        keys = info.find_all("tr")

        table_info = InfoTable()
        for k in keys:
            item = k.find_all("td")
            key = item[0].text.strip()
            if key == "Рейтинги:":
                table_info.rates = self.extract_rates(item[1])
            elif key == "Входит в списки:":
                table_info.on_the_lists = self.extract_lists(item[1])
            elif key == "Слоган:":
                table_info.tagline = item[1].text.strip()
            elif key in ("Год:", "Дата выхода:"):
                table_info.release = self.extract_date_release(item[1])
            elif key == "Страна:":
                table_info.country = self.extract_country(item[1])
            elif key == "Режиссер:":
                table_info.producer = self.extract_person(item[1])
            elif key == "Жанр:":
                table_info.genre = self.extract_genre(item[1])
            elif key == "Возраст:":
                table_info.age_restrictions = item[1].span.text.strip()
            elif key == "Время:":
                table_info.duration = item[1].text.strip().replace(".", "")
            elif key == "Из серии:":
                table_info.collections = self.extract_collections(item[1])
            elif key == "В качестве:":
                table_info.quality = item[1].text.strip()
            elif key == "В переводе:":
                table_info.translate = [i.strip() for i in re.split(r", | и ", item[1].text) if i.strip()]
            elif item[0].find("div", class_="persons-list-holder"):
                table_info.cast = self.extract_person(item[0])
            else:
                raise TypeError(item)  # pragma: NO COVER
        return table_info

    @staticmethod
    def extract_date_release(data) -> Union[CustomString, str]:
        release = data.text.strip()
        url = data.find("a")
        return CustomString(release, url.get("href")) if url else release

    @staticmethod
    def extract_country(data) -> List[Union[CustomString]]:
        result_string = []
        for item in data.find_all("a"):
            country = item.string.strip()
            url = item.get("href")
            result_string.append(CustomString(country, url))
        return result_string

    @staticmethod
    def extract_genre(data) -> List[CustomString]:
        result_string = []
        for item in data.find_all("a"):
            genre = item.text.strip()
            url = item.get("href")
            result_string.append(CustomString(genre, url))
        return result_string

    @staticmethod
    def extract_rates(data):
        result_lst = []
        rates_blanks = data.find_all("span", class_="b-post__info_rates")
        for blank in rates_blanks:
            rate = Rating()
            if blank.a is not None:
                rate.name = blank.a.text.strip()
                rate.source = unquote(base64.b64decode(blank.a.get("href").split("/")[-2]).decode("utf-8"))
            else:
                rate.name = blank.next.strip()[:-1]
            rate.rates = float(blank.span.text.strip())
            rate.votes = int(blank.i.text.strip()[1:-1].replace(" ", ""))
            result_lst.append(rate)
        return result_lst

    @staticmethod
    def extract_lists(data):
        result_lst = []
        lists = [i for i in data if i.text != ""]
        for link, place in zip(lists[::2], lists[1::2]):  # split the list in pairs
            top = TopLists()
            top.title = link.text.strip()
            top.place = place.strip()[1:-1]
            top.url = link.get("href").strip()
            result_lst.append(top)
        return result_lst

    @staticmethod
    def extract_person(data):
        result_lst = []
        persons = data.find_all("span", class_="item")
        for item in persons:
            person_obj = item.find("span", class_="person-name-item")
            if person_obj:
                img_url = person_obj.get("data-photo", "null")
                job = person_obj.get("data-job", "null")
                result_lst.append(
                    PersonBriefInfo(
                        id=int(person_obj.get("data-id").strip()),
                        film_id=int(person_obj.get("data-pid").strip()),
                        name=person_obj.a.span.text.strip(),
                        url=person_obj.a.get("href").strip(),
                        img_url=img_url.strip() if img_url != "null" else None,
                        job=person_obj.attrs.get("data-job").strip() if job != "null" else None,
                    )
                )
            else:
                if item.text == "и другие":
                    continue
                result_lst.append(PersonBriefInfo(name=item.text.replace(",", "").strip()))
        return result_lst

    @staticmethod
    def extract_collections(data):
        result_lst = []
        collections = data.find_all("a")
        for c in collections:
            collection = movie_collections.CollectionBriefInfo()
            collection.id = int(re.search(r"/(\d+)-", c.get("href")).group(1))
            collection.title = c.text.strip()
            collection.url = c.get("href").strip()
            result_lst.append(collection)
        return result_lst


class MovieDetailsBuilder(PageRepresentation):
    def extract_content(self):
        page = MovieDetails()
        page.id = int(re.search(r"/(\d*)-", self.page.soup.find("meta", property="og:url").get("content")).group(1))
        page.title = self.page.soup.find("div", class_="b-post__title").text.strip()
        page.url = self.page.soup.find("meta", property="og:url").get("content").strip()
        page.original_title = self.extract_original_name()
        page.status = self.extract_status()
        page.img_url = self.page.soup.find("div", class_="b-sidecover").a.get("href")
        page.trailer = self.extract_trailer()
        page.info_table = InfoTableBuilder(self.page).extract_content()
        page.description = self.extract_description()
        page.player = PlayerBuilder(self.page).extract_content()
        page.comments_count = self.extract_comments_count()
        page.franchise = franchise.FranchiseBriefInfoBuilder(self.page).extract_content()
        page.recommendations = self.extract_recommendations()
        page.schedule_block = self.extract_schedule_block()
        page.questions_asked = self.extract_questions()
        page.comment = CommentsIterator(page.id)

        rezka_rates = self.extract_rates()
        if rezka_rates:
            page.info_table.rates.append(rezka_rates)

        return page

    def extract_original_name(self) -> Optional[str]:
        original_name = self.page.soup.find("div", class_="b-post__origtitle")
        if original_name is None:
            return original_name
        return original_name.text.strip()

    def extract_status(self) -> Optional[str]:
        status = self.page.soup.find("div", class_="b-post__infolast")
        if status is None:
            return status
        return status.text.strip()

    def extract_trailer(self) -> Optional[TrailerBuilder]:
        trailer = self.page.soup.find("a", class_="b-sidelinks__link")
        if trailer is None:
            return trailer
        trailer_id = trailer.get("data-id")
        if isinstance(trailer_id, str) and trailer_id.isdigit():
            return TrailerBuilder(film_id=int(trailer_id))
        return None

    def extract_description(self) -> Optional[str]:
        description = self.page.soup.find("div", class_="b-post__description_text")
        if description is None:
            return description
        return description.text.strip()

    def extract_rates(self) -> Optional[Rating]:
        try:
            rate = Rating()
            rate.name = "HDrezka"
            rate.rates = float(self.page.soup.find("span", class_="num").text.strip())
            rate.votes = int(self.page.soup.find("span", class_="votes").span.text.strip())
            rate.source = self.page.soup.find("meta", property="og:url").get("content").strip()
            return rate
        except AttributeError:
            return None

    def extract_recommendations(self) -> List[Poster]:
        recommendations = self.page.soup.find("div", class_="b-sidelist")
        return movie_posters.PosterBuilder(str(recommendations)).extract_content()

    def extract_comments_count(self) -> Optional[int]:
        comments_count = self.page.soup.find("button", id="comments-list-button").em
        if comments_count is None:
            return comments_count
        return int(comments_count.string.strip())

    def extract_schedule_block(self) -> Optional[List[EpisodeOverview]]:
        lst_seasons = self.page.soup.find_all("div", class_="b-post__schedule_list")
        result_lst = []
        for s in lst_seasons:
            for e in s.find_all("tr"):
                try:
                    original_title = e.find(class_="td-2").span.text.strip() or None
                    localize_title = e.find(class_="td-2").b.text.strip() or None
                    current_episode = e.find(class_="td-1").text.strip()

                    episode = EpisodeOverview()
                    episode.season, episode.episode = map(
                        int, re.search(r"(?:(\d+) сезон)?\s?(?:(\d+) серия)?", current_episode).groups()
                    )
                    episode.original_title = original_title if original_title else localize_title
                    episode.localize_title = localize_title if original_title else None
                    episode.release_date = convert_string_into_datetime(e.find(class_="td-4").text.strip()) or None
                    status = e.find(class_="td-5").text.strip()
                    episode.exists_episode = status if status not in ("&check;", "") else status == "&check;"
                    result_lst.append(episode)
                except AttributeError:
                    continue
        return result_lst

    def extract_questions(self) -> List[QuestionBanner]:
        faq_block = self.page.soup.find("div", class_="b-post__qa_list_block")
        if faq_block is None:
            return []
        return QuestionsBannerBuilder(str(faq_block)).extract_content()

    def __repr__(self):
        return f"<{MovieDetailsBuilder.__name__}>"
