import unittest
import pytest
from flashlearn.models import User, Card, Deck, StudyPlan
from flashlearn import create_app, db


class BaseTestCase(unittest.TestCase):
	"""Base test case"""
	def setUp(self) -> None:
		self.app = create_app('testing')
		self.assertEqual(self.app.testing, True)  # Ensure that the set environment is testing
		self.client = self.app.test_client()
		db.clear_db()
		db.init_db()

		# Setup common model instances
		self.alice = User(username = 'alice', email = 'alice@email.com')
		self.alice.set_password('password')
		self.alice.save()

		self.algos = Deck(
			name = 'Algorithms', description = 'Common Algorithms in Computer Science', user = self.alice)
		self.algos.save()
		self.dp = Deck(
			name = 'DP', description = 'Dynamic Programming', user = self.alice, parent_id = self.algos.id)
		self.dp.save()

		back = """
		Dynamic Programming (DP) is an algorithmic technique for solving an optimization problem by breaking it down
		into simpler subproblems and utilizing the fact that the optimal solution to the overall problem depends upon
		the optimal solution to its subproblems.
		"""
		self.card = Card(
			front = 'What is dynamic programming', back = back, user_id = self.alice.id, deck_id = self.dp.id)
		self.card.save()

		self.plan = StudyPlan(name = 'Grokking Algorithms', user = self.alice)
		self.plan.save()

	def login(self, username = None, password = None):
		if not (username and password):
			username = self.alice.username
			password = 'password'
		return self.client.post(
			'/user/login', data = dict(username = username, password = password),
			follow_redirects = True)

	def logout(self):
		return self.client.post('/user/logout')

	@staticmethod
	def refresh(*args):
		"""Refresh objects as needed in derived test cases"""
		for obj in args:
			db.session.refresh(obj)

	def tearDown(self) -> None:
		# db.session.refresh_()
		db.close_session()
		db.clear_db()


@pytest.fixture
def test_app():
	"""Fixture that serves the app within test env"""
	return create_app('testing')


@pytest.fixture
def test_client(test_app):
	"""Pytest Fixture that serves the test_client"""
	return test_app.test_client()

