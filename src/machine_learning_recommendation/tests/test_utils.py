import unittest
from unittest import mock, TestCase
import sys

sys.path.append("/home/chuck/folder/recommend/recommend-api/src/")
from machine_learning_recommendation.recommendation.utils import (
    get_arg_or_default,
    get_error_return,
)
import flask
import json


class TestUtils(TestCase):
    def test_get_arg_or_default(self):
        app = flask.Flask(__name__)
        with app.test_request_context("/api/ml/v1/recommendation/?qp=Abc"):
            response = get_arg_or_default("qp", str, None)
            self.assertEqual(response, "Abc")
        with app.test_request_context("/api/ml/v1/recommendation/"):
            response = get_arg_or_default("qp", str, None)
            self.assertEqual(response, None)
        with app.test_request_context("/api/ml/v1/recommendation/?qp=123"):
            response = get_arg_or_default("qp", int, None)
            self.assertEqual(response, 123)
        with app.test_request_context("/api/ml/v1/recommendation/"):
            response = get_arg_or_default("qp", int, 10)
            self.assertEqual(response, 10)

    def test_get_error_return(self):
        with mock.patch(
            "machine_learning_recommendation.recommendation.utils.json.dumps",
            return_value="abc",
        ):
            expected = (
                "abc",
                400,
                {"ContentType": "application/json"},
            )
            self.assertEqual(get_error_return("whatever"), expected)


if __name__ == "__main__":
    unittest.main()