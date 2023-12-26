from dataclasses import dataclass

from HDrezka.connector import NetworkClient
from HDrezka.html_representation import PageRepresentation


@dataclass
class PersonBriefInfo:
    id: int = None  # идентификатор человека
    name: str = None  # имя человека
    url: str = None  # ссылка на полную информацию о человеке

    def get(self):
        return PersonBuilder(NetworkClient(self.url).text).extract_content()

    def __repr__(self):
        return f"<PersonBriefInfo({self.name})>"


@dataclass
class Person:
    ...


class PersonBuilder(PageRepresentation):
    def extract_content(self):
        ...
