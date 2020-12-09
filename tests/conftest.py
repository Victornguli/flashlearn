import pytest
from flashlearn.models import User, Card, Deck, StudyPlan, StudySession, StudySessionLog
from flashlearn import create_app, db


@pytest.fixture
def test_app():
    """Fixture that serves the app within test env"""
    return create_app("testing")


@pytest.fixture
def client(test_app):
    """Pytest Fixture that serves the test_client"""
    with test_app.app_context():
        db.create_all()
        yield test_app.test_client()


@pytest.fixture
def user(client) -> User:
    alice = User(username="alice", email="alice@email.com")
    alice.set_password("password")
    alice.save()
    return alice


@pytest.fixture
def super_user(client) -> User:
    bob = User(username="bob", email="bob@email.com")
    bob.set_password("password")
    bob.is_superuser = True
    bob.save()
    return bob


@pytest.fixture
def decks(client, user):
    algos = Deck(
        name="Algorithms",
        description="Common Algorithms in Computer Science",
        user=user,
    )
    algos.save()
    dp = Deck(
        name="DP", description="Dynamic Programming", user=user, parent_id=algos.id
    )
    dp.save()
    return algos, dp


@pytest.fixture
def card(client, decks, user):
    back = (
        "Dynamic Programming (DP) is an algorithmic technique for solving and"
        "optimization problem by breaking it down into simpler subproblems and"
        "utilizing the fact that the optimal solution to the overall problem"
        "depends upon the optimal solution to its subproblems."
    )
    card = Card(
        front="What is dynamic programming",
        back=back,
        user_id=user.id,
        deck_id=decks[1].id,
    )
    card.save()
    return card


@pytest.fixture
def plan(client, user):
    plan = StudyPlan(name="Grokking Algorithms", user=user)
    plan.save()
    return plan


@pytest.fixture
def study_session(client, user, decks):
    study_session = StudySession(deck_id=decks[0].id, user_id=user.id)
    study_session.save()
    return study_session


@pytest.fixture
def study_session_log(client, card, study_session):
    study_session_log = StudySessionLog(
        study_session_id=study_session.id, card_id=card.id
    )
    study_session_log.save()
    return study_session_log


@pytest.fixture
def login(client, user, super_user):
    def inner(username=None, password=None):
        if not (username and password):
            username = user.username
            password = "password"
        return client.post(
            "/user/login",
            data=dict(username=username, password=password),
            follow_redirects=True,
        )

    return inner


@pytest.fixture
def logout(client):
    def inner():
        return client.post("/user/logout")

    return inner
