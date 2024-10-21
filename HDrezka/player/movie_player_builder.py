from __future__ import annotations

import base64
import json
import re
from typing import Union, List, Dict, Tuple, TYPE_CHECKING

from bs4 import BeautifulSoup

from HDrezka.html_representation import PageRepresentation
from HDrezka.trailer import Trailer
from . import entities
from .construct_types import (
    MovieQueryData,
    SerialQueryData,
    QueryData,
    Translator,
    Subtitle,
    Season,
    Episode,
)

if TYPE_CHECKING:
    from .entities import Serial, Film

UNKNOWN_TRANSLATE = "Unknown translate"
TRASH_LIST = (
    "//_//QEBAQEAhIyMhXl5e",
    "//_//Xl5eIUAjIyEhIyM=",
    "//_//JCQhIUAkJEBeIUAjJCRA",
    "//_//IyMjI14hISMjIUBA",
    "//_//JCQjISFAIyFAIyM=",
)


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
        return entities.Film(
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
        return entities.Serial(
            metadata=metadata,
            # У рабочих фильмов ссылки на фильм закодированы в поле streams, у не рабочих - url
            url_dict=self.decode_video_urls(player_config.get("streams") or player_config.get("url")),
            subtitle_list=self.make_subtitles_list(player_config),
            translate_list=translate_list,
            seasons_tabs=self.extract_seasons_tabs(),
            popularity_translate=self.extract_rg_stats(translate_list),
        )

    def extract_translators(self, metadata: QueryData = None) -> List[Translator]:
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
