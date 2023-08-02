from random import randint
import re
from unittest import TestCase, skip

from HDrezka.filters import Filters, ShowCategory
from HDrezka.parse_page import New


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
            with self.assertRaises(AttributeError):
                fun(element)
                print(element)

    def test_positive_filter(self):
        self.assertEqual("https://rezka.ag/new/", self.movie.filter(None).__str__())
        self.assertEqual("https://rezka.ag/new/?filter=last", self.movie.filter().__str__())
        for filter_obj in self.get_filters():
            response = self.movie.filter(filter_obj).__str__()
            correct_url = f"https://rezka.ag/new/?filter={filter_obj}"
            self.assertEqual(correct_url, response)

    def test_negative_filter(self):
        self.enter_bad_args(
            fun=self.movie.filter,
            data=(0, 6, -4, 4.48, -58.1, 13 - 12j,
                  [1, 2, 8], (1, 2, 3), {1, 2, 3},
                  {"a": 1, "b": 14, "c": 3}, True, False,
                  Filters, range(10), b"hello world"))

    def test_positive_show_only(self):
        self.assertEqual("https://rezka.ag/new/", self.movie.show_only(None).__str__())
        self.assertEqual("https://rezka.ag/new/?filter=last", self.movie.show_only().__str__())
        for category_obj in self.get_category():
            response = self.movie.show_only(category_obj).__str__()
            if category_obj != 0:
                correct_url = f"https://rezka.ag/new/?filter=last&genre={category_obj}"
            else:
                correct_url = f"https://rezka.ag/new/?filter=last"
            self.assertEqual(correct_url, response)

    def test_negative_show_only(self):
        self.enter_bad_args(
            fun=self.movie.show_only,
            data=(-5, "1", 4.458, -5.1, 12 - 10j, [1, 2, 3], (1, 2, 3), {1, 2, 3}, {"a": 1, "b": 2, "c": 3},
                  True, False, Filters, range(10), "hello world", b"hello world"))

    def test_filter_show_only(self):
        for filter_obj in self.get_filters():
            for category_obj in self.get_category():
                response = self.movie.filter(filter_obj).show_only(category_obj).__str__()
                if category_obj != 0:
                    correct_url = f"https://rezka.ag/new/?filter={filter_obj}&genre={category_obj}"
                else:
                    correct_url = f"https://rezka.ag/new/?filter={filter_obj}"
                self.assertEqual(correct_url, response)

    def test_positive_page(self):
        for filter_obj in self.get_filters():
            page = randint(1, 99)
            response = self.movie.filter(filter_obj).page(page).__str__()
            correct_url = f"https://rezka.ag/new/page/{page}/?filter={filter_obj}"
            self.assertEqual(correct_url, response)

            response = self.movie.filter(filter_obj).page(str(page)).__str__()
            self.assertEqual(correct_url, response)

    def test_negative_page(self):
        self.enter_bad_args(
            fun=self.movie.page,
            data=(0, -4, 4.458, -5.2, 12 - 10j, [1, 2, 3], (1, 2, 3), {1, 2, 3}, {"a": 1, "b": 2, "c": 3},
                  None, True, False, Filters, range(10), "hello world", b"hello world"))

    @skip
    def test_get(self):
        self.fail()
