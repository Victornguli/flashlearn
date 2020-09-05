from flask import Blueprint

bp = Blueprint(
    "user",
    __name__,
    url_prefix="/user",
    static_folder="static",
    template_folder="templates",
)
