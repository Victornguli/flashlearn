import unittest
from flask_bcrypt import Bcrypt
from flashlearn import create_app
from flashlearn.db import init_db, clear_db, db_session, close_db_session
from flashlearn.models import User, Card, Group, StudyPlan, StudyPlanGroup


class BaseTestCase(unittest.TestCase):
	"""Base test case"""
	def setUp(self) -> None:
		self.app = create_app('testing')
		assert self.app.testing  # Ensure that the set environment is testing
		self.client = self.app.test_client()
		init_db()

		# Setup common model instances
		self.alice = User(username = 'alice', email = 'alice@email.com')
		self.alice.set_password('password')
		self.alice.save()

		self.algos = Group(
			name = 'Algorithms', description = 'Common Algorithms in Computer Science', user = self.alice)
		self.algos.save()
		self.dp = Group(
			name = 'DP', description = 'Dynamic Programming', user = self.alice, parent_id = self.algos.id)
		self.dp.save()

		back = """
		Dynamic Programming (DP) is an algorithmic technique for solving an optimization problem by breaking it down 
		into simpler subproblems and utilizing the fact that the optimal solution to the overall problem depends upon 
		the optimal solution to its subproblems.
		"""
		self.card = Card(
			name = 'Dynamic Programming', front = 'What is dynamic programming', back = back,user_id = self.alice.id,
			group_id = self.dp.id, description = 'Basic definition of Dynamic Programming', is_snippet = False)
		self.card.save()

		self.plan = StudyPlan(name = 'Grokking Algorithms', user = self.alice)
		self.plan.save()

		self.plan_group = StudyPlanGroup(group_id = self.dp.id, study_plan_id = self.plan.id)
		self.plan_group.save()

	def tearDown(self) -> None:
		close_db_session()
		clear_db()


class TestModels(BaseTestCase):
	"""Test class for flashlearn models"""
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
		child = Group(
			name = 'Recursion', description='Recursive Algorithms', user = self.alice, parent_id = self.algos.id)
		child.save()
		assert child in self.alice.user_groups, "Child group should be available in the user's groups"
		assert child in self.algos.children, "Child group should be available in parent's children"

	def test_card_model(self):
		card = Card(
			name = 'Bridge of Death', front = 'What is the air velocity of unladen swallow',
			back = 'African or European?', user_id = self.alice.id, group_id = self.dp.id,
			description = 'Basic quiz from Monty Python', is_snippet = False)
		card.save()
		assert card.state == 'Active', 'Should be saved with an active state'
		card.description = 'I don\'t know that!'
		card.save()
		assert card.description == 'I don\'t know that!'

	def test_study_plan_model(self):
		plan = StudyPlan(name = 'Grokking CS Algorithms', user = self.alice)
		plan.save()
		assert plan.state == 'Active', 'Should create a plan with state active'
		assert plan in self.alice.user_study_plans, 'Should be accessible from Alice\'s study plans'
		StudyPlan.query.filter_by(id = plan.id).delete()
		assert StudyPlan.query.filter_by(id = plan.id).first() is None, 'Should be deleted'

	def test_study_plan_group_model(self):
		assert self.plan_group in self.plan.study_plan_groups, 'Test backref accessibility'
		assert self.plan_group in self.dp.group_study_plans, 'Test backref accessibility'
