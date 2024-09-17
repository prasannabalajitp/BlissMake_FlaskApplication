from flask import Flask
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from AppConstants.Constants import Constants
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv(Constants.SECRET_KEY)

mongo_uri = os.getenv(Constants.MONGO_URI)

# Initialize PyMongo
mongo = PyMongo(app, uri=mongo_uri)


# Import and register the blueprint
from blissmake import blissmake
app.register_blueprint(blissmake)

if __name__ == Constants.MAIN:
    app.run(debug=True)