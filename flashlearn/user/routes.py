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
from flashlearn.decorators import login_required


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
            flash("You were successfully logged in")
            if next_url:
                return redirect(next_url)
            return redirect(url_for("index"))
        return render_template("login.html", error=error)
    else:
        return render_template("login.html")


@user.route("/register", methods=("POST", "GET"))
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email", None)
        error = ""
        user = User.query.filter_by(username=username).first()
        if user is not None:
            error = "User already exists"
        if not error:
            user = User(username=username, password=password, email=email)
            user.save()
            return redirect(url_for("user.login"))
        return jsonify(error)  # TODO: Replace with flash(message)
    return jsonify("Register Route")


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
def list_users():
    users = [user.to_json for user in User.all()]
    return jsonify(users)


@user.route("/<int:user_id>")
@login_required
def get_user(user_id):
    if request.method == "GET":
        user = User.query.get_or_404(user_id)
        if user is None:  # pragma:no cover
            return "User not found", 404
        return jsonify(User.query.get_or_404(user_id).to_json)
    return jsonify("Invalid request ")


@user.route("/<int:user_id>/delete", methods=("GET", "POST"))
@login_required
def delete_user(user_id):
    user = User.query.filter_by(id=user_id, state="active").first()
    user.delete()
    return "deleted"


@user.route("/<int:user_id>/edit", methods=("GET", "POST"))
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == "GET":
        return render_template("dashboard/settings.html", user=user)
    else:
        password = request.form.get("password", None)
        email = request.form.get("email", user.email)

        if password is not None:  # pragma:no-cover
            user.set_password(password)
        user.update(email=email)
        return jsonify(user.to_json)


@user.route("/reset-password", methods=("POST", "GET"))
def reset_password():
    if request.method == "GET":  # pragma:no cover
        return render_template("forgot-password.html")
    elif request.method == "POST":  # pragma:no cover
        flash("Password reset successfully")
        return redirect("reset-password")
