import unittest
from unittest import mock, TestCase
import sys

sys.path.append("/home/chuck/folder/recommend/recommend-api/src/")
from datetime import datetime
from machine_learning_recommendation.recommendation.filters import (
    fetch_busy_users,
    fetch_unavailable_users,
)
import json

file_path = "machine_learning_recommendation.recommendation.filters"


class TestFilters(TestCase):
    def setUp(self):
        self.qsse = [
            [datetime.now(), datetime.now()],
            [datetime.now(), datetime.now()],
            [datetime.now(), datetime.now()],
        ]
        self.url = "tzbackend"
        self.headers = {"headers": "headers"}

    @mock.patch(file_path + ".requests.request")
    def test_fetch_busy_users(self, mock_request):

        side_effect = iter(
            [
                [
                    {"booked-users": ["u11", "u12", "u13", "uc1"], "booked": True},
                    {"booked-users": ["u21", "u22", "u23", "uc1"], "booked": True},
                ],
                [
                    {"booked-users": ["u31", "u32", "u33", "uc2"], "booked": True},
                    {"booked-users": ["u41", "u42", "u43", "uc2"], "booked": True},
                ],
                [
                    {"booked-users": ["u51", "u52", "u53"], "booked": True},
                    {"booked-users": ["u61", "u62", "u63"], "booked": True},
                ],
            ]
        )
        # Note that the expected returns are sets, since later on it needs to union with other sets in get_excluded_users.
        expected = [
            {"u11", "u12", "u13", "u21", "u22", "u23", "uc1"},
            {"u31", "u32", "u33", "u41", "u42", "u43", "uc2"},
            {"u51", "u52", "u53", "u61", "u62", "u63"},
        ]
        mock_request.text = "whatever"
        with mock.patch(file_path + ".json.loads", side_effect=side_effect):
            result = fetch_busy_users(self.qsse, self.url, self.headers)
            # sets are orderless.
            self.assertEqual(result, expected)

    @mock.patch(file_path + ".requests.request")
    def test_fetch_unavailable_users(self, mock_request):
        side_effect = iter(
            [
                [
                    {"user-id": "u1"},
                    {"user-id": "u2"},
                ],
                [
                    {"user-id": "u3"},
                    {"user-id": "u4"},
                ],
                [
                    {"user-id": "u5"},
                    {"user-id": "u6"},
                ],
            ]
        )
        expected = [
            {"u1", "u2"},
            {"u3", "u4"},
            {"u5", "u6"},
        ]
        mock_request.text = "whatever"
        with mock.patch(file_path + ".json.loads", side_effect=side_effect):
            result = fetch_unavailable_users(self.qsse, self.url, self.headers)
            # sets are orderless.
            self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()