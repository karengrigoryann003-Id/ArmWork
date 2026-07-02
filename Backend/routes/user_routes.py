"""Օգտատերերի որոնման API route-եր։"""

from flask import Blueprint, jsonify, request

from db import get_connection, is_sqlite, rows_to_dicts, table_name


user_bp = Blueprint("users", __name__)


@user_bp.get("/search")
def search_users():
    """Որոնում է օգտատերերին username-ով։ Օգտագործվում է նոր chat սկսելու համար։"""
    username = (request.args.get("username") or "").strip().lower()
    current_user_id = request.args.get("current_user_id", type=int)

    if len(username) < 2:
        return jsonify({"users": []})

    users_table = table_name("Users")
    select_limit = "" if is_sqlite() else "TOP 10"
    limit_suffix = "LIMIT 10" if is_sqlite() else ""

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT {select_limit} UserId, Username, FullName, Role
            FROM {users_table}
            WHERE Username LIKE ? AND (? IS NULL OR UserId <> ?)
            ORDER BY Username
            {limit_suffix}
            """,
            (f"%{username}%", current_user_id, current_user_id),
        )
        users = rows_to_dicts(cursor)

    return jsonify({"users": [
        {
            "user_id": user["UserId"],
            "username": user["Username"],
            "full_name": user["FullName"],
            "role": user["Role"],
        }
        for user in users
    ]})
