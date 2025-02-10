from app import db
from app.auth import bp
from app.auth.auth import basic_auth


@bp.route("/tokens", methods=["POST"])
@basic_auth.login_required()
def get_token():
    token = basic_auth.current_user().get_token()
    db.session.commit()
    return {"token": token}


# @bp.route("/users", methods=["POST"])
# def create_user():
#     data = request.get_json()
