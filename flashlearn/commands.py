import click
from flask.cli import with_appcontext
from flashlearn import db


@click.command('init-db')
@with_appcontext
def init_db_command():
	confirm = click.prompt(
		'The database will be re-defined.\
		\nReply with Y/N to confirm or cancel', type=str)
	if confirm == 'Y' or confirm == 'y':
		db.init_db()
		click.echo("Initialized the database.")
	else:
		click.echo("Cancelled db init.")


@click.command('clear-db')
@with_appcontext
def clear_db_command():
	confirm = click.prompt(
		'All database tables will be dropped and all data will be lost.\
		\nReply with Y/N to confirm or cancel.', type=str)
	if confirm == 'Y' or confirm == 'y':
		db.clear_db()
		click.echo('All database tables successfully deleted.')
	else:
		click.echo('Canceled clear_db.')


def prompt_password():
	password = click.prompt('Password', type=str, hide_input = True)
	password_2 = click.prompt('Confirm your password', type=str, hide_input = True)
	if password == password_2:
		return password
	else:
		click.echo('Passwords do not match. Try again.')
		prompt_password()


@click.command('create-user')
@with_appcontext
def create_user_command():
	from flashlearn.models import User
	username = click.prompt('Username', type=str)
	if User.query.filter_by(username = username).first() is None:
		password = prompt_password()
		email = click.prompt('Email', default = None)
		u = User(username = username, password = password, email = email)
		u.save()
		assert u.state == 'Active'
		click.echo('User created successfully.')
	else:
		click.echo('Username already in use. Try again with a different one.')


def register_commands(app):
	"""
	Registers custom CLI commands via click.
	"""
	app.cli.add_command(init_db_command)
	app.cli.add_command(clear_db_command)
	app.cli.add_command(create_user_command)
