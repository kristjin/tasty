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

@app.route('/api/flavor/id/<int:fid>', methods=['POST'])
def add_combo(fid):
    """ Add a flavor combination """
    combo_id = request.args.get("id")
    combo_name = request.args.get("name")
    flavor = session.query(Flavor).get(fid)

    if combo_id and combo_name:
        data_name = session.query(Flavor).filter(Flavor.name == combo_name).all()
        data_id = session.query(Flavor).filter(Flavor.id == combo_id).all()
        if data_name != data_id:
            message = "Data ID and Name mismatch."
            return Response(json.dumps(message), 422, mimetype="application/json")
    elif not combo_id and not combo_name:
        message = "Must supply either ID or Name to be matched to ID in URL."
        return Response(json.dumps(message), 422, mimetype="application/json")
    elif combo_id:
        flavor.match(combo_id)
    else:
        combo = session.query(Flavor).filter(Flavor.name == combo_name).all()
        flavor.match(combo.id)
    session.add(flavor)
    session.commit()
    data = flavor.as_dictionary()
    headers = {"Location": "/api/flavor/id/{}".format(flavor.id)}

    return Response(json.dumps(data), 201,
                    headers=headers,
                    mimetype="application/json")




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
    print data
    # And create the header for the new ingredient
    headers = {"Location": "/api/flavor/id/{}".format(flavor.id)}
    # Return that with 201 created
    return Response(json.dumps(data), 201,
                    headers=headers,
                    mimetype="application/json")
