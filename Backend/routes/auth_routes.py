"""Գրանցման և մուտքի API route-եր։"""

from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from db import DatabaseIntegrityError, get_connection, is_sqlite, row_to_dict, table_name


auth_bp = Blueprint("auth", __name__)


def clean_text(value):
    return str(value or "").strip()


def normalize_username(value):
    return clean_text(value).lower()


def public_user(user):
    """Frontend-ին վերադարձնում ենք միայն անվտանգ user տվյալները։"""
    if not user:
        return None

    return {
        "user_id": user["UserId"],
        "role": user["Role"],
        "username": user["Username"],
        "email": user["Email"],
        "full_name": user["FullName"],
        "created_at": user.get("CreatedAt"),
    }


def insert_user(cursor, role, username, email, password_hash, full_name):
    """User insert-ը անում ենք ըստ database engine-ի։"""
    users_table = table_name("Users")

    if is_sqlite():
        cursor.execute(
            f"""
            INSERT INTO {users_table} (Role, Username, Email, PasswordHash, FullName)
            VALUES (?, ?, ?, ?, ?)
            """,
            (role, username, email, password_hash, full_name),
        )
        return cursor.lastrowid

    cursor.execute(
        f"""
        INSERT INTO {users_table} (Role, Username, Email, PasswordHash, FullName)
        OUTPUT INSERTED.UserId
        VALUES (?, ?, ?, ?, ?)
        """,
        role,
        username,
        email,
        password_hash,
        full_name,
    )
    return cursor.fetchone()[0]


@auth_bp.post("/register")
def register():
    """Ստեղծում է նոր ֆրիլանսեր կամ պատվիրատու։"""
    data = request.get_json(silent=True) or {}

    role = clean_text(data.get("role"))
    username = normalize_username(data.get("username"))
    email = clean_text(data.get("email")).lower()
    password = clean_text(data.get("password"))
    full_name = clean_text(data.get("full_name") or data.get("company_name"))

    if role not in ("freelancer", "client"):
        return jsonify({"error": "Դերը պետք է լինի freelancer կամ client։"}), 400

    if not username or not email or not password or not full_name:
        return jsonify({"error": "Լրացրեք բոլոր պարտադիր դաշտերը։"}), 400

    if len(password) < 6:
        return jsonify({"error": "Գաղտնաբառը պետք է լինի առնվազն 6 նիշ։"}), 400

    password_hash = generate_password_hash(password)
    users_table = table_name("Users")
    freelancer_profiles_table = table_name("FreelancerProfiles")
    client_profiles_table = table_name("ClientProfiles")

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            user_id = insert_user(cursor, role, username, email, password_hash, full_name)

            if role == "freelancer":
                cursor.execute(
                    f"INSERT INTO {freelancer_profiles_table} (UserId, Specialty) VALUES (?, ?)",
                    (user_id, clean_text(data.get("specialty"))),
                )
            else:
                cursor.execute(
                    f"INSERT INTO {client_profiles_table} (UserId, CompanyName) VALUES (?, ?)",
                    (user_id, clean_text(data.get("company_name") or full_name)),
                )

            conn.commit()

            cursor.execute(
                f"SELECT UserId, Role, Username, Email, FullName, CreatedAt FROM {users_table} WHERE UserId = ?",
                (user_id,),
            )
            user = row_to_dict(cursor, cursor.fetchone())

        return jsonify({"message": "Հաշիվը ստեղծվեց։", "user": public_user(user)}), 201

    except DatabaseIntegrityError:
        return jsonify({"error": "Այս email-ը կամ username-ը արդեն օգտագործվում է։"}), 409


@auth_bp.post("/login")
def login():
    """Ստուգում է email/password-ը և վերադարձնում user տվյալները։"""
    data = request.get_json(silent=True) or {}

    email = clean_text(data.get("email")).lower()
    password = clean_text(data.get("password"))
    role = clean_text(data.get("role"))

    if not email or not password:
        return jsonify({"error": "Մուտքագրեք email և գաղտնաբառ։"}), 400

    users_table = table_name("Users")

    with get_connection() as conn:
        cursor = conn.cursor()

        if role in ("freelancer", "client"):
            cursor.execute(
                f"SELECT UserId, Role, Username, Email, FullName, PasswordHash, CreatedAt FROM {users_table} WHERE Email = ? AND Role = ?",
                (email, role),
            )
        else:
            cursor.execute(
                f"SELECT UserId, Role, Username, Email, FullName, PasswordHash, CreatedAt FROM {users_table} WHERE Email = ?",
                (email,),
            )

        user = row_to_dict(cursor, cursor.fetchone())

    if not user or not check_password_hash(user["PasswordHash"], password):
        return jsonify({"error": "Email-ը կամ գաղտնաբառը սխալ է։"}), 401

    return jsonify({"message": "Մուտքը հաջողվեց։", "user": public_user(user)})
