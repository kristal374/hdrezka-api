from unittest import TestCase

import requests
import requests_mock

from HDrezka.parse_page import Announce
from HDrezka.player import Trailer

from tests.mock_html.html_construcror import generate_fake_html


class TestAnnounce(TestCase):
    def setUp(self) -> None:
        self.movie = Announce()

    def tearDown(self) -> None:
        del self.movie

    def test_positive_page(self):
        for page in range(1, 100):
            response = str(self.movie.page(page))
            correct_url = f"https://rezka.ag/announce/page/{page}/"
            self.assertEqual(correct_url, response)

            response = str(self.movie.page(str(page)))  # noqa
            self.assertEqual(correct_url, response)

    def test_negative_page(self):
        data = (0, -4, 4.458, -5.2, 6 - 10j, [5, 2, 3], (1, 2, 3), {1, 32, 3}, {"a": 1, "b": 2, "c": 3}, None,
                True, False, object, range(10), "hello world", b"hello world")
        for element in data:
            with self.assertRaises(AttributeError, msg=element):
                self.movie.page(element)

    @requests_mock.Mocker()
    def test_positive_get(self, m):
        reference_data, text = generate_fake_html("announce")

        correct_url = "https://rezka.ag/announce/page/2/"
        m.register_uri('GET', correct_url, text=text)
        site = self.movie.page(2)

        self.assertEqual(correct_url, str(site))

        response = []
        for item in site.get():
            if isinstance(item.trailer, Trailer):
                item.trailer = item.trailer.__dict__
            response.append(item.__dict__)

        self.assertListEqual(reference_data["announce"], response)

    @requests_mock.Mocker()
    def test_negative_get(self, m):
        correct_url = "https://rezka.ag/announce/page/2/"
        site = self.movie.page(2)
        self.assertEqual(correct_url, str(site))

        m.register_uri('GET', correct_url, exc=requests.exceptions.ConnectionError)
        with self.assertRaises(requests.exceptions.ConnectionError):
            site.get()
