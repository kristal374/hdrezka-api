import re
from dataclasses import dataclass
from typing import Union

from HDrezka import NetworkClient
from HDrezka.exceptions import AJAXFail, ServiceUnavailable


@dataclass
class Trailer:
    id = None
    title = None
    original_title = None
    description: str = None
    release_year = None
    trailer_url = None
    url = None


class TrailerBuilder:
    def __init__(self, film_id):
        """film_id: идентификатор фильма"""
        self.id = film_id

    def _get_trailer(self) -> Union[dict, bool]:
        connector = NetworkClient()
        url = f"{connector.url}/engine/ajax/gettrailervideo.php"
        response = connector.post(url, data={'id': self.id})
        if response.status_code == 200:
            return response.json()
        raise ServiceUnavailable("Service is temporarily unavailable")

    def extract_content(self):
        response = self._get_trailer()
        if not response["success"]:
            raise AJAXFail(response.get("message", "field \"success\" is False"))
        content = Trailer()
        content.id = int(self.id)
        content.title = self._regular_search('(?<=&laquo;)[^(&raquo;)]*', response.get('title'))
        content.original_title = self._regular_search('(?<=")[^",]*', response.get('title'))
        content.release_year = self._regular_search('\\d\\d\\d\\d[^)]*', response.get('title'))
        content.release_year = int(content.release_year) if content.release_year else None
        content.description = response.get('description')
        content.trailer_url = self._regular_search('(?<=src=")[^"]*', response.get('code'))
        content.url = response.get('link')
        return content

    @staticmethod
    def _regular_search(pattern, string):
        answer = re.search(pattern, string)
        return answer.group(0).strip() if answer else None

    def __repr__(self):
        return f"<Trailer(\"{self.id}\")>"
