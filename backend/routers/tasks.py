from flask import jsonify, request, Blueprint, current_app
from database import db
from models import Task
from utils import token_required
from sqlalchemy import select


task_bp = Blueprint("task_bp", __name__)


@task_bp.route("/tasks", methods=["POST"])
@token_required
def create_tasks():

    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({"message": "Dữ liệu không hợp lệ"}), 400

    input_title = data.get("title", "")

    if not isinstance(input_title, str) or not input_title.strip():
        return jsonify({"message": "Title không được để trống"}), 400

    input_description = data.get("description", "")

    if not isinstance(input_description, str) or not input_description.strip():
        return jsonify({"message": "Mô tả không được bỏ trống"}), 400

    task = Task(
        title=input_title.strip(),
        description=input_description,
        user_id=request.user_id,
    )

    try:
        db.session.add(task)
        db.session.commit()

        return (
            jsonify({"message": "Task created successfully", "task": task.to_dict()}),
            201,
        )
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Không thể tạo Task")
        return jsonify({"error": "Failed to create task", "details": str(e)}), 500


@task_bp.route("/tasks", methods=["GET"])
@token_required
def get_tasks():

    stmt = select(Task).where(Task.user_id == request.user_id)
    tasks = db.session.execute(stmt).scalars().all()

    return jsonify([task.to_dict() for task in tasks]), 200


@task_bp.route("/tasks/<int:task_id>", methods=["GET"])
@token_required
def get_task(task_id):

    stmt = select(Task).where(Task.id == task_id)
    task = db.session.execute(stmt).scalars().first()

    if not task:
        return jsonify({"message": "Task không tìm thấy"}), 404

    if task.user_id != request.user_id:
        return jsonify({"error": "Không có quyền truy cập"}), 403
    else:
        return jsonify(task.to_dict()), 200


@task_bp.route("/tasks/<int:task_id>", methods=["PUT"])
@token_required
def update_task(task_id):

    stmt = select(Task).where(Task.id == task_id)
    task = db.session.execute(stmt).scalars().first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"message": "Dữ liệu không hợp lệ"}), 400

    title = data.get("title", task.title)
    description = data.get("description", task.description)

    if not isinstance(title, str) or not title.strip():
        return jsonify({"message": "Title không được để trống"}), 400

    if task.user_id != request.user_id:
        return jsonify({"error": "Không có quyền truy cập"}), 403

    task.title = title.strip()
    task.description = description
    
    try:
        db.session.commit()
        return (
            jsonify({"message": "Task updated successfully", "task": task.to_dict()}),
            200,
        )
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Không thể cập nhật Task")
        return jsonify({"error": "Failed to update task", "details": str(e)}), 500


@task_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
@token_required
def delete_task(task_id):

    stmt = select(Task).where(Task.id == task_id)
    task = db.session.execute(stmt).scalars().first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    if task.user_id != request.user_id:
        return jsonify({"error": "Không có quyền truy cập"}), 403

    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": "Task deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Không thể xóa Task")
        return jsonify({"error": "Failed to delete task", "details": str(e)}), 500
