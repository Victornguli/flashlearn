from flashlearn.models import User


class TestAuth:
	"""Auth blueprint test class"""

	def test_get_login(self, client):
		res = client.get('user/login')
		assert res.status_code == 200
		assert 'Login Route' in res.get_data(as_text = True)

	def test_get_register(self, client):
		res = client.get('user/register')
		assert res.status_code == 200, 'Should return 200 status code'
		assert 'Register Route' in res.get_data(as_text = True), 'Should get register page'

	def test_valid_login(self, login):
		response = login()
		assert response.status_code == 200, 'Should login user'
		assert 'Index' in response.get_data(as_text = True)

	def test_invalid_login(self, login):
		response = login('username', 'password')
		assert 'Invalid login credentials' in response.get_data(as_text = True)

	def test_register_pass(self, client):
		res = client.post(
			'user/register', data = {
				'username': 'testuser', 'password': 'pass@134#', 'email': 'mail@example.com'
			}, follow_redirects = True)
		assert res.status_code == 200
		assert User.query.filter_by(username = 'testuser').first() is not None,\
			'Should create user successfully'
		assert 'Login Route' in res.get_data(as_text = True)

	def test_register_fail(self, user, client):
		"""
		Keep user as an unused fixture that will ensure a user is created
		beforehand to test duplicate user creation fail.
		"""
		res = client.post(
			'user/register', data = {
				'username': 'alice', 'email': '', 'password': 'password'
			}, follow_redirects = True)
		assert res.status_code == 200
		assert 'User already exists' in res.get_data(as_text = True)

	def test_logout(self, logout):
		response = logout()
		assert response.status_code == 302, 'Should logout and redirect to login'

	def test_login_required(self, client):
		res = client.get('/cards')
		assert res.status_code == 302, 'Should redirect to login page'
		# self.assertIn(b'fmdk', res.data)
