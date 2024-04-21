import re
from random import randint
from unittest import TestCase

import requests
import requests_mock

from HDrezka.filters import GenreSeries, Filters
from HDrezka.site_navigation import Series
from HDrezka.trailer import TrailerBuilder
from tests.mock_html.html_construcror import generate_fake_html


class TestSeries(TestCase):
    def setUp(self) -> None:
        self.movie = Series()
        self.data = [0, 8, -14, 45.48, -5.1, 12 - 10j, [1, 2, 3], (1, 2, 3), {1, 2, 3},
                     {"a": 1, "b": 2, "c": 3}, True, False, GenreSeries, range(10), b"hello world"]

    def tearDown(self) -> None:
        del self.movie

    @staticmethod
    def get_genre():
        genre_list = [i for i in dir(GenreSeries) if not re.search(r"__.*__", i)]
        for name in genre_list:
            genre = getattr(GenreSeries, name)
            yield genre.value

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
        self.assertEqual("https://rezka.ag/series/", str(self.movie.selected_category(None)))
        for genre in self.get_genre():
            response = str(self.movie.selected_category(genre))
            correct_url = f"https://rezka.ag/series/{genre}/"
            self.assertEqual(correct_url, response)

    def test_negative_selected_category(self):
        self.enter_bad_args(
            fun=self.movie.selected_category,
            data=self.data
        )

    def test_positive_filter(self):
        self.assertEqual("https://rezka.ag/series/", str(self.movie.filter(None)))
        for genre in self.get_genre():
            for filter_obj in self.get_filters():
                response = str(self.movie.selected_category(genre).filter(filter_obj))
                custom_filter = f"?filter={filter_obj.value}" if filter_obj.value != "last" else ""
                correct_url = f"https://rezka.ag/series/{genre}/{custom_filter}"
                self.assertEqual(correct_url, response)

    def test_negative_filter(self):
        self.enter_bad_args(
            fun=self.movie.filter,
            data=self.data
        )

    def test_positive_page(self):
        for genre in self.get_genre():
            for filter_obj in self.get_filters():
                page = randint(1, 99)
                response = str(self.movie.selected_category(genre).filter(filter_obj).page(page))
                page_path = f'/page/{page}' if page > 1 else ''
                custom_filter = f"?filter={filter_obj.value}" if filter_obj.value != "last" else ""
                correct_url = f"https://rezka.ag/series/{genre}{page_path}/{custom_filter}"
                self.assertEqual(correct_url, response)

                response = str(self.movie.selected_category(genre).filter(filter_obj).page(str(page)))
                self.assertEqual(correct_url, response)

    def test_negative_page(self):
        data = self.data.copy()
        data.append(None)
        data.append("hello world")
        data.remove(8)
        self.enter_bad_args(
            fun=self.movie.page,
            data=data
        )

    def test_positive_find_best(self):
        self.assertEqual("https://rezka.ag/series/best/2021/",
                         str(self.movie.find_best(year=2021)))
        self.assertEqual("https://rezka.ag/series/best/fiction/",
                         str(self.movie.find_best(genre=GenreSeries.FICTION)))
        for genre in self.get_genre():
            year = randint(1911, 2023)
            response = str(self.movie.find_best(genre=genre, year=year))
            correct_url = f"https://rezka.ag/series/best/{genre}/{year}/"
            self.assertEqual(correct_url, response)

    def test_negative_find_best(self):
        lst_genre = self.data
        lst_year = self.data.copy()
        lst_year.append(1895)
        lst_year.append("Hello world!")
        for y in lst_year:
            for g in lst_genre:
                with self.assertRaises(AttributeError, msg=(y, g)):
                    self.movie.find_best(year=y, genre=g)  # noqa

    def test_positive_find_best_page(self):
        self.assertEqual("https://rezka.ag/series/best/2021/page/8/",
                         str(self.movie.find_best(year=2021).page(8)))
        self.assertEqual("https://rezka.ag/series/best/fiction/page/8/",
                         str(self.movie.find_best(genre=GenreSeries.FICTION).page(8)))
        for genre in self.get_genre():  # noqa
            year = randint(1895, 2100)
            page = randint(2, 9)
            response = str(self.movie.find_best(genre=genre, year=year).page(page))
            correct_url = f"https://rezka.ag/series/best/{genre}/{year}/page/{page}/"
            self.assertEqual(correct_url, response)

    @requests_mock.Mocker()
    def test_positive_get(self, m):
        reference_data, text = generate_fake_html("series")

        correct_url = "https://rezka.ag/series/"
        m.register_uri('GET', correct_url, text=text)
        site = self.movie

        self.assertEqual(correct_url, str(site))

        response = []
        for item in site.get():
            if isinstance(item.trailer, TrailerBuilder):
                item.trailer = item.trailer.__dict__
            response.append(item.__dict__)

        self.assertListEqual(reference_data, response)

    @requests_mock.Mocker()
    def test_negative_get(self, m):
        correct_url = "https://rezka.ag/series/"
        site = self.movie
        self.assertEqual(correct_url, str(site))

        m.register_uri('GET', correct_url, exc=requests.exceptions.ConnectionError)
        with self.assertRaises(requests.exceptions.ConnectionError):
            site.get()
