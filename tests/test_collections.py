import json
import requests
import requests_mock

from unittest import TestCase

from HDrezka.parse_page import Collections


class TestCollections(TestCase):
    def setUp(self) -> None:
        self.movie = Collections()

    def tearDown(self) -> None:
        del self.movie

    def test_positive_page(self):
        for page in range(1, 100):
            response = self.movie.page(page).__str__()
            correct_url = f"https://rezka.ag/collections/page/{page}/"
            self.assertEqual(correct_url, response)

            response = self.movie.page(str(page)).__str__()  # noqa
            self.assertEqual(correct_url, response)

    def test_negative_page(self):
        data = (0, -1, 4.458, -5.2, 6 - 10j, [5, 2, 3], (1, 2, 6), {1, 32, 3}, {"a": 1, "b": 2, "c": 3}, None,
                True, False, object, range(10), "hello world", b"hello world")
        for element in data:
            with self.assertRaises(AttributeError, msg=element):
                self.movie.page(element)

    @requests_mock.Mocker()
    def test_positive_get(self, m):
        with open("mock_html/collections_3.html", encoding="utf-8") as file:
            text = file.read()

        with open("mock_html/reference_data.json", "r", encoding="utf-8") as json_file:
            reference_data = json.loads(json_file.read())

        correct_url = "https://rezka.ag/collections/page/3/"
        m.register_uri('GET', correct_url, text=text)
        site = self.movie.page(3)

        self.assertEqual(correct_url, site.__str__())

        response = [i.__dict__ for i in site.get() if i.__repr__()]
        self.assertListEqual(reference_data["collections"], response)

    @requests_mock.Mocker()
    def test_negative_get(self, m):
        correct_url = "https://rezka.ag/collections/page/3/"
        site = self.movie.page(3)
        self.assertEqual(correct_url, site.__str__())

        m.register_uri('GET', correct_url, exc=requests.exceptions.ConnectionError)
        with self.assertRaises(requests.exceptions.ConnectionError):
            site.get()
