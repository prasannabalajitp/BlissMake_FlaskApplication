from flask import Flask
from flask_mail import Mail
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from AppConstants.Constants import Constants
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv(Constants.SECRET_KEY)

app.config[Constants.MAIL_SERVER] = os.getenv(Constants.MAIL_SERVER)
app.config[Constants.MAIL_PORT] = os.getenv(Constants.MAIL_PORT)
app.config[Constants.MAIL_USERNAME] = os.getenv(Constants.MAIL_USERNAME)
app.config[Constants.MAIL_PWD] = os.getenv(Constants.MAIL_PWD)
app.config[Constants.MAIL_TLS] = True


mongo_uri = os.getenv(Constants.MONGO_URI)

# Initialize PyMongo
mongo = PyMongo(app, uri=mongo_uri)

mail = Mail(app)

# Import and register the blueprint
from blissmake import blissmake
from admin import admin
app.register_blueprint(blissmake)
app.register_blueprint(admin)

if __name__ == Constants.MAIN:
    app.run(debug=True)