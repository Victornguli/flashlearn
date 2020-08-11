from tests.conftest import BaseTestCase
from flashlearn.models import Card, Deck


class TestRoutes(BaseTestCase):
	"""Flashlearn routes test class"""

	def test_index_route(self):
		res = self.client.get('/')
		self.assertEqual(200, res.status_code)
		self.assertIn(b'Index', res.data)

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
