from flask import redirect, url_for, g, request, abort
from functools import wraps


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            next_url = request.endpoint if request.endpoint != "index" else "core.decks"
            return redirect(url_for("user.login", next=url_for(next_url)))
        return view(*args, **kwargs)

    return wrapped_view


def super_user_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not g.user.is_superuser:
            return abort(401)
        return view(*args, **kwargs)

    return wrapped_view
