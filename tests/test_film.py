import re
from random import randint
from unittest import TestCase

import requests
import requests_mock

from HDrezka.filters import GenreFilm, Filters
from HDrezka.site_navigation import Films
from HDrezka.trailer import TrailerBuilder
from tests.mock_html.html_construcror import generate_fake_html


class TestFilms(TestCase):
    def setUp(self) -> None:
        self.movie = Films()

    def tearDown(self) -> None:
        del self.movie

    @staticmethod
    def get_genre():
        genre_list = [i for i in dir(GenreFilm) if not re.search(r"__.*__", i)]
        for name in genre_list:
            genre = getattr(GenreFilm, name)
            yield genre

    @staticmethod
    def get_filters():
        filters_list = [i for i in dir(Filters) if not re.search(r"__.*__", i)]
        for name in filters_list:
            filter_obj = getattr(Filters, name)
            yield filter_obj

    def enter_bad_args(self, fun, data):
        for element in data:
            with self.assertRaises(AttributeError, msg=element):
                fun(element)

    def test_positive_selected_category(self):
        self.assertEqual("https://rezka.ag/films/", str(self.movie.selected_category(None)))
        for genre in self.get_genre():
            response = str(self.movie.selected_category(genre))
            correct_url = f"https://rezka.ag/films/{genre}/"
            self.assertEqual(correct_url, response)

    def test_negative_selected_category(self):
        self.enter_bad_args(
            fun=self.movie.selected_category,
            data=(0, 12, -8, 4.48, -5.1, 12 - 10j, [1, 2, 3], (1, 2, 3), {1, 2, 3},
                  {"a": 1, "b": 2, "c": 3}, True, False, GenreFilm, range(10), b"hello world"))

    def test_positive_filter(self):
        self.assertEqual("https://rezka.ag/films/", str(self.movie.filter(None)))
        self.assertEqual("https://rezka.ag/films/?filter=last", str(self.movie.filter()))
        for genre in self.get_genre():
            for filter_obj in self.get_filters():
                response = str(self.movie.selected_category(genre).filter(filter_obj))
                correct_url = f"https://rezka.ag/films/{genre}/?filter={filter_obj}"
                self.assertEqual(correct_url, response)

    def test_negative_filter(self):
        self.enter_bad_args(
            fun=self.movie.filter,
            data=(0, 12, -4, 4.48, -5.1, 12 - 10j,
                  [1, 2, 3], (1, 2, 3), {1, 2, 3},
                  {"a": 1, "b": 2, "c": 3}, True, False,
                  GenreFilm, range(10), b"hello world"))

    def test_positive_page(self):
        for genre in self.get_genre():
            for filter_obj in self.get_filters():
                page = randint(1, 100)
                response = str(self.movie.selected_category(genre).filter(filter_obj).page(page))
                correct_url = f"https://rezka.ag/films/{genre}/page/{page}/?filter={filter_obj}"
                self.assertEqual(correct_url, response)

                response = str(self.movie.selected_category(genre).filter(filter_obj).page(str(page)))
                self.assertEqual(correct_url, response)

    def test_negative_page(self):
        self.enter_bad_args(
            fun=self.movie.page,
            data=(0, -8, 4.48, -5.1, 12 - 10j, [1, 2, 3], (1, 2, 3), {1, 2, 3}, {"a": 1, "b": 2, "c": 3},
                  None, True, False, GenreFilm, range(10), "hello world", b"hello world"))

    def test_positive_find_best(self):
        self.assertEqual("https://rezka.ag/films/best/2021/",
                         str(self.movie.find_best(year=2021)))
        self.assertEqual("https://rezka.ag/films/best/fiction/",
                         str(self.movie.find_best(genre=GenreFilm.FICTION)))
        for genre in self.get_genre():
            year = randint(1911, 2023)
            response = str(self.movie.find_best(genre=genre, year=year))
            correct_url = f"https://rezka.ag/films/best/{genre}/{year}/"
            self.assertEqual(correct_url, response)

    def test_negative_find_best(self):
        lst_year = (1895, 0, -8, 14, 4.48, -5.1, 12 - 10j, [1, 2, 3], (1, 2, 3), {1, 2, 3}, {"a": 1, "b": 2, "c": 3},
                    True, False, GenreFilm, range(10), "hello world", b"hello world")
        lst_genre = (0, -8, 14, 4.48, -5.1, 12 - 10j, [1, 2, 3], (1, 2, 3), {1, 2, 3}, {"a": 1, "b": 2, "c": 3},
                     True, False, GenreFilm, range(10), b"hello world")

        for y in lst_year:
            for g in lst_genre:
                with self.assertRaises(AttributeError, msg=(y, g)):
                    self.movie.find_best(year=y, genre=g)  # noqa

    def test_positive_find_best_page(self):
        self.assertEqual("https://rezka.ag/films/best/2021/page/8/",
                         str(self.movie.find_best(year=2021).page(8)))
        self.assertEqual("https://rezka.ag/films/best/fiction/page/8/",
                         str(self.movie.find_best(genre=GenreFilm.FICTION).page(8)))
        for genre in self.get_genre():
            year = randint(1911, 2023)
            page = randint(1, 100)
            response = str(self.movie.find_best(genre=genre, year=year).page(page))
            correct_url = f"https://rezka.ag/films/best/{genre}/{year}/page/{page}/"
            self.assertEqual(correct_url, response)

    @requests_mock.Mocker()
    def test_positive_get(self, m):
        reference_data, text = generate_fake_html("films")

        correct_url = "https://rezka.ag/films/page/3/"
        m.register_uri('GET', correct_url, text=text)
        site = self.movie.page(3)

        self.assertEqual(correct_url, str(site))

        response = []
        for item in site.get():
            if isinstance(item.trailer, TrailerBuilder):
                item.trailer = item.trailer.__dict__
            response.append(item.__dict__)

        self.assertListEqual(reference_data["films"], response)

        site = self.movie.find_best(year=2018)
        m.register_uri('GET', str(site), text="Success")
        self.assertEqual(0, len(site.get()))

    @requests_mock.Mocker()
    def test_negative_get(self, m):
        correct_url = "https://rezka.ag/films/page/3/"
        site = self.movie.page(3)
        self.assertEqual(correct_url, str(site))

        m.register_uri('GET', correct_url, exc=requests.exceptions.ConnectionError)
        with self.assertRaises(requests.exceptions.ConnectionError):
            site.get()
