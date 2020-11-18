from flask import Blueprint

user = Blueprint(
    "user",
    __name__,
    url_prefix="/user",
    static_folder="static",
    template_folder="templates",
)
