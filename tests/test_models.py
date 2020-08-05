from flask_bcrypt import Bcrypt
from flashlearn.models import User, Card, Deck, StudyPlan
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

	def test_deck_model(self):
		child = Deck(
			name = 'Recursion', description='Recursive Algorithms', user = self.alice, parent_id = self.algos.id)
		child.save()
		assert child in self.alice.decks, "Child deck should be available in the user's decks"
		assert child in self.algos.children, "Child deck should be available in parent's children"
		Deck.query.filter_by(name = 'Recursion').delete()
		assert Deck.query.filter_by(name = 'Recursion').first() is None, 'Should delete the deck'

	def test_card_model(self):
		test_card = Card(
			name = 'Bridge of Death', front = 'What is the air velocity of unladen swallow',
			back = 'African or European?', user_id = self.alice.id, deck_id = self.dp.id,
			description = 'Basic quiz from Monty Python')
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
		assert plan in self.alice.study_plans, 'Should be accessible from Alice\'s study plans'
		StudyPlan.query.filter_by(id = plan.id).delete()
		assert StudyPlan.query.filter_by(id = plan.id).first() is None, 'Should be deleted'
