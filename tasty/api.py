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

    # Obtain any supplied ID
    combo_id = int(request.args.get("id"))
    # Obtain any supplied name
    combo_name = request.args.get("name")
    # Obtain the parent flavor ID from the URI
    flavor = session.query(Flavor).get(fid)

    # If receiving both an ID and a name, validate they ref same ingredient or error
    if combo_id and combo_name:
        data_name = session.query(Flavor).filter(Flavor.name == combo_name).all()
        data_id = session.query(Flavor).filter(Flavor.id == combo_id).all()
        if data_name != data_id:
            message = "UNPROCESSABLE ENTITY: Data ID and Name mismatch."
            return Response(json.dumps(message), 422, mimetype="application/json")

    # If neither an ID or name is received, error
    elif not combo_id and not combo_name:
        message = "UNPROCESSABLE ENTITY: Must supply either ID or Name to be matched to ID in URL."
        return Response(json.dumps(message), 422, mimetype="application/json")

    # If only an ID is received, process
    elif combo_id:
        combo = session.query(Flavor).get(combo_id)
        flavor.match(combo)

    # If only a name is received, process
    else:
        combo = session.query(Flavor).filter(Flavor.name == combo_name).first()
        flavor.match(combo)

    # Save and commit the data
    session.add(flavor)
    session.commit()

    # Obtain the flavor data as a dictionary
    data = flavor.as_dictionary()

    # Set the header to the page for the parent ingredient
    headers = {"Location": "/flavor/{}".format(flavor.id)}

    # Return the response
    return Response(json.dumps(data), 201,
                    headers=headers,
                    mimetype="application/json")


@app.route('/api/flavor', methods=['POST'])
def add_flavor():
    """ Add a flavor to the DB """
    # Get creator user name passed with request as argument
    creator = request.args.get("creator")
    # Get flavor name passed as argument
    flavor_name = request.args.get("flavor")

    # Try to get the flavor being added from the DB
    data = session.query(Flavor).filter(Flavor.name == flavor_name).all()
    # If you got the item back from the DB, issue a warning
    if data:
        message = {"message": "Entry matching request already exists in database."}
        return Response(json.dumps(message), 422, mimetype="application/json")
    # Otherwise create the flavor
    flavor = Flavor()
    flavor.name = flavor_name
    flavor.creator = creator
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
