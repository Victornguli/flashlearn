from tests.conftest import BaseTestCase
from flashlearn.models import Card, Deck, StudyPlan, User


class TestRoutes(BaseTestCase):
	"""Flashlearn routes test class"""

	def test_index_route(self):
		res = self.client.get('/')
		self.assertEqual(200, res.status_code)
		self.assertIn(b'Index', res.data)

	def test_get_users(self):
		self.refresh(self.alice)
		self.login()
		res = self.client.get('/user/list')
		self.assertEqual(200, res.status_code)
		self.assertIn(b'alice', res.data)

	def test_get_user(self):
		self.refresh(self.alice)
		self.login()
		res = self.client.get(f'/user/{self.alice.id}')
		self.assertEqual(200, res.status_code)
		self.assertIn('alice', res.get_data(as_text = True))

	def test_get_user_fail(self):
		self.login()
		res = self.client.get(f'/user/{10}')
		self.assertEqual(404, res.status_code),\
			'Should return 404 if user is not found'

	def test_edit_user(self):
		self.login()
		user = User(
			username = 'test', email = 'test@mail.com', password = 'test')
		user.save()
		res = self.client.post(f'/user/{user.id}/edit', data = {
			'password': 'test', 'email': 'new_mail@test.com'})
		self.assertEqual(200, res.status_code)
		user = User.query.filter_by(id = user.id).first()
		self.assertEqual('new_mail@test.com', user.email)

	def test_delete_user(self):
		self.refresh(self.alice)
		self.login()
		user = User(username = 'test', email = 'test', password = 'test')
		user.save()
		self.assertEqual('test', user.username), 'Should save user'
		res = self.client.get(f'/user/{user.id}/delete')
		self.assertEqual(200, res.status_code), 'Should return 200 status'
		self.assertEqual(None, User.query.filter_by(
			username = 'test').first()), 'Query should return None'

	def test_create_card(self):
		self.refresh(self.alice, self.algos, self.dp)
		self.login()
		res = self.client.post(
			'/card', data = {
				'front': 'front', 'back': 'back',
				'deck_id': self.algos.id, 'user_id': self.alice.id
			})
		self.assertEqual(200, res.status_code)

	def test_get_card(self):
		self.refresh(self.alice, self.card)
		self.login()
		res = self.client.get(f'/card/{self.card.id}')
		self.assertEqual(200, res.status_code)

	def test_edit_card(self):
		self.refresh(self.alice, self.card)
		self.login()
		res = self.client.post(
			f'/card/{self.card.id}/edit', data = {
				'front': 'New Front', 'state': 'solved'})
		self.assertEqual(200, res.status_code)
		self.card = Card.query.filter_by(id = self.card.id).first()
		self.assertEqual('solved', self.card.state)
		self.assertEqual('New Front', self.card.front)

	def test_delete_card(self):
		self.refresh(self.alice, self.card)

		self.login()
		res = self.client.post(f'/card/{self.card.id}/delete')
		self.assertEqual(200, res.status_code)
		self.assertEqual(None, Card.query.filter_by(id = self.card.id).first())

	def test_get_cards(self):
		self.login()
		res = self.client.get('/cards')
		self.assertEqual(200, res.status_code)
		self.assertIn(b'Dynamic Programming', res.data)

	def test_create_deck(self):
		self.login()
		group_response = self.client.post(
			'/deck', data = {
				'name': 'BFS', 'description': 'Breadth First Search',
				'user_id': self.alice.id})
		self.assertEqual(200, group_response.status_code)
		self.assertIn(b'BFS', group_response.data)

	def test_get_deck(self):
		self.refresh(self.alice, self.algos)
		self.login()
		res = self.client.get(f'deck/{self.algos.id}')
		self.assertEqual(200, res.status_code)

	def test_edit_deck(self):
		self.refresh(self.algos)
		self.login()
		res = self.client.post(
			f'/deck/{self.algos.id}/edit', data = {'name': 'Algorythms'})
		self.assertEqual(200, res.status_code)
		self.assertIn(b'Algorythms', res.data)

	def test_delete_deck(self):
		self.refresh(self.algos)
		self.login()
		res = self.client.post(
			f'/deck/{self.algos.id}/delete')
		self.assertEqual(200, res.status_code)
		self.assertEqual(None, Deck.query.filter_by(id = self.algos.id).first())

	def test_get_groups(self):
		self.refresh(self.alice, self.algos)
		self.login()
		res = self.client.get('/decks')
		self.assertEqual(200, res.status_code)

	def test_create_study_plan(self):
		self.login()
		res = self.client.post('/plan', data = {
			'name': 'test_plan', 'description': 'test study plan', 'order': 'random'})
		self.assertEqual(200, res.status_code)

	def test_get_study_plan(self):
		self.refresh(self.plan)
		self.login()
		res = self.client.get(f'/plan/{self.plan.id}')
		self.assertEqual(200, res.status_code)

	def test_get_study_plans(self):
		self.refresh(self.plan)
		self.login()
		res = self.client.get('/plans')
		self.assertEqual(200, res.status_code)

	def test_reset_deck(self):
		self.refresh(self.dp, self.card)
		self.login()
		res = self.client.post(f'/deck/{self.dp.id}/reset', data = {
			'state': 'solved'})
		self.assertEqual(200, res.status_code)
		card = Card.query.filter_by(deck_id = self.dp.id).first()
		self.assertEqual('solved', card.state)

	def test_get_next_card(self):
		self.refresh(self.dp, self.card, self.plan)
		self.login()
		self.plan = StudyPlan.get_by_id(self.plan.id)
		card2 = Card(front = 'test', back = 'test', deck = self.dp, user = self.alice)
		card2.save()
		res = self.client.post('/study_plan/next', data = {
			'study_plan_id': self.plan.id, 'deck_id': self.dp.id})
		self.assertEqual(200, res.status_code)
		self.assertIn(b'Dynamic Programming', res.data)
