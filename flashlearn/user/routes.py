from flask import (
    jsonify,
    g,
    request,
    session,
    url_for,
    redirect,
    render_template,
    flash,
)
from flashlearn.user import user
from flashlearn.models import User
from flashlearn.decorators import login_required, super_user_required


@user.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        next_url = request.form.get("next")

        error = ""
        user = User.query.filter_by(username=username).first()
        if user is None or not user.password_is_valid(password):
            error = "Invalid login credentials"

        if not error:
            session.clear()
            session["user_id"] = user.id
            flash(f"Welcome back {username}")
            if next_url:
                return redirect(next_url)
            return redirect(url_for("index"))
        return render_template("login.html", error=error)
    else:
        return render_template("login.html")


@user.route("/register", methods=("POST", "GET"))
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        password_confirm = request.form.get("password_confirm")

        user = User.query.filter_by(username=username).first()
        if user is not None:
            flash("Username is taken")
            return render_template("register.html")

        if password == password_confirm:
            user = User(username=username, password=password)
            user.save()
            return redirect(url_for("user.login"))
        else:
            flash("Password and password confirm don't match")
            return render_template("register.html")


@user.before_app_request
def load_user():
    """Load authenticated user"""
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get_or_404(user_id)


@user.route("/logout", methods=("GET", "POST"))
def logout():
    session.clear()
    return redirect(url_for("user.login"))


@user.route("/list")
@login_required
@super_user_required
def list_users():
    users = [user.to_json for user in User.all()]
    return jsonify(users)


@user.route("/details")
@login_required
def get_user():
    if request.method == "GET":
        return jsonify(g.user.to_json)
    return jsonify("Invalid request ")


@user.route("/<int:user_id>/delete", methods=("GET", "POST"))
@login_required
def delete_user(user_id):
    user = User.query.filter_by(id=user_id, state="active").first()
    user.delete()
    return "deleted"


@user.route("/account", methods=("GET", "POST"))
@login_required
def account():
    if request.method == "GET":
        return render_template("dashboard/settings.html", user=g.user)
    elif request.method == "POST":
        password = request.form.get("password", None)
        email = request.form.get("email", g.user.email)
        logged_in_user = g.user
        if password is not None:  # pragma:no-cover
            logged_in_user.set_password(password)
        logged_in_user.update(email=email)
        return jsonify(logged_in_user.to_json)


@user.route("/reset-password", methods=("POST", "GET"))
def reset_password():
    if request.method == "GET":  # pragma:no cover
        return render_template("forgot-password.html")
    elif request.method == "POST":  # pragma:no cover
        flash("Password reset successfully")
        return redirect("reset-password")
