__author__ = 'kristjin@github'

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

# Anything that will use the app must be
# imported after its creation
from . import views  # Same as import tasty.views
from . import filters  # Same as import tasty.filters
