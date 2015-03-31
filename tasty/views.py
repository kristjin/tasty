__author__ = 'kristjin@github'
import json
from flask import flash, render_template, request, redirect, url_for
from flask.ext.login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from tasty import app
from .database import session
from .models import Flavor, User, Match


@app.route('/default_unmatch/<int:fid>/<int:mid>', methods=['GET'])
@login_required
def unmatch_default_flavors(fid, mid=0):
    """ Unpair a flavor and a default matching flavor """
    f = get_flavor(fid)
    if mid:
        dmids = f.get_default_mids()
        if mid in dmids:
            m = session.query(Match)\
                       .filter(Match.owner_id == 0,
                               Match.parent_id == fid,
                               Match.matched_id == mid).first()
            print "in unmatch_default_flavors m is {}".format(m)
            session.delete(m)
            session.commit()

    return render_template("match_default_flavors.html",
                           flavor=f,
                           all_matches=f.get_all_mobs(0),
                           unmatched_flavors=f.get_unmobs(0))


@app.route('/default_match/<int:fid>')
@app.route('/default_match/<int:fid>/<int:mid>', methods=['GET'])
@login_required
def match_default_flavors(fid, mid=0):
    """ Pair a flavor and a default matching flavor """
    f = get_flavor(fid)
    if mid:
        dmids = f.get_default_mids()
        if mid not in dmids:
            m = Match(owner_id=0,
                      parent_id=fid,
                      matched_id=mid)
            print "the state of m is {}".format(m)
            session.add(m)
            session.commit()

    return render_template("match_default_flavors.html",
                           flavor=f,
                           all_matches=f.get_all_mobs(0),
                           unmatched_flavors=f.get_unmobs(0)
                           )


@app.route('/unmatch/<int:fid>/<int:mid>', methods=['GET'])
@login_required
def unmatch_flavors(fid, mid):
    """ Unpair a user's flavor and a matching flavor """
    f = get_flavor(fid)
    if mid:
        umids = f.get_user_mids(uid())
        if mid in umids:
            m = session.query(Match)\
                       .filter(Match.owner_id == uid(),
                               Match.parent_id == fid,
                               Match.matched_id == mid).first()
            print "the state of m is {}".format(m)
            session.delete(m)
            session.commit()

    return render_template("match_flavors.html",
                           flavor=f,
                           all_matches=f.get_all_mobs(uid()),
                           unmatched_flavors=f.get_unmobs(uid())
                           )


@app.route('/match/<int:fid>')
@app.route('/match/<int:fid>/<int:mid>', methods=['GET'])
@login_required
def match_flavors(fid, mid=0):
    """ Pair a flavor and a user's matching flavor """
    f = get_flavor(fid)
    if mid:
        umids = f.get_user_mids(current_user.id)
        if mid not in umids:
            m = Match(owner_id=current_user.id,
                      parent_id=fid,
                      matched_id=mid)
            session.add(m)
            session.commit()

    return render_template("match_flavors.html",
                           flavor=f,
                           all_matches=f.get_all_mobs(uid()),
                           unmatched_flavors=f.get_unmobs(uid())
                           )


@app.route("/flavor/<int:fid>")
def view_flavor_get(fid):
    f = get_flavor(fid)
    """ View match details of a given ingredient """
    return render_template("flavor.html",
                           all_matches=f.get_all_mobs(uid()),
                           flavor=f,
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
            password=generate_password_hash(pw1)
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
                           uid=uid())


def get_flavor(fid):
    return session.query(Flavor).get(fid)


def get_all_fobs():
    return session.query(Flavor).all()


def uid():
    if current_user.is_anonymous():
        return 0
    if current_user.is_authenticated():
        return current_user.id