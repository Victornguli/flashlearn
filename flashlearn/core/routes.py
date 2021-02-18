from flask import request, jsonify, g, abort, render_template, session
from sqlalchemy import or_
from flashlearn.core import core
from flashlearn.models import Card, Deck, StudyPlan, StudySession, StudySessionLog
from flashlearn.decorators import login_required
from flashlearn.enums import OrderTypeEnum
from flashlearn.utils import to_bool

from flashlearn import db


@core.route("/card/<int:card_id>")
@login_required
def get_card(card_id):
    target_card = Card.get_by_user_or_404(card_id, g.user.id)
    return jsonify(target_card.to_json)


@core.route("/card", methods=("GET", "POST"))
@login_required
def create_card():
    if request.method == "GET":
        decks = Deck.query.filter_by(user_id=g.user.id)
        error = ""
        if decks is None:
            error += "You have not created any deck yet."
        return render_template("dashboard/cards/_create.html", decks=decks, error=error)
    else:
        front = request.form.get("front")
        back = request.form.get("back")
        deck_id = request.form.get("deck_id")
        user = g.user
        error = ""

        if not front or not back or not deck_id:
            error += "front back and deck_id fields are required."
        if Deck.query.filter_by(id=deck_id).first() is None:
            error += "\nSelected deck does not exist"
        if not error:
            new_card = Card(
                front=front,
                back=back,
                deck_id=deck_id,
                user_id=user.id,
                state="Active",
            )
            new_card.save()
            return jsonify("Success")
        return jsonify(error)


@core.route("/card/bulk/add/<int:deck_id>", methods=("POST",))
@login_required
def bulk_add_cards(deck_id):
    data = request.get_json().get("data", [])
    cards = []
    for card in data:
        cards.append(
            Card(
                front=card["front"],
                back=card["back"],
                deck_id=deck_id,
                user_id=g.user.id,
            )
        )
    db.session.bulk_save_objects(cards)
    db.session.commit()
    return jsonify({"status": 1, "message": "Cards added successfully"})


@core.route("/card/<int:card_id>/edit", methods=("POST",))
@login_required
def edit_card(card_id):
    if request.method == "POST":
        card = Card.get_by_user_or_404(card_id, g.user.id)
        state = request.form.get("state", card.state)
        if state not in ("Active", "Disabled"):
            abort(400)
        card.update(
            front=request.form.get("front", card.front),
            back=request.form.get("back", card.back),
            deck_id=request.form.get("deck_id", card.deck_id),
            state=state,
        )
        return jsonify("OK")


@core.route("/card/<int:card_id>/delete", methods=("POST",))
@login_required
def delete_card(card_id):
    if request.method == "POST":
        card = Card.get_by_user_or_404(card_id, g.user.id)
        card.delete()
        return jsonify({"status": 1, "message": "Card deleted successfully"})


@core.route("/card/bulk/delete", methods=("POST",))
@login_required
def bulk_delete_cards():
    """Bulk delete cards"""
    if request.method == "POST":
        data = request.get_json().get("data", [])
        for card_id in data:
            card = Card.get_by_user_or_404(card_id, g.user.id)
            card.delete()
        return jsonify({"status": 1, "message": "Cards deleted successfully"})


@core.route("/cards")
@login_required
def cards():
    if request.method == "GET":
        cards = Card.query.filter_by(user_id=g.user.id)
        return render_template("dashboard/cards/_cards.html", cards=cards)


@core.route("/deck", methods=("POST", "GET"))
@login_required
def create_deck():
    if request.method == "GET":
        return render_template("dashboard/decks/_create.html")
    elif request.method == "POST":
        deck = Deck(
            name=request.form.get("name"),
            description=request.form.get("description"),
            user_id=g.user.id,
            parent_id=request.form.get("parent_id", None),
            state="New",
        )
        deck.save()
        return jsonify("Success")


@core.route("/deck/<int:deck_id>", methods=("POST", "GET"))
@login_required
def get_deck(deck_id):
    deck = Deck.get_by_user_or_404(deck_id, g.user.id)
    if request.method == "GET":
        return render_template("dashboard/decks/_deck.html", deck=deck)
    else:
        return jsonify(deck.to_json)


@core.route("/deck/<int:deck_id>/edit", methods=("POST",))
@login_required
def edit_deck(deck_id):
    deck = Deck.get_by_user_or_404(deck_id, g.user.id)
    deck.update(
        name=request.form.get("name", deck.name),
        description=request.form.get("description", deck.description),
        parent_id=request.form.get("parent_id", deck.parent_id),
    )
    return jsonify("Success")


@core.route("/deck/<int:deck_id>/delete", methods=("POST",))
@login_required
def delete_deck(deck_id):
    if request.method == "POST":
        deck = Deck.query.get_or_404(deck_id)
        deck.delete()
        return jsonify({"status": 1, "message": "Deck deleted succesfully"})


@core.route("/deck/bulk/delete", methods=("POST",))
@login_required
def bulk_delete_decks():
    """Bulk delete decks"""
    if request.method == "POST":
        data = request.get_json().get("data", [])
        for deck_id in data:
            deck = Deck.get_by_user_or_404(deck_id, g.user.id)
            deck.delete()
        return jsonify({"status": 1, "message": "Decks deleted succesfully"})


@core.route("/decks", methods=("GET", "POST"))
@login_required
def decks():
    decks = Deck.query.filter_by(user_id=g.user.id)
    if request.method == "GET":
        return render_template("dashboard/decks/_decks.html", decks=decks)
    elif request.method == "POST":
        res = []
        for deck in decks:
            res.append(deck.to_json)
        return jsonify(res)


@core.route("/deck/<int:deck_id>/reset", methods=("GET", "POST"))
@login_required
def reset_deck(deck_id):
    state = request.form.get("state")
    if state not in ("active", "solved"):
        abort(400)
    deck = Deck.get_by_user_or_404(deck_id, g.user.id)
    cards = Card.query.filter_by(deck_id=deck.id)
    for card in cards:
        card.update(state=state)
    return jsonify("OK")


@core.route("/plans", methods=("GET", "POST"))
@login_required
def study_plans():
    if request.method == "GET":
        study_plans = StudyPlan.query.filter_by(user_id=g.user.id)
        return render_template("dashboard/plans/_plans.html", study_plans=study_plans)
    else:
        plans = [plan.to_json for plan in StudyPlan.query.filter_by(user_id=g.user.id)]
        return jsonify(plans)


@core.route("/plan/<int:plan_id>")
@login_required
def get_study_plan(plan_id):
    study_plan = StudyPlan.get_by_user_or_404(plan_id, g.user.id)
    return jsonify(study_plan.to_json)


@core.route("/plan", methods=("GET", "POST"))
@login_required
def create_study_plan():
    if request.method == "GET":
        return render_template("dashboard/plans/_create.html")
    else:
        order = request.form.get("order", None)
        if order is None or not hasattr(OrderTypeEnum, order):
            abort(400)

        study_plan = StudyPlan(
            name=request.form.get("name"),
            description=request.form.get("description", None),
            user_id=g.user.id,
            order=order,
            see_solved=to_bool(request.form.get("see_solved", False)),
        )
        study_plan.save()
        return jsonify("Success")


@core.route("/plan/<int:plan_id>/delete", methods=["POST", "GET"])
@login_required
def delete_plan(plan_id):
    plan = StudyPlan.query.get_or_404(plan_id)
    plan.delete()
    return jsonify({"status": 1, "message": "Study Plan deleted successfully"})


@core.route("deck/<int:deck_id>/study")
@login_required
def study_deck(deck_id):
    """Study a deck"""
    deck = Deck.get_by_user_or_404(deck_id, g.user.id)
    study_session = (
        db.session.query(StudySession)
        .filter(
            StudySession.deck_id == deck.id,
            StudySession.user_id == g.user.id,
            or_(StudySession.state == "Studying"),
        )
        .first()
    )
    if study_session is None:
        study_session = StudySession(
            user_id=g.user.id,
            deck_id=deck.id,
            known=0,
            unknown=0,
            state="Studying",
        )
        study_session.save()
        deck.state = "Studying"
        deck.save()
    first_card = Card.get_next_card(study_session.id, deck_id)
    session["active_study_session"] = study_session.to_json
    session["active_deck"] = deck.to_json
    if first_card:
        session["active_card"] = first_card.to_json
    return render_template(
        "dashboard/decks/_study.html",
        deck=deck.to_json,
        study_session=study_session,
        first_card=first_card,
    )


@core.route("deck/<int:deck_id>/study/<int:study_session_id>/next", methods=["POST"])
@login_required
def get_next_study_card(deck_id, study_session_id):
    if request.method == "POST":
        study_session = StudySession.get_by_user_or_404(study_session_id, g.user.id)
        if study_session.state != "Studying":
            abort(400)
        deck = Deck.get_by_user_or_404(deck_id, g.user.id)
        card_state = request.form.get("state", "")
        card_id = request.form.get("card_id", None)
        if card_state not in ("Known", "Unknown") or not card_id:
            abort(400)
        # Create a study session log and update the study_session
        log = StudySessionLog(
            study_session_id=study_session_id, card_id=card_id, state=card_state
        )
        log.save()
        if card_state == "Known":
            study_session.update(known=study_session.known + 1)
        else:
            study_session.update(unknown=study_session.unknown + 1)
        session["active_deck"] = deck.to_json
        session["active_study_session"] = study_session.to_json
        next_card = Card.get_next_card(study_session_id, deck_id)
        status, data = 0, {
            "active_deck": deck.to_json,
            "active_study_session": study_session.to_json,
            "active_card": None,
        }
        markup = None
        if next_card is not None:
            data["active_card"] = next_card.to_json
            status = 1
            message = "Study Session Studying"
            session["active_card"] = next_card.to_json
            session["previous_study_session"] = None
        else:
            deck.update(state="Complete")
            study_session.update(state="Complete")
            session["active_card"] = None
            message = "Study Session Complete"
            markup = render_template(
                "dashboard/decks/partials/session_stats.html",
                previous_study_session=study_session,
            )
        return jsonify(
            {"status": status, "message": message, "data": data, "markup": markup}
        )


@core.route("deck/<int:deck_id>/add-cards", methods=("GET",))
@login_required
def add_cards(deck_id):
    """Add cards to a deck"""
    if request.method == "GET":
        deck = Deck.query.get_or_404(deck_id)
        return render_template("dashboard/decks/_add_cards.html", deck=deck)
