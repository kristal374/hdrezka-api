from __future__ import annotations

import time
import warnings
import zlib
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Optional, Union, List, Dict, overload, Generic

from HDrezka.connector import NetworkClient
from HDrezka.downloader import media_loader
from HDrezka.exceptions import AJAXFail, LoadingError
from .construct_types import QueryData, Subtitle, Translator, Quality, Actions


class BaseMovie(Generic[QueryData], ABC):
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

    @abstractmethod
    def _update_state(self):
        new_hash = zlib.adler32(str(dict(self._metadata)).encode("utf-8"))
        if self._metadata_hash == new_hash or self._flag_update_block:
            return None
        self._metadata_hash = new_hash
        return self._get()

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
            quality: Union[Quality, str] = Quality.MaximumAvailable,
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
