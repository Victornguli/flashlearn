from flask import request, jsonify, flash, g, abort, render_template
from sqlalchemy.sql.expression import func
from flashlearn.core import bp
from flashlearn.models import Card, Deck, StudyPlan
from flashlearn.decorators import login_required
from flashlearn.enums import OrderTypeEnum
from flashlearn.utils import to_bool


@bp.route("/card/<int:card_id>")
@login_required
def get_card(card_id):
    target_card = Card.query.filter_by(id=card_id).first()
    if target_card:
        return jsonify(target_card.to_json)
    flash("Failed to retrieve card")


@bp.route("/card", methods=("GET", "POST"))
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
        if Deck.query.filter_by(id=deck_id, state="active").first() is None:
            error += "\nSelected deck does not exist"
        if not error:
            new_card = Card(front=front, back=back, deck_id=deck_id, user_id=user.id)
            new_card.save()
            return jsonify("Success")
        return jsonify(error)


@bp.route("/card/<int:card_id>/edit", methods=("POST",))
@login_required
def edit_card(card_id):
    if request.method == "POST":
        state = request.form.get("state")
        if state.lower() not in ("active", "solved"):
            abort(400)
        card = Card.query.filter_by(id=card_id).first()
        if not card:
            abort(404)
        card.update(
            front=request.form.get("front", card.front),
            back=request.form.get("back", card.back),
            deck_id=request.form.get("deck_id", card.deck_id),
            state=state.lower(),
        )
        return jsonify("OK")
    return "Failed to update card"  # Render edit_card template instead...


@bp.route("/card/<int:card_id>/delete", methods=("POST",))
@login_required
def delete_card(card_id):
    if request.method == "POST":
        card = Card.query.filter_by(id=card_id)
        error = None
        if not card.first():
            error = "Card not found"
        if not error:
            card.first().delete()
            return jsonify("OK")
        return jsonify(error)
    return "Not Allowed"


@bp.route("/cards")
@login_required
def cards():
    if request.method == "GET":
        cards = Card.query.filter_by(user_id=g.user.id)
        return render_template("dashboard/cards/_cards.html", cards=cards)


@bp.route("/deck", methods=("POST", "GET"))
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
        )
        deck.save()
        return jsonify("Success")


@bp.route("/deck/<int:deck_id>", methods=("POST", "GET"))
@login_required
def get_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if request.method == "GET":
        return render_template("dashboard/decks/_deck.html", deck=deck)
    else:
        return jsonify(deck.to_json)


@bp.route("/deck/<int:deck_id>/edit", methods=("POST",))
@login_required
def edit_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    deck.update(
        name=request.form.get("name", deck.name),
        description=request.form.get("description", deck.description),
        parent_id=request.form.get("parent_id", deck.parent_id),
    )
    return jsonify("Success")


@bp.route("/deck/<int:deck_id>/delete", methods=("POST",))
@login_required
def delete_deck(deck_id):
    if request.method == "POST":
        deck = Deck.query.get_or_404(deck_id)
        deck.delete()
        return jsonify("success")


@bp.route("/decks", methods=("GET", "POST"))
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


@bp.route("/deck/<int:deck_id>/reset", methods=("GET", "POST"))
@login_required
def reset_deck(deck_id):
    state = request.form.get("state")
    if state not in ("active", "solved"):
        abort(400)
    deck = Deck.get_by_id(deck_id)
    if not deck:
        abort(400)
    cards = Card.query.filter_by(deck_id=deck.id)
    for card in cards:
        card.update(state=state)
    return jsonify("OK")


@bp.route("/plans", methods=("GET", "POST"))
@login_required
def study_plans():
    if request.method == "GET":
        study_plans = StudyPlan.query.filter_by(user_id=g.user.id)
        return render_template("dashboard/plans/_plans.html", study_plans=study_plans)
    else:
        plans = [plan.to_json for plan in StudyPlan.query.filter_by(user_id=g.user.id)]
        return jsonify(plans)


@bp.route("/plan/<int:plan_id>")
@login_required
def get_study_plan(plan_id):
    study_plan = StudyPlan.query.get_or_404(plan_id)
    return jsonify(study_plan.to_json)


@bp.route("/plan", methods=("GET", "POST"))
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


@bp.route("/plan/<int:plan_id>/delete", methods=["POST", "GET"])
@login_required
def delete_plan(plan_id):
    plan = StudyPlan.query.get_or_404(plan_id)
    plan.delete()
    return jsonify("OK")


@bp.route("deck/<int:deck_id>/study")
@login_required
def study_deck(deck_id):
    """Study a deck"""
    deck = Deck.query.get_or_404(deck_id)
    card = Card.query.filter_by(deck_id=deck_id, state="unknown").first()
    return render_template("dashboard/decks/_study.html", deck=deck, card=card)


@bp.route("study_plan/next", methods=("GET", "POST"))
@login_required
def get_next_card():
    study_plan_id = request.form.get("study_plan_id")
    deck_id = request.form.get("deck_id")
    deck = Deck.get_by_id(deck_id)
    study_plan = StudyPlan.get_by_id(study_plan_id)

    if not (study_plan and deck):
        abort(404)
    order = study_plan.order.value
    cards = Card.query.filter_by(deck_id=deck_id)
    if order == "latest":
        order_by = Card.id.desc()
    elif order == "oldest":
        order_by = Card.date_created.asc()
    else:
        order_by = func.random()

    card = cards.order_by(order_by).first()
    if card is not None:
        return jsonify(card.to_json)
    flash("You have studied all cards in this deck")
    return "OK"


@bp.route("deck/<int:deck_id>/add-cards", methods=("GET", "POST"))
@login_required
def add_cards(deck_id):
    """Add cards to a deck"""
    if request.method == "GET":
        deck = Deck.query.get_or_404(deck_id)
        return render_template("dashboard/decks/_add_cards.html", deck=deck)
    else:
        # Bulk add cards to the decks
        return jsonify("OK")
