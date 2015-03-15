__author__ = 'kristjin@github'

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from tasty import app

# Create the engine conx to db at URI specified in config.py
engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
# Create a declarative base
Base = declarative_base()
# Start the session
Session = sessionmaker(bind=engine)
session = Session()