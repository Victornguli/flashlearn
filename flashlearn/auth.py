"""Auth blueprint"""
from flask import Blueprint, jsonify, g, request, session, url_for, redirect
from flashlearn.models import User

bp = Blueprint('auth', __name__, url_prefix = '/auth')


@bp.route('/login', methods = ('GET', 'POST'))
def login():
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')
		error = ''
		user = User.query.filter_by(username = username).first()
		if user is None or not user.password_is_valid(password):
			error = 'Invalid login credentials'

		if not error:
			session.clear()
			session['user_id'] = user.id
			if request.args.get('next'):
				return redirect(request.args.get('next', ''))
			return redirect(url_for('index'))
		return jsonify(error)  # TODO: Replace with flash(message)
	return jsonify('Login Route')


@bp.route('/register', methods = ('POST', 'GET'))
def register():
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')
		email = request.form.get('email', None)
		error = ''
		user = User.query.filter_by(username = username).first()
		if user is not None:
			error = 'User already exists'
		if not error:
			user = User(username = username, password = password, email = email)
			user.save()
			return redirect(url_for('auth.login'))
		return jsonify(error)  # TODO: Replace with flash(message)
	return jsonify('Register Route')


@bp.before_app_request
def load_user():
	"""Load authenticated user"""
	user_id = session.get('user_id')
	if user_id is None:
		g.user = None
	else:
		g.user = User.query.filter_by(id = user_id).first()


@bp.route('/logout', methods = ('GET', 'POST'))
def logout():
	session.clear()
	return redirect(url_for('auth.login'))
