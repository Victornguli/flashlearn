import json
from flashlearn.models import Card, Deck, StudyPlan


class TestRoutes:
    """Flashlearn routes test class"""

    def test_create_card(self, user, decks, login, client):
        login()
        create_card_page = client.get("/card")
        assert create_card_page.status_code == 200, "Should retrieve create card page"

        res = client.post(
            "/card",
            data={
                "front": "front",
                "back": "back",
                "deck_id": decks[0].id,
                "user_id": user.id,
            },
        )
        assert 200 == res.status_code, "Should create card"

    def test_get_card(self, client, card, login):
        login()
        res = client.get(f"/card/{card.id}")
        assert 200 == res.status_code

    def test_edit_card(self, user, card, login, client):
        login()
        res = client.post(
            f"/card/{card.id}/edit", data={"front": "New Front", "state": "disabled"}
        )
        assert 200 == res.status_code
        solved_card = Card.query.filter_by(id=card.id).first()
        assert "disabled" == solved_card.state
        assert "New Front" == solved_card.front

    def test_delete_card(self, card, login, client):
        login()
        res = client.post(f"/card/{card.id}/delete")
        assert 200 == res.status_code
        assert Card.query.filter_by(id=card.id).first() is None

    def test_bulk_delete_cards(self, card, login, client):
        login()
        card_2 = Card(
            front="Test Front",
            back="Test back",
            user_id=card.user_id,
            deck_id=card.deck_id,
        )
        card_2.save()
        res = client.post(
            "/card/bulk/delete",
            data=json.dumps({"data": [card.id, card_2.id]}),
            content_type="application/json",
        )
        assert 200 == res.status_code, "Should return a 200 status code"
        assert Card.query.filter_by(id=card.id).first() is None
        assert Card.query.filter_by(id=card_2.id).first() is None

    def test_get_cards(self, card, login, client):
        login()
        res = client.get("/cards")
        assert 200 == res.status_code
        assert "Dynamic Programming" in res.get_data(as_text=True)

    def test_create_deck(self, user, login, client):
        login()
        create_page = client.get("/deck")
        assert create_page.status_code == 200

        deck_response = client.post(
            "/deck",
            data={
                "name": "BFS",
                "description": "Breadth First Search",
                "user_id": user.id,
            },
        )
        assert 200 == deck_response.status_code
        assert "BFS", deck_response.get_data(as_text=True)

    def test_get_deck(self, client, login, decks):
        login()
        res = client.get(f"deck/{decks[0].id}")
        assert 200 == res.status_code

    def test_edit_deck(self, decks, login, client):
        login()
        res = client.post(f"/deck/{decks[0].id}/edit", data={"name": "Algorythms"})
        assert res.status_code == 200
        assert "Algorythms", res.get_data(as_text=True)

    def test_delete_deck(self, decks, login, client):
        login()
        res = client.post(f"/deck/{decks[0].id}/delete")
        assert 200 == res.status_code
        assert Deck.query.filter_by(id=decks[0].id).first() is None

    def test_get_decks(self, login, decks, client):
        login()
        decks_page = client.get("/decks")
        assert 200 == decks_page.status_code
        ajax_decks = client.post("/decks")
        assert 200 == ajax_decks.status_code

    def test_create_study_plan(self, login, client):
        login()
        create_page_res = client.get("/plan")
        assert 200 == create_page_res.status_code, "Should retrieve create plan page"
        res = client.post(
            "/plan",
            data={
                "name": "test_plan",
                "description": "test study plan",
                "order": "random",
            },
        )
        assert 200 == res.status_code

    # def test_edit_study_plan(self, login, client, plan):
    #     login()
    #     create_page_res = client.get("/plan")
    #     assert 200 == create_page_res.status_code, "Should retrieve create plan page"
    #     res = client.post(
    #         f"/plan/{plan.id}/edit",
    #         data={
    #             "name": "New Study Plan",
    #             "description": "Random Study Plan",
    #             "order": "random",
    #         },
    #     )
    #     assert 200 == res.status_code
    #     assert StudyPlan.query.get(plan.id).name == "New Study Plan"

    def test_get_study_plan(self, plan, login, client):
        login()
        res = client.get(f"/plan/{plan.id}")
        assert 200 == res.status_code

    def test_get_study_plans(self, plan, login, client):
        login()
        res = client.get("/plans")
        rest_res = client.post("plans")
        assert 200 == res.status_code, "Should return plans page"
        assert 200 == rest_res.status_code, "Should fetch plans as json"

    @staticmethod
    def test_delete_study_plan(plan, login, client):
        login()
        res = client.get(f"/plan/{plan.id}/delete")
        assert res.status_code == 200
        assert StudyPlan.query.filter_by(id=plan.id).first() is None

    def test_reset_deck(self, card, decks, login, client):
        login()
        res = client.post(f"/deck/{decks[1].id}/reset", data={"state": "solved"})
        assert 200 == res.status_code
        card = Card.query.filter_by(deck_id=decks[1].id).first()
        assert card.state == "solved"

    def test_study_deck(self, card, decks, login, client):
        login()

        res = client.get(f"/deck/{decks[1].id}/study")
        assert 200 == res.status_code

    def test_get_next_card(self, login, card, plan, decks, study_session, client):
        login()
        res = client.post(
            f"deck/{decks[0].id}/study/{study_session.id}/next",
        )

        assert 200 == res.status_code

    def test_add_cards_to_deck(self, decks, login, client):
        login()
        res = client.get(f"/deck/{decks[1].id}/add-cards")
        assert 200 == res.status_code
