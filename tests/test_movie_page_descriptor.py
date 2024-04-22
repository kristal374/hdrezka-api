import json
from datetime import datetime, date
from unittest import TestCase

import requests_mock

from HDrezka.exceptions import EmptyPage
from HDrezka.movie_page_descriptor import MovieDetailsBuilder, InfoTableBuilder
from tests.mock_html.page_html_constructor import generate_info_table, read_reference_file


class TestInfoTable(TestCase):
    def test_extract_content(self):
        reference_data = generate_info_table()

        for item in reference_data:
            generated_info_table = InfoTableBuilder(item[1]).extract_content()
            reference_info_table = item[0]

            generated_info_table = json.loads(json.dumps(generated_info_table, default=lambda x: x.__dict__))

            rates = reference_info_table["rates"]
            hdrezka_item = list(filter(lambda x: x["name"] == "HDrezka", rates))
            hdrezka_index = rates.index(hdrezka_item[0]) if hdrezka_item else 3
            reference_info_table["rates"] = rates[0:hdrezka_index] + rates[hdrezka_index + 1:0]

            self.assertEqual(reference_info_table, generated_info_table)


class TestMovieDetailBuilder(TestCase):
    def test_extract_content(self):
        self.maxDiff = None
        reference_html = read_reference_file("reference_movie_html.json")
        reference_data = read_reference_file("reference_movie_data.json")

        for key in reference_html:
            raw_movie_info = MovieDetailsBuilder(reference_html[key]).extract_content()
            extracted_movie_info = json.loads(
                json.dumps(
                    raw_movie_info,
                    default=lambda x: x.__dict__ if not isinstance(x, (datetime, date)) else str(x)
                )
            )
            reference_movie_info = reference_data[key]

            self.assertEqual(extracted_movie_info, reference_movie_info)


class TestTopList(TestCase):
    @requests_mock.Mocker()
    def test_get(self, m):
        reference_data = generate_info_table()
        for item in reference_data:
            info_table = InfoTableBuilder(item[1]).extract_content()
            if info_table.on_the_lists is None:
                continue
            for lists in info_table.on_the_lists:
                m.get(lists.url, "")
                with self.assertRaises(EmptyPage) as cm:
                    lists.get()
                self.assertEqual(cm.exception.args[0], "No Posters were found on the page")


class TestCollectionBriefInfo(TestCase):
    @requests_mock.Mocker()
    def test_get(self, m):
        reference_data = generate_info_table()
        for item in reference_data:
            info_table = InfoTableBuilder(item[1]).extract_content()
            for collection in info_table.collections:
                m.get(collection.url, "")
                with self.assertRaises(EmptyPage) as cm:
                    collection.get()
                self.assertEqual(cm.exception.args[0], "No Posters were found on the page")


class TestPartContent(TestCase):
    @requests_mock.Mocker()
    def test_get(self, m):
        reference_html = read_reference_file("reference_movie_html.json")
        for key in list(reference_html.keys())[42:48]:
            movie_info = MovieDetailsBuilder(reference_html[key]).extract_content()
            if len(movie_info.franchise) == 0:
                continue
            for movie in movie_info.franchise:
                m.get(movie.url, "")
                with self.assertRaises(AttributeError) as cm:
                    movie.get()
                self.assertEqual(cm.exception.args[0], "'NoneType' object has no attribute 'get'")


class TestCustomString(TestCase):
    @requests_mock.Mocker()
    def test_get(self, m):
        reference_data = generate_info_table()
        for item in reference_data:
            info_table = InfoTableBuilder(item[1]).extract_content()
            custom_string_list = []
            if info_table.country is not None:
                custom_string_list.extend(info_table.country)
            if info_table.genre is not None:
                custom_string_list.extend(info_table.genre)
            if info_table.release is not None:
                custom_string_list.append(info_table.release)
            for string in custom_string_list:
                m.get(string.url, "")
                with self.assertRaises(EmptyPage) as cm:
                    string.get()
                self.assertEqual(cm.exception.args[0], "No Posters were found on the page")
