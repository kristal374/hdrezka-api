from __future__ import annotations

from io import IOBase
from typing import Union, IO

from bs4 import BeautifulSoup, Tag
from requests.models import Response


class HTMLDocument:
    def __init__(self, text: Union[str, bytes, IO, Response, Tag]):
        self.html = self.__extract_html(text)
        self.soup = BeautifulSoup(self.html, "lxml") if not isinstance(text, Tag) else text

    @staticmethod
    def __extract_html(html: Union[str, bytes, IO, Response, Tag]) -> str:
        if isinstance(html, IOBase):
            html = html.read()
        if isinstance(html, Response):
            return html.text
        if isinstance(html, bytes):
            return html.decode("utf-8")
        if isinstance(html, str):
            return html
        if isinstance(html, Tag):
            return str(html)
        raise TypeError(f"HTML document cannot be of type {type(html).__name__}")


class PageRepresentation:
    def __init__(self, html_content: Union[str, bytes, IO, Response, PageRepresentation, HTMLDocument, Tag]):
        if isinstance(html_content, HTMLDocument):
            self.page = html_content
        elif isinstance(html_content, PageRepresentation):
            self.page = html_content.page
        else:
            self.page = HTMLDocument(html_content)
