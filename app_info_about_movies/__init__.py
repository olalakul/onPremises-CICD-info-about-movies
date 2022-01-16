from flask import Flask

app = Flask(__name__)

# necessary for running the flask app, but gives an error with pyflakes
from app_info_about_movies import routes
assert routes
