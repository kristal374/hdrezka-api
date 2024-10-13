import io
from unittest import TestCase

import requests_mock

from HDrezka.connector import NetworkClient
from HDrezka.html_representation import PageRepresentation


class TestPageRepresentation(TestCase):
    html = '<!DOCTYPE html><html lang="en"><head><title>Важное</title></head><body>' \
           '<div class="wrapper"><div class="main"><div class="content"><div ' \
           'class="message-title">Тут был Саша...</div></div></div></div></body></html>'

    def test_html_content_IO(self):
        buf = io.BytesIO()
        buf.write(bytes(self.html.encode("utf-8")))
        buf.seek(0)
        content = PageRepresentation(buf)
        self.assertIsNotNone(content.page.soup.find("div", class_="message-title"))

    @requests_mock.Mocker()
    def test_html_content_response(self, m):
        url = 'https://rezka.ag/test/data/'
        m.get(url, text=self.html)
        response = NetworkClient().get(url)
        content = PageRepresentation(response)
        self.assertIsNotNone(content.page.soup.find("div", class_="message-title"))

    def test_html_content_byte(self):
        content = PageRepresentation(bytes(self.html.encode("utf-8")))
        self.assertIsNotNone(content.page.soup.find("div", class_="message-title"))

    def test_html_content_string(self):
        content = PageRepresentation(self.html)
        self.assertIsNotNone(content.page.soup.find("div", class_="message-title"))

    def test_negative_html_content(self):
        with self.assertRaises(TypeError):
            PageRepresentation(1234567890)  # noqa
