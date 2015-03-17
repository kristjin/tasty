__author__ = 'kristjin@github'
import os.path
import json

from flask import request, Response, url_for, send_from_directory
from werkzeug.utils import secure_filename
from jsonschema import validate, ValidationError

from models import Flavor
import decorators
from tasty import app
from database import session
from utils import upload_path


@app.route('/api/flavor', methods=['POST'])
def add_flavor():
    """ Add a flavor to the DB """
    # Get name passed with request as argument
    name = request.args.get("name")
    # Try to get the flavor being added from the DB
    data = session.query(Flavor).filter(Flavor.name == name).all()
    # If you got the item back from the DB, issue a warning
    if data:
        message = {"message": "Entry matching request already exists in database."}
        return Response(json.dumps(message), 422, mimetype="application/json")
    # Otherwise create the flavor
    flavor = Flavor()
    flavor.name = name
    # Add it to the DB
    session.add(flavor)
    session.commit()
    # Obtain the dict info for the created object
    data = flavor.as_dictionary()
    # And create the header for the new ingredient
    headers = {"Location": "/api/flavor/id/{}".format(flavor.id)}
    # Return that with 201 created
    return Response(json.dumps(data), 201,
                    headers=headers,
                    mimetype="application/json")
