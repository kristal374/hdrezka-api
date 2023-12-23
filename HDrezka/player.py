import dataclasses
import re
from typing import Union

from HDrezka import NetworkClient


@dataclasses.dataclass
class TrailerInfo:
    id = None
    title = None
    original_title = None
    description: str = None
    release_year = None
    trailer_link = None
    movie_link = None


class TrailerBuilder:
    def __init__(self, id_):
        """id_: идентификатор фильма"""
        self.data_id = id_

    def _get_trailer(self) -> Union[dict, bool]:
        connector = NetworkClient()
        url = f"{connector.url}/engine/ajax/gettrailervideo.php"
        response = connector.post(url, {'id': self.data_id})
        if response.status_code == 200:
            if response.json().get('success'):
                return response.json()
        return False

    def extract_content(self):
        response = self._get_trailer()
        if not response:
            return None

        content = TrailerInfo()
        content.id = self.data_id
        content.title = self._regular_search('(?<=&laquo;)[^(&raquo;)]*', response.get('title'))
        content.original_title = self._regular_search('(?<=")[^",]*', response.get('title'))
        content.release_year = self._regular_search('\\d\\d\\d\\d[^)]*', response.get('title'))
        content.release_year = int(content.release_year) if content.release_year else None
        content.description = response.get('description')
        content.trailer_link = self._regular_search('(?<=src=")[^"]*', response.get('code'))
        content.movie_link = response.get('link')
        return content

    @staticmethod
    def _regular_search(pattern, string):
        answer = re.search(pattern, string)
        return answer.group(0).strip() if answer else None

    def __repr__(self):
        return f"<Trailer(\"{self.data_id}\")>"
