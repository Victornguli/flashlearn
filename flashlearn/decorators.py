from flask import redirect, url_for, g, request, abort
from instance.config import BaseConfig
from functools import wraps

if BaseConfig.USE_REDIS_CACHE:
    from flask_caching.backends import RedisCache

    redis_cache = RedisCache(port=6379, host="redis", default_timeout=300)
else:
    from flask_caching.backends import SimpleCache

    redis_cache = SimpleCache(default_timeout=300)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            next_url = request.endpoint if request.endpoint != "index" else "core.decks"
            return redirect(
                url_for("user.login", next=url_for(next_url, *args, **kwargs))
            )
        return view(*args, **kwargs)

    return wrapped_view


def super_user_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not g.user.is_superuser:
            return abort(401)
        return view(*args, **kwargs)

    return wrapped_view


def cache(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        cached_key = ""
        if args:
            cached_key = args[0]
        else:
            for k, v in kwargs.items():
                cached_key = f"{k}:{v}"
                break
        print(cached_key)
        cached_view = redis_cache.get(str(cached_key))
        if cached_view:
            return cached_view
        _ = view(*args, **kwargs)
        redis_cache.set(str(cached_key), str(_))
        return _

    return wrapper
