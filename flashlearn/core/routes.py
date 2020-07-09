from flask import request, url_for, jsonify
from flashlearn.core import bp


# Card Routes
@bp.route('/card', methods = ('GET', 'POST'))
def get_card():
	return jsonify('OK')


@bp.route
def pass_it():
	pass
