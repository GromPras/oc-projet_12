from app import db
from app.auth import bp
from app.auth.auth import basic_auth


@bp.route("/tokens", methods=["POST"])
@basic_auth.login_required
def get_token():
    return {"token": ""}


# @bp.route("/users", methods=["POST"])
# def create_user():
#     data = request.get_json()
