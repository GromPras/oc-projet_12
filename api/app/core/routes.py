import sqlalchemy as sa
from flask import jsonify, request
from app import db
from app.core import bp
from app.models import User, Role
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


# update [auth, admin]
# destroy [auth, admin]


# Client views

# index [auth]
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
