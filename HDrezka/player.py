import base64
import json
import re
import time
from dataclasses import dataclass
from typing import Union, Optional, Dict, List

from bs4 import BeautifulSoup

from .connector import NetworkClient
from .downloader import media_loader
from .exceptions import AJAXFail
from .html_representation import PageRepresentation


@dataclass
class InfoByEpisode:
    id: int
    title: str

    def __repr__(self):
        return f"InfoByEpisode(\"{self.title}\")"


class Film:
    def __init__(self, metadata, url_dict, translators_dict: Dict[str, str],
                 subtitle_dict: Optional[Dict[str, str]] = None):
        self.metadata: Dict[str, Union[str, int]] = metadata
        self.url_dict: Dict[str, str] = url_dict
        self.translators_dict: Dict[str, str] = translators_dict
        self.subtitle_dict: Optional[Dict[str, str]] = subtitle_dict

    def set_translate(self, translator_id: int):
        if translator_id not in self.translators_dict.values():
            raise AttributeError(f"This translator_id({translator_id}) is missing "
                                 f"from translators list {list(self.translators_dict.values())}")
        self.metadata["translator_id"] = translator_id
        self.update_inside_state()
        return self

    def get_subtitle_url(self, code_lang: Optional[str] = None) -> Optional[Union[Dict[str, str], str]]:
        if code_lang is None or self.subtitle_dict is None:
            return self.subtitle_dict
        return self.subtitle_dict[code_lang]

    def get_video_url(self, quality: Optional[str] = None) -> Union[Dict[str, str], str]:
        if quality is None:
            return self.url_dict
        return self.url_dict[quality]

    def update_inside_state(self):
        response = self._get('ajax/get_cdn_series/', self.metadata)
        self.url_dict = self.extract_video_urls(response["url"])
        self.subtitle_dict = self.extract_subtitle_urls(response)

    @classmethod
    def extract_video_urls(cls, encoded_string: str) -> dict:
        """Извлекает из закодированных данных url"""
        return dict(re.findall('\\[(.*?)](\\bhttps?://\\S+\\.mp4\\b)', cls._clear_trash(encoded_string)))

    @classmethod
    def extract_subtitle_urls(cls, player_config: dict):
        subtitle = cls._decode_subtitle_urls(player_config["subtitle"])
        subtitle_lns = player_config["subtitle_lns"]
        if subtitle:
            return {subtitle_lns[k]: v for k, v in subtitle.items()}
        return None

    @staticmethod
    def _clear_trash(data: str):
        trash_list = ("//_//QEBAQEAhIyMhXl5e",
                      "//_//Xl5eIUAjIyEhIyM=",
                      "//_//JCQhIUAkJEBeIUAjJCRA",
                      "//_//IyMjI14hISMjIUBA",
                      "//_//JCQjISFAIyFAIyM=")
        while any(substring in data for substring in trash_list):
            data = re.sub('|'.join(map(re.escape, trash_list)), '', data)
        return base64.b64decode(data.replace('#h', '', 1)).decode('utf-8')

    @staticmethod
    def _decode_subtitle_urls(encoded_string: str) -> Optional[dict]:
        if encoded_string:
            return dict(re.findall(r"\[(.+?)](https?://\S+?\.vtt\b)", encoded_string))
        return None

    @staticmethod
    def _get(url, data):
        connector = NetworkClient()
        params = {'t': int(time.time() * 1000)}
        response = connector.post(url=f"{connector.url}/{url}", params=params, data=data).json()
        if not response["success"]:
            raise AJAXFail(response.get("message", "field \"success\" is False"))
        return response

    def load_video(self, file_name, quality="1080p", create_dump_file=False, chunk_size=2 ** 10 * 512):
        media_loader.load_from_player(self, file_name, quality, create_dump_file, chunk_size)

    def __repr__(self):
        return f"<{Film.__name__}(id=\"{self.metadata['id']}\")>"


class Serial(Film):
    def __init__(self,
                 metadata,
                 url_dict,
                 translators_dict: Dict[str, str],
                 episode_info_by_season: Dict[int, List[InfoByEpisode]],
                 subtitle_dict: Optional[Dict[str, str]] = None):
        super().__init__(metadata, url_dict, translators_dict, subtitle_dict)
        self.episode_info_by_season = episode_info_by_season

    def set_translate(self, translator_id: int):
        if translator_id not in self.translators_dict.values():
            raise AttributeError(f"This translator_id({translator_id}) is missing "
                                 f"from translators list {list(self.translators_dict.values())}")
        self.metadata["translator_id"] = translator_id
        self.metadata["season"] = 1
        self.metadata["episode"] = 1
        self.update_inside_state()
        return self

    def set_season(self, season_id):
        if season_id not in self.episode_info_by_season.keys():
            raise AttributeError(f"This season_id({season_id}) is missing "
                                 f"from seasons list {list(self.episode_info_by_season.keys())}")
        self.metadata["season"] = season_id
        self.metadata["episode"] = self.episode_info_by_season[season_id][0].id
        super().update_inside_state()
        return self

    def set_episode(self, episode_id):
        episode_list = [i.id for i in self.episode_info_by_season[self.metadata["season"]]]
        if episode_id not in episode_list:
            raise AttributeError(f"This episode_id({episode_id}) is missing "
                                 f"from episode list {episode_list}")
        self.metadata["episode"] = episode_id
        super().update_inside_state()
        return self

    def set_params(self, season_id=None, episode_id=None, translator_id=None):
        if season_id is not None:
            self.set_season(season_id=season_id)
        if episode_id is not None:
            self.set_episode(episode_id=episode_id)
        if translator_id is not None:
            self.set_translate(translator_id=translator_id)
        return self

    @staticmethod
    def extract_episode_info_by_season(seasons_tabs):
        seasons = {}
        for s in seasons_tabs.find_all("ul"):
            season_id = int(s["id"].split("-")[-1])
            episode_list = []
            for e in s.find_all("li"):
                episode_list.append(
                    InfoByEpisode(
                        id=int(e["data-episode_id"]),
                        title=e.contents[0]
                    )
                )
            seasons.setdefault(season_id, episode_list)
        return seasons

    def update_inside_state(self):
        data = {
            "id": self.metadata["id"],
            "translator_id": self.metadata["translator_id"],
            "favs": self.metadata["favs"],
            "action": "get_episodes"
        }
        response = self._get('ajax/get_cdn_series/', data)
        self.url_dict = self.extract_video_urls(response["url"])
        self.subtitle_dict = self.extract_subtitle_urls(response)
        soup = BeautifulSoup(response["episodes"], "lxml")
        self.episode_info_by_season = self.extract_episode_info_by_season(soup)

    def load_all_series(self, file_name, quality="1080p", create_dump_file=False, chunk_size=2 ** 10 * 512):
        for season in self.episode_info_by_season:
            self.set_season(season)
            for episode in self.episode_info_by_season[season]:
                self.set_episode(episode.id)
                postfix = f"_T{self.metadata['translator_id']}_S{season}_E{episode.id}"
                full_path = file_name.format(postfix)
                print(f"Load start file: {full_path}")
                media_loader.load_from_player(self, full_path, quality, create_dump_file, chunk_size)

    def __repr__(self):
        return f"<{Serial.__name__}(id=\"{self.metadata['id']}\")>"


class PlayerBuilder(PageRepresentation):
    def extract_content(self) -> Optional[Union[Serial, Film]]:
        regex = r"sof\.tv\.(.*?)\((\d+), (\d+), (\d+), (\d+), (\d+|false" \
                r"|true), '(.*?)', (false|true), ({\".*?\":\".*?\"})\);"
        match = re.search(regex, self.page.html)
        if not match:
            return None
        if match.group(1) == "initCDNMoviesEvents":
            # match -> function, id, translator_id, is_camrip, is_ads, is_director, web_host, is_logged, player_info
            return self.get_movie(match)
        # match -> function, id, translator_id, season_id, episode_id, url, web_host, is_logged, player_info
        return self.get_series(match)  # "initCDNSeriesEvents"

    def get_movie(self, match):
        metadata = {
            "id": int(match.group(2)),
            "translator_id": int(match.group(3)),
            "is_camrip": int(match.group(4)),
            "is_ads": int(match.group(5)),
            "is_director": int(match.group(6)),
            "favs": self.page.soup.find("input", id="ctrl_favs").attrs.get("value"),
            "action": "get_movie"
        }
        player_config = json.loads(match[9])

        return Film(
            metadata=metadata,
            url_dict=Film.extract_video_urls(player_config["streams"]),
            translators_dict=self.get_all_translators(match[3]),
            subtitle_dict=Film.extract_subtitle_urls(player_config)
        )

    def get_series(self, match):
        metadata = {"id": int(match.group(2)),
                    "translator_id": int(match.group(3)),
                    "season": int(match.group(4)),
                    "episode": int(match.group(5)),
                    "favs": self.page.soup.find("input", id="ctrl_favs").attrs.get("value"),
                    "action": "get_stream"
                    }
        player_config = json.loads(match[9])

        return Serial(
            metadata=metadata,
            episode_info_by_season=self.get_episode_info_by_season(),
            url_dict=Serial.extract_video_urls(player_config["streams"]),
            translators_dict=self.get_all_translators(match[3]),
            subtitle_dict=Serial.extract_subtitle_urls(player_config)
        )

    def get_episode_info_by_season(self):
        seasons_tabs = self.page.soup.find("div", id="simple-episodes-tabs")
        return Serial.extract_episode_info_by_season(seasons_tabs)

    def get_all_translators(self, default_translator_id):
        voice_overs = {}
        for item in self.page.soup.find_all("li", class_="b-translator__item"):
            # 376 is the translator ID of "HDrezka Studio (ua)"
            title = item["title"].strip() + " (ua)" if item["data-translator_id"] == "376" else item["title"].strip()
            voice_overs[title] = int(item["data-translator_id"])

        if not voice_overs:
            element = [i for i in self.page.soup.select('td.l h2') if 'В переводе' in i.get_text()]
            if element:
                translator_name = element[0].find_parent('td').find_next_sibling('td').get_text(strip=True)
            else:
                translator_name = "Unknown translate"
            voice_overs[translator_name] = default_translator_id
        return voice_overs
