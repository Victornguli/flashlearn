from flask import Blueprint

bp = Blueprint(
    "core", __name__, url_prefix="", static_folder="static", template_folder="templates"
)
