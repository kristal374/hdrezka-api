import json
import urllib.parse
from unittest import TestCase
from datetime import datetime

import bs4
import requests_mock

from HDrezka.comments import CommentsIterator
from HDrezka.exceptions import ServiceUnavailable
from tests.mock_html.html_construcror import generate_comments_tree, generate_navigation_string


def converter_into_json(value):
    if not isinstance(value, datetime):
        return value.__dict__
    return value.__str__()


class TestCommentsIterator(TestCase):
    def setUp(self) -> None:
        self.film_id = 43477
        self.data = {
            "news_id": self.film_id,
            "cstart": 1,
            "type": '0',
            "comment_id": '0',
            "skin": "hdrezka"
        }
        self.iterator = CommentsIterator(self.film_id)

    def tearDown(self) -> None:
        del self.data
        del self.iterator

    @requests_mock.Mocker()
    def test_positive_get_page(self, m):
        reference_data = generate_comments_tree()
        m.get('https://rezka.ag/ajax/get_comments/' + "?" + urllib.parse.urlencode(self.data),
              json=reference_data[0][1])
        server_response = self.iterator.get_page(1)
        extracted_comment = json.loads(json.dumps(server_response, default=converter_into_json))
        self.assertEqual(extracted_comment, reference_data[0][0])

    @requests_mock.Mocker()
    def test_negative_get_page(self, m):
        test_url = 'https://rezka.ag/ajax/get_comments/' + "?" + urllib.parse.urlencode(self.data)

        m.get(test_url.format(self.film_id), status_code=504, text="request fall")
        with self.assertRaises(ServiceUnavailable):
            self.iterator.get_page(1)

    def test_extract_last_page_number(self):
        for number_pages in range(50):
            page_list = list(range(1, number_pages + 1))
            for n in page_list:
                navigation = generate_navigation_string(self.film_id, n, 1, len(page_list))
                num_page = self.iterator._extract_last_page_number(navigation)
                self.assertEqual(num_page, len(page_list))

    @requests_mock.Mocker()
    def test_positive_get(self, m):
        reference_data = generate_comments_tree()
        m.get('https://rezka.ag/ajax/get_comments/' + "?" + urllib.parse.urlencode(self.data),
              json=reference_data[0][1])
        server_response = self.iterator._get(1)
        extracted_comment = json.loads(json.dumps(server_response, default=converter_into_json))
        self.assertEqual(extracted_comment, reference_data[0][1])

    @requests_mock.Mocker()
    def test_negative_get(self, m):
        test_url = 'https://rezka.ag/ajax/get_comments/' + "?" + urllib.parse.urlencode(self.data)

        m.get(test_url.format(self.film_id), status_code=504, text="request fall")
        with self.assertRaises(ServiceUnavailable):
            self.iterator._get(1)

    def test_positive_extreact_comments(self):
        reference_data = generate_comments_tree()
        comments = bs4.BeautifulSoup(reference_data[0][1]["comments"], "lxml")
        comment_list = self.iterator.extreact_comments(comments)
        extracted_comment = json.loads(json.dumps(comment_list, default=converter_into_json))
        self.assertEqual(extracted_comment, reference_data[0][0])

    @requests_mock.Mocker()
    def test_iteration(self, m):
        reference_data = generate_comments_tree()
        for page_number, server_response in enumerate(reference_data, 1):
            self.data["cstart"] = page_number
            m.get('https://rezka.ag/ajax/get_comments/' + "?" + urllib.parse.urlencode(self.data),
                  json=server_response[1])

        for page_number, comment in enumerate(self.iterator):
            for i, j in zip(comment, reference_data[page_number][0]):
                extracted_comment, reference_comment = json.loads(json.dumps(i, default=converter_into_json)), j
                self.assertEqual(extracted_comment, reference_comment)
