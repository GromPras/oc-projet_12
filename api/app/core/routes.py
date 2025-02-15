import sqlalchemy as sa
from flask import jsonify, request
from app import db
from app.core import bp
from app.models import User, Client
from app.auth.auth import token_auth


# User views


# index [auth, admin]
@bp.route("/users", methods=["GET"])
@token_auth.login_required(role="admin")
def user_index():
    stmt = db.select(User)
    users = db.session.execute(stmt).scalars().all()
    users = [user.serialize for user in users]
    return jsonify(users)


# create [auth, admin]
@bp.route("/users", methods=["POST"])
@token_auth.login_required(role="admin")
def user_create():
    data = request.get_json()
    required_fiels = ["fullname", "email", "phone", "role", "password"]
    for field in required_fiels:
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


# show [auth, admin]
# update [auth, admin]
# destroy [auth, admin]
@bp.route("/users/<id>", methods=["GET", "PUT", "DELETE"])
@token_auth.login_required(role="admin")
def user_update(id):
    user = db.session.scalar(sa.select(User).where(User.id == id))
    if not user:
        return {"error": "User doesn't exists"}, 404
    else:
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
@bp.route("/clients", methods=["GET"])
@token_auth.login_required()
def client_index():
    clients = db.session.scalars(sa.select(Client).join(Client.sales_contact)).all()
    clients = [client.serialize for client in clients]
    return jsonify(clients)


# create [auth, sales]
# update [auth, author]
# destroy [auth, author]


# Contract views

# index [auth]
# create [auth, admin]
# update [auth, admin]
# destroy [auth, author]


# Event views

# index [auth]
# create [auth, sales] => must be client_author && contract_status == 'signed'
# update [auth, admin, event_contact_support]
# destroy [auth, author]
