from tests.conftest import BaseTestCase


class TestAuth(BaseTestCase):
	def test_valid_login(self):
		response = self.login(self.alice.username, 'password')
		assert response.status_code == 200, 'Should login user'
		self.assertIn(b'username', response.data)

	def test_invalid_login(self):
		response = self.login('username', 'password')
		self.assertIn(b'Invalid login credentials', response.data)

	def test_logout(self):
		response = self.logout()
		self.assertEqual(302, response.status_code), 'Should logout and redirect to login'

	def test_login_required(self):
		res = self.client.get('/')
		self.assertEqual(302, res.status_code), 'Should redirect to login page'
		# self.assertIn('fmdk', dir(res))
