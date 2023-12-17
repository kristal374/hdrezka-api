import re
import json
from unittest import TestCase
from random import randint

import requests
import requests_mock

from HDrezka.parse_page import Animation
from HDrezka.filters import GenreAnimation, Filters
from HDrezka.player import Trailer


class TestAnimations(TestCase):
    def setUp(self) -> None:
        self.movie = Animation()

    def tearDown(self) -> None:
        del self.movie

    @staticmethod
    def get_genre():
        genre_list = [i for i in dir(GenreAnimation) if not re.search(r"__.*__", i)]
        for name in genre_list:
            genre = getattr(GenreAnimation, name)
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
        self.assertEqual("https://rezka.ag/animation/", self.movie.selected_category(None).__str__())
        for genre in self.get_genre():
            response = self.movie.selected_category(genre).__str__()
            correct_url = f"https://rezka.ag/animation/{genre}/"
            self.assertEqual(correct_url, response)

    def test_negative_selected_category(self):
        self.enter_bad_args(
            fun=self.movie.selected_category,
            data=(0, 8, -14, 45.48, -5.1, 12 - 10j, [1, 2, 3], (1, 2, 3), {1, 2, 3},
                  {"a": 1, "b": 2, "c": 3}, True, False, GenreAnimation, range(10), b"hello world"))

    def test_positive_filter(self):
        self.assertEqual("https://rezka.ag/animation/", self.movie.filter(None).__str__())
        self.assertEqual("https://rezka.ag/animation/?filter=last", self.movie.filter().__str__())
        for genre in self.get_genre():
            for filter_obj in self.get_filters():
                response = self.movie.selected_category(genre).filter(filter_obj).__str__()
                correct_url = f"https://rezka.ag/animation/{genre}/?filter={filter_obj}"
                self.assertEqual(correct_url, response)

    def test_negative_filter(self):
        self.enter_bad_args(
            fun=self.movie.filter,
            data=(0, 12, -4, 4.48, -58.1, 162 - 12j,
                  [1, 2, 3], (1, 2, 3), {1, 2, 3},
                  {"a": 1, "b": 2, "c": 3}, True, False,
                  GenreAnimation, range(10), b"hello world"))

    def test_positive_page(self):
        for genre in self.get_genre():
            for filter_obj in self.get_filters():
                page = randint(1, 99)
                response = self.movie.selected_category(genre).filter(filter_obj).page(page).__str__()
                correct_url = f"https://rezka.ag/animation/{genre}/page/{page}/?filter={filter_obj}"
                self.assertEqual(correct_url, response)

                response = self.movie.selected_category(genre).filter(filter_obj).page(str(page)).__str__()
                self.assertEqual(correct_url, response)

    def test_negative_page(self):
        self.enter_bad_args(
            fun=self.movie.page,
            data=(0, -5, 4.458, -5.1, 12 - 10j, [1, 2, 3], (1, 2, 3), {1, 2, 3}, {"a": 1, "b": 2, "c": 3},
                  None, True, False, GenreAnimation, range(10), "hello world", b"hello world"))

    def test_positive_find_best(self):
        self.assertEqual("https://rezka.ag/animation/best/2021/",
                         self.movie.find_best(year=2021).__str__())
        self.assertEqual("https://rezka.ag/animation/best/fiction/",
                         self.movie.find_best(genre=GenreAnimation.FICTION).__str__())
        for genre in self.get_genre():
            year = randint(1911, 2023)
            response = self.movie.find_best(genre=genre, year=year).__str__()
            correct_url = f"https://rezka.ag/animation/best/{genre}/{year}/"
            self.assertEqual(correct_url, response)

    def test_negative_find_best(self):
        lst_year = (1895, 0, -8, 14, 4.48, -5.12, 12 - 10j, [1, 2, 3], (12, 2, 3), {1, 2, 3}, {"a": 41, "b": 2, "c": 3},
                    True, False, GenreAnimation, range(10), "hello world", b"hello world")
        lst_genre = (0, -8, 14, 4.48, -5.1, 12 - 10j, [1, 82, 3], (1, 2, 63), {1, 2, 43}, {"a": 1, "b": 2, "c": 3},
                     True, False, GenreAnimation, range(10), b"hello world")

        for y in lst_year:
            for g in lst_genre:
                with self.assertRaises(AttributeError, msg=(y, g)):
                    self.movie.find_best(year=y, genre=g)  # noqa

    def test_positive_find_best_page(self):
        self.assertEqual("https://rezka.ag/animation/best/2021/page/8/",
                         self.movie.find_best(year=2021).page(8).__str__())
        self.assertEqual("https://rezka.ag/animation/best/fiction/page/8/",
                         self.movie.find_best(genre=GenreAnimation.FICTION).page(8).__str__())
        for genre in self.get_genre():
            year = randint(1895, 2114)
            page = randint(1, 9)
            response = self.movie.find_best(genre=genre, year=year).page(page).__str__()
            correct_url = f"https://rezka.ag/animation/best/{genre}/{year}/page/{page}/"
            self.assertEqual(correct_url, response)

    @requests_mock.Mocker()
    def test_positive_get(self, m):
        with open("tests/mock_html/animation_4.html", encoding="utf-8") as file:
            text = file.read()

        with open("tests/mock_html/reference_data.json", "r", encoding="utf-8") as json_file:
            reference_data = json.loads(json_file.read())

        correct_url = "https://rezka.ag/animation/page/4/"
        m.register_uri('GET', correct_url, text=text)
        site = self.movie.page(4)

        self.assertEqual(correct_url, site.__str__())

        response = []
        for item in site.get():
            if isinstance(item.trailer, Trailer):
                item.trailer = item.trailer.__dict__
            response.append(item.__dict__)

        self.assertListEqual(reference_data["animation"], response)

        site = self.movie.find_best(year=2018)
        m.register_uri('GET', site.__str__(), text="Success")
        self.assertEqual(0, len(site.get()))

    @requests_mock.Mocker()
    def test_negative_get(self, m):
        correct_url = "https://rezka.ag/animation/page/4/"
        site = self.movie.page(4)
        self.assertEqual(correct_url, site.__str__())

        m.register_uri('GET', correct_url, exc=requests.exceptions.ConnectionError)
        with self.assertRaises(requests.exceptions.ConnectionError):
            site.get()
