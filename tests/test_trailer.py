import json
from unittest import TestCase

import requests_mock

from HDrezka.exceptions import AJAXFail, ServiceUnavailable
from HDrezka.trailer import TrailerBuilder
from tests.mock_html.html_construcror import generate_trailer_info


class TestTrailerBuilder(TestCase):
    url = 'https://rezka.ag/engine/ajax/gettrailervideo.php'

    @requests_mock.Mocker()
    def test_positive_extract_content(self, m):
        reference_data = generate_trailer_info()
        response_dict = {f'id={trailer_obj["id"]}': server_response for trailer_obj, server_response in reference_data}

        m.post(self.url, json=lambda request_obj, content: response_dict.get(request_obj.text, ""))

        for trailer_obj, _ in reference_data:
            trailer = TrailerBuilder(trailer_obj["id"]).extract_content()
            self.assertEqual(trailer_obj, json.loads(json.dumps(trailer, default=lambda x: x.__dict__)))

    @requests_mock.Mocker()
    def test_negative_extract_content(self, m):
        response_dict = {"id=768": {'success': False, 'message': 'Возникла неизвестная ошибка'}}
        m.post(self.url, json=lambda request_obj, content: response_dict.get(request_obj.text, ""))

        with self.assertRaises(AJAXFail):
            TrailerBuilder(768).extract_content()

    @requests_mock.Mocker()
    def test_positive_get_trailer(self, m):
        correct_response = {'success': True, 'message': 'Возникла неизвестная ошибка'}
        response_dict = {"id=29584": correct_response}
        m.post(self.url, json=lambda request_obj, content: response_dict.get(request_obj.text, ""))

        response = TrailerBuilder(29584)._get_trailer()
        self.assertEqual(response, correct_response)

    @requests_mock.Mocker()
    def test_negative_get_trailer(self, m):
        m.post(self.url, status_code=504)

        with self.assertRaises(ServiceUnavailable):
            TrailerBuilder(30073)._get_trailer()
