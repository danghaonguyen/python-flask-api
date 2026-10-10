from functools import wraps
from flask import request, current_app, jsonify
from models import User
from database import db
import jwt

def token_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        # 1. Lấy Authorization header
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "Thiếu token xác thực"}), 401

        # 2. Tách JWT khỏi chuỗi Bearer
        token = auth_header.split(" ", 1)[1]

        # 3. Xác minh token
        try:
            payload = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token không hợp lệ hoặc đã hết hạn"}), 401

        # 4. Lấy user_id từ payload
        user_id = payload.get("user_id")

        if user_id is None:
            return jsonify({"message": "Token thiếu user_id"}), 401

        request.user_id = user_id

        # 5. Token hợp lệ thì chạy route gốc
        return route_function(*args, **kwargs)

    return wrapper


def admin_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        user = db.session.get(User, request.user_id)

        if user is None:
            return jsonify({
                "message": "Không tìm thấy user"
            }), 401

        if user.role != "admin":
            return jsonify({
                "message": "Bạn không có quyền Admin"
            }), 403

        return route_function(*args, **kwargs)

    return wrapper