from flask import request, url_for, jsonify, flash, g, redirect, abort
from sqlalchemy.sql.expression import func
from flashlearn.core import bp
from flashlearn.models import User, Card, Deck, StudyPlan
from flashlearn.decorators import login_required
from flashlearn.enums import OrderTypeEnum


@bp.route('/card', methods = ('POST',), defaults = {'card_id': None})
@bp.route('/card/<int:card_id>', methods = ('GET', 'POST'))
@login_required
def get_or_create_card(card_id):
	if request.method == 'GET':
		if card_id is not None:
			target_card = Card.query.filter_by(id = card_id).first()
			if target_card:
				return jsonify(target_card.to_json)
		flash('Failed to retrieve card')
	elif request.method == 'POST':
		front = request.form.get('front')
		back = request.form.get('back')
		deck_id = request.form.get('deck_id')
		user = g.user
		error = ''

		if not front or not back:
			error += f'front and back fields are required.'
		if not Deck.query.filter_by(id = deck_id, state = 'active').first():
			error += 'Selected deck does not exist'
		if not error:
			new_card = Card(
				front = front, back = back, deck_id = deck_id, user_id = user.id)
			new_card.save()
			return jsonify(new_card.to_json)
		return jsonify(error)
	return jsonify('OK')


@bp.route('/card/<int:card_id>/edit', methods = ('POST',))
def edit_card(card_id):
	if request.method == 'POST':
		state = request.form.get('state')
		if state.lower() not in ('active', 'solved'):
			abort(400)
		card = Card.query.filter_by(id = card_id).first()
		if not card:
			abort(404)
		card.update(
			front = request.form.get('front', card.front),
			back = request.form.get('back', card.back),
			deck_id = request.form.get('deck_id', card.deck_id),
			state = state.lower())
		return jsonify('OK')
	return 'Failed to update card'  # Render edit_card template instead...


@bp.route('/card/<int:card_id>/delete', methods = ('POST',))
def delete_card(card_id):
	if request.method == 'POST':
		card = Card.query.filter_by(id = card_id)
		error = None
		if not card.first():
			error = 'Card not found'
		if not error:
			card.first().delete()
			return jsonify('OK')
		return jsonify(error)
	return 'Not Allowed'


@bp.route('/cards')
@login_required
def list_cards():
	cards = Card.query.all()
	res = []
	for card in cards:
		res.append(card.to_json)
	return jsonify(res)


@bp.route('/deck', defaults = {'deck_id': None}, methods = ('POST',))
@bp.route('/deck/<int:deck_id>')
@login_required
def get_or_create_deck(deck_id):
	if request.method == 'GET':
		deck = Deck.query.filter_by(id = deck_id, state = 'active').first()
		if deck is not None:
			return jsonify(deck.to_json)
	elif request.method == 'POST':
		deck = Deck(
			name = request.form.get('name'), description = request.form.get('description'),
			user_id = g.user.id, parent_id = request.form.get('parent_id', None))
		deck.save()
		return jsonify(deck.to_json)
	return 'Deck not found'


@bp.route('/deck/<int:deck_id>/edit', methods = ('POST',))
def edit_deck(deck_id):
	deck = Deck.query.filter_by(id = deck_id, state = 'active').first()
	error = ''
	if not deck:
		error = 'Deck not found'
	if not error:
		deck.update(
			name = request.form.get('name', deck.name), description = request.form.get(
				'description', deck.description), parent_id = request.form.get('parent_id', deck.parent_id))
		deck.save()
		return jsonify(deck.to_json)
	return jsonify(error)


@bp.route('/deck/<int:deck_id>/delete', methods = ('POST',))
def delete_deck(deck_id):
	if request.method == 'POST':
		deck = Deck.query.filter_by(id = deck_id, state = 'active').first()
		error = ''
		if not deck:
			error = 'Deck not found'
		if not error:
			deck.delete()
			return jsonify('OK')
		return jsonify(error)
	return jsonify('Could not delete deck')


@bp.route('/decks', methods = ('GET', 'POST'))
def list_decks():
	decks = Deck.query.all()
	res = []
	for deck in decks:
		res.append(deck.to_json)
	return jsonify(res)


@bp.route('/deck/<int:deck_id>/reset', methods = ('GET', 'POST'))
def reset_deck(deck_id):
	state = request.form.get('state')
	if state not in ('active', 'solved'):
		abort(400)
	deck = Deck.get_by_id(deck_id)
	if not deck:
		abort(400)
	cards = Card.query.filter_by(deck_id = deck.id)
	for card in cards:
		card.update(state = state)
	return jsonify('OK')


@bp.route('/users')
def list_users():
	users = [user.to_json for user in User.all()]
	return jsonify(users)


@bp.route('/user/<int:user_id>')
def get_user(user_id):
	if request.method == 'GET':
		user = User.get_by_id(user_id)
		if user is None:
			return 'User not found', 404
		return jsonify(User.get_by_id(user_id).to_json)
	return jsonify('Invalid request ')


@bp.route('/plans', methods = ('GET', 'POST'))
def list_study_plans():
	plans = [plan.to_json for plan in StudyPlan.all()]
	return jsonify(plans)


@bp.route('/plan', methods = ('POST',), defaults = {'plan_id': None})
@bp.route('/plan/<int:plan_id>')
def get_or_create_study_plan(plan_id):
	if request.method == 'POST':
		order = request.form.get('order', None)
		if not hasattr(OrderTypeEnum, order):
			abort(400)

		study_plan = StudyPlan(
			name = request.form.get('name'), description = request.form.get('description', None),
			user_id = g.user.id, order = order
		)
		study_plan.save()
		return jsonify('Study Plan created successfully')
	elif request.method == 'GET':
		study_plan = StudyPlan.query.filter_by(id = plan_id).first()
		if not study_plan:
			abort(404)
		return jsonify(study_plan.to_json)
	return jsonify('study plan')


@bp.route('study_plan/next', methods = ('GET', 'POST'))
def get_next_card():
	study_plan_id = request.form.get('study_plan_id')
	deck_id = request.form.get('deck_id')
	deck = Deck.get_by_id(deck_id)
	study_plan = StudyPlan.get_by_id(study_plan_id)

	if not (study_plan and deck):
		abort(404)
	order = study_plan.order.value
	cards = Card.query.filter_by(deck_id = deck_id)
	if order == 'latest':
		order_by = Card.id.desc()
	elif order == 'oldest':
		order_by = Card.date_created.asc()
	else:
		order_by = func.random()

	card = cards.order_by(order_by).first()
	return jsonify(card.to_json)


@bp.route('user/<int:user_id>/delete', methods = ('GET', 'POST'))
def delete_user(user_id):
	user = User.query.filter_by(id = user_id, state = 'active').first()
	user.delete()
	return 'deleted'
