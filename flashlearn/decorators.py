from flask import redirect, url_for, g, request
from functools import wraps


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("user.login", next=request.url))
        return view(*args, **kwargs)

    return wrapped_view
