from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from flashlearn.db import Base
from flask_bcrypt import Bcrypt

from flashlearn.db import db_session


class TimestampedModel(Base):
	"""Base class for all timestamped models"""
	__abstract__ = True

	id = Column(Integer, primary_key = True)
	date_created = Column(DateTime(timezone = True), server_default = func.now())
	date_updated = Column(DateTime(timezone = True), server_default = func.now(), onupdate = func.now())
	state = Column(String, default = 'Active')

	def save(self):
		"""Save a user to a database. This includes creating a new user and editing too"""
		db_session.add(self)
		db_session.commit()


class User(TimestampedModel):
	"""User model class"""
	__tablename__ = 'users'

	username = Column(String(50), nullable = False)
	password = Column(String(256), nullable = False)
	email = Column(String(256))

	def __init__(self, username, password, email = None):
		"""Initialize new user model"""
		self.username = username
		self.password = Bcrypt().generate_password_hash(password).decode()
		self.email = email

	def password_is_valid(self, password):
		"""Checks a submitted password against its stored hash"""
		return Bcrypt().check_password_hash(self.password, password)

	def __repr__(self):
		return f'<User: {self.username} - {self.state}>'


class Group(TimestampedModel):
	"""Group model class"""
	__tablename__ = 'groups'

	name = Column(String(20), nullable = False)
	description = Column(String(20), nullable = False)
	user_id = Column(Integer, ForeignKey('users.id'), nullable = True)
	user = relationship('User', backref = 'users')
	parent_id = Column(Integer, ForeignKey('groups.id'), nullable = True)
	children = relationship('Group')

	def __init__(self, name, description, user_id = None, parent_id = None):
		"""Setup Group entry"""
		self.name = name
		self.description = description
		self.user_id = user_id
		self.parent_id = parent_id

	def __repr__(self):
		children = [i.name for i in self.children] if self.children else []
		return f'<Group: {self.name} - {children}>'
