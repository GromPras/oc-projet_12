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


@bp.route("/tokens", methods=["Get"])
@token_auth.login_required()
def authenticate_token():
    return {"message": "Authenticated"}, 200
