from __future__ import annotations

import zlib
from typing import Optional, Union, List, Dict, overload

from HDrezka.downloader import media_loader
from . import movie_player_builder
from .base_movie import BaseMovie
from .construct_types import (
    Translator,
    SerialQueryData,
    MovieQueryData,
    Season,
    Subtitle,
    Actions,
    Quality,
)


class Film(BaseMovie[MovieQueryData]):
    def set_translate(self, translate: Union[Translator, int, str], is_director: bool = False):
        return self._set_translate(translate=translate, is_director=is_director)

    def _update_translate(self, translate: Translator):
        self._metadata.is_camrip = translate.is_camrip
        self._metadata.is_ads = translate.is_abs
        self._metadata.is_director = translate.is_director
        return super()._update_translate(translate)

    def _update_state(self):
        response = super()._update_state()
        if not response:
            return None
        self._url_dict = movie_player_builder.PlayerBuilder.decode_video_urls(response["url"])
        self._subtitle_list = movie_player_builder.PlayerBuilder.make_subtitles_list(response)
        return response


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
            if episode_id is None:
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
            quality: Union[Quality, str] = Quality.MaximumAvailable,
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
        if not response:
            return None
        self._url_dict = movie_player_builder.PlayerBuilder.decode_video_urls(response["url"])
        self._subtitle_list = movie_player_builder.PlayerBuilder.make_subtitles_list(response)

        if response.get("seasons") and response.get("episodes"):
            self.seasons_tabs = movie_player_builder.PlayerBuilder.create_seasons_tabs_from_data(
                response["seasons"], response["episodes"]
            )
            self._metadata.season = self.seasons_tabs[0].id
            self._metadata.episode = self.seasons_tabs[0].episodes[0].id
            self._metadata_hash = zlib.adler32(str(dict(self._metadata)).encode("utf-8"))
        return response
