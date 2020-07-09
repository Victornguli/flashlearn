import unittest
from flashlearn.models import User, Card, Group, StudyPlan, StudyPlanGroup
from flashlearn import create_app, db


class BaseTestCase(unittest.TestCase):
	"""Base test case"""
	def setUp(self) -> None:
		self.app = create_app('testing')
		self.assertEqual(self.app.testing, True)  # Ensure that the set environment is testing
		self.client = self.app.test_client()
		db.init_db()

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

	def login(self, username, password):
		return self.client.post(
			'/auth/login', data = dict(username = username, password = password),
			follow_redirects = True)

	def logout(self):
		return self.client.post('/auth/logout')

	def tearDown(self) -> None:
		db.close_session()
		db.clear_db()
