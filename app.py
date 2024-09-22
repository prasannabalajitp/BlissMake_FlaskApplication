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

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True


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