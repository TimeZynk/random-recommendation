from flask_restful import Api
from machine_learning_recommendation import create_app
from machine_learning_recommendation.setup_logging import setup_logging

# from os import path
# import logging.config


app = create_app()
api = Api(app)

if __name__ == "__main__":
    # Configuring logging from file also works.
    # log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logger.conf')
    # logging.config.fileConfig(log_file_path)
    setup_logging("DEBUG")
    app.run(host="0.0.0.0")
