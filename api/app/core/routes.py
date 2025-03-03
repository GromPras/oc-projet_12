import sentry_sdk
import sqlalchemy as sa
from flask import jsonify, request
from app import db
from app.core import bp
from app.models import Contract, ContractStatus, Role, User, Client, Event
from app.auth.auth import token_auth

# User views


# index [auth, admin]
@bp.route("/users", methods=["GET"])
@token_auth.login_required(role=["admin", "sales"])
def user_index():
    conditions = []
    filter_dept = request.args.get("dept")
    if filter_dept and filter_dept.upper() in Role._member_names_:
        conditions.append(User.role == Role(filter_dept))
    if conditions:
        users = db.session.scalars(sa.select(User).where(*conditions)).all()
    else:
        users = db.session.scalars(sa.select(User)).all()
    users = [user.serialize for user in users]
    return jsonify(users), 200


# create [auth, admin]
@bp.route("/users", methods=["POST"])
@token_auth.login_required(role="admin")
def user_create():
    data = request.get_json()
    required_fields = ["fullname", "email", "phone", "role", "password"]
    for field in required_fields:
        if field not in data:
            return {"error": "Bad request"}, 400
    if db.session.scalar(sa.select(User).where(User.email == data["email"])):
        # Don't return a clear message to avoid finding if email exists
        return {"error": "Bad request email"}, 400
    user = User()
    user.deserialize(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    sentry_sdk.capture_message(
        f"{token_auth.current_user().fullname} created a new user: {user.fullname}"
    )

    return user.serialize, 201


# TODO: keep all routes on same function or separate?


# show [auth, admin]
# update [auth, admin]
# destroy [auth, admin]
@bp.route("/users/<id>", methods=["GET", "PUT", "DELETE"])
@token_auth.login_required(role="admin")
def user_update(id):
    user = db.get_or_404(User, id)
    # Return one User
    if request.method == "GET":
        return user.serialize, 200
    # Update a User
    elif request.method == "PUT":
        data = request.get_json()
        allowed_fields = ["fullname", "email", "phone", "role", "password"]
        for field in allowed_fields:
            if field in data:
                if field == "password":
                    user.set_password(data[field])
                else:
                    setattr(user, field, data[field])
        db.session.commit()
        sentry_sdk.capture_message(
            f"{token_auth.current_user().fullname} updated a user: {user.fullname}"
        )
        return user.serialize, 200
    # Delete a User
    elif request.method == "DELETE":
        db.session.delete(user)
        db.session.commit()
        return {"message": "User removed"}, 200


# Client views


# index [auth]
# create [auth, sales]
@bp.route("/clients", methods=["GET", "POST"])
@token_auth.login_required()
def client_index():
    # Return all clients
    if request.method == "GET":
        clients = db.session.scalars(sa.select(Client).join(Client.sales_contact)).all()
        clients = [client.serialize for client in clients]
        return jsonify(clients)
    # Create a Client
    elif request.method == "POST":
        author = token_auth.current_user()
        if author:
            if not author.role == Role.SALES:
                return {"message": "You are not authorized to do this"}, 403

            data = request.get_json()
            required_fields = ["fullname", "email", "phone", "company"]
            for field in required_fields:
                if field not in data:
                    return {"error": "Bad request"}, 400
            if db.session.scalar(
                sa.select(Client).where(Client.email == data["email"])
            ):
                return {"error": "A client with that email already exists"}, 400
            client = Client()
            data["sales_contact"] = author
            client.deserialize(data)
            db.session.add(client)
            db.session.commit()

            return client.serialize, 201


# show [auth]
@bp.route("/clients/<id>", methods=["GET"])
@token_auth.login_required()
def client_show(id):
    client = db.get_or_404(Client, id)
    return jsonify(client.serialize), 200


# update [auth, author]
@bp.route("/clients/<id>", methods=["PUT", "DELETE"])
@token_auth.login_required(role="sales")
def client_update(id):
    client = db.get_or_404(Client, id)
    user = token_auth.current_user()
    if user and not user.id == client.sales_contact_id:
        return {"error": "You are not authorize to do this"}, 403
    else:
        # Update a User
        if request.method == "PUT":
            data = request.get_json()
            allowed_fields = [
                "fullname",
                "email",
                "phone",
                "company",
                "sales_contact_id",
            ]
            for field in allowed_fields:
                if field in data:
                    setattr(client, field, data[field])
            db.session.commit()
            return client.serialize, 200
        # Delete a User
        elif request.method == "DELETE":
            db.session.delete(client)
            db.session.commit()
            return {"message": "Client removed"}, 200


# Contract views


# index [auth]
@bp.route("/contracts", methods=["GET"])
@token_auth.login_required()
def contract_index():
    conditions = []
    filter_status = request.args.get("status")
    filter_remaining_amount = request.args.get("remaining-amount")
    if filter_status and filter_status.upper() in ContractStatus._member_names_:
        conditions.append(Contract.status == ContractStatus(filter_status))
    if filter_remaining_amount:
        conditions.append(Contract.remaining_amount > 0.0)
    if conditions:
        contracts = db.session.scalars(sa.select(Contract).where(*conditions)).all()
    else:
        contracts = db.session.scalars(sa.select(Contract)).all()

    contracts = [contract.serialize() for contract in contracts]

    return jsonify(contracts), 200


# show [auth]
@bp.route("/contracts/<id>", methods=["GET"])
@token_auth.login_required()
def contract_show(id):
    contract = db.get_or_404(Contract, id)
    return jsonify(contract.serialize()), 200


# create [auth, admin]
@bp.route("/contracts", methods=["POST"])
@token_auth.login_required(role="admin")
def contract_create():
    data = request.get_json()
    required_fields = ["client_id", "total_amount"]
    for field in required_fields:
        if field not in data:
            return {"error": "Bad request"}, 400
    client = db.get_or_404(Client, data["client_id"])
    contract = Contract()
    contract.deserialize(
        {
            "client_id": client.id,
            "sales_contact_id": client.sales_contact.id,
            "total_amount": data["total_amount"],
        }
    )
    db.session.add(contract)
    db.session.commit()

    return contract.serialize(), 201


# update [auth, admin]
# destroy [auth, author]
@bp.route("/contracts/<id>", methods=["PUT", "DELETE"])
@token_auth.login_required(role="admin")
def contract_update(id):
    contract = db.get_or_404(Contract, id)
    # Update a Contract
    contract_signed = False
    if request.method == "PUT":
        data = request.get_json()
        allowed_fields = [
            "total_amount",
            "remaining_amount",
            "status",
        ]
        for field in allowed_fields:
            if field in data:
                # convert status string to enum if set
                if field == "status":
                    if data[field] == "signed":
                        data[field] = ContractStatus.SIGNED
                        contract_signed = True
                setattr(contract, field, data[field])
        db.session.commit()
        if contract_signed:
            sentry_sdk.capture_message(
                f"{token_auth.current_user().fullname} signed a contract for: {contract.client.fullname} (contract: {contract.id})"
            )

        return contract.serialize(), 200
    # Delete a Contract
    if request.method == "DELETE":
        db.session.delete(contract)
        db.session.commit()
        return {"message": "Contract removed"}, 200


# Event views


# index [auth]
@bp.route("/events", methods=["GET"])
@token_auth.login_required()
def event_index():
    conditions = []
    filter_support = request.args.get("support")
    if filter_support:
        if filter_support == "none":
            conditions.append(Event.support_contact_id == None)
        if filter_support == "current-user":
            conditions.append(Event.support_contact_id == token_auth.current_user().id)
    if conditions:
        events = db.session.scalars(sa.select(Event).where(*conditions)).all()
    else:
        events = db.session.scalars(sa.select(Event)).all()
    events = [event.serialize for event in events]

    return jsonify(events), 200


# show [auth]
@bp.route("/events/<id>", methods=["GET"])
@token_auth.login_required()
def event_show(id):
    event = db.get_or_404(Event, id)
    return jsonify(event.serialize), 200


# create [auth, sales] => must be client_author && contract_status == 'signed'
@bp.route("/events", methods=["POST"])
@token_auth.login_required(role="sales")
def event_create():
    data = request.get_json()
    required_fields = [
        "title",
        "contract_id",
        "event_start",
        "event_end",
        "location",
        "attendees",
    ]
    for field in required_fields:
        if not field in data:
            return {"error": "Bad request"}, 400
    # make sure client exists, contract is related and current_user is in contact
    contract = db.get_or_404(Contract, data["contract_id"])
    current_user = token_auth.current_user()
    if (
        not contract.sales_contact_id == current_user.id
        or not contract.status.value == "signed"
    ):
        return {"error": "You are not authorized to do this"}, 403

    data["sales_contact_id"] = current_user.id
    data["client_id"] = contract.client.id
    event = Event()
    event.deserialize(data)
    db.session.add(event)
    db.session.commit()

    return event.serialize, 201


# update [auth, admin]
# add support_contact to event
@bp.route("/events/<id>/add-support", methods=["PUT"])
@token_auth.login_required(role="admin")
def event_add_support(id):
    event = db.get_or_404(Event, id)
    data = request.get_json()
    allowed_fields = ["support_contact_id"]
    support_contact = None
    for field in allowed_fields:
        if field in data:
            support_contact = db.get_or_404(User, data[field])
    if support_contact.role is not Role.SUPPORT:
        return {"error": "Bad request"}, 400
    setattr(event, "support_contact_id", support_contact.id)
    db.session.commit()
    return event.serialize, 200


# update [auth, sales]
@bp.route("/events/<id>", methods=["PUT"])
@token_auth.login_required(role="support")
def event_update(id):
    event = db.get_or_404(Event, id)
    current_user = token_auth.current_user()
    if not event.support_contact_id or event.support_contact_id is not current_user.id:
        return {"error": "You are not authorized to do this"}, 403

    data = request.get_json()
    allowed_fields = [
        "title",
        "event_start",
        "event_end",
        "location",
        "attendees",
        "notes",
    ]

    for field in allowed_fields:
        if field in data:
            setattr(event, field, data[field])
    db.session.commit()
    return event.serialize, 200


# destroy [auth, author]
@bp.route("/events/<id>", methods=["DELETE"])
@token_auth.login_required(role="sales")
def event_destroy(id):
    event = db.get_or_404(Event, id)
    current_user = token_auth.current_user()
    if current_user.id is not event.sales_contact_id:
        return {"error": "You are not authorized to do this"}, 403
    db.session.delete(event)
    db.session.commit()
    return {"message": "Event removed"}, 200
