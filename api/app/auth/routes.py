from app import db
from app.auth import bp


@bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
