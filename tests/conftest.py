import unittest
import pytest
from flashlearn.models import User, Card, Deck, StudyPlan
from flashlearn import create_app, db


@pytest.fixture
def test_app():
	"""Fixture that serves the app within test env"""
	return create_app('testing')


@pytest.fixture
def client(test_app):
	"""Pytest Fixture that serves the test_client"""
	with test_app.app_context():
		db.create_all()
		yield test_app.test_client()


@pytest.fixture
def user(client) -> User:
	alice = User(username = 'alice', email = 'alice@email.com')
	alice.set_password('password')
	alice.save()
	return alice


@pytest.fixture
def login(client, user):
	def inner(username = None, password = None):
		if not (username and password):
			username = user.username
			password = 'password'
		return client.post(
			'/user/login', data = dict(username = username, password = password),
			follow_redirects = True)
	return inner


@pytest.fixture
def logout(client):
	def inner():
		return client.post('/user/logout')
	return inner


	# self.algos = Deck(
	# 	name = 'Algorithms', description = 'Common Algorithms in Computer Science', user = self.alice)
	# self.algos.save()
	# self.dp = Deck(
	# 	name = 'DP', description = 'Dynamic Programming', user = self.alice, parent_id = self.algos.id)
	# self.dp.save()
	#
	# back = """
	# Dynamic Programming (DP) is an algorithmic technique for solving an optimization problem by breaking it down
	# into simpler subproblems and utilizing the fact that the optimal solution to the overall problem depends upon
	# the optimal solution to its subproblems.
	# """
	# self.card = Card(
	# 	front = 'What is dynamic programming', back = back, user_id = self.alice.id, deck_id = self.dp.id)
	# self.card.save()
	#
	# self.plan = StudyPlan(name = 'Grokking Algorithms', user = self.alice)
	# self.plan.save()

# class BaseTestCase:
# 	"""Base test case"""
# 	def __init__(self, client) -> None:
# 		# Setup common model instances
#
#
# 	def login(self, username = None, password = None):
# 		if not (username and password):
# 			username = self.alice.username
# 			password = 'password'
# 		return client.post(
# 			'/user/login', data = dict(username = username, password = password),
# 			follow_redirects = True)
#
# 	def logout(self):
# 		return client.post('/user/logout')

	# @staticmethod
	# def refresh(*args):
	# 	"""Refresh objects as needed in derived test cases"""
	# 	for obj in args:
	# 		db.session.refresh(obj)
