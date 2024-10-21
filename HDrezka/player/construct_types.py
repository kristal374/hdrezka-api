from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union, List, Dict, TypeVar


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
