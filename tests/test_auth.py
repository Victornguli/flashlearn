from tests.conftest import BaseTestCase
from flashlearn.models import User


class TestAuth(BaseTestCase):
	"""Auth blueprint test class"""

	def test_get_login(self):
		res = self.client.get('auth/login')
		self.assertEqual(200, res.status_code)
		self.assertIn(b'Login Route', res.data)

	def test_get_register(self):
		res = self.client.get('auth/register')
		self.assertEqual(200, res.status_code)
		self.assertIn(b'Register Route', res.data)

	def test_valid_login(self):
		response = self.login(self.alice.username, 'password')
		assert response.status_code == 200, 'Should login user'
		self.assertIn(b'Index', response.data)

	def test_invalid_login(self):
		response = self.login('username', 'password')
		self.assertIn(b'Invalid login credentials', response.data)

	def test_register_pass(self):
		res = self.client.post(
			'auth/register', data = {
				'username': 'testuser', 'password': 'pass@134#', 'email': 'mail@example.com'
			}, follow_redirects = True)
		self.assertEqual(200, res.status_code)
		assert User.query.filter_by(username = 'testuser').first() is not None,\
			'Should create user successfully'
		self.assertIn(b'Login Route', res.data)

	def test_register_fail(self):
		res = self.client.post(
			'auth/register', data = {
				'username': 'alice', 'email': ''
			}, follow_redirects = True)
		self.assertEqual(200, res.status_code)
		self.assertIn(b'User already exists', res.data)

	def test_logout(self):
		response = self.logout()
		self.assertEqual(302, response.status_code), 'Should logout and redirect to login'

	def test_login_required(self):
		res = self.client.get('/cards')
		self.assertEqual(302, res.status_code), 'Should redirect to login page'
		# self.assertIn(b'fmdk', res.data)
