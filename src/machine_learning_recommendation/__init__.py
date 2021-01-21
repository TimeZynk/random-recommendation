from flask import Flask
from machine_learning_recommendation.config import Config
import os


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    from machine_learning_recommendation.recommendation.routes import recommendation

    app.register_blueprint(recommendation)

    return app