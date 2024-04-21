import json
from unittest import TestCase

import requests_mock

from HDrezka.exceptions import EmptyPage
from HDrezka.movie_posters import PosterBuilder
from HDrezka.movie_collections import MovieCollectionBuilder
from tests.mock_html.html_construcror import generate_fake_html


class TestPosterBuilder(TestCase):
    def test_positive_extract_content(self):
        reference_data, text = generate_fake_html("films")
        films_list = PosterBuilder(text).extract_content()

        extracted_data = json.loads(json.dumps(films_list, default=lambda x: x.__dict__))

        self.assertListEqual(reference_data, extracted_data)

    def test_negative_extract_content(self):
        with self.assertRaises(EmptyPage):
            PosterBuilder("").extract_content()


class TestMovieCollectionsBuilder(TestCase):
    def test_positive_extract_content(self):
        reference_data, text = generate_fake_html("collections")
        collections_list = MovieCollectionBuilder(text).extract_content()

        extracted_data = json.loads(json.dumps(collections_list, default=lambda x: x.__dict__))

        self.assertListEqual(reference_data, extracted_data)

    def test_negative_extract_content(self):
        with self.assertRaises(EmptyPage):
            MovieCollectionBuilder("").extract_content()


class TestPoster(TestCase):
    @requests_mock.Mocker()
    def test_get(self, m):
        _, text = generate_fake_html("cartoons")
        cartoons_list = PosterBuilder(text).extract_content()
        for poster in cartoons_list:
            m.get(poster.url, text=poster.title)
            with self.assertRaises(AttributeError):
                poster.get()


class TestMovieCollections(TestCase):
    @requests_mock.Mocker()
    def test_get(self, m):
        _, text = generate_fake_html("collections")
        collections_list = MovieCollectionBuilder(text).extract_content()
        for collection in collections_list:
            m.get(collection.url, text=collection.title)
            with self.assertRaises(EmptyPage):
                collection.get()
