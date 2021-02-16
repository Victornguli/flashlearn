from flask_bcrypt import Bcrypt
from flashlearn.models import User, Card, Deck, StudyPlan, StudySession, StudySessionLog


class TestModels:
    """Test class for flashlearn models"""

    def test_user_model(self, client):
        """Client fixture is only used to provide app_context and create db tables"""
        u = User(username="admin", password="12345", email="admin@mail.com")
        u.save()
        assert u.password != "12345"
        assert u.state == "Active"
        u.password = Bcrypt().generate_password_hash("TheShrubbery@007").decode()
        u.save()
        assert u.password_is_valid("TheShrubbery@007"), "Should confirm password change"
        User.query.filter_by(username="admin").delete()
        assert (
            User.query.filter_by(username="admin").first() is None
        ), "Should delete the user"

    def test_deck_model(self, user, decks):
        child = Deck(
            name="Recursion",
            description="Recursive Algorithms",
            user=user,
            parent_id=decks[0].id,
        )
        child.save()
        assert child in user.decks, "Child deck should be available in the user's decks"
        assert (
            child in decks[0].children
        ), "Child deck should be available in parent's children"
        Deck.query.filter_by(name="Recursion").delete()
        assert (
            Deck.query.filter_by(name="Recursion").first() is None
        ), "Should delete the deck"

    def test_card_model(self, user, decks):
        test_card = Card(
            front="What is the air velocity of unladen swallow",
            back="African or European?",
            user_id=user.id,
            deck_id=decks[1].id,
        )
        test_card.save()
        assert test_card.state == "Active", "Should be saved with an Active state"
        test_card.update(state="Solved")
        assert test_card.state == "Solved", "State should be Solved"
        Card.query.filter_by(back="African or European?").first().delete()
        assert (
            Card.query.filter_by(back="African or European?").first() is None
        ), "Should delete the card"
        # self.db.session.expire(card)

    def test_study_plan_model(self, user):
        plan = StudyPlan(name="Grokking CS Algorithms", user=user)
        plan.save()
        assert plan.state == "Active", "Should create a plan with state Active"
        assert plan in user.study_plans, "Should be accessible from Alice's study plans"
        StudyPlan.query.filter_by(id=plan.id).delete()
        assert (
            StudyPlan.query.filter_by(id=plan.id).first() is None
        ), "Should be deleted"

    def test_study_session(self, user, decks):
        study_session = StudySession(deck_id=decks[0].id, user_id=user.id)
        study_session.save()
        assert study_session.state == "new", "Should create a new Study Session"
        assert (
            study_session.unknown == decks[0].card_count
        ), "Should create a new Study Session"
        StudySession.query.filter_by(id=study_session.id).delete()
        assert (
            StudySession.query.filter_by(id=study_session.id).first() is None
        ), "Should delete the study_session"

    def test_study_session_log(self, user, study_session, card):
        study_session_log = StudySessionLog(
            study_session_id=study_session.id, card_id=card.id
        )
        study_session_log.save()
        assert (
            study_session_log.state == "Active"
        ), "Should create a study session log with state Active"
        assert (
            study_session_log in study_session.study_session_logs
        ), "Should be accessible from StudySession's logs"
        StudySessionLog.query.filter_by(id=study_session_log.id).delete()
        assert (
            StudySessionLog.query.filter_by(id=study_session_log.id).first() is None
        ), "Should be deleted"
