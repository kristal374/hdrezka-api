from io import IOBase
from typing import Union, IO

from bs4 import BeautifulSoup
from requests.models import Response


class HTMLDocument:
    def __init__(self, text: Union[str, bytes, IO, Response]):
        self.html = self.__extract_html(text)
        self.soup = BeautifulSoup(self.html, "lxml")

    @staticmethod
    def __extract_html(html: Union[str, bytes, IO, Response]) -> str:
        if isinstance(html, IOBase):
            html = html.read()
        if isinstance(html, Response):
            return html.text
        if isinstance(html, bytes):
            return html.decode('utf-8')
        return html


class PageRepresentation:
    def __init__(self, html_content: Union[str, bytes, IO, Response, HTMLDocument]):
        self.page = html_content if isinstance(html_content, HTMLDocument) else HTMLDocument(html_content)
