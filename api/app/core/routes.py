import sqlalchemy as sa
from flask import jsonify, request
from app import db
from app.core import bp
from app.models import Contract, ContractStatus, Role, User, Client
from app.auth.auth import token_auth


# User views


# index [auth, admin]
@bp.route("/users", methods=["GET"])
@token_auth.login_required(role="admin")
def user_index():
    stmt = db.select(User)
    users = db.session.execute(stmt).scalars().all()
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

    return user.serialize, 201


# TODO: keep all routes on same function or separate?


# show [auth, admin]
# update [auth, admin]
# destroy [auth, admin]
@bp.route("/users/<id>", methods=["GET", "PUT", "DELETE"])
@token_auth.login_required(role="admin")
def user_update(id):
    user = db.get_or_404(User, id)
    if request.method == "GET":
        return user.serialize, 200
    elif request.method == "PUT":
        data = request.get_json()
        allowed_fields = ["fullname", "email", "phone", "role"]
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        db.session.commit()
        return user.serialize, 200
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
    if request.method == "GET":
        clients = db.session.scalars(sa.select(Client).join(Client.sales_contact)).all()
        clients = [client.serialize for client in clients]
        return jsonify(clients)
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
    client = db.session.scalar(sa.select(Client).where(Client.id == id))
    if not client:
        return {"error": "Client doesn't exists"}, 404
    user = token_auth.current_user()
    if user and not user.id == client.sales_contact_id:
        return {"error": "You are not authorize to do this"}, 403
    else:
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
        elif request.method == "DELETE":
            db.session.delete(client)
            db.session.commit()
            return {"message": "Client removed"}, 200


# Contract views


# index [auth]
@bp.route("/contracts", methods=["GET"])
@token_auth.login_required()
def contract_index():
    contracts = db.session.scalars(sa.select(Contract)).all()
    contracts = [contract.serialize for contract in contracts]

    return jsonify(contracts), 200


# show [auth]
@bp.route("/contracts/<id>", methods=["GET"])
@token_auth.login_required()
def contract_show(id):
    contract = db.get_or_404(Contract, id)
    return jsonify(contract.serialize), 200


# create [auth, admin]
@bp.route("/contracts", methods=["POST"])
@token_auth.login_required(role="admin")
def contract_create():
    data = request.get_json()
    required_fields = ["client_id", "sales_contact_id", "total_amount"]
    for field in required_fields:
        if field not in data:
            return {"error": "Bad request"}, 400
    contract = Contract()
    contract.deserialize(data)
    db.session.add(contract)
    db.session.commit()

    return contract.serialize, 201


# update [auth, admin]
@bp.route("/contracts/<id>", methods=["PUT"])
@token_auth.login_required(role="admin")
def contract_update(id):
    contract = db.get_or_404(Contract, id)
    data = request.get_json()
    allowed_fields = ["sales_contact_id", "total_amount", "remaining_amount", "status"]
    for field in allowed_fields:
        if field in data:
            # convert status string to enum if set
            if field == "status":
                data[field] = (
                    ContractStatus.SIGNED
                    if data[field] == "signed"
                    else ContractStatus.PENDING
                )
            setattr(contract, field, data[field])
    db.session.commit()
    return contract.serialize, 200


# destroy [auth, author]


# Event views

# index [auth]
# create [auth, sales] => must be client_author && contract_status == 'signed'
# update [auth, admin, event_contact_support]
# destroy [auth, author]
