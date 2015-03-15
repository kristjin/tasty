__author__ = 'kristjin@github'

# Import the Flask object
from flask import Flask
# Instantiate the Flask object as app
app = Flask(__name__)
# Anything that will use the app must be
# imported after its creation
from . import views  # Same as import tasty.views
from . import filters  # Same as import tasty.filters
