import unittest
from unittest import mock, TestCase
import sys

sys.path.append("/home/chuck/folder/recommend/recommend-api/src/")
from machine_learning_recommendation.recommendation.utils import (
    get_arg_or_default,
    get_error_return,
    concoct,
    machine_learning_query,
    lists_union,
)
import flask
import json
from datetime import datetime


file_path = "machine_learning_recommendation.recommendation.utils"


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

    def test_concoct(self):
        ml = [["u1", "u2", "u3"], ["u2", "u3", "u4"]]
        rl = [["u1", "u2", "u3", "u4", "u5"], ["u1", "u2", "u3", "u4", "u5"]]
        # ml part the order is reserved.
        self.assertEqual(concoct(ml, rl, 3), ml)
        result = concoct(ml, rl, 5)
        # first three order maintained, last two orders can be messed.
        self.assertEqual([result[0][:3], result[1][:3]], ml)
        self.assertCountEqual(result[0][3:], ["u4", "u5"])
        self.assertCountEqual(result[1][3:], ["u1", "u5"])

        ml_empty = [[], []]
        # same elements, messed orders in both lists.
        self.assertCountEqual(concoct(ml_empty, rl, 5)[0], rl[0])
        self.assertCountEqual(concoct(ml_empty, rl, 5)[1], rl[1])

        # If num_candidates greater than size of recommend, everything kept.
        self.assertCountEqual(concoct(ml, rl, 10)[0], rl[0])
        self.assertCountEqual(concoct(ml, rl, 9)[1], rl[1])

    def test_machine_learning_query(self):
        qssec = [
            [
                datetime.strftime(datetime(2020, 12, 24), "%Y-%m-%dT%H:%M:%S.%f"),
                datetime.strftime(datetime(2020, 12, 25), "%Y-%m-%dT%H:%M:%S.%f"),
                datetime(2020, 12, 26),
            ],
            [
                datetime.strftime(datetime(2020, 12, 22), "%Y-%m-%dT%H:%M:%S.%f"),
                datetime.strftime(datetime(2020, 12, 23), "%Y-%m-%dT%H:%M:%S.%f"),
                datetime(2020, 12, 24),
            ],
            [
                datetime.strftime(datetime(2020, 11, 22), "%Y-%m-%dT%H:%M:%S.%f"),
                datetime.strftime(datetime(2020, 11, 23), "%Y-%m-%dT%H:%M:%S.%f"),
                datetime(2020, 11, 24),
            ],
        ]

        query_shifts = ["s1", "s2", "s3"]
        with mock.patch(
            file_path + ".machine_learning_models.recommend",
            return_value=["user"],
        ):
            # Only wanna test if ml_on switched off, if it just returns
            # list of lists.
            result = machine_learning_query(False, qssec, query_shifts, 10)
            self.assertNotEqual(result, [["user"], ["user"], ["user"]])
            self.assertEqual(result, [[], [], []])

            # or if ml returns empty lists, should return empty lists too.
        with mock.patch(
            file_path + ".machine_learning_models.recommend",
            return_value=[],
        ):
            result = machine_learning_query(True, qssec, query_shifts, 10)
            self.assertEqual(result, [[], [], []])

        # if different id are returned.
        with mock.patch(
            file_path + ".machine_learning_models.recommend",
            side_effect=iter([["u1", "u2"], ["u3", "u4"], ["u5", "u6"]]),
        ):
            result = machine_learning_query(True, qssec, query_shifts, 10)
            self.assertEqual(result, [["u1", "u2"], ["u3", "u4"], ["u5", "u6"]])

    def test_list_union(self):
        l1 = [{1, 2}]
        l2 = [{2, 3}]
        l3 = [{3, 4}]
        l4 = [{4, 5}]
        # result = lists_union(l1, l2, l3, l4)
        # self.assertEqual(result, [{1, 2, 3, 4, 5}])

        l5 = [{5, 6}]
        result = lists_union(l1, l2, l3, l4, l5)
        self.assertEqual(result, [{1, 2, 3, 4, 5, 6}])


if __name__ == "__main__":
    unittest.main()
