import re
from dataclasses import dataclass, field
from typing import List, Optional, Union, TYPE_CHECKING

from HDrezka import page_representation
from HDrezka.connector import NetworkClient
from HDrezka.html_representation import PageRepresentation
from HDrezka.person import PersonBriefInfo
from HDrezka.player import TrailerBuilder

if TYPE_CHECKING:
    from HDrezka.page_representation import Poster
    from HDrezka.filters import Filters


@dataclass
class Rating:
    name: str = None  # Имя сайта представляющего оценку
    rates: float = None  # Оценка от 1 до 10
    votes: int = None  # Количество голосовавших

    def __repr__(self):
        return f"<Rating( {self.name}: {self.rates}({self.votes}) )>"


@dataclass
class TopLists:
    title: str = None  # Название подборки
    place: str = None  # Занятое место в подборке
    url: str = None  # ссылка на подборку

    def get(self) -> List["Poster"]:
        return page_representation.PosterBuilder(NetworkClient().get(self.url).text).extract_content()

    def __repr__(self):
        return f"<TopLists({self.title} - {self.place})>"


@dataclass
class CollectionBriefInfo:
    id: int = None  # идентификатор коллекции
    title: str = None  # название коллекции
    url: str = None  # ссылка на коллекцию

    def get(self, custom_filter: Optional[Union["Filters", str]] = None) -> List["Poster"]:
        filter_param = f"?filter={custom_filter}" if custom_filter else ""
        return page_representation.PosterBuilder(
            NetworkClient().get(f"{self.url}{filter_param}").text).extract_content()

    def __repr__(self):
        return f"<CollectionBriefInfo({self.title})>"


@dataclass
class PartContent:
    num: int = None  # Номер фильма/сериала во франшизе
    title: str = None  # Название фильма
    year: str = None  # год выпуска фильма
    rating: str = None  # рейтинг фильма
    url: str = None  # ссылка на фильм

    def get(self) -> "MovieDetails":
        return MovieDetailsBuilder(NetworkClient().get(self.url).text).extract_content()

    def __repr__(self):
        return f"<PartContent({self.title})>"


@dataclass
class Episode:
    current_episode: str = None  # Номер сезона и серии текущего эпизода
    localize_title: str = None  # Локализированное название эпизода
    original_title: str = None  # Название в оригинале
    release_date: str = None  # Дата выхода эпизода
    exists_episode: Union[bool, str] = None  # Вышел ли эпизод или время до его выхода

    def __repr__(self):
        name = self.original_title if not self.localize_title else self.localize_title
        return f"<Episode({self.current_episode} - {name})>"


@dataclass
class InfoTable:
    rates: Optional[List[Rating]] = field(default_factory=list)  # Рейтинг
    on_the_lists: Optional[List[PartContent]] = None  # Входит в списки
    tagline: Optional[str] = None  # Слоган фильма
    release: str = None  # Дата выхода
    country: str = None  # Страна производитель
    producer: List[PersonBriefInfo] = None  # Режиссёры
    genre: List[str] = None  # Жанры
    age: Optional[str] = None  # Возрастное ограничение
    time: str = None  # Продолжительность
    collections: List[CollectionBriefInfo] = None  # Из серии
    quality: str = None  # В качестве
    translate: Optional[str] = None  # В переводе
    cast: Optional[List[PersonBriefInfo]] = None  # В ролях

    def __repr__(self):
        return "<PageInfo>"


@dataclass
class MovieDetails:
    id: int = None  # Идентификатор фильма
    title: str = None  # Название фильма
    url: str = None  # Ссылка на страницу
    original_name: Optional[str] = None  # Название фильма на английском(зачастую)
    status: Optional[str] = None  # Статус проекта(завершён или номер сезона и серии)
    image: str = None  # Промо-постер
    trailer: Optional[TrailerBuilder] = None  # наличие трейлера
    info_table: InfoTable = None  # Таблица с краткой информацией по фильму
    description: str = None  # Описание фильма
    player = None  #
    part_content: Optional[List[PartContent]] = None  # Фильмы из того же цикла(Приквелы, Сиквелы и тд)
    recommendations: List = None
    schedule_block: Optional[List[Episode]] = None  # Список выхода серий
    comment = None  # Комментарии к данному фильму


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
            elif key == 'Слоган:':
                table_info.tagline = item[1].text.strip()
            elif key in ("Год:", 'Дата выхода:'):
                table_info.release = item[1].a.text.strip()
            elif key == "Страна:":
                table_info.country = item[1].a.text.strip()
            elif key == "Режиссер:":
                table_info.producer = self.extract_person(item[1])
            elif key == "Жанр:":
                table_info.genre = [i.text.strip() for i in item[1].find_all("span")]
            elif key == 'Возраст:':
                table_info.age = item[1].span.text.strip()
            elif key == "Время:":
                table_info.time = item[1].text.strip().replace(".", "")
            elif key == "Из серии:":
                table_info.collections = self.extract_collections(item[1])
            elif key == "В качестве:":
                table_info.quality = item[1].text.strip()
            elif key == 'В переводе:':
                table_info.translate = re.split(r', | и ', item[1].text.strip())
            elif item[0].find("div", class_="persons-list-holder"):
                table_info.cast = self.extract_person(item[0])
            else:
                raise TypeError(item)
        return table_info

    @staticmethod
    def extract_rates(data):
        result_lst = []
        rates_blanks = data.find_all("span", class_="b-post__info_rates")
        for blank in rates_blanks:
            rate = Rating()
            rate.name = blank.a.text.strip()
            rate.rates = float(blank.span.text.strip())
            rate.votes = blank.i.text.strip()[1:-1]
            result_lst.append(rate)
        return result_lst

    @staticmethod
    def extract_lists(data):
        result_lst = []
        lists = [i for i in data if i.text != ""]
        for link, place in zip(lists[::2], lists[1::2]):
            top = TopLists()
            top.title = link.text.strip()
            top.place = place.strip()[1:-1]
            top.url = link.get("href").strip()
            result_lst.append(top)
        return result_lst

    @staticmethod
    def extract_person(data):
        result_lst = []
        persons = data.find_all("span", class_="person-name-item")
        for p in persons:
            person = PersonBriefInfo()
            person.id = int(p.get("data-id").strip())
            person.name = p.a.span.text.strip()
            person.url = p.a.get("href").strip()
            result_lst.append(person)
        return result_lst

    @staticmethod
    def extract_collections(data):
        result_lst = []
        collections = data.find_all("a")
        for c in collections:
            collection = CollectionBriefInfo()
            collection.id = int(re.search(r"/(\d+)-", c.get("href")).group(1))
            collection.title = c.text.strip()
            collection.url = c.get("href").strip()
            result_lst.append(collection)
        return result_lst


class MovieDetailsBuilder(PageRepresentation):
    def extract_content(self):
        page = MovieDetails()
        page.id = int(re.search(r"/(\d*)-", self.page.soup.find('meta', property='og:video').get("content")).group(1))
        page.title = self.page.soup.find("div", class_="b-post__title").text.strip()
        page.url = self.page.soup.find('meta', property='og:video').get("content").strip()
        page.original_name = self.extract_original_name()
        page.status = self.extract_status()
        page.image = self.page.soup.find("div", class_="b-sidecover").a.get("href")
        page.trailer = self.extract_trailer()
        page.info_table = InfoTableBuilder(self.page).extract_content()
        page.description = self.page.soup.find("div", class_="b-post__description_text").text.strip()
        page.player = None  # TODO
        (lambda x: page.info_table.rates.append(x) if x is not None else None)(self.extract_rates())
        page.part_content = self.extract_part_content()
        page.recommendations = self.extract_recommendations()
        page.schedule_block = self.extract_schedule_block()
        page.comment = None  # TODO
        return page

    def extract_original_name(self):
        original_name = self.page.soup.find("div", class_="b-post__origtitle")
        if original_name is None:
            return original_name
        return original_name.text.strip()

    def extract_status(self):
        status = self.page.soup.find("div", class_="b-post__infolast")
        if status is None:
            return status
        return status.text.strip()

    def extract_trailer(self) -> Union[TrailerBuilder, None]:
        trailer = self.page.soup.find("a", class_="b-sidelinks__link")
        if trailer is None:
            return trailer
        return TrailerBuilder(trailer.get("data-id"))

    def extract_rates(self):
        try:
            rate = Rating()
            rate.name = "HDrezka"
            rate.rates = float(self.page.soup.find("span", class_="num").text.strip())
            rate.votes = self.page.soup.find("span", class_="votes").span.text.strip()
            return rate
        except AttributeError:
            return None

    def extract_part_content(self):
        content = self.page.soup.find_all("div", class_="b-post__partcontent_item")
        result_lst = []
        for item in content:
            p = PartContent()
            p.num = int(item.find("div", class_="num").text.strip())
            p.title = item.find("div", class_="title").text.strip()
            url = item.find("div", class_="title").a
            p.url = url.get("href") if url else None
            p.year = item.find("div", class_="year").text.strip()
            p.rating = item.find("div", class_="rating").text.strip()
            result_lst.append(p)
        return result_lst

    def extract_recommendations(self):
        recommendations = self.page.soup.find("div", class_="b-sidelist")
        return page_representation.PosterBuilder(str(recommendations)).extract_content()

    def extract_schedule_block(self):
        lst_seasons = self.page.soup.find_all("div", class_="b-post__schedule_list")
        result_lst = []
        for s in lst_seasons:
            for e in s.find_all("tr"):
                try:
                    episode = Episode()
                    episode.current_episode = e.find(class_="td-1").text.strip()
                    episode.localize_title = e.find(class_="td-2").b.text.strip()
                    episode.original_title = e.find(class_="td-2").span.text.strip()
                    episode.release_date = e.find(class_="td-4").text.strip()
                    status = e.find(class_="td-5").text.strip()
                    episode.exists_episode = status if status not in ("&check;", "") else status == "&check;"
                    result_lst.append(episode)
                except AttributeError:
                    continue
        return result_lst
