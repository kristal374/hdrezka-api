from unittest import TestCase

import requests
import requests_mock

from HDrezka.parse_page import Search
from HDrezka.player import Trailer

from tests.mock_html.html_construcror import generate_fake_html


class TestSearch(TestCase):
    def setUp(self) -> None:
        self.movie = Search()
        self.data = (0, -4, 4.458, -5.2, 6 - 10j, [5, 2, 3], (1, 2, 3), {1, 32, 3}, {"a": 1, "b": 2, "c": 3}, None,
                     True, False, object, range(10), b"hello world")

    def tearDown(self) -> None:
        del self.movie

    def test_positive_page(self):
        self.assertEqual("https://rezka.ag/search/", str(self.movie))
        self.movie.query("Blob")
        for page in range(1, 100):
            response = str(self.movie.page(page))
            correct_url = f"https://rezka.ag/search/?do=search&subaction=search&q=Blob&page={page}"
            self.assertEqual(correct_url, response)

            response = str(self.movie.page(str(page)))  # noqa
            self.assertEqual(correct_url, response)

    def test_negative_page(self):
        self.movie.query("Blob")
        for element in self.data:
            with self.assertRaises(AttributeError, msg=element):
                self.movie.page(element)

    def test_positive_query(self):
        data = (
            ("hello world", "https://rezka.ag/search/?do=search&subaction=search&q=hello+world"),
            ("qwery", "https://rezka.ag/search/?do=search&subaction=search&q=qwery"),
            ("9-4-6: Start", "https://rezka.ag/search/?do=search&subaction=search&q=9-4-6%3A+Start"),
            ("2078", "https://rezka.ag/search/?do=search&subaction=search&q=2078"),
            ("Тандер, болт.", "https://rezka.ag/search/?do=search&subaction=search&q=%D0%A2%D0%B0%D0%BD%D0%B4%D0%B5"
                              "%D1%80%2C+%D0%B1%D0%BE%D0%BB%D1%82."),
            ("Афродита№", "https://rezka.ag/search/?do=search&subaction=search&q=%D0%90%D1%84%D1%80%D0%BE%D0%B4%D0%B8"
                          "%D1%82%D0%B0%E2%84%96"),
            ("Звездопад!", "https://rezka.ag/search/?do=search&subaction=search&q=%D0%97%D0%B2%D0%B5%D0%B7%D0%B4%D0"
                           "%BE%D0%BF%D0%B0%D0%B4%21"),
            ("(Гвардия)", "https://rezka.ag/search/?do=search&subaction=search&q=%28%D0%93%D0%B2%D0%B0%D1%80%D0%B4%D0"
                          "%B8%D1%8F%29"),
            ("Коралл{|}", "https://rezka.ag/search/?do=search&subaction=search&q=%D0%9A%D0%BE%D1%80%D0%B0%D0%BB%D0%BB"
                          "%7B%7C%7D"),
            ("+Баобаб*", "https://rezka.ag/search/?do=search&subaction=search&q=%2B%D0%91%D0%B0%D0%BE%D0%B1%D0%B0%D0"
                         "%B1*"),
            ("$Пингвин#", "https://rezka.ag/search/?do=search&subaction=search&q=%24%D0%9F%D0%B8%D0%BD%D0%B3%D0%B2%D0"
                          "%B8%D0%BD%23"),
            ("_Сёгун~", "https://rezka.ag/search/?do=search&subaction=search&q=_%D0%A1%D1%91%D0%B3%D1%83%D0%BD%7E"),
            ("<Карибы=>", "https://rezka.ag/search/?do=search&subaction=search&q=%3C%D0%9A%D0%B0%D1%80%D0%B8%D0%B1%D1"
                          "%8B%3D%3E"),
            ("Грека реку ^ через рака", "https://rezka.ag/search/?do=search&subaction=search&q=%D0%93%D1%80%D0%B5%D0"
                                        "%BA%D0%B0+%D1%80%D0%B5%D0%BA%D1%83+%5E+%D1%87%D0%B5%D1%80%D0%B5%D0%B7+%D1%80"
                                        "%D0%B0%D0%BA%D0%B0"),
            ("форт, [ракета доктор жаб]", "https://rezka.ag/search/?do=search&subaction=search&q=%D1%84%D0%BE%D1%80"
                                          "%D1%82%2C+%5B%D1%80%D0%B0%D0%BA%D0%B5%D1%82%D0%B0+%D0%B4%D0%BE%D0%BA%D1%82"
                                          "%D0%BE%D1%80+%D0%B6%D0%B0%D0%B1%5D"),
            (r"\Квантификатор@", "https://rezka.ag/search/?do=search&subaction=search&q=%5C%D0%9A%D0%B2%D0%B0%D0%BD%D1"
                                 "%82%D0%B8%D1%84%D0%B8%D0%BA%D0%B0%D1%82%D0%BE%D1%80%40"),
            ("Биба&Боба", "https://rezka.ag/search/?do=search&subaction=search&q=%D0%91%D0%B8%D0%B1%D0%B0%26%D0%91%D0"
                          "%BE%D0%B1%D0%B0"),
            ("Экватор?", "https://rezka.ag/search/?do=search&subaction=search&q=%D0%AD%D0%BA%D0%B2%D0%B0%D1%82%D0%BE"
                         "%D1%80%3F"),
            ("Жбан;", "https://rezka.ag/search/?do=search&subaction=search&q=%D0%96%D0%B1%D0%B0%D0%BD%3B"),
            ("Сектор \"Абадон'", "https://rezka.ag/search/?do=search&subaction=search&q=%D0%A1%D0%B5%D0%BA%D1%82%D0"
                                 "%BE%D1%80+%22%D0%90%D0%B1%D0%B0%D0%B4%D0%BE%D0%BD%27"),
            ("99%", "https://rezka.ag/search/?do=search&subaction=search&q=99%25"),
            ("разрез/порез", "https://rezka.ag/search/?do=search&subaction=search&q=%D1%80%D0%B0%D0%B7%D1%80%D0%B5%D0"
                             "%B7%2F%D0%BF%D0%BE%D1%80%D0%B5%D0%B7"),
            ("черт`а", "https://rezka.ag/search/?do=search&subaction=search&q=%D1%87%D0%B5%D1%80%D1%82%60%D0%B0"),
            (""" \"\"\"""", "https://rezka.ag/search/?do=search&subaction=search&q=%22%22%22"),
        )
        for text_query, correct_url in data:
            response = str(self.movie.query(text_query))
            self.assertEqual(correct_url, response, msg=text_query)

    def test_negative_query(self):
        for element in self.data:
            with self.assertRaises(AttributeError, msg=element):
                self.movie.query(element)  # noqa

    @requests_mock.Mocker()
    def test_positive_get(self, m):
        reference_data, text = generate_fake_html("search")

        correct_url = "https://rezka.ag/search/?do=search&subaction=search&q=%D0%94%D1%80%D0%B0%D0%BA%D0%BE%D0%BD%D1%8B"
        m.register_uri('GET', correct_url, text=text)
        site = self.movie.query("Драконы")

        self.assertEqual(correct_url, str(site))

        response = []
        for item in site.get():
            if isinstance(item.trailer, Trailer):
                item.trailer = item.trailer.__dict__
            response.append(item.__dict__)

        self.assertListEqual(reference_data["search"], response)

    @requests_mock.Mocker()
    def test_negative_get(self, m):
        correct_url = "https://rezka.ag/search/?do=search&subaction=search&q=%D0%94%D1%80%D0%B0%D0%BA%D0%BE%D0%BD%D1%8B"
        site = self.movie.query("Драконы")
        self.assertEqual(correct_url, str(site))

        m.register_uri('GET', correct_url, exc=requests.exceptions.ConnectionError)
        with self.assertRaises(requests.exceptions.ConnectionError):
            site.get()
