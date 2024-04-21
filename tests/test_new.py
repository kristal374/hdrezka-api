import re
from random import randint
from unittest import TestCase

import requests
import requests_mock

from HDrezka.filters import Filters, ShowCategory
from HDrezka.site_navigation import New
from HDrezka.trailer import TrailerBuilder
from tests.mock_html.html_construcror import generate_fake_html


class TestNew(TestCase):
    def setUp(self) -> None:
        self.movie = New()

    def tearDown(self) -> None:
        del self.movie

    @staticmethod
    def get_filters():
        filters_list = [i for i in dir(Filters) if not re.search(r"__.*__", i)]
        for name in filters_list:
            filter_obj = getattr(Filters, name)
            yield filter_obj

    @staticmethod
    def get_category():
        category_list = [i for i in dir(ShowCategory) if not re.search(r"__.*__", i)]
        for name in category_list:
            category_obj = getattr(ShowCategory, name)
            yield category_obj

    def enter_bad_args(self, fun, data):
        for element in data:
            with self.assertRaises(AttributeError, msg=element):
                fun(element)

    def test_positive_filter(self):
        self.assertEqual("https://rezka.ag/new/", str(self.movie.filter(None)))
        self.assertEqual("https://rezka.ag/new/?filter=soon", str(self.movie.filter(Filters.SOON)))
        for filter_obj in self.get_filters():
            response = str(self.movie.filter(filter_obj))
            custom_filter = f"?filter={filter_obj.value}" if filter_obj.value != "last" else ""
            correct_url = f"https://rezka.ag/new/{custom_filter}"
            self.assertEqual(correct_url, response)

    def test_negative_filter(self):
        self.enter_bad_args(
            fun=self.movie.filter,
            data=(0, 6, -4, 4.48, -58.1, 13 - 12j,
                  [1, 2, 8], (1, 2, 3), {1, 2, 3},
                  {"a": 1, "b": 14, "c": 3}, True, False,
                  Filters, range(10), b"hello world"))

    def test_positive_show_only(self):
        self.assertEqual("https://rezka.ag/new/", str(self.movie.show_only()))
        for category_obj in self.get_category():
            response = str(self.movie.show_only(category_obj))
            if category_obj.value != 0:
                correct_url = f"https://rezka.ag/new/?filter=last&genre={category_obj.value}"
            else:
                correct_url = "https://rezka.ag/new/"
            self.assertEqual(correct_url, response)

    def test_negative_show_only(self):
        self.enter_bad_args(
            fun=self.movie.show_only,
            data=(-5, "1", 4.458, -5.1, 12 - 10j, [1, 2, 3], (1, 2, 3), {1, 2, 3}, {"a": 1, "b": 2, "c": 3},
                  True, False, Filters, range(10), "hello world", b"hello world"))

    def test_filter_show_only(self):
        for filter_obj in self.get_filters():
            for category_obj in self.get_category():
                response = str(self.movie.filter(filter_obj).show_only(category_obj))

                if category_obj.value != 0:
                    correct_url = f"https://rezka.ag/new/?filter={filter_obj.value}&genre={category_obj.value}"
                else:
                    custom_filter = f"?filter={filter_obj.value}" if filter_obj.value != "last" else ""
                    correct_url = f"https://rezka.ag/new/{custom_filter}"
                self.assertEqual(correct_url, response)

    def test_positive_page(self):
        for filter_obj in self.get_filters():
            page = randint(2, 99)
            response = str(self.movie.filter(filter_obj).page(page))
            custom_filter = f"?filter={filter_obj.value}" if filter_obj.value != "last" else ""
            correct_url = f"https://rezka.ag/new/page/{page}/{custom_filter}"
            self.assertEqual(correct_url, response)

            response = str(self.movie.filter(filter_obj).page(str(page)))
            self.assertEqual(correct_url, response)

    def test_negative_page(self):
        self.enter_bad_args(
            fun=self.movie.page,
            data=(0, -4, 4.458, -5.2, 12 - 10j, [1, 2, 3], (1, 2, 3), {1, 2, 3}, {"a": 1, "b": 2, "c": 3},
                  None, True, False, Filters, range(10), "hello world", b"hello world"))

    @requests_mock.Mocker()
    def test_positive_get(self, m):
        reference_data, text = generate_fake_html("new")

        correct_url = "https://rezka.ag/new/page/5/"
        m.register_uri('GET', correct_url, text=text)
        site = self.movie.page(5)

        self.assertEqual(correct_url, str(site))

        response = []
        for item in site.get():
            if isinstance(item.trailer, TrailerBuilder):
                item.trailer = item.trailer.__dict__
            response.append(item.__dict__)
        self.assertListEqual(reference_data, response)

    @requests_mock.Mocker()
    def test_negative_get(self, m):
        correct_url = "https://rezka.ag/new/page/5/"
        site = self.movie.page(5)
        self.assertEqual(correct_url, str(site))

        m.register_uri('GET', correct_url, exc=requests.exceptions.ConnectionError)
        with self.assertRaises(requests.exceptions.ConnectionError):
            site.get()
