__author__ = 'kristjin@github'

# Import the OS stuffs
import os

# Import the Flask object
from flask import Flask

# Instantiate the Flask object as app
app = Flask(__name__)

# Load the configuration
# Check for an os.environment variable setting config path
# If none is found, use the default found in tasty.config.DevelopmentConfig
config_path = os.environ.get("CONFIG_PATH", "tasty.config.DevelopmentConfig")

# Configure the app using the object specified
app.config.from_object(config_path)

import api
import views
import filters

from database import Base, engine
Base.metadata.create_all(engine)

from . import login