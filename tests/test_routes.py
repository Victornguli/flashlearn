from flashlearn.models import Card, Deck, StudyPlan, User


class TestRoutes:
	"""Flashlearn routes test class"""

	def test_index_route(self, client):
		res = client.get('/')
		assert 200 == res.status_code
		assert 'Index' in res.get_data(as_text = True)

	def test_get_users(self, login, client):
		login()
		res = client.get('/user/list')
		assert 200 == res.status_code
		assert 'alice' in res.get_data(as_text = True)

	def test_get_user(self, login, client, user):
		login()
		res = client.get(f'/user/{user.id}')
		assert 200 == res.status_code
		assert 'alice' in res.get_data(as_text = True)

	def test_get_user_fail(self, login, client):
		login()
		res = client.get(f'/user/{10}')
		assert 404 == res.status_code,\
			'Should return 404 if user is not found'

	def test_edit_user(self, login, client):
		login()
		user = User(
			username = 'test', email = 'test@mail.com', password = 'test')
		user.save()
		res = client.post(f'/user/{user.id}/edit', data = {
			'password': 'test', 'email': 'new_mail@test.com'})
		assert 200 == res.status_code
		user = User.query.filter_by(id = user.id).first()
		assert 'new_mail@test.com' == user.email

	def test_delete_user(self, user, login, client):
		login()
		user = User(username = 'test', email = 'test', password = 'test')
		user.save()
		assert 'test' == user.username, 'Should save user'
		res = client.get(f'/user/{user.id}/delete')
		assert 200 == res.status_code, 'Should return 200 status'
		assert None == User.query.filter_by(
			username = 'test').first(), 'Query should return None'

	def test_create_card(self, user, decks, login, client):
		login()
		res = client.post(
			'/card', data = {
				'front': 'front', 'back': 'back',
				'deck_id': decks[0].id, 'user_id': user.id
			})
		assert 200 == res.status_code

	def test_get_card(self, client, card, login):
		login()
		res = client.get(f'/card/{card.id}')
		assert 200 == res.status_code

	def test_edit_card(self, user, card, login, client):
		login()
		res = client.post(
			f'/card/{card.id}/edit', data = {
				'front': 'New Front', 'state': 'solved'})
		assert 200 == res.status_code
		solved_card = Card.query.filter_by(id = card.id).first()
		assert 'solved' == solved_card.state
		assert 'New Front' == solved_card.front

	def test_delete_card(self, card, login, client):
		login()
		res = client.post(f'/card/{card.id}/delete')
		assert 200 == res.status_code
		assert Card.query.filter_by(id = card.id).first() is None

	def test_get_cards(self, card, login, client):
		login()
		res = client.get('/cards')
		assert 200 == res.status_code
		assert 'Dynamic Programming' in res.get_data(as_text = True)

	def test_create_deck(self, user, login, client):
		login()
		group_response = client.post(
			'/deck', data = {
				'name': 'BFS', 'description': 'Breadth First Search',
				'user_id': user.id})
		assert 200 == group_response.status_code
		assert 'BFS', group_response.get_data(as_text = True)

	def test_get_deck(self, decks, login, client):
		login()
		res = client.get(f'deck/{decks[0].id}')
		assert 200 == res.status_code

	def test_edit_deck(self, decks, login, client):
		login()
		res = client.post(
			f'/deck/{decks[0].id}/edit', data = {'name': 'Algorythms'})
		assert res.status_code == 200
		assert 'Algorythms', res.get_data(as_text = True)

	def test_delete_deck(self, decks, login, client):
		login()
		res = client.post(
			f'/deck/{decks[0].id}/delete')
		assert 200 == res.status_code
		assert Deck.query.filter_by(id = decks[0].id).first() is None

	def test_get_decks(self, login, decks, client):
		login()
		res = client.get('/decks')
		assert 200 == res.status_code

	def test_create_study_plan(self, login, client):
		login()
		res = client.post('/plan', data = {
			'name': 'test_plan', 'description': 'test study plan', 'order': 'random'})
		assert 200 == res.status_code

	def test_get_study_plan(self, plan, login, client):
		login()
		res = client.get(f'/plan/{plan.id}')
		assert 200 == res.status_code

	def test_get_study_plans(self, plan, login, client):
		login()
		res = client.get('/plans')
		assert 200 == res.status_code

	def test_reset_deck(self, card, decks, login, client):
		login()
		res = client.post(f'/deck/{decks[1].id}/reset', data = {
			'state': 'solved'})
		assert 200 == res.status_code
		card = Card.query.filter_by(deck_id = decks[1].id).first()
		assert card.state == 'solved'

	def test_get_next_card(self, login, plan, decks, user, client, card):
		login()
		study_plan = StudyPlan.get_by_id(plan.id)
		card2 = Card(front = 'test', back = 'test', deck = decks[0], user = user)
		card2.save()
		res = client.post('/study_plan/next', data = {
			'study_plan_id': study_plan.id, 'deck_id': decks[1].id})
		assert 200 == res.status_code
		assert 'Dynamic Programming' in res.get_data(as_text = True)
