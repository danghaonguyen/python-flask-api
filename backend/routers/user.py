from flask import jsonify, request, Blueprint, current_app
from sqlalchemy import select
from database import db
from models import User
from werkzeug.security import generate_password_hash
from utils import token_required, admin_required

user_bp = Blueprint("user_bp", __name__)


# Đăng ký tài khoản
@user_bp.route("/users", methods=["POST"])
def register():
    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({"message": "Dữ liệu không hợp lệ"}), 400

    input_username = data.get("username", "")
    input_email = data.get("email", "")
    input_password = data.get("password", "")

    if not isinstance(input_username, str) or not input_username.strip():
        return jsonify({"message": "Username không được để trống"}), 400

    if not isinstance(input_email, str) or not input_email.strip():
        return jsonify({"message": "Email không được để trống"}), 400

    if not isinstance(input_password, str) or not input_password:
        return jsonify({"message": "Password không được để trống"}), 400

    if len(input_password) < 6:
        return jsonify({"message": "Password phải có ít nhất 6 ký tự"}), 400

    input_username = input_username.strip()
    input_email = input_email.strip()

    # Kiểm tra email đã tồn tại
    stmt = select(User).where(User.email == input_email)
    existing_user = db.session.execute(stmt).scalar_one_or_none()

    if existing_user:
        return jsonify({"message": "Email đã được sử dụng"}), 409

    # Hash mật khẩu
    password_hash = generate_password_hash(input_password)

    new_user = User(
        username=input_username,
        email=input_email,
        password_hash=password_hash,
    )

    try:
        db.session.add(new_user)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "User created successfully",
                    "user": new_user.to_dict(),
                }
            ),
            201,
        )

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Không thể tạo User")
        return jsonify({"error": "Không thể tạo tài khoản"}), 500


# Xem tất cả tài khoản
@user_bp.route("/users", methods=["GET"])
@token_required
@admin_required
def get_users():
    stmt = select(User)
    users = db.session.execute(stmt).scalars().all()

    return jsonify([user.to_dict() for user in users]), 200


# Xem thông tin tài khoản của chính mình
@user_bp.route("/users/<int:user_id>", methods=["GET"])
@token_required
def get_user(user_id):
    if user_id != request.user_id:
        return jsonify({"message": "Không có quyền xem tài khoản này"}), 403

    stmt = select(User).where(User.id == user_id)
    user = db.session.execute(stmt).scalar_one_or_none()

    if user is None:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user.to_dict()), 200


# Cập nhật tài khoản
@user_bp.route("/users/<int:user_id>", methods=["PUT"])
@token_required
def update_user(user_id):
    if user_id != request.user_id:
        return jsonify({"message": "Không có quyền cập nhật tài khoản này"}), 403

    stmt = select(User).where(User.id == user_id)
    user = db.session.execute(stmt).scalar_one_or_none()

    if user is None:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({"message": "Dữ liệu không hợp lệ"}), 400

    new_username = data.get("username", user.username)
    new_email = data.get("email", user.email)

    if not isinstance(new_username, str) or not new_username.strip():
        return jsonify({"message": "Username không được để trống"}), 400

    if not isinstance(new_email, str) or not new_email.strip():
        return jsonify({"message": "Email không được để trống"}), 400

    new_username = new_username.strip()
    new_email = new_email.strip()

    # Kiểm tra email có thuộc tài khoản khác không
    stmt = select(User).where(User.email == new_email)
    existing_user = db.session.execute(stmt).scalar_one_or_none()

    if existing_user and existing_user.id != user.id:
        return jsonify({"message": "Email đã được sử dụng"}), 409

    # Kiểm tra username có thuộc tài khoản khác không
    stmt = select(User).where(User.username == new_username)
    existing_username = db.session.execute(stmt).scalar_one_or_none()

    if existing_username and existing_username.id != user.id:
        return jsonify({"message": "Username đã được sử dụng"}), 409

    user.username = new_username
    user.email = new_email

    try:
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "User updated successfully",
                    "user": user.to_dict(),
                }
            ),
            200,
        )

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Không thể cập nhật User")
        return jsonify({"error": "Không thể cập nhật tài khoản"}), 500


# Xóa tài khoản
@user_bp.route("/users/<int:user_id>", methods=["DELETE"])
@token_required
def delete_user(user_id):
    if user_id != request.user_id:
        return jsonify({"message": "Không có quyền xóa tài khoản này"}), 403

    stmt = select(User).where(User.id == user_id)
    user = db.session.execute(stmt).scalar_one_or_none()

    if user is None:
        return jsonify({"error": "User not found"}), 404

    try:
        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "User deleted successfully"}), 200

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Không thể xóa User")
        return jsonify({"error": "Không thể xóa tài khoản"}), 500
