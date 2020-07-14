from flask import request, url_for, jsonify, flash, g, redirect
from flashlearn.core import bp
from flashlearn.models import User, Card, Group, StudyPlan
from flashlearn.decorators import login_required
from flashlearn.utils import to_bool


# Card Routes
@bp.route('/card', methods = ('POST',), defaults = {'card_id': None})
@bp.route('/card/<int:card_id>', methods = ('GET', 'POST'))
@login_required
def get_or_create_card(card_id):
	if request.method == 'GET':
		if card_id is not None:
			target_card = Card.query.filter_by(id = card_id).first()
			if target_card:
				return jsonify(target_card.serialized)
		flash('Failed to retrieve card')
	elif request.method == 'POST':
		name = request.form.get('name')
		description = request.form.get('description')
		front = request.form.get('front')
		back = request.form.get('back')
		is_snippet = to_bool(request.form.get('is_snippet'))
		group_id = request.form.get('group_id')
		user = g.user
		error = ''

		if not name or not front or not back:
			error += f'name, front and back fields are required. '
		if not Group.query.filter_by(id = group_id, state = 'Active').first():
			error += 'Selected group does not exist'
		if not error:
			new_card = Card(
				name = name, description = description, front = front, back = back,
				is_snippet = is_snippet,  group_id = group_id, user_id = user.id
			)
			new_card.save()
			return jsonify(new_card.serialized)
		return jsonify(error)
	return jsonify('OK')


@bp.route('/card/<int:card_id>/edit', methods = ('POST',))
def edit_card(card_id):
	if request.method == 'POST':
		error = None
		card = Card.query.filter_by(id = card_id).first()
		if not card:
			error = 'Card does not exist '
		if not error:
			card.update(
				name = request.form.get('name', card.name),
				front = request.form.get('front', card.front),
				back = request.form.get('back', card.back),
				description = request.form.get('description', card.description),
				group_id = request.form.get('group_id', card.group_id),
				is_snippet = to_bool(request.form.get('is_snippet', card.is_snippet))
			)
			return jsonify('OK')
		flash(error)
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
def get_cards():
	cards = Card.query.all()
	res = []
	for card in cards:
		res.append(card.serialized)
	return jsonify(res)


@bp.route('/group', defaults = {'group_id': None}, methods = ('POST',))
@bp.route('/group/<int:group_id>')
@login_required
def get_or_create_group(group_id):
	if request.method == 'GET':
		group = Group.query.filter_by(id = group_id, state = 'Active').first()
		if group is not None:
			return jsonify(group.serialized)
	elif request.method == 'POST':
		group = Group(
			name = request.form.get('name'), description = request.form.get('description'),
			user_id = g.user.id, parent_id = request.form.get('parent_id', None))
		group.save()
		return jsonify(group.serialized)
	return 'Group not found'


@bp.route('/group/<int:group_id>/edit', methods = ('POST',))
def edit_group(group_id):
	group = Group.query.filter_by(id = group_id, state = 'Active').first()
	error = ''
	if not group:
		error = 'Group not found'
	if not error:
		group.update(
			name = request.form.get('name', group.name), description = request.form.get('description', group.description),
			parent_id = request.form.get('parent_id', group.parent_id))
		group.save()
		return jsonify(group.serialized)
	return jsonify(error)


@bp.route('/group/<int:group_id>/delete', methods = ('POST',))
def delete_group(group_id):
	if request.method == 'POST':
		group = Group.query.filter_by(id = group_id, state = 'Active').first()
		error = ''
		if not group:
			error = 'Group not found'
		if not error:
			group.delete()
			return jsonify('OK')
		return jsonify(error)
	return jsonify('Could not delete group')


@bp.route('/groups')
def get_groups():
	groups = Group.query.all()
	res = []
	for group in groups:
		res.append(group.serialized)
	return jsonify(res)
