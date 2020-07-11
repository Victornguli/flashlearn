from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from flashlearn import db
from flask_bcrypt import Bcrypt


class TimestampedModel(db.Base):
	"""Base class for all timestamped models"""
	__abstract__ = True

	id = Column(Integer, primary_key = True)
	date_created = Column(DateTime(timezone = True), server_default = func.now())
	date_updated = Column(DateTime(timezone = True), server_default = func.now(), onupdate = func.now())
	state = Column(String, default = 'Active')

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


class BaseModel(TimestampedModel):
	"""A base model class implementing name and description fields"""
	__abstract__ = True

	name = Column(String(20), nullable = False, unique = True)
	description = Column(String(100))


class User(TimestampedModel):
	"""User model class"""
	__tablename__ = 'users'

	username = Column(String(50), nullable = False)
	password = Column(String(256), nullable = False)
	email = Column(String(256))

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

	def __repr__(self):
		return f'<User: {self.username} - {self.state}>'


class Group(BaseModel):
	"""Group model class"""
	__tablename__ = 'groups'

	user_id = Column(Integer, ForeignKey('users.id'))
	user = relationship('User', backref = 'user_groups')
	parent_id = Column(Integer, ForeignKey('groups.id'))
	children = relationship('Group')
	group_study_plans = relationship(
		'StudyPlanGroup', backref = 'group_study_plans', cascade = 'all, delete-orphan')

	def __init__(self, name, description, user_id = None, user = None, parent_id = None):
		"""Setup Group entry"""
		self.name = name
		self.description = description
		if user_id:
			self.user_id = user_id
		elif user:
			self.user = user
		self.parent_id = parent_id

	def __repr__(self):
		return f'<Group: {self.name}>'

	@property
	def serialized(self):
		return {
			'id': self.id,
			'name': self.name,
			'description': self.description,
			'user_id': self.user_id,
			'parent_id': self.parent_id
		}


class Card(BaseModel):
	"""Class for Card model"""
	__tablename__ = 'cards'

	front = Column(Text(), nullable = False)
	back = Column(Text(), nullable = False)
	is_snippet = Column(Boolean(), default = False)
	user_id = Column(Integer, ForeignKey('users.id'), nullable = False)
	user = relationship('User', backref = 'user_cards')  # usable via user.user_cards
	group_id = Column(Integer, ForeignKey('groups.id'), nullable = False)
	group = relationship('Group', backref = 'group_cards')  # usable via group.group_cards

	def __init__(
			self, name, front, back, user_id, group_id, description = None, is_snippet = False):
		"""Setup card instance"""
		self.name = name
		self.front = front
		self.back = back
		self.description = description
		self.is_snippet = is_snippet
		self.user_id = user_id
		self.group_id = group_id

	def __repr__(self):
		return f'<Card: {self.name} - {self.user.username} - {self.group.name}>'

	@property
	def serialized(self):
		return {
			'id': self.id,
			'name': self.name,
			# 'description': self.description,
			'front': self.front,
			'back': self.back,
			'is_snippet': self.is_snippet,
			'user_id': self.user_id,
			'group_id': self.group_id
		}


class StudyPlan(BaseModel):
	"""Study plan model class"""
	__tablename__ = 'study_plans'

	ordering = Column(String(10))
	see_solved = Column(Boolean(), default = False)
	user_id = Column(Integer, ForeignKey('users.id'))
	user = relationship('User', backref = 'user_study_plans')  # backref to user -> study_plans
	study_plan_groups = relationship(
		'StudyPlanGroup', backref = 'study_plan_groups', cascade = 'all, delete-orphan')

	def __init__(self, name, ordering = False, user_id = None, user = None):
		"""Initialize study plan instance"""
		self.name = name
		self.ordering = ordering
		if user_id:
			self.user_id = user_id
		elif user:
			self.user = user

	def __repr__(self):
		return f'<StudyPlan: {self.name} - {self.state}>'


class StudyPlanGroup(TimestampedModel):
	"""Many to Many through table for groups and study plans"""
	__tablename__ = 'study_plan_groups'

	group_id = Column(Integer, ForeignKey('groups.id'), nullable = False)
	study_plan_id = Column(Integer, ForeignKey('study_plans.id'), nullable = False)

	def __init__(self, group_id, study_plan_id):
		"""Initialize StudyPlanGroup association"""
		self.group_id = group_id
		self.study_plan_id = study_plan_id

	def __repr__(self):
		return f'<StudyPlanGroup: {self.study_plan.name} - {self.group.name}>'
