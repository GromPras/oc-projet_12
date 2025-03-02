from flask import request
from app import db
from app.auth import bp
from app.auth.auth import basic_auth
from app.auth.auth import token_auth


@bp.route("/tokens", methods=["POST"])
@basic_auth.login_required()
def get_token():
    token = basic_auth.current_user().get_token()
    db.session.commit()
    return {"token": token}


@bp.route("/tokens", methods=["GET"])
@token_auth.login_required()
def authenticate_token():
    return {"message": "Authenticated"}, 200


@bp.route("/authorizations", methods=["POST"])
@token_auth.login_required()
def check_authorizations():
    target = request.get_json()["target"]
    if not target:
        return {"message": "Bad request"}, 400
    user_role = token_auth.current_user().role.value
    authorizations = {
        "admin": [
            "users:create",
            "users:list",
            "users:show",
            "users:update",
            "users:delete",
            "clients:list",
            "clients:show",
            "contracts:list",
            "contracts:show",
            "contracts:create",
            "contracts:update",
            "contracts:delete",
            "events:list",
            "events:show",
            "events:update-support",
        ],
        "sales": [
            "users:list",
            "clients:create",
            "clients:list",
            "clients:show",
            "clients:update",
            "clients:delete",
            "contracts:list",
            "contracts:show",
            "events:list",
            "events:show",
            "events:create",
            "events:delete",
        ],
        "support": [
            "clients:list",
            "clients:show",
            "contracts:list",
            "contracts:show",
            "events:list",
            "events:show",
            "events:update",
        ],
    }

    if target in authorizations[user_role]:
        return {"message": "Authorized"}, 200
    return {"message": "Unauthorized"}, 403
