from .conftest import BaseTestCase


class TestCommands(BaseTestCase):

	def test_init_db(self):
		cli_runner = self.app.test_cli_runner()
		res = cli_runner.invoke(args = ["init-db"], input = "N")
		assert "Cancelled db init" in res.output, 'Should cancel db initialization'

	def test_clear_db(self):
		cli_runner = self.app.test_cli_runner()
		res = cli_runner.invoke(args = ["clear-db"], input = "N")
		assert "Cancelled clear_db" in res.output, 'Should cancel drop all command'

	def test_create_user(self):
		with self.app.app_context():
			cli_runner = self.app.test_cli_runner()
			init_db_command = cli_runner.invoke(args = ["init-db"], input = "Y")
			assert "Initialized the database" in init_db_command.output, 'Should initialize db successfully'
			res = cli_runner.invoke(args = ["create-user"], input = "\n".join(
				["test_user", "pass1", "pass1", "u@mail.com"]))
			assert "User created successfully" in res.output, 'Should successfully create the user'
