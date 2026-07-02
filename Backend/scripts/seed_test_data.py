"""ArmWork-ի test user-ները database-ում ավելացնելու script։

Script-ը անվտանգ է մի քանի անգամ գործարկելու համար․ եթե user-ը կա, թարմացնում է password-ը
և profile տվյալները, եթե չկա՝ ստեղծում է։
"""

from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from werkzeug.security import generate_password_hash

from db import get_connection, is_sqlite, table_name

TEST_PASSWORD = "ArmWork123!"

TEST_USERS = [
    {
        "role": "client",
        "username": "client_demo",
        "email": "client.demo@armwork.test",
        "full_name": "Milena Grigoryan",
        "company_name": "Milena Studio",
    },
    {
        "role": "freelancer",
        "username": "freelancer_demo",
        "email": "freelancer.demo@armwork.test",
        "full_name": "Aram Freelancer",
        "specialty": "Frontend Developer",
    },
]


def execute(cursor, sql, params=()):
    """Միասնական execute helper՝ SQLite և pyodbc-ի համար։"""
    cursor.execute(sql, params)


def get_user_id(cursor, username):
    users_table = table_name("Users")
    execute(cursor, f"SELECT UserId FROM {users_table} WHERE Username = ?", (username,))
    row = cursor.fetchone()
    return row[0] if row else None


def insert_user(cursor, user, password_hash):
    users_table = table_name("Users")

    if is_sqlite():
        execute(
            cursor,
            f"""
            INSERT INTO {users_table} (Role, Username, Email, PasswordHash, FullName)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user["role"], user["username"], user["email"], password_hash, user["full_name"]),
        )
        return cursor.lastrowid

    cursor.execute(
        f"""
        INSERT INTO {users_table} (Role, Username, Email, PasswordHash, FullName)
        OUTPUT INSERTED.UserId
        VALUES (?, ?, ?, ?, ?)
        """,
        user["role"],
        user["username"],
        user["email"],
        password_hash,
        user["full_name"],
    )
    return cursor.fetchone()[0]


def upsert_user(cursor, user):
    """Ստեղծում կամ թարմացնում է test user-ին։"""
    users_table = table_name("Users")
    password_hash = generate_password_hash(TEST_PASSWORD)
    user_id = get_user_id(cursor, user["username"])

    if user_id:
        execute(
            cursor,
            f"""
            UPDATE {users_table}
            SET Role = ?, Email = ?, PasswordHash = ?, FullName = ?
            WHERE UserId = ?
            """,
            (user["role"], user["email"], password_hash, user["full_name"], user_id),
        )
        return user_id

    return insert_user(cursor, user, password_hash)


def profile_exists(cursor, table, user_id):
    execute(cursor, f"SELECT 1 FROM {table} WHERE UserId = ?", (user_id,))
    return cursor.fetchone() is not None


def upsert_profile(cursor, user_id, user):
    """User-ի role-ին համապատասխան profile row-ը ստեղծում կամ թարմացնում է։"""
    if user["role"] == "client":
        table = table_name("ClientProfiles")
        if profile_exists(cursor, table, user_id):
            execute(
                cursor,
                f"UPDATE {table} SET CompanyName = ? WHERE UserId = ?",
                (user["company_name"], user_id),
            )
        else:
            execute(
                cursor,
                f"INSERT INTO {table} (UserId, CompanyName) VALUES (?, ?)",
                (user_id, user["company_name"]),
            )
        return

    table = table_name("FreelancerProfiles")
    if profile_exists(cursor, table, user_id):
        execute(
            cursor,
            f"UPDATE {table} SET Specialty = ? WHERE UserId = ?",
            (user["specialty"], user_id),
        )
    else:
        execute(
            cursor,
            f"INSERT INTO {table} (UserId, Specialty) VALUES (?, ?)",
            (user_id, user["specialty"]),
        )


def find_conversation(cursor, client_id, freelancer_id):
    participants_table = table_name("ConversationParticipants")
    execute(
        cursor,
        f"""
        SELECT p1.ConversationId
        FROM {participants_table} p1
        INNER JOIN {participants_table} p2 ON p2.ConversationId = p1.ConversationId
        WHERE p1.UserId = ? AND p2.UserId = ?
        """,
        (client_id, freelancer_id),
    )
    row = cursor.fetchone()
    return row[0] if row else None


def create_conversation(cursor, client_id, freelancer_id):
    conversations_table = table_name("Conversations")
    participants_table = table_name("ConversationParticipants")

    if is_sqlite():
        execute(cursor, f"INSERT INTO {conversations_table} DEFAULT VALUES")
        conversation_id = cursor.lastrowid
    else:
        cursor.execute(f"INSERT INTO {conversations_table} OUTPUT INSERTED.ConversationId DEFAULT VALUES")
        conversation_id = cursor.fetchone()[0]

    execute(
        cursor,
        f"INSERT INTO {participants_table} (ConversationId, UserId) VALUES (?, ?), (?, ?)",
        (conversation_id, client_id, conversation_id, freelancer_id),
    )
    return conversation_id


def seed_welcome_message(cursor, conversation_id, sender_id):
    messages_table = table_name("Messages")
    execute(
        cursor,
        f"SELECT COUNT(*) FROM {messages_table} WHERE ConversationId = ?",
        (conversation_id,),
    )
    message_count = cursor.fetchone()[0]
    if message_count:
        return

    execute(
        cursor,
        f"INSERT INTO {messages_table} (ConversationId, SenderId, Body) VALUES (?, ?, ?)",
        (conversation_id, sender_id, "Բարև, սա ArmWork-ի test նամակն է։"),
    )


def main():
    with get_connection() as conn:
        cursor = conn.cursor()

        user_ids = {}
        for user in TEST_USERS:
            user_id = upsert_user(cursor, user)
            upsert_profile(cursor, user_id, user)
            user_ids[user["role"]] = user_id

        conversation_id = find_conversation(cursor, user_ids["client"], user_ids["freelancer"])
        if not conversation_id:
            conversation_id = create_conversation(cursor, user_ids["client"], user_ids["freelancer"])

        seed_welcome_message(cursor, conversation_id, user_ids["client"])
        conn.commit()

    print("ArmWork test users-ը պատրաստ են։")
    print("Client: username=client_demo password=ArmWork123!")
    print("Freelancer: username=freelancer_demo password=ArmWork123!")


if __name__ == "__main__":
    main()
