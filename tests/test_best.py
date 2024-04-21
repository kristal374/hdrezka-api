import re
from random import randint
from unittest import TestCase

import requests
import requests_mock

from HDrezka.filters import GenreFilm
from HDrezka.site_navigation import Best
from HDrezka.trailer import TrailerBuilder
from tests.mock_html.html_construcror import generate_fake_html


class TestBest(TestCase):
    def setUp(self) -> None:
        self.movie = Best("films")
        self.data = [0, 8, -15, 45.48, -5.1, 12 - 10j, [1, 2, 31], (1, 2, 3), {1, 2, 3},
                     {"a": 1, "b": 45, "c": 3}, True, False, GenreFilm, range(10), b"hello world"]

    def tearDown(self) -> None:
        del self.movie

    @staticmethod
    def get_genre() -> str:
        genre_list = [i for i in dir(GenreFilm) if not re.search(r"__.*__", i)]
        for name in genre_list:
            genre = getattr(GenreFilm, name)
            yield genre.value

    def enter_bad_args(self, fun, data):
        for element in data:
            with self.assertRaises(AttributeError, msg=element):
                fun(element)

    def test_positive_selected(self):
        self.assertEqual("https://rezka.ag/films/best/", str(self.movie))
        for genre in self.get_genre():
            for year in range(1895, 2024):
                response = str(self.movie.select(genre=genre, year=year))
                correct_url = f"https://rezka.ag/films/best/{genre}/{year}/"
                self.assertEqual(correct_url, response)
            response = str(self.movie.select(genre=genre))
            correct_url = f"https://rezka.ag/films/best/{genre}/"
            self.assertEqual(correct_url, response)

    def test_negative_selected(self):
        lst_year = self.data.copy()
        lst_genre = self.data
        lst_year.append(1894)
        lst_year.append("Hello world!")

        for g in lst_genre:
            for y in lst_year:
                with self.assertRaises(AttributeError, msg=(g, y)):
                    self.movie.select(genre=g, year=y)  # noqa
            with self.assertRaises(AttributeError, msg=g):
                self.movie.select(genre=g)  # noqa

    def test_positive_page(self):
        self.assertEqual("https://rezka.ag/films/best/", str(self.movie.page(1)))
        for genre in self.get_genre():
            page = randint(2, 99)
            response = str(self.movie.select(genre=genre).page(page))
            correct_url = f"https://rezka.ag/films/best/{genre}/page/{page}/"
            self.assertEqual(correct_url, response)

            year = randint(1895, 2024)
            correct_url = f"https://rezka.ag/films/best/{genre}/{year}/page/{page}/"
            response = str(self.movie.select(genre=genre, year=year).page(str(page)))
            self.assertEqual(correct_url, response)

    def test_negative_page(self):
        data = self.data.copy()
        data.remove(8)
        self.enter_bad_args(fun=self.movie.page, data=data)

    @requests_mock.Mocker()
    def test_positive_get(self, m):
        reference_data, text = generate_fake_html("best")
        correct_url = "https://rezka.ag/films/best/"
        m.get(correct_url, text=text)

        self.assertEqual(correct_url, str(self.movie))

        response = []
        for item in self.movie.get():
            if isinstance(item.trailer, TrailerBuilder):
                item.trailer = item.trailer.__dict__
            response.append(item.__dict__)

        self.assertListEqual(reference_data, response)

    @requests_mock.Mocker()
    def test_negative_get(self, m):
        correct_url = "https://rezka.ag/films/best/"
        self.assertEqual(correct_url, str(self.movie))

        m.get(correct_url, exc=requests.exceptions.ConnectionError)
        with self.assertRaises(requests.exceptions.ConnectionError):
            self.movie.get()
