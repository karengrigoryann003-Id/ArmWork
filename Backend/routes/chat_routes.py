"""Chat և հաղորդագրությունների API route-եր։"""

from flask import Blueprint, jsonify, request

from db import get_connection, is_sqlite, row_to_dict, rows_to_dicts, table_name, utc_now_sql


chat_bp = Blueprint("chats", __name__)


def user_is_participant(cursor, conversation_id, user_id):
    participants_table = table_name("ConversationParticipants")
    cursor.execute(
        f"""
        SELECT 1
        FROM {participants_table}
        WHERE ConversationId = ? AND UserId = ?
        """,
        (conversation_id, user_id),
    )
    return cursor.fetchone() is not None


def conversation_payload(row):
    return {
        "conversation_id": row["ConversationId"],
        "other_user_id": row["OtherUserId"],
        "other_username": row["OtherUsername"],
        "other_full_name": row["OtherFullName"],
        "other_role": row["OtherRole"],
        "last_message": row.get("LastMessage"),
        "last_message_at": row.get("LastMessageAt"),
    }


def list_chats_sql():
    conversations_table = table_name("Conversations")
    participants_table = table_name("ConversationParticipants")
    users_table = table_name("Users")
    messages_table = table_name("Messages")

    if is_sqlite():
        return f"""
            SELECT
                c.ConversationId,
                otherUser.UserId AS OtherUserId,
                otherUser.Username AS OtherUsername,
                otherUser.FullName AS OtherFullName,
                otherUser.Role AS OtherRole,
                (
                    SELECT m.Body
                    FROM {messages_table} m
                    WHERE m.ConversationId = c.ConversationId
                    ORDER BY m.CreatedAt DESC
                    LIMIT 1
                ) AS LastMessage,
                (
                    SELECT m.CreatedAt
                    FROM {messages_table} m
                    WHERE m.ConversationId = c.ConversationId
                    ORDER BY m.CreatedAt DESC
                    LIMIT 1
                ) AS LastMessageAt
            FROM {participants_table} me
            INNER JOIN {conversations_table} c ON c.ConversationId = me.ConversationId
            INNER JOIN {participants_table} otherParticipant
                ON otherParticipant.ConversationId = c.ConversationId
                AND otherParticipant.UserId <> me.UserId
            INNER JOIN {users_table} otherUser ON otherUser.UserId = otherParticipant.UserId
            WHERE me.UserId = ?
            ORDER BY COALESCE(LastMessageAt, c.UpdatedAt) DESC
        """

    return f"""
        SELECT
            c.ConversationId,
            otherUser.UserId AS OtherUserId,
            otherUser.Username AS OtherUsername,
            otherUser.FullName AS OtherFullName,
            otherUser.Role AS OtherRole,
            lastMessage.Body AS LastMessage,
            lastMessage.CreatedAt AS LastMessageAt
        FROM {participants_table} me
        INNER JOIN {conversations_table} c ON c.ConversationId = me.ConversationId
        INNER JOIN {participants_table} otherParticipant
            ON otherParticipant.ConversationId = c.ConversationId
            AND otherParticipant.UserId <> me.UserId
        INNER JOIN {users_table} otherUser ON otherUser.UserId = otherParticipant.UserId
        OUTER APPLY (
            SELECT TOP 1 Body, CreatedAt
            FROM {messages_table}
            WHERE ConversationId = c.ConversationId
            ORDER BY CreatedAt DESC
        ) lastMessage
        WHERE me.UserId = ?
        ORDER BY COALESCE(lastMessage.CreatedAt, c.UpdatedAt) DESC
    """


@chat_bp.get("")
def list_chats():
    """Վերադարձնում է տվյալ user-ի conversation-ների ցանկը։"""
    user_id = request.args.get("user_id", type=int)

    if not user_id:
        return jsonify({"error": "user_id-ը պարտադիր է։"}), 400

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(list_chats_sql(), (user_id,))
        rows = rows_to_dicts(cursor)

    return jsonify({"chats": [conversation_payload(row) for row in rows]})


@chat_bp.post("/start")
def start_chat():
    """Սկսում է chat username-ով կամ user_id-ով։ Եթե chat-ը կա, վերադարձնում է եղածը։"""
    data = request.get_json(silent=True) or {}
    current_user_id = data.get("current_user_id")
    other_user_id = data.get("other_user_id")
    username = str(data.get("username") or "").strip().lower()

    if not current_user_id:
        return jsonify({"error": "current_user_id-ը պարտադիր է։"}), 400

    users_table = table_name("Users")
    conversations_table = table_name("Conversations")
    participants_table = table_name("ConversationParticipants")

    with get_connection() as conn:
        cursor = conn.cursor()

        if not other_user_id and username:
            cursor.execute(f"SELECT UserId FROM {users_table} WHERE Username = ?", (username,))
            row = cursor.fetchone()
            if not row:
                return jsonify({"error": "Այդ username-ով օգտատեր չգտնվեց։"}), 404
            other_user_id = row[0]

        if not other_user_id:
            return jsonify({"error": "Մուտքագրեք username կամ other_user_id։"}), 400

        if int(current_user_id) == int(other_user_id):
            return jsonify({"error": "Չեք կարող chat սկսել ինքներդ ձեզ հետ։"}), 400

        cursor.execute(
            f"""
            SELECT p1.ConversationId
            FROM {participants_table} p1
            INNER JOIN {participants_table} p2 ON p2.ConversationId = p1.ConversationId
            WHERE p1.UserId = ? AND p2.UserId = ?
            """,
            (current_user_id, other_user_id),
        )
        existing = cursor.fetchone()

        if existing:
            conversation_id = existing[0]
        else:
            if is_sqlite():
                cursor.execute(f"INSERT INTO {conversations_table} DEFAULT VALUES")
                conversation_id = cursor.lastrowid
            else:
                cursor.execute(f"INSERT INTO {conversations_table} OUTPUT INSERTED.ConversationId DEFAULT VALUES")
                conversation_id = int(cursor.fetchone()[0])

            cursor.execute(
                f"INSERT INTO {participants_table} (ConversationId, UserId) VALUES (?, ?), (?, ?)",
                (conversation_id, current_user_id, conversation_id, other_user_id),
            )
            conn.commit()

        cursor.execute(
            f"""
            SELECT
                c.ConversationId,
                otherUser.UserId AS OtherUserId,
                otherUser.Username AS OtherUsername,
                otherUser.FullName AS OtherFullName,
                otherUser.Role AS OtherRole,
                NULL AS LastMessage,
                NULL AS LastMessageAt
            FROM {conversations_table} c
            INNER JOIN {participants_table} otherParticipant
                ON otherParticipant.ConversationId = c.ConversationId
                AND otherParticipant.UserId = ?
            INNER JOIN {users_table} otherUser ON otherUser.UserId = otherParticipant.UserId
            WHERE c.ConversationId = ?
            """,
            (other_user_id, conversation_id),
        )
        conversation = row_to_dict(cursor, cursor.fetchone())

    return jsonify({"chat": conversation_payload(conversation)})


@chat_bp.get("/<int:conversation_id>/messages")
def list_messages(conversation_id):
    """Վերադարձնում է conversation-ի հաղորդագրությունները։"""
    user_id = request.args.get("user_id", type=int)

    if not user_id:
        return jsonify({"error": "user_id-ը պարտադիր է։"}), 400

    messages_table = table_name("Messages")

    with get_connection() as conn:
        cursor = conn.cursor()

        if not user_is_participant(cursor, conversation_id, user_id):
            return jsonify({"error": "Դուք այս chat-ի մասնակից չեք։"}), 403

        cursor.execute(
            f"""
            SELECT MessageId, ConversationId, SenderId, Body, CreatedAt, IsRead
            FROM {messages_table}
            WHERE ConversationId = ?
            ORDER BY CreatedAt ASC
            """,
            (conversation_id,),
        )
        messages = rows_to_dicts(cursor)

    return jsonify({"messages": [
        {
            "message_id": message["MessageId"],
            "conversation_id": message["ConversationId"],
            "sender_id": message["SenderId"],
            "body": message["Body"],
            "created_at": message["CreatedAt"],
            "is_read": bool(message["IsRead"]),
        }
        for message in messages
    ]})


@chat_bp.post("/<int:conversation_id>/messages")
def send_message(conversation_id):
    """Ավելացնում է նոր հաղորդագրություն chat-ում։"""
    data = request.get_json(silent=True) or {}
    sender_id = data.get("sender_id")
    body = str(data.get("body") or "").strip()

    if not sender_id or not body:
        return jsonify({"error": "sender_id և body դաշտերը պարտադիր են։"}), 400

    messages_table = table_name("Messages")
    conversations_table = table_name("Conversations")

    with get_connection() as conn:
        cursor = conn.cursor()

        if not user_is_participant(cursor, conversation_id, sender_id):
            return jsonify({"error": "Դուք այս chat-ի մասնակից չեք։"}), 403

        if is_sqlite():
            cursor.execute(
                f"INSERT INTO {messages_table} (ConversationId, SenderId, Body) VALUES (?, ?, ?)",
                (conversation_id, sender_id, body),
            )
            message_id = cursor.lastrowid
            cursor.execute(
                f"SELECT MessageId, ConversationId, SenderId, Body, CreatedAt, IsRead FROM {messages_table} WHERE MessageId = ?",
                (message_id,),
            )
            message = row_to_dict(cursor, cursor.fetchone())
        else:
            cursor.execute(
                f"""
                INSERT INTO {messages_table} (ConversationId, SenderId, Body)
                OUTPUT INSERTED.MessageId, INSERTED.ConversationId, INSERTED.SenderId, INSERTED.Body, INSERTED.CreatedAt, INSERTED.IsRead
                VALUES (?, ?, ?)
                """,
                conversation_id,
                sender_id,
                body,
            )
            message = row_to_dict(cursor, cursor.fetchone())

        cursor.execute(
            f"UPDATE {conversations_table} SET UpdatedAt = {utc_now_sql()} WHERE ConversationId = ?",
            (conversation_id,),
        )
        conn.commit()

    return jsonify({
        "message": {
            "message_id": message["MessageId"],
            "conversation_id": message["ConversationId"],
            "sender_id": message["SenderId"],
            "body": message["Body"],
            "created_at": message["CreatedAt"],
            "is_read": bool(message["IsRead"]),
        }
    }), 201
