import logging
from flask import abort
from sqlalchemy.orm import backref
from sqlalchemy.sql import func
from flask_bcrypt import Bcrypt
from werkzeug.http import http_date
from flashlearn import db
from flashlearn.enums import OrderTypeEnum

logger = logging.getLogger("flashlearn")


class TimestampedModel(db.Model):
    """Base model class for all timestamped models"""

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    date_updated = db.Column(
        db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    state = db.Column(db.String, default="active")

    def save(self):
        """
        Save an object to the database.
        """
        db.session.add(self)
        db.session.commit()

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        db.session.commit()

    def delete(self):
        db.session.delete(self.query.filter_by(id=self.id).first())
        db.session.commit()

    @classmethod
    def all(cls):
        return cls.query.filter(cls.state == "active")

    @classmethod
    def get_by_id(cls, _id):
        return cls.query.filter(cls.id == _id).first()

    @classmethod
    def get_by_user_or_404(cls, _id, _user_id):
        obj = cls.query.get(_id)
        if obj.id != _user_id:
            abort(404)
        return obj


class User(TimestampedModel):
    """User model class"""

    __tablename__ = "users"

    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256))

    def __init__(self, username=username, password=None, email=None):
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
            id=self.id,
            username=self.username,
            email=self.email,
            date_created=http_date(self.date_created),
            date_modified=http_date(self.date_updated),
            decks=[d.to_json for d in self.decks],
            study_plans=[p.to_json for p in self.study_plans],
            is_active=True if self.state == "active" else False,
        )

    def save(self):
        """
        Overrides default save method.
        """
        db.session.add(self)
        db.session.commit()
        Deck.create_default_deck(user_id=self.id)
        StudyPlan.create_default_study_plan(user_id=self.id)

    def __repr__(self):
        return f"<User: {self.username} - {self.state}>"


class Deck(TimestampedModel):
    """Deck model class"""

    __tablename__ = "decks"

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    parent_id = db.Column(db.Integer, db.ForeignKey("decks.id"))

    user = db.relationship(User, backref=backref("decks", cascade="all,delete"))
    children = db.relationship("Deck", cascade="all,delete")

    def __init__(self, **kwargs):
        """Initialize a Deck"""
        user = False
        for k, v in kwargs.items():
            if k == "user":
                user = True
        if user and "user_id" in kwargs:
            kwargs.pop("user_id")
        super(Deck, self).__init__(**kwargs)

    def save(self):
        if self.parent_id and Deck.query.filter_by(id=self.parent_id).first() is None:
            raise ValueError("Parent does not exist")
        db.session.add(self)
        db.session.commit()

    @property
    def to_json(self):
        return dict(
            id=self.id,
            name=self.name,
            description=self.description,
            user=self.user_id,
            parent=self.parent_id,
            child_count=self.child_count,
            card_count=self.card_count,
        )

    @property
    def children_to_json(self):
        return dict([child.to_json for child in self.children])

    @property
    def child_count(self):
        return len(self.children)

    @property
    def card_count(self):
        return len(self.cards)

    @classmethod
    def create_default_deck(cls, user_id):
        user = User.query.get_or_404(user_id)
        default_deck = Deck(name="Default", description="Default Deck", user=user)
        default_deck.save()
        return default_deck

    def delete(self):
        create_default = False
        user = User.query.filter_by(id=self.user_id).first()
        if user and len(user.decks) < 2:
            create_default = True
        db.session.delete(self.query.filter_by(id=self.id).first())
        db.session.commit()
        if create_default:
            self.create_default_deck(user_id=user.id)

    def __repr__(self):
        return f"<Deck: {self.name}>"


class Card(TimestampedModel):
    """Card model class"""

    __tablename__ = "cards"

    front = db.Column(db.Text(), nullable=False)
    back = db.Column(db.Text(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    deck_id = db.Column(db.Integer, db.ForeignKey("decks.id"), nullable=False)

    user = db.relationship(User, backref=backref("cards", cascade="all,delete"))
    deck = db.relationship(Deck, backref=backref("cards", cascade="all,delete"))

    def __init__(self, **kwargs):
        """Initialize a card"""
        super(Card, self).__init__(**kwargs)

    @property
    def short_front(self):
        if len(self.front) > 50:
            return self.front[:50]

    def __repr__(self):
        return (
            f"<Card: {self.short_front} - {self.user.username}" f" - {self.deck.name}>"
        )

    @property
    def to_json(self):
        return dict(
            id=self.id,
            front=self.front,
            back=self.back,
            short_front=self.short_front,
            user=self.user.to_json,
        )


class StudyPlan(TimestampedModel):
    """Study plan model class"""

    __tablename__ = "study_plans"

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String)
    order = db.Column(
        db.Enum(OrderTypeEnum), default=OrderTypeEnum.oldest, nullable=False
    )
    see_solved = db.Column(db.Boolean(), default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    user = db.relationship(User, backref=backref("study_plans", cascade="all,delete"))

    def __init__(self, **kwargs):
        """Initialize a study plan"""
        user = False
        for k, v in kwargs.items():
            if k == "user":
                user = True
        if user and "user_id" in kwargs:
            kwargs.pop("user_id")
        if "order" not in kwargs:
            kwargs["order"] = OrderTypeEnum.oldest
        super(StudyPlan, self).__init__(**kwargs)

    def __repr__(self):
        return f"<StudyPlan: {self.name} - {self.state}>"

    @property
    def to_json(self):
        return dict(
            id=self.id,
            name=self.name,
            description=self.description,
            user=self.user_id,
            order=self.order.value,
        )

    @classmethod
    def create_default_study_plan(cls, user_id):
        user = User.query.get_or_404(user_id)
        default_plan = StudyPlan(
            name="Default", description="Default Study Plan", user=user
        )
        default_plan.save()
        return default_plan

    def delete(self):
        create_default = False
        user = User.query.filter_by(id=self.user_id).first()
        if user and len(user.study_plans) < 2:
            create_default = True
        db.session.delete(self.query.filter_by(id=self.id).first())
        db.session.commit()
        if create_default:
            self.create_default_study_plan(user_id=user.id)


class StudySession(TimestampedModel):
    """
    Represents a study session. Keeps track of deck study progress
    """

    __tablename__ = "study_sessions"

    deck_id = db.Column(db.Integer, db.ForeignKey("decks.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    known = db.Column(db.Integer, nullable=True, default=0)
    unknown = db.Column(db.Integer, nullable=True)

    decks = db.relationship(
        Deck, backref=backref("study_sessions", cascade="all,delete")
    )

    def __init__(self, **kwargs):
        """Initialize a Study Session"""
        if 'unknown' not in kwargs.keys():
            deck = Deck.get_by_id(kwargs['deck_id'])
            kwargs['unknown'] = deck.card_count
        super(StudySession, self).__init__(**kwargs)

    def save(self):
        self.state = "new"
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f"<StudySession: {self.deck.name} - {self.state}>"


class StudySessionLog(TimestampedModel):
    """
    Tracks a study session. Records each card as a study session progresses
    """

    __tablename__ = "study_session_logs"

    study_session_id = db.Column(
        db.Integer, db.ForeignKey("study_sessions.id"), nullable=False
    )
    card_id = db.Column(db.Integer, db.ForeignKey("cards.id"), nullable=False)
    study_session = db.relationship(
        StudySession, backref=backref("study_session_logs", cascade="all,delete")
    )

    def __init__(self, **kwargs):
        """Initialize a Study Session Log"""
        super(StudySessionLog, self).__init__(**kwargs)

    def __repr__(self):
        return f"<StudySessionLog: {self.study_session.deck.name} - {self.state}>"
