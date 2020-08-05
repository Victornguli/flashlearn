from tests.conftest import BaseTestCase
from flashlearn.models import Card, Deck


class TestRoutes(BaseTestCase):
	"""Flashlearn routes test class"""

	def test_index_route(self):
		res = self.client.get('/')
		self.assertEqual(200, res.status_code)
		self.assertIn(b'Index', res.data)

	def test_create_card(self):
		super().refresh(self.alice, self.algos, self.dp)
		self.login(self.alice.username, 'password')
		res = self.client.post(
			'/card', data = {
				'name': 'Test new card', 'front': 'front', 'back': 'back',
				'deck_id': self.algos.id, 'user_id': self.alice.id
			}
		)
		self.assertEqual(200, res.status_code)

	def test_get_card(self):
		super().refresh(self.alice, self.card)
		self.login(self.alice.username, 'password')
		res = self.client.get(f'/card/{self.card.id}')
		self.assertEqual(200, res.status_code)

	def test_edit_card(self):
		super().refresh(self.alice, self.card)

		self.login(self.alice.username, 'password')
		res = self.client.post(
			f'/card/{self.card.id}/edit', data = {
				'name': 'Not Algos card', 'is_snippet': False
			}
		)
		self.assertEqual(200, res.status_code)
		self.assertEqual('Not Algos card', Card.query.filter_by(id = self.card.id).first().name)

	def test_delete_card(self):
		super().refresh(self.alice, self.card)

		self.login(self.alice.username, 'password')
		res = self.client.post(f'/card/{self.card.id}/delete')
		self.assertEqual(200, res.status_code)
		self.assertEqual(None, Card.query.filter_by(id = self.card.id).first())

	def test_get_cards(self):
		self.login(self.alice.username, 'password')
		res = self.client.get('/cards')
		self.assertEqual(200, res.status_code)
		self.assertIn(b'Dynamic Programming', res.data)

	def test_create_deck(self):
		login = self.login(self.alice.username, 'password')
		assert login.status_code == 200, 'Should login user'
		group_response = self.client.post(
			'/deck', data = {
				'name': 'BFS', 'description': 'Breadth First Search',
				'user_id': self.alice.id}
		)
		self.assertEqual(200, group_response.status_code)
		self.assertIn(b'BFS', group_response.data)

	def test_get_deck(self):
		self.refresh(self.alice, self.algos)
		self.login(self.alice.username, 'password')
		res = self.client.get(f'deck/{self.algos.id}')
		self.assertEqual(200, res.status_code)

	def test_edit_deck(self):
		super().refresh(self.algos)
		login = self.login(self.alice.username, 'password')
		assert login.status_code == 200, 'Should login user'
		res = self.client.post(
			f'/deck/{self.algos.id}/edit', data = {'name': 'Algorythms'}
		)
		self.assertEqual(200, res.status_code)
		self.assertIn(b'Algorythms', res.data)

	def test_delete_deck(self):
		self.refresh(self.algos)
		login = self.login(self.alice.username, 'password')
		assert login.status_code == 200, 'Should login user'
		res = self.client.post(
			f'/deck/{self.algos.id}/delete', data = {'name': 'Algorythms'}
		)
		self.assertEqual(200, res.status_code)
		self.assertEqual(None, Deck.query.filter_by(id = self.algos.id).first())

	def test_get_groups(self):
		self.refresh(self.alice, self.algos)
		self.login(self.alice.username, 'password')
		res = self.client.get('/decks')
		self.assertEqual(200, res.status_code)
