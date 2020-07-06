from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from flashlearn.db import Base


class TimestampedModel(Base):
	"""Base class for all timestamped models"""
	__tablename__ = 'timestamped_model'
	id = Column(Integer, primary_key = True)
	date_created = Column(DateTime(timezone = True), server_default = func.now())
	date_updated = Column(DateTime(timezone = True), server_default = func.now(), onupdate = func.now())
	state = Column(String, default = 'Disabled')
