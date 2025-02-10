from flask import jsonify
from app import db
from app.core import bp
from app.models import User
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
