from flask import jsonify, request, Blueprint, current_app
from database import db
from models import User
from werkzeug.security import check_password_hash
import jwt
from datetime import datetime, timedelta, timezone
from flask import current_app
from utils import token_required
from sqlalchemy import select

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not isinstance(data, dict):
        return {"message": "Dữ liệu không hợp lệ"}, 400

    input_email = data.get("email", "").strip().lower()
    input_password = data.get("password", "")

    if not input_email or not isinstance(input_password, str) or not input_password:
        return jsonify({"message": "Email và password là bắt buộc"}), 400

    stmt = select(User).where(User.email == input_email)
    user = db.session.execute(stmt).scalars().first()

    if user is None:
        return jsonify({"message": "Tài khoản không tồn tại"}), 401

    if not check_password_hash(user.password_hash, input_password):
        return jsonify({"message": "Email và mật khẩu không đúng"}), 401

    payload = {
        "user_id": user.id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }

    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")

    return {
        "message": "Đăng nhập thành công",
        "access_token": token,
        "token_type": "bearer",
    }, 200


@auth_bp.route("/profile", methods=["GET"])
@token_required
def profile():
    user_id = request.user_id
    user = db.session.get(User, user_id)

    if user is None:
        return {"message": "Tài khoản không tồn tại"}, 404

    return {"id": user.id, "email": user.email}, 200
