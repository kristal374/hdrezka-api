import re
from dataclasses import dataclass
from typing import Union

from .connector import NetworkClient
from .exceptions import AJAXFail, ServiceUnavailable


@dataclass
class Trailer:
    id: int  # Идентификатор фильма
    title: str  # Название фильма
    original_title: str  # Оригинальное название фильма
    description: str  # Описание фильма
    release_year: int  # Год выхода фильма
    trailer_url: str  # Ссылка на трейлер
    url: str  # Ссылка на фильм

    def __repr__(self):
        return f"<Trailer({self.title})>"


class TrailerBuilder:
    def __init__(self, film_id):
        """film_id: идентификатор фильма"""
        self.id = film_id

    def _get_trailer(self) -> Union[dict, bool]:
        connector = NetworkClient()
        url = f"{connector.url}/engine/ajax/gettrailervideo.php"
        response = connector.post(url, data={"id": self.id})
        if response.status_code == 200:
            return response.json()
        raise ServiceUnavailable("Service is temporarily unavailable")

    def extract_content(self):
        response = self._get_trailer()
        if not response["success"]:
            raise AJAXFail(response.get("message", 'field "success" is False'))
        return Trailer(
            id=int(self.id),
            title=self._regular_search("(?<=&laquo;).*?(?=&raquo;)", response.get("title")),
            original_title=self._regular_search('(?<=")[^",]*', response.get("title")),
            release_year=self.extract_release_year(response),
            description=response.get("description"),
            trailer_url=self._regular_search('(?<=src=")[^"]*', response.get("code")),
            url=response.get("link"),
        )

    def extract_release_year(self, response):
        release_year = self._regular_search(r"\d{4}(?=\)</small>$)", response.get("title"))
        if release_year is None:
            return release_year
        return int(release_year)

    @staticmethod
    def _regular_search(pattern, string):
        answer = re.search(pattern, string)
        return answer.group(0).strip() if answer else None

    def __repr__(self):
        return f'<TrailerBuilder("{self.id}")>'
