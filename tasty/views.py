__author__ = 'kristjin@github'
from flask import flash, render_template, request, redirect, url_for
from flask.ext.login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

from tasty import app
from .database import session
from .models import Flavor, User

@app.route("/")
@app.route("/page/<int:page>")
def main_tasty(page=1, paginate_by=10):
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


@app.route("/flavor/<int:fid>")
def tasty(fid):
    flavor = session.query(Flavor).get(fid)
    return render_template("flavor.html",
                           current_user=current_user,
                           flavor=flavor,
                           pair_list=flavor.matched_ids,
                           )


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
    return redirect(request.args.get('next') or url_for("main_tasty"))