import unittest
from flask_bcrypt import Bcrypt
from flashlearn import create_app
from flashlearn.db import init_db, clear_db, db_session, close_db_session
from flashlearn.models import User, Card, Group, StudyPlan, StudyPlanGroup


class TestBase(unittest.TestCase):
	"""Test base class for flashlearn models"""
	def setUp(self) -> None:
		self.app = create_app('testing')
		self.client = self.app.test_client()
		init_db()

	def test_app(self):
		assert self.app.testing

	def tearDown(self) -> None:
		close_db_session()
		clear_db()


class TestUserModel(TestBase):
	def test_user_model(self):
		u = User(username = 'admin', password = '12345', email = 'admin@mail.com')
		u.save()
		assert u.password != '12345'
		assert u.state == 'Active'
		u.password = Bcrypt().generate_password_hash('TheShrubbery@007').decode()
		u.save()
		assert u.password_is_valid('TheShrubbery@007'), 'Should confirm password change'
		User.query.filter_by(username='admin').delete()
		assert User.query.filter_by(username='admin').first() is None, 'Should delete the user'

	def test_group_model(self):
		u = User(username = 'admin', password = '12345', email = 'admin@mail.com')
		u.save()
		parent = Group(name = 'Algos', description = 'General Algorithms', user_id = u)
		parent.save()
		child = Group(
			name = 'DP', description='Dynamic Programming', user_id = u, parent_id = parent.id
		)
		child.save()
		assert parent, child in u.user_groups
		assert child in parent.children

	def test_card_model(self):
		pass
