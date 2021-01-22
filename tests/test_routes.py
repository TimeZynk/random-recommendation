from unittest import mock, TestCase

mock_return = [
    [
        "5f3e25255b248f4528668396",
        "5f3e1fc8d048e76cbdb4e609",
        "5f3e20ba5b248f452864aec3",
        "5f3e24075b248f452866024f",
        "5f3f78935b248f452897d97c",
        "5f3fd514d048e76cbd01bd38",
        "5f4299e25b248f4528f7e44f",
        "5f4ab2979d8ae849a774201b",
        "5f5a77588fc50c43b1e1b5fc",
        "5f7c6e2ddf038d003f9b4e2d",
    ]
]


class TestRoutes(TestCase):
    def test_recommend_and_return(client, backend_auth):
        # with mock.patch('src.machine_learning_recommendation.recommendation.routes.recommend_and_return.machine_learning_models.recommend', return_value=mock_return):

        pass

    # create a unique username
    # make the signup api call
    # make the oauth2 api call to obtain the token
    # use the token as header to authenticate request.