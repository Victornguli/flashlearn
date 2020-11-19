import click
from flask_migrate import Migrate, MigrateCommand
from flask.cli import with_appcontext
from flashlearn import db


@click.command("init-db")
@with_appcontext
def init_db_command():
    """
    Initialize a local database on devevelopment
    """
    confirm = click.prompt(
        "The database will be re-initialized." "\nReply with Y/N to confirm or cancel",
        type=str,
    )
    if confirm.lower() == "y":
        db.create_all()
        click.echo("Initialized the database.")
    else:
        click.echo("Cancelled db init.")


@click.command("drop-all")
@with_appcontext
def drop_all_command():
    """
    Drop all tables on current env
    Don't use this command on production
    """
    confirm = click.prompt(
        "All database tables will be dropped." "\nReply with Y/N to confirm or cancel.",
        type=str,
    )
    if confirm.lower() == "y":
        db.drop_all()
        click.echo("All database tables successfully deleted.")
    else:
        click.echo("Cancelled drop-all.")


@click.command("create-user")
@with_appcontext
def create_user_command():
    """Quick create a user for development env"""

    from flashlearn.models import User

    username = click.prompt("Username", type=str)
    if User.query.filter_by(username=username).first() is None:
        password = click.prompt(
            "Password",
            type=str,
            hide_input=True,
            confirmation_prompt=True,
        )
        email = click.prompt("Email", default=None)
        u = User(username=username, password=password, email=email)
        u.save()
        click.echo("User created successfully.")
    else:
        click.echo("Username not available. Try again with a different one.")


def register_commands(app):
    """
    Registers custom CLI commands via click withing the app context..
    """
    # Setup Alembic Migrations
    Migrate(app, db)
    app.cli.add_command(MigrateCommand, name="db")

    app.cli.add_command(init_db_command)
    app.cli.add_command(drop_all_command)
    app.cli.add_command(create_user_command)
