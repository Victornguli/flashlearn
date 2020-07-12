from tests.conftest import BaseTestCase


class TestRoutes(BaseTestCase):

	def test_create_card(self):
		pass

	def test_create_group(self):
		login = self.login(self.alice.username, 'password')
		assert login.status_code == 200, 'Should login user'
		group_response = self.client.post(
			'/group', data = {
				'name': 'BFS', 'description': 'Breadth First Search',
				'user_id': self.alice.id}
		)
		self.assertEqual(200, group_response.status_code)
		self.assertIn(b'BFS', group_response.data)
