from io import IOBase
from typing import Union, IO

from bs4 import BeautifulSoup, Tag
from requests.models import Response


class HTMLDocument:
    def __init__(self, text: Union[str, bytes, IO, Response, Tag]):
        self.html = self.__extract_html(text)
        self.soup = BeautifulSoup(self.html, "lxml") if not isinstance(text, Tag) else text

    @staticmethod
    def __extract_html(html: Union[str, bytes, IO, Response]) -> str:
        if isinstance(html, IOBase):
            html = html.read()
        if isinstance(html, Response):
            return html.text
        if isinstance(html, bytes):
            return html.decode('utf-8')
        if isinstance(html, str):
            return html
        if isinstance(html, Tag):
            return str(html)
        raise AttributeError(f"HTML document cannot be of type {type(html)}")


class PageRepresentation:
    def __init__(self, html_content: Union[str, bytes, IO, Response, HTMLDocument, Tag]):
        self.page = html_content if isinstance(html_content, HTMLDocument) else HTMLDocument(html_content)
