from random import randint
import re
from unittest import TestCase, skip

from HDrezka.filters import GenreFilm, Filters
from HDrezka.parse_page import Films


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
            with self.assertRaises(AttributeError):
                fun(element)
                print(element)

    def test_positive_selected_category(self):
        self.assertEqual("https://rezka.ag/films/", self.movie.selected_category(None).__str__())
        for genre in self.get_genre():
            response = self.movie.selected_category(genre).__str__()
            correct_url = f"https://rezka.ag/films/{genre}/"
            self.assertEqual(correct_url, response)

    def test_negative_selected_category(self):
        self.enter_bad_args(
            fun=self.movie.selected_category,
            data=(0, 12, -8, 4.48, -5.1, 12 - 10j, [1, 2, 3], (1, 2, 3), {1, 2, 3},
                  {"a": 1, "b": 2, "c": 3}, True, False, GenreFilm, range(10), b"hello world"))

    def test_positive_filter(self):
        self.assertEqual("https://rezka.ag/films/", self.movie.filter(None).__str__())
        self.assertEqual("https://rezka.ag/films/?filter=last", self.movie.filter().__str__())
        for genre in self.get_genre():
            for filter_obj in self.get_filters():
                response = self.movie.selected_category(genre).filter(filter_obj).__str__()
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
                response = self.movie.selected_category(genre).filter(filter_obj).page(page).__str__()
                correct_url = f"https://rezka.ag/films/{genre}/page/{page}/?filter={filter_obj}"
                self.assertEqual(correct_url, response)

    def test_negative_page(self):
        self.enter_bad_args(
            fun=self.movie.page,
            data=(0, -8, 4.48, -5.1, 12 - 10j, [1, 2, 3], (1, 2, 3), {1, 2, 3}, {"a": 1, "b": 2, "c": 3},
                  None, True, False, GenreFilm, range(10), "hello world", b"hello world"))

    def test_positive_find_best(self):
        self.assertEqual("https://rezka.ag/films/best/2021/",
                         self.movie.find_best(year=2021).__str__())
        self.assertEqual("https://rezka.ag/films/best/fiction/",
                         self.movie.find_best(genre=GenreFilm.FICTION).__str__())
        for genre in self.get_genre():
            year = randint(1911, 2023)
            response = self.movie.find_best(genre=genre, year=year).__str__()
            correct_url = f"https://rezka.ag/films/best/{genre}/{year}/"
            self.assertEqual(correct_url, response)

    def test_negative_find_best(self):
        lst_year = (0, -8, 14, 4.48, -5.1, 12 - 10j, [1, 2, 3], (1, 2, 3), {1, 2, 3}, {"a": 1, "b": 2, "c": 3},
                    True, False, GenreFilm, range(10), "hello world", b"hello world")
        lst_genre = (0, -8, 14, 4.48, -5.1, 12 - 10j, [1, 2, 3], (1, 2, 3), {1, 2, 3}, {"a": 1, "b": 2, "c": 3},
                     True, False, GenreFilm, range(10), b"hello world")

        for y in lst_year:
            for g in lst_genre:
                with self.assertRaises(AttributeError):
                    self.movie.find_best(year=y, genre=g)  # noqa
                    print(y, g)

    def test_positive_find_best_page(self):
        self.assertEqual("https://rezka.ag/films/best/2021/page/8/",
                         self.movie.find_best(year=2021).page(8).__str__())
        self.assertEqual("https://rezka.ag/films/best/fiction/page/8/",
                         self.movie.find_best(genre=GenreFilm.FICTION).page(8).__str__())
        for genre in self.get_genre():
            year = randint(1911, 2023)
            page = randint(1, 100)
            response = self.movie.find_best(genre=genre, year=year).page(page).__str__()
            correct_url = f"https://rezka.ag/films/best/{genre}/{year}/page/{page}/"
            self.assertEqual(correct_url, response)

    @skip
    def test_get(self):
        self.fail()