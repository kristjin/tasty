__author__ = 'kristjin@github'
import json
from flask import flash, render_template, request, redirect, url_for
from flask.ext.login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from tasty import app
from .database import session
from .models import Flavor, User


@app.route('/default_unmatch/<int:fid>')
@app.route('/default_unmatch/<int:fid>/<int:mid>', methods=['GET'])
@login_required
def unmatch_default_flavors(fid, mid=0):
    """ Unpair a flavor and a default matching flavor """
    if mid:
        flavor = get_flavor(fid)
        match = session.query(Flavor).get(mid)
        flavor.unmatch(match)
        session.add(flavor)
        session.commit()
    return render_template("match_default_flavors.html",
                           flavor=get_flavor(fid),
                           all_matches=get_matched_objects(fid),
                           unmatched_flavors=get_unmatched_objects(fid))


@app.route('/default_match/<int:fid>')
@app.route('/default_match/<int:fid>/<int:mid>', methods=['GET'])
@login_required
def match_default_flavors(fid, mid=0):
    """ Pair a flavor and a default matching flavor """
    if mid:
        flavor = get_flavor(fid)
        match = get_flavor(mid)
        flavor.match(match)
        session.add(flavor)
        session.commit()
    print "get matched objects is ".format(get_matched_objects(1))
    print "get unmatched objects is ".format(get_unmatched_objects(1))

    return render_template("match_default_flavors.html",
                           flavor=get_flavor(fid),
                           all_matches=get_matched_objects(fid),
                           unmatched_flavors=get_unmatched_objects(fid)
                           )


@app.route('/unmatch/<int:fid>')
@app.route('/unmatch/<int:fid>/<int:mid>', methods=['GET'])
@login_required
def unmatch_flavors(fid, mid=0):
    """ Unpair a user's flavor and a matching flavor """
    if mid:
        usr_m_dict = json.loads(current_user.matches)
        usr_m_dict[fid].remove(mid)
        current_user.matches = json.dumps(usr_m_dict)
        session.add(current_user)
        session.commit()

    return render_template("match_flavors.html",
                           flavor=get_flavor(fid),
                           all_matches=get_matched_objects(fid),
                           unmatched_flavors=get_unmatched_objects(fid)
                           )


@app.route('/match/<int:fid>')
@app.route('/match/<int:fid>/<int:mid>', methods=['GET'])
@login_required
def match_flavors(fid, mid=0):
    """ Pair a flavor and a user's matching flavor """

    if mid:
        usr_m_dict = json.loads(current_user.matches)
        if not usr_m_dict[fid]:
            usr_m_dict[fid] = {mid}
            current_user.matches = json.dumps(usr_m_dict)
            session.add(current_user)
            session.commit()
        else:
            if mid not in usr_m_dict[fid]:
                usr_m_dict[fid].add(mid)
                current_user.matches = json.dumps(usr_m_dict)
                session.add(current_user)
                session.commit()

    return render_template("match_flavors.html",
                           flavor=get_flavor(fid),
                           all_matches=get_matched_objects(fid),
                           unmatched_flavors=get_unmatched_objects(fid)
                           )


@app.route("/flavor/<int:fid>")
def view_flavor_get(fid):
    """ View match details of a given ingredient """
    return render_template("flavor.html",
                           all_matches=get_matched_objects(fid),
                           flavor=get_flavor(fid),
                           )


@app.route("/flavor/add", methods=["POST"])
@login_required
def add_flavor_post():
    flavor_name = request.form["flavor"]
    flavor = session.query(Flavor).filter(Flavor.name == flavor_name).first()
    if flavor:
        flash("That flavor already exists in the database", "danger")
        return redirect("/flavor/{}".format(flavor.id))
    else:
        flavor = Flavor(
            name=flavor_name,
            creator=current_user,
        )
        session.add(flavor)
        session.commit()
        return redirect("/flavor/{}".format(flavor.id))

@app.route("/flavor/add", methods=["GET"])
@login_required
def add_flavor_get():
    return render_template("add_flavor.html")


@app.route("/logout", methods=["GET"])
@login_required
def logout_get():
    logout_user()
    return render_template("login.html")


@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))

    login_user(user)
    return redirect(request.args.get('next') or url_for("view_flavors_list"))

@app.route("/newuser", methods=["POST"])
def create_new_user_post():
    email = request.form["email"]
    name = request.form["name"]
    pw1 = request.form["pw1"]
    pw2 = request.form["pw2"]
    matches = json.dumps({})

    user = session.query(User).filter(User.email == email).first()
    if user:
        flash("An account with that email already exists in the database.", "danger")
        return redirect("/login")
    elif not email or not name or not pw1 or not pw2:
        flash("All fields are required.  Please enter the missing data and try again.", "danger")
        return redirect("/newuser")
    elif pw1 != pw2:
        flash("Passwords do not match.", "danger")
        return redirect("/newuser")
    else:
        user = User(
            email=email,
            name=name,
            password=generate_password_hash(pw1),
            matches=matches
        )
        session.add(user)
        session.commit()
        return redirect("/login")


@app.route("/newuser")
def create_new_user_get():
    """ View the page for creating a new user """
    return render_template("newuser.html")


@app.route("/")
@app.route("/page/<int:page>")
def view_flavors_list(page=1, paginate_by=10):
    """ view a list of flavors """
    # Zero-indexed page
    page_index = page - 1

    count = session.query(Flavor).count()

    start = page_index * paginate_by
    end = start + paginate_by

    total_pages = (count - 1) / paginate_by + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    flavors = session.query(Flavor)
    flavors = flavors[start:end]

    return render_template("flavors.html",
                           flavors=flavors,
                           has_next=has_next,
                           has_prev=has_prev,
                           page=page,
                           total_pages=total_pages,
                           current_user=current_user)


def get_flavor(fid):
    # print "get_flavor()"
    return session.query(Flavor).get(fid)


def get_umids(fid):
    """ Return a list of all ids matched to fid """
    # print "get_matched_ids"
    user_match_dict = json.loads(current_user.matches)
    try:
        user_matched_ids = user_match_dict[fid]
    except KeyError:
        user_matched_ids = []
    return set(user_matched_ids)

def get_matched_ids(fid):
    f = get_flavor(fid)
    umids = get_umids(fid)
    fmids = f.mids()


def get_matched_objects(fid):
    """ Return a list of all objects matched to fid """
    # print "get_matched_objects"
    mobjs = []
    for m in get_matched_ids(fid):
        mobjs.append(m)
    return mobjs


def get_unmatched_ids(fid):
    """ Return a list of all ids NOT matched to fid """
    # print "get_unmatched_ids"
    all_flavor_objects = session.query(Flavor).all()
    all_fids = set([f.id for f in all_flavor_objects])
    mids = get_matched_ids(fid)
    umids = set(all_fids - mids)
    umids.remove(fid)
    return umids


def get_unmatched_objects(fid):
    """ Return a list of all objects NOT matched to fid """
    # print "get_unmatched_objects"
    umobjs = set()
    for fid in get_unmatched_ids(fid):
        umobjs.add(session.query(Flavor).get(fid))
    return umobjs
