from __future__ import annotations

import base64
import json
import re
import time
import warnings
import zlib
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union, List, Dict, Tuple, overload, Generic, TypeVar

from bs4 import BeautifulSoup

from .connector import NetworkClient
from .downloader import media_loader
from .exceptions import AJAXFail, LoadingError
from .html_representation import PageRepresentation
from .trailer import Trailer

UNKNOWN_TRANSLATE = "Unknown translate"
TRASH_LIST = (
    "//_//QEBAQEAhIyMhXl5e",
    "//_//Xl5eIUAjIyEhIyM=",
    "//_//JCQhIUAkJEBeIUAjJCRA",
    "//_//IyMjI14hISMjIUBA",
    "//_//JCQjISFAIyFAIyM=",
)


@dataclass
class Episode:
    id: int
    title: str

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.title})>"


@dataclass
class Season:
    id: int
    title: str
    episodes: List[Episode] = field(default_factory=list)

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.title})>"


@dataclass
class Translator:
    id: int
    title: str
    original_title: str
    flag_url: Optional[str] = None
    premium: bool = False
    is_camrip: Optional[bool] = None
    is_abs: Optional[bool] = None
    is_director: Optional[bool] = None

    @property
    def full_title(self):
        flag_code = self.flag_url.split("/")[-1].split(".")[0] if self.flag_url is not None else None

        director_particle = " (реж. версия)" if self.is_director else ""
        abs_particle = " (AD)" if self.is_abs else ""
        camrip_particle = " (CAMRip)" if self.is_camrip else ""
        flag_particle = f" ({flag_code.upper()})" if flag_code is not None else ""
        premium_particle = " (PREMIUM)" if self.premium else ""

        return (
            f"{self.original_title}{director_particle}{abs_particle}"
            f"{camrip_particle}{flag_particle}{premium_particle}"
        )

    def __repr__(self):
        return f"<Translator({self.full_title})>"


@dataclass
class Subtitle:
    code_lang: str
    lang: str
    url: str

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.lang})>"


class Actions(str, Enum):
    get_movie = "get_movie"
    get_stream = "get_stream"
    get_episodes = "get_episodes"

    def __str__(self):
        return self.value


class Quality(str, Enum):
    Q360p = "360p"
    Q480p = "480p"
    Q720p = "720p"
    Q1080p = "1080p"
    Q1080p_Ultra = "1080p Ultra"
    Q2K = "2K"
    Q4K = "4K"
    MaximumAvailable = "QualityBest"

    def __str__(self):
        return self.value


@dataclass
class BaseQueryData(ABC):
    id: int
    translator_id: int
    favs: str

    def __iter__(self):
        for item in self._to_dict().items():
            yield item

    @abstractmethod
    def _to_dict(self) -> Dict[str, Union[int, str]]:
        ...


@dataclass
class MovieQueryData(BaseQueryData):
    is_camrip: bool
    is_ads: bool
    is_director: bool
    action: Actions = field(default=Actions.get_movie)

    def _to_dict(self):
        return {
            "id": self.id,
            "translator_id": self.translator_id,
            "is_camrip": int(self.is_camrip),
            "is_ads": int(self.is_ads),
            "is_director": int(self.is_director),
            "favs": self.favs,
            "action": self.action,
        }


@dataclass
class SerialQueryData(BaseQueryData):
    season: int
    episode: int
    action: Actions = field(default=Actions.get_stream)

    def _to_dict(self):
        return {
            "id": self.id,
            "translator_id": self.translator_id,
            "season": self.season,
            "episode": self.episode,
            "favs": self.favs,
            "action": self.action,
        }


QueryData = TypeVar("QueryData", bound=BaseQueryData)


class BaseMovie(Generic[QueryData]):
    _metadata: QueryData

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_connector"):
            cls._connector = NetworkClient()
        return super().__new__(cls)

    def __init__(
            self,
            metadata: QueryData,
            url_dict: Dict[str, List[str]],
            subtitle_list: List[Subtitle],
            translate_list: List[Translator],
    ):
        self._metadata = metadata
        self._metadata_hash = zlib.adler32(str(dict(self._metadata)).encode("utf-8"))
        self._flag_update_block = False
        self._url_dict = url_dict
        self._subtitle_list = subtitle_list
        self.translate_list = translate_list

    def get_current_translate(self):
        return [t for t in self.translate_list if t.id == self._metadata.translator_id][0]

    @overload
    def get_video_url(self, quality: None = None) -> Dict[str, List[str]]:
        ...

    @overload
    def get_video_url(self, quality: str) -> List[str]:
        ...

    def get_video_url(self, quality: Union[Quality, str, None] = None) -> Union[Dict[str, List[str]], List[str]]:
        if quality is not None and not isinstance(quality, (str, Quality)):
            raise TypeError(
                f"Attribute 'quality' ({quality}) must be of type 'str' or 'NoneType', "
                f"but not of type '{type(quality).__name__}'."
            )
        if quality is None:
            return self._url_dict
        if quality == Quality.MaximumAvailable:
            for q in list(Quality)[::-1]:
                if q == Quality.MaximumAvailable:
                    continue
                url = self._url_dict.get(q)
                if url is not None:
                    return url
            raise KeyError("Quality is unavailable.")
        if not self._url_dict.get(quality, False):
            raise ValueError(
                f"This 'quality' attribute ({quality}) is not " f"in the quality list {list(self._url_dict.keys())}."
            )
        return self._url_dict[quality]

    @overload
    def get_subtitle_url(self, lang: str) -> str:
        ...

    @overload
    def get_subtitle_url(self, *, code_lang: str) -> str:
        ...

    @overload
    def get_subtitle_url(self, lang: None = None, code_lang: None = None) -> List[Subtitle]:
        ...

    def get_subtitle_url(
            self, lang: Optional[str] = None, *, code_lang: Optional[str] = None
    ) -> Union[str, List[Subtitle]]:
        if lang is not None and isinstance(lang, str):
            subtitle = [i for i in self._subtitle_list if i.lang == lang]
        elif code_lang is not None and isinstance(code_lang, str):
            subtitle = [i for i in self._subtitle_list if i.code_lang == code_lang]
        elif lang is None and code_lang is None:
            return self._subtitle_list
        else:
            if lang is not None:
                raise TypeError(
                    f"Attribute 'lang' ({lang}) must be of type 'str', " f"but not of type '{type(lang).__name__}'."
                )
            raise TypeError(
                f"Attribute 'code_lang' ({code_lang}) must be of type 'str', "
                f"but not of type '{type(code_lang).__name__}'."
            )
        if len(subtitle) != 1:
            if lang is not None:
                raise ValueError(
                    f"This 'lang' attribute ({lang}) is missing from the list "
                    f"of subtitle languages {[i.lang for i in self._subtitle_list]}"
                )
            raise ValueError(
                f"This 'code_lang' attribute ({code_lang}) is missing from the list "
                f"of subtitle language codes {[i.code_lang for i in self._subtitle_list]}"
            )
        return subtitle[0].url

    def _set_translate(self, translate: Union[Translator, int, str], is_director: bool = False):
        if isinstance(translate, Translator):
            if translate in self.translate_list:
                return self._update_translate(translate)
            raise ValueError(
                f"This Translator ({translate}) is not available for this {self.__class__.__name__.lower()}."
            )

        if isinstance(translate, int) and not isinstance(translate, bool):
            translates_list = [i for i in self.translate_list if i.id == translate]
            if len(translates_list) == 1:
                return self._update_translate(translates_list[0])
            if len(translates_list) > 1:
                # У озвучек фильмов присутствуют поля is_director и т.п. что делает озвучку уникальной,
                # в то время как ID может повторяться в рамках одного фильма, у сериалов ID всегда уникален.
                correct_translate = [i for i in translates_list if i.is_director == is_director]
                return self._update_translate(correct_translate[0])
            raise ValueError(
                f"This 'translate' attribute ({translate}) is not in "
                f"this translator IDs list {[t.id for t in self.translate_list]}."
            )
        if isinstance(translate, str):
            # Существуют озвучки с одинаковыми названиями, но разными флагами стран.
            # При сравнении которых title будет идентичен, но по сути это будут
            # разные озвучки, вследствие чего пользователь мог иметь в виду одну
            # озвучку, но будет установлена совершенно другая.

            # Я рекомендую для установки желаемой озвучки использовать объект озвучки,
            # ну или хотя бы ID совместно с is_director(реж. версия) если это необходимо.

            # Тем не менее данный функционал необходим т.к. на сайте все озвучки представлены своими
            # названиями и пользователю может быть банально удобнее указывать их в таком формате.

            warnings.warn("Using the translates title is less reliable and may result in unexpected behavior.")

            translates_list = [i for i in self.translate_list if translate in (i.title, i.original_title, i.full_title)]
            if len(translates_list) > 0:
                return self._update_translate(translates_list[0])
            raise ValueError(
                f"This 'translate' attribute ({translate}) is not in "
                f"this translator list {[t.title for t in self.translate_list]}."
            )
        raise TypeError(
            f"Attribute 'translate' ({translate}) must be of type 'Translator', 'str' or 'int', "
            f"but not of type '{type(translate).__name__}'."
        )

    def _update_translate(self, translate: Translator):
        self._metadata.translator_id = translate.id
        if isinstance(self, Film):
            self._metadata.is_camrip = translate.is_camrip
            self._metadata.is_ads = translate.is_abs
            self._metadata.is_director = translate.is_director
        self._update_state()
        return self

    def update(self):
        self._metadata_hash = None
        self._update_state()
        return self

    @contextmanager
    def _block_updates(self):
        try:
            self._flag_update_block = True
            yield
        finally:
            self._flag_update_block = False

    def _update_state(self):
        new_hash = zlib.adler32(str(dict(self._metadata)).encode("utf-8"))
        if self._metadata_hash == new_hash or self._flag_update_block:
            return None
        response = self._get()
        self._url_dict = PlayerBuilder.decode_video_urls(response["url"])
        self._subtitle_list = PlayerBuilder.make_subtitles_list(response)
        self._metadata_hash = new_hash
        return response

    def _get(self):
        data = dict(self._metadata)

        if self._metadata.action == Actions.get_episodes:
            del data["episode"]
            del data["season"]

        params = {"t": int(time.time() * 1000)}
        query_url = f"{self._connector.url}/ajax/get_cdn_series/"
        response = self._connector.post(url=query_url, params=params, data=data)

        if 200 < response.status_code >= 300:
            raise LoadingError(f"Status code = {response.status_code}, {response.reason}")

        json_response = response.json()
        if not json_response["success"]:
            raise AJAXFail(json_response.get("message", 'Field "success" is False.'))

        return json_response

    def load(
            self,
            file_name: str,
            quality: Union[Quality, str] = Quality.Q1080p,
            subtitle: Optional[str] = None,
            create_dump_file: bool = False,
            chunk_size: int = 2 ** 10 * 512,
    ):
        full_path = file_name.format(
            **{
                "id": self._metadata.id,
                "T": self.get_current_translate().title,
                "t": self._metadata.translator_id,
                "Q": quality,
            }
        )
        media_loader.load_from_player(self, f"{full_path}.mp4", quality, create_dump_file, chunk_size)
        subtitle_url = self.get_subtitle_url(subtitle) if subtitle is not None else None
        if subtitle_url:
            media_loader.load_from_url(subtitle_url, f"{file_name}.vtt", chunk_size)

    def __repr__(self):
        return f'<{self.__class__.__name__}(id="{self._metadata.id}")>'


class Film(BaseMovie[MovieQueryData]):
    def set_translate(self, translate: Union[Translator, int, str], is_director: bool = False):
        return self._set_translate(translate=translate, is_director=is_director)


class Serial(BaseMovie[SerialQueryData]):
    popularity_translate: Dict[str, float]

    def __init__(
            self,
            metadata: SerialQueryData,
            url_dict: Dict[str, List[str]],
            subtitle_list: List[Subtitle],
            translate_list: List[Translator],
            seasons_tabs: List[Season],
            popularity_translate: Dict[str, float],
    ):
        super().__init__(metadata, url_dict, subtitle_list, translate_list)
        self.seasons_tabs = seasons_tabs
        self.popularity_translate = popularity_translate

    def get_current_season(self):
        return [s for s in self.seasons_tabs if s.id == self._metadata.season][0]

    def get_current_episode(self):
        return [e for e in self.get_current_season().episodes if e.id == self._metadata.episode][0]

    @overload
    def set_season(self, season_id: int) -> Serial:
        ...

    @overload
    def set_season(self, *, season_title: str) -> Serial:
        ...

    def set_season(self, season_id: Optional[int] = None, *, season_title: Optional[str] = None):
        if season_id is not None and season_title is not None:
            raise ValueError("Expected either 'season_id' or 'season_title', but not both.")
        if season_id is None and season_title is None:
            raise ValueError("At least one of 'season_id' or 'season_title' must be provided.")
        if season_id and (not isinstance(season_id, int) or isinstance(season_id, bool)):
            raise TypeError(
                f"Attribute 'season_id' ({season_id}) must be of type 'int', "
                f"but not of type '{type(season_id).__name__}'."
            )
        if season_title and not isinstance(season_title, str):
            raise TypeError(
                f"Attribute 'season_title' ({season_title}) must be of type 'str', "
                f"but not of type '{type(season_title).__name__}'."
            )

        target_season = [i for i in self.seasons_tabs if i.id == season_id or i.title == season_title]
        if len(target_season) == 0:
            if season_title is not None:
                raise ValueError(
                    f"This 'season_title' attribute ({season_title}) is missing "
                    f"from seasons list {[i.title for i in self.seasons_tabs]}"
                )
            raise ValueError(
                f"This 'season_id' attribute ({season_id}) is missing "
                f"from seasons IDs list {[i.id for i in self.seasons_tabs]}"
            )
        self._metadata.season = target_season[0].id
        self._metadata.episode = target_season[0].episodes[0].id
        self._update_state()
        return self

    @overload
    def set_episode(self, episode_id: int) -> Serial:
        ...

    @overload
    def set_episode(self, *, episode_title: str) -> Serial:
        ...

    def set_episode(self, episode_id: Optional[int] = None, *, episode_title: Optional[str] = None):
        if episode_id is not None and episode_title is not None:
            raise ValueError("Expected either 'episode_id' or 'episode_title', but not both.")
        if episode_id is None and episode_title is None:
            raise ValueError("At least one of 'episode_id' or 'episode_title' must be provided.")
        if episode_id and (not isinstance(episode_id, int) or isinstance(episode_id, bool)):
            raise TypeError(
                f"Attribute 'episode_id' ({episode_id}) must be of type 'int', "
                f"but not of type '{type(episode_id).__name__}'."
            )
        if episode_title and (not isinstance(episode_title, str)):
            raise TypeError(
                f"Attribute 'episode_title' ({episode_title}) must be of type 'str', "
                f"but not of type '{type(episode_title).__name__}'."
            )
        target_season = self.get_current_season()
        target_episode = [e for e in target_season.episodes if e.id == episode_id or e.title == episode_title]

        if len(target_episode) == 0:
            if episode_title is not None:
                raise ValueError(
                    f"This 'episode_title' attribute ({episode_title}) is missing "
                    f"from episode list {[e.title for e in target_season.episodes]}"
                )
            raise ValueError(
                f"This 'episode_id' attribute ({episode_id}) is missing "
                f"from episode IDs list {[e.id for e in target_season.episodes]}"
            )
        self._metadata.episode = episode_id
        self._update_state()
        return self

    def set_translate(self, translate: Union[Translator, int, str]):
        try:
            # При смене озвучки у сериала мы должны дополнительно запросить список серий и эпизодов
            # поскольку у разных озвучек он может отличаться, для этого при запросе надо сменить action
            self._metadata.action = Actions.get_episodes
            return self._set_translate(translate=translate)
        finally:
            self._metadata.action = Actions.get_stream

    def set_params(
            self,
            *,
            season_id: Optional[int] = None,
            season_title: Optional[str] = None,
            episode_id: Optional[int] = None,
            episode_title: Optional[str] = None,
            translate: Union[Translator, int, str, None] = None,
    ):
        if season_id is not None and season_title is not None:
            raise ValueError("Expected either 'season_id' or 'season_title', but not both.")
        if episode_id is not None and episode_title is not None:
            raise ValueError("Expected either 'episode_id' or 'episode_title', but not both.")

        # Если мы хотим сменить серию или сезон у ДРУГОЙ озвучки, мы должны перед
        # этим обновить список этих сезонов и серий, установив необходимую озвучку.
        # Это необходимо поскольку у новой озвучки может быть озвучено другое
        # количество серий и сезонов.
        if translate is not None:
            self.set_translate(translate=translate)

        # Для уменьшения количества запросов блокируем обновление объекта
        with self._block_updates():
            if season_id is not None or season_title is not None:
                if season_id is not None:
                    self.set_season(season_id=season_id)
                else:
                    self.set_season(season_title=season_title)
            if episode_id is not None or episode_title is not None:
                if episode_id is not None:
                    self.set_episode(episode_id=episode_id)
                else:
                    self.set_episode(episode_title=episode_title)

        # Поскольку объект не обновлялся - обновляем его
        self._update_state()
        return self

    def slice_seasons(
            self,
            season_from: int = 1,
            episode_from: int = 1,
            season_to: int = -1,
            episode_to: int = 1,
    ) -> List[Season]:
        # season_to = -1 До конца сериала
        # season_to = -2 До конца сезона
        if not isinstance(season_from, int):
            raise TypeError(f"'season_from' should be of type 'int', but got {type(season_from).__name__}.")
        if not isinstance(season_to, int):
            raise TypeError(f"'season_to' should be of type 'int', but got {type(season_to).__name__}.")
        if not isinstance(episode_from, int):
            raise TypeError(f"'episode_from' should be of type 'int', but got {type(episode_from).__name__}.")
        if not isinstance(episode_to, int):
            raise TypeError(f"'episode_to' should be of type 'int', but got {type(episode_to).__name__}.")

        if season_to == -1:
            season_to = self.seasons_tabs[-1].id
            episode_to = self.seasons_tabs[-1].episodes[-1].id
        elif season_to == -2:
            season_to = season_from
            episode_to = [s for s in self.seasons_tabs if s.id == season_from][0].episodes[-1].id

        min_season = self.seasons_tabs[0].id
        max_season = self.seasons_tabs[-1].id
        min_episode_start = self.seasons_tabs[0].episodes[0].id
        max_episode_start = self.seasons_tabs[0].episodes[-1].id
        min_episode_end = self.seasons_tabs[-1].episodes[0].id
        max_episode_end = self.seasons_tabs[-1].episodes[-1].id

        if not min_season <= season_from <= max_season:
            raise ValueError(
                f"The start season number '{season_from}' must be " f"between '{min_season}' and '{max_season}'."
            )
        if not min_season <= season_to <= max_season:
            raise ValueError(
                f"The end season number '{season_to}' must be " f"between '{min_season}' and '{max_season}'."
            )
        if season_from > season_to:
            raise ValueError(
                f"The start season number '{season_from}' cannot be "
                f"greater than the end season number '{season_to}'."
            )

        if season_from == season_to and episode_from > episode_to:
            raise ValueError(
                f"The start episode number '{episode_from}' cannot be "
                f"greater than the end episode number '{episode_to}'."
            )
        if not min_episode_start <= episode_from <= max_episode_start:
            raise ValueError(
                f"The start episode number '{episode_from}' must be "
                f"between '{min_episode_start}' and '{max_episode_start}' in this season."
            )
        if not min_episode_end <= episode_to <= max_episode_end:
            raise ValueError(
                f"The end episode number '{episode_to}' must be "
                f"between '{min_episode_end}' and '{max_episode_end}' in this season."
            )

        result_list = []
        for season in self.seasons_tabs:
            if season.id < season_from or season.id > season_to:
                continue

            sliced_episodes = season.episodes.copy()
            if season.id == season_from:
                sliced_episodes = [e for e in sliced_episodes if e.id >= episode_from]
            if season.id == season_to:
                sliced_episodes = [e for e in sliced_episodes if e.id <= episode_to]
            result_list.append(Season(season.id, season.title, sliced_episodes))

        return result_list

    def load_serial(  # pylint: disable=R0913
            self,
            file_name: str,
            season_start: int = 1,
            episode_start: int = 1,
            season_end: int = -1,
            episode_end: int = 1,
            quality: Union[Quality, str] = Quality.Q1080p,
            subtitle: Optional[str] = None,
            create_dump_file: bool = False,
            chunk_size: int = 2 ** 10 * 512,
    ):
        n = 0
        for season in self.slice_seasons(season_start, episode_start, season_end, episode_end):
            self.set_season(season.id)
            for episode in season.episodes:
                n += 1
                self.set_episode(episode.id)
                full_path = file_name.format(
                    **{
                        "n": n,
                        "id": self._metadata.id,
                        "S": season.title,
                        "s": season.id,
                        "E": episode.title,
                        "e": episode.id,
                        "T": self.get_current_translate().title,
                        "t": self._metadata.translator_id,
                        "Q": quality,
                    }
                )
                subtitle_url = self.get_subtitle_url(subtitle) if subtitle is not None else None

                media_loader.load_from_player(self, f"{full_path}.mp4", quality, create_dump_file, chunk_size)
                if subtitle_url:
                    media_loader.load_from_url(subtitle_url, f"{full_path}.vtt", chunk_size)

    def update(self):
        self._metadata_hash = None
        old_season = self._metadata.season
        old_episode = self._metadata.episode
        try:
            # Для полноценного обновления объекта нам необходимо так же обновить список серий,
            # а для этого нужно установить action = get_episodes
            self._metadata.action = Actions.get_episodes
            self._update_state()
        finally:
            self._metadata.action = Actions.get_stream

        if not (self._metadata.season == old_season and self._metadata.episode == old_episode):
            self.set_params(season_id=old_season, episode_id=old_episode)
        return self

    def _update_state(self):
        response = super()._update_state()
        if response is not None and response.get("seasons") and response.get("episodes"):
            self.seasons_tabs = PlayerBuilder.create_seasons_tabs_from_data(response["seasons"], response["episodes"])
            self._metadata.season = self.seasons_tabs[0].id
            self._metadata.episode = self.seasons_tabs[0].episodes[0].id
        return response


class PlayerBuilder(PageRepresentation):
    def extract_content(self) -> Union[Serial, Film, Trailer, None]:
        movie_type, *movie_params = self.extract_init_params()

        if movie_type == "initCDNMoviesEvents":
            # movie_params -> movie_id, translator_id, is_camrip, is_ads, is_director, web_host, is_logged, player_info
            return self.extract_movie(movie_params)  # Фильм
        if movie_type == "initCDNSeriesEvents":
            # movie_params -> movie_id, translator_id, season_id, episode_id, url, web_host, is_logged, player_info
            return self.extract_series(movie_params)  # Сериал
        if movie_type is None and self.page.soup.find("iframe", src=re.compile("youtube")):
            return self.extract_trailer()  # Трейлер
        if movie_type is None:
            return None  # Movie unavailable: "Мы работаем над восстановлением. Часть данных уже доступна для просмотра"
        raise TypeError(f"Unknown type of player initialization function: {movie_type}")

    def extract_init_params(self) -> Tuple:
        """
        Using a regular expression in the HTML code, it finds the player initialization function,
        extracts its name and the parameters with which it is called.
        """
        regex = (
            r"sof\.tv\.(.*?)\((\d+), (\d+), (\d+), (\d+), (\d+|false"
            r"|true), '(.*?)', (false|true), ({\".*?\":.*?})\);"
        )
        match = re.search(regex, self.page.html)
        return match.groups() if match else (None,)

    def extract_favs(self) -> str:
        return self.page.soup.find("input", id="ctrl_favs").attrs.get("value")

    def extract_trailer(self) -> Trailer:
        regexp_year = re.compile("Год|Дата выхода")
        regexp_youtube = re.compile("youtube")

        site_url = self.page.soup.find("meta", property="og:url").get("content")
        trailer_id = int(re.search(r"/(\d*)-", site_url).group(1))
        title = self.page.soup.find("div", class_="b-post__title").get_text(strip=True)
        original_title = self.page.soup.find("div", class_="b-post__origtitle")
        year_element = self.page.soup.find("h2", string=regexp_year) or self.page.soup.find("td", string=regexp_year)
        year = year_element.find_next("a").get_text(strip=True)
        description = self.page.soup.find("div", class_="b-post__description_text")
        trailer_url = self.page.soup.find("iframe", src=regexp_youtube).get("src")

        return Trailer(
            id=trailer_id,
            title=title,
            original_title=original_title.get_text(strip=True) if original_title else None,
            release_year=int(re.search(r"\d{4}", year).group(0)),
            description=description.get_text(strip=True) if description else None,
            trailer_url=trailer_url,
            url=site_url,
        )

    def extract_movie(self, movie_params: Tuple[str]) -> Film:
        metadata = MovieQueryData(
            id=int(movie_params[0]),
            translator_id=int(movie_params[1]),
            is_camrip=movie_params[2] == "1",
            is_ads=movie_params[3] == "1",
            is_director=movie_params[4] == "1",
            favs=self.extract_favs(),
        )
        player_config = json.loads(movie_params[7])
        return Film(
            metadata=metadata,
            # У рабочих фильмов ссылки на фильм закодированы в поле streams, у не рабочих - url
            url_dict=self.decode_video_urls(player_config.get("streams") or player_config.get("url")),
            subtitle_list=self.make_subtitles_list(player_config),
            translate_list=self.extract_translators(metadata),
        )

    def extract_series(self, movie_params: Tuple[str]) -> Serial:
        metadata = SerialQueryData(
            id=int(movie_params[0]),
            translator_id=int(movie_params[1]),
            season=int(movie_params[2]),
            episode=int(movie_params[3]),
            favs=self.extract_favs(),
        )
        player_config = json.loads(movie_params[7])
        translate_list = self.extract_translators(metadata)
        return Serial(
            metadata=metadata,
            # У рабочих фильмов ссылки на фильм закодированы в поле streams, у не рабочих - url
            url_dict=self.decode_video_urls(player_config.get("streams") or player_config.get("url")),
            subtitle_list=self.make_subtitles_list(player_config),
            translate_list=translate_list,
            seasons_tabs=self.extract_seasons_tabs(),
            popularity_translate=self.extract_rg_stats(translate_list),
        )

    def extract_translators(self, metadata: Union[MovieQueryData, SerialQueryData] = None) -> List[Translator]:
        voice_overs = []
        for item in self.page.soup.find_all("li", class_="b-translator__item"):
            original_title_tag = item.find(string=True, recursive=False)
            original_title = original_title_tag.strip() if original_title_tag and original_title_tag.strip() else None
            voice_overs.append(
                Translator(
                    id=int(item["data-translator_id"]),
                    title=item.text.strip() or UNKNOWN_TRANSLATE,
                    original_title=original_title if original_title else UNKNOWN_TRANSLATE,
                    flag_url=item.img["src"].strip() if item.img else None,
                    premium=any(i == "b-prem_translator" for i in item["class"]),
                    is_camrip=item.attrs.get("data-camrip") == "1" if "data-camrip" in item.attrs else None,
                    is_abs=item.attrs.get("data-ads") == "1" if "data-ads" in item.attrs else None,
                    is_director=item.attrs.get("data-director") == "1" if "data-director" in item.attrs else None,
                )
            )

        # В случае если у фильма/сериала только одна озвучка,
        # она не будет отображаться и её надо извлечь другим способом
        if not voice_overs:
            is_camrip = bool(dict(metadata)["is_camrip"]) if "is_camrip" in dict(metadata) else None
            is_abs = bool(dict(metadata)["is_ads"]) if "is_ads" in dict(metadata) else None
            is_director = bool(dict(metadata)["is_director"]) if "is_director" in dict(metadata) else None

            if metadata.id in (376, 111):
                title = "HDrezka Studio"
            else:
                translator = self.page.soup.find("h2", string="В переводе")
                title = translator.find_next().text.strip() if translator else UNKNOWN_TRANSLATE
            original_title = title.replace("(режиссёрская версия)", "").strip() if is_director else title

            voice_overs.append(
                Translator(
                    id=metadata.translator_id,
                    title=title,
                    original_title=original_title if original_title else UNKNOWN_TRANSLATE,
                    # 376 is the translator ID of "HDrezka Studio (ua)"
                    flag_url="https://static.hdrezka.ac/i/flags/ua.png" if metadata.id == 376 else None,
                    premium=False,
                    is_camrip=is_camrip,
                    is_abs=is_abs,
                    is_director=is_director,
                )
            )
        return voice_overs

    def extract_rg_stats(self, translate_list: List[Translator]) -> Dict[str, float]:
        popularity_dict = {}
        rg_stats_obj = self.page.soup.find(class_="b-rgstats__help")
        if not rg_stats_obj or "title" not in rg_stats_obj.attrs:
            return popularity_dict
        soup = BeautifulSoup(rg_stats_obj["title"], "lxml")
        for item in soup.select("li.b-rgstats__list_item"):
            title = item.find("div", class_="title").get_text(strip=True)
            image = item.find("img")
            image_url = f"https://static.hdrezka.ac{image['src'].strip()}" if image else None
            popularity = float(
                item.find("div", class_="count").text.replace("%", "").replace(",", ".").replace(" ", "")
            )

            matched = [t for t in translate_list if t.original_title == title]
            if len(matched) > 1 and image_url:
                matched = [t for t in matched if t.flag_url == image_url]
            if matched:
                popularity_dict[matched[0].full_title] = popularity
        return popularity_dict

    @staticmethod
    def decode_video_urls(encoded_string: Union[str, False]) -> Dict[str, List[str]]:
        if encoded_string is False:
            return {}

        # Удаляем мусор из закодированной строки
        while any(substring in encoded_string for substring in TRASH_LIST):
            encoded_string = re.sub("|".join(map(re.escape, TRASH_LIST)), "", encoded_string)

        decoded_string = base64.b64decode(encoded_string.replace("#h", "", 1)).decode("utf-8")
        urls_container = {}
        for line in decoded_string.split(","):
            quality_name = re.search(r"\[.*?]", line)[0]
            quality_urls = line[len(quality_name):]
            filtered_urls = [url for url in re.split(r"\sor\s", quality_urls) if re.match(r"https?://.*\.mp4$", url)]
            urls_container[quality_name[1:-1]] = filtered_urls
        return urls_container

    @staticmethod
    def make_subtitles_list(subtitle_data: Dict[str, Union[False, str, Dict[str, str]]]) -> List[Subtitle]:
        if not subtitle_data["subtitle"]:
            return []

        subtitles = dict(re.findall(r"\[(.+?)](https?://\S+?\.vtt\b)", subtitle_data["subtitle"]))
        return [
            Subtitle(
                code_lang=subtitle_data["subtitle_lns"].get(lang, ""),
                lang=lang,
                url=url,
            )
            for lang, url in subtitles.items()
        ]

    def extract_seasons_tabs(self):
        seasons = "".join(map(str, self.page.soup.find_all("li", class_="b-simple_season__item")))
        episodes = "".join(map(str, self.page.soup.find_all("ul", class_="b-simple_episodes__list")))
        return self.create_seasons_tabs_from_data(seasons, episodes)

    @staticmethod
    def create_seasons_tabs_from_data(seasons: str, episodes: str) -> List[Season]:
        seasons_list = PlayerBuilder.make_seasons_list(seasons)
        episodes_lists = PlayerBuilder.make_episodes_lists(episodes)
        for season in seasons_list:
            season.episodes = episodes_lists[season.id]
        return seasons_list

    @staticmethod
    def make_seasons_list(seasons_string: str) -> List[Season]:
        soup = BeautifulSoup(seasons_string, "lxml")
        seasons_list = []
        for s in soup.find_all(class_="b-simple_season__item"):
            seasons_list.append(Season(id=int(s["data-tab_id"]), title=s.next.get_text(strip=True)))
        return seasons_list

    @staticmethod
    def make_episodes_lists(episodes_string: str) -> Dict[int, List[Episode]]:
        soup = BeautifulSoup(episodes_string, "lxml")
        episodes_lists = {}
        for episodes_list in soup.find_all("ul", class_="b-simple_episodes__list"):
            for e in episodes_list.find_all("li", class_="b-simple_episode__item"):
                season_id = int(e["data-season_id"])
                if season_id not in episodes_lists:
                    episodes_lists[season_id] = []
                episodes_lists[season_id].append(
                    Episode(
                        id=int(e["data-episode_id"]),
                        title=e.next.get_text(strip=True),
                    )
                )
        return episodes_lists

    def __repr__(self):
        return f"<{self.__class__.__name__}>"
