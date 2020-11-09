from flashlearn.models import User


class TestUserRoutes:
    """Flashlearn user routes test class"""

    def test_get_users(self, login, client):
        login()
        res = client.get("/user/list")
        assert 200 == res.status_code
        assert "alice" in res.get_data(as_text=True)

    def test_get_user(self, login, client, user):
        login()
        res = client.get(f"/user/{user.id}")
        assert 200 == res.status_code
        assert "alice" in res.get_data(as_text=True)

    def test_get_user_fail(self, login, client):
        login()
        res = client.get(f"/user/{10}")
        assert 404 == res.status_code, "Should return 404 if user is not found"

    def test_edit_user(self, login, client):
        login()
        user = User(username="test", email="test@mail.com", password="test")
        user.save()
        res = client.post(
            f"/user/{user.id}/edit",
            data={"password": "test", "email": "new_mail@test.com"},
        )
        assert 200 == res.status_code
        user = User.query.filter_by(id=user.id).first()
        assert "new_mail@test.com" == user.email

    def test_delete_user(self, user, login, client):
        login()
        user = User(username="test", email="test", password="test")
        user.save()
        assert "test" == user.username, "Should save user"
        res = client.get(f"/user/{user.id}/delete")
        assert 200 == res.status_code, "Should return 200 status"
        assert (
            User.query.filter_by(username="test").first() is None
        ), "Query should return None"
