import unittest
from unittest import mock, TestCase
import sys

sys.path.append("/home/chuck/folder/recommend/recommend-api/src/")
from machine_learning_recommendation.recommendation.routes import recommend_and_return
from machine_learning_recommendation.recommendation.utils import object_and_200
import flask
from datetime import datetime
import json


file_path = "machine_learning_recommendation.recommendation.routes"


class TestRoutes(TestCase):
    def setUp(self):
        date_list = [
            [datetime(2020, 12, 24), datetime(2020, 12, 25), datetime(2020, 12, 26)],
            [datetime(2020, 12, 22), datetime(2020, 12, 23), datetime(2020, 12, 24)],
        ]
        self.func_mock1 = mock.patch(
            file_path + ".fetch_shifts_start_end_created",
            return_value=date_list,
        )
        self.func_mock1.start()
        self.func_mock2 = mock.patch(
            file_path + ".machine_learning_query",
            return_value=[["user1"], ["user2"]],
        )
        self.func_mock2.start()
        self.func_mock3 = mock.patch(
            file_path + ".get_excluded_users",
            return_value=[["user3", "user4"], ["user1", "user4"]],
        )
        self.func_mock3.start()
        self.func_mock4 = mock.patch(
            file_path + ".get_expanded_user_ids",
            return_value=[
                [
                    "user1",
                    "user2",
                    "user3",
                    "user4",
                ],
                [
                    "user1",
                    "user2",
                    "user3",
                    "user4",
                ],
            ],
        )
        self.func_mock4.start()
        self.func_mock5 = mock.patch(
            file_path + ".os.getenv",
            return_value="http://000.000.0.00:0000/api",
        )
        self.func_mock5.start()

    def test_recommend_and_return(self):
        app = flask.Flask(__name__)
        with app.test_client() as client:
            client.get(
                "/api/ml/v1/recommendation?user-id=mock_user_id&ids=shift1,shift2&limit=10&ml-recommend=1&ml_num_candidates=10"
            )
            flask.request.headers = mock.MagicMock()
            flask.request.headers.__getitem__.return_value = "auth"

            return_to_test = recommend_and_return()
            # The return is converted into a string in object_or_200
            # Need to revert that.
            result_list = eval(return_to_test[0])

            self.assertEqual(return_to_test[1], 200)
            self.assertNotEqual(return_to_test[1], 400)
            self.assertNotIn("user3", result_list[0])
            self.assertNotIn("user4", result_list[0])
            self.assertNotIn("user1", result_list[1])
            self.assertNotIn("user4", result_list[1])
            # Machine learning recommendations kept to the first.
            self.assertEqual("user1", result_list[0][0])
            self.assertEqual("user2", result_list[1][0])

    # create a unique username
    # make the signup api call
    # make the oauth2 api call to obtain the token
    # use the token as header to authenticate request.
    def tearDown(self):
        self.func_mock1.stop()
        self.func_mock2.stop()
        self.func_mock3.stop()
        self.func_mock4.stop()
        self.func_mock5.stop()


if __name__ == "__main__":
    unittest.main()