from flask import redirect, url_for, g
from functools import wraps


def login_required(view):
	@wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None:
			# Hacky way of reversing the view url then adding it to the next argument
			# for an intuitive redirect after login. view.__name__ -> the route method name
			view_name = view.__name__
			if len(view.__module__.split(".")) > 2:
				bp = (view.__module__.split(".")[1])  # Get the blueprint name, for accurate urls.
				view_name = f'{bp}.{view_name}'
			return redirect(url_for('auth.login', next = url_for(view_name)))
		return view(**kwargs)
	return wrapped_view
