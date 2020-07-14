from flask_bcrypt import Bcrypt
from flashlearn.models import User, Card, Group, StudyPlan
from tests.conftest import BaseTestCase


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
		Group.query.filter_by(name = 'Recursion').delete()
		assert Group.query.filter_by(name = 'Recursion').first() is None, 'Should delete the group'

	def test_card_model(self):
		test_card = Card(
			name = 'Bridge of Death', front = 'What is the air velocity of unladen swallow',
			back = 'African or European?', user_id = self.alice.id, group_id = self.dp.id,
			description = 'Basic quiz from Monty Python', is_snippet = False)
		test_card.save()
		assert test_card.state == 'Active', 'Should be saved with an active state'
		test_card.description = 'I don\'t know that!'
		test_card.save()
		assert test_card.description == 'I don\'t know that!'
		Card.query.filter_by(name = 'Bridge of Death').delete()
		assert Card.query.filter_by(name = 'Bridge of Death').first() is None, 'Should delete the card'
		# self.db.session.expire(card)

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
