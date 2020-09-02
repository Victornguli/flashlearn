import logging
from sqlalchemy import event
from sqlalchemy.orm import backref
from sqlalchemy.sql import func
from flask_bcrypt import Bcrypt
from werkzeug.http import http_date
from flashlearn import db
from flashlearn.enums import OrderTypeEnum

logger = logging.getLogger('flashlearn')


class TimestampedModel(db.Model):
	"""Base model class for all timestamped models"""
	__abstract__ = True

	id = db.Column(db.Integer, primary_key = True)
	date_created = db.Column(db.DateTime(timezone = True), server_default = func.now())
	date_updated = db.Column(db.DateTime(timezone = True), server_default = func.now(), onupdate = func.now())
	state = db.Column(db.String, default = 'active')

	def save(self):
		"""Save a user to a database. This includes creating a new user and editing too"""
		db.session.add(self)
		db.session.commit()

	def update(self, **kwargs):
		for k, v in kwargs.items():
			setattr(self, k, v)
		db.session.commit()

	def delete(self):
		db.session.delete(self.query.filter_by(id = self.id).first())
		db.session.commit()

	@classmethod
	def all(cls):
		return cls.query.filter(cls.state == 'active')

	@classmethod
	def get_by_id(cls, _id):
		return cls.query.filter(cls.id == _id).first()


class User(TimestampedModel):
	"""User model class"""
	__tablename__ = 'users'

	username = db.Column(db.String(50), nullable = False)
	password = db.Column(db.String(256), nullable = False)
	email = db.Column(db.String(256))

	def __init__(self, username, password = None, email = None):
		"""Initialize new user model"""
		self.username = username
		if password:
			self.password = Bcrypt().generate_password_hash(password).decode()
		self.email = email

	def password_is_valid(self, password):
		"""Checks a submitted password against its stored hash"""
		return Bcrypt().check_password_hash(self.password, password)

	def set_password(self, password):
		"""Set password"""
		self.password = Bcrypt().generate_password_hash(password).decode()

	@property
	def to_json(self):
		return dict(
			id = self.id, username = self.username, email = self.email,
			date_created = http_date(self.date_created), date_modified = http_date(self.date_updated),
			decks = [d.to_json for d in self.decks],
			study_plans = [p.to_json for p in self.study_plans],
			is_active = True if self.state == 'active' else False)

	def __repr__(self):
		return f'<User: {self.username} - {self.state}>'


class Deck(TimestampedModel):
	"""Deck model class"""
	__tablename__ = 'decks'

	name = db.Column(db.String(100), nullable = False)
	description = db.Column(db.String)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	parent_id = db.Column(db.Integer, db.ForeignKey('decks.id'))

	user = db.relationship(User, backref = backref('decks', cascade = 'all,delete'))
	children = db.relationship('Deck', cascade = 'all,delete')

	def __init__(self, name, description, user_id = None, user = None, parent_id = None):
		"""Initialize a Deck"""
		self.name = name
		self.description = description
		if user_id:
			self.user_id = user_id
		elif user:
			self.user = user
		self.parent_id = parent_id

	def save(self):
		if self.parent_id and Deck.query.filter_by(id = self.parent_id).first() is None:
			raise ValueError('Parent does not exist')
		db.session.add(self)
		db.session.commit()

	@property
	def to_json(self):
		return dict(
			id = self.id, name = self.name, description = self.description,
			user = self.user_id, parent = self.parent_id,
			child_count = self.child_count)

	@property
	def children_to_json(self):
		return dict([child.to_json for child in self.children])

	@property
	def child_count(self):
		return len(self.children)

	def __repr__(self):
		return f'<Deck: {self.name}>'


class Card(TimestampedModel):
	"""Card model class"""
	__tablename__ = 'cards'

	front = db.Column(db.Text(), nullable = False)
	back = db.Column(db.Text(), nullable = False)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
	deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), nullable = False)

	user = db.relationship(User, backref = backref('cards', cascade = 'all,delete'))
	deck = db.relationship(Deck, backref = backref('cards', cascade = 'all,delete'))

	def __init__(self, **kwargs):
		"""Initialize a card"""
		super(Card, self).__init__(**kwargs)

	def __repr__(self):
		return f'<Card: {self.name} - {self.user.username} - {self.group.name}>'

	@property
	def to_json(self):
		return dict(
			id = self.id, front = self.front, back = self.back, user = self.user.to_json)


class StudyPlan(TimestampedModel):
	"""Study plan model class"""
	__tablename__ = 'study_plans'

	name = db.Column(db.String(100), nullable = False)
	description = db.Column(db.String)
	order = db.Column(db.Enum(OrderTypeEnum), default = OrderTypeEnum.oldest, nullable = False)
	see_solved = db.Column(db.Boolean(), default = False)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

	user = db.relationship(User, backref = backref('study_plans', cascade = 'all,delete'))

	def __init__(
			self, name,
			description = None,
			order = OrderTypeEnum.oldest,
			user_id = None,
			user = None
	):
		"""Initialize a study plan"""
		self.name = name
		self.order = order
		self.description = description
		if user_id:
			self.user_id = user_id
		elif user:
			self.user = user

	def __repr__(self):
		return f'<StudyPlan: {self.name} - {self.state}>'

	@property
	def to_json(self):
		return dict(
			id = self.id, name = self.name, description = self.description,
			user = self.user_id, order = self.order.value)


@event.listens_for(User, 'after_insert')
def add_defaults_on_user_create(mapper, connection, target):
	assert target.id is not None
	if not target.decks:
		deck = Deck.__table__
		connection.execute(
			deck.insert().values(
				name = 'Default', description = 'Default Deck', user_id = target.id
			))

	if not target.study_plans:
		study_plan = StudyPlan.__table__
		connection.execute(
			study_plan.insert().values(
				name = 'Default', description = 'Default Study Plan', user_id = target.id
			))


@event.listens_for(Deck, 'after_delete')
def set_default_deck_on_delete(mapper, connection, target):
	assert target.id is not None
	if len(target.user.decks) == 0:
		deck = Deck.__table__
		connection.execute(
			deck.insert().values(
				name = 'Default', description = 'Default Deck', user_id = target.id
			))


@event.listens_for(StudyPlan, 'after_delete')
def set_default_plan_on_delete(mapper, connection, target):
	assert target.id is not None
	if len(target.user.study_plans) == 0:
		deck = Deck.__table__
		connection.execute(
			deck.insert().values(
				name = 'Default', description = 'Default Deck', user_id = target.id
			))
