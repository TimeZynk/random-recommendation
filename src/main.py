from flask import Flask
from flask_restful import Api
from recommendation import recommendation
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.register_blueprint(recommendation)
api = Api(app)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
