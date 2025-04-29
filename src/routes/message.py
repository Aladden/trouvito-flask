# src/routes/message.py
import os
import sys
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_, and_
from src.models import db, Message, User

message_bp = Blueprint("message", __name__)

# Get list of conversations for the current user
@message_bp.route("/conversations", methods=["GET"])
@login_required
def get_conversations():
    # Find all unique users the current user has exchanged messages with
    sent_to_users = db.session.query(Message.receiver_id).filter(Message.sender_id == current_user.id).distinct()
    received_from_users = db.session.query(Message.sender_id).filter(Message.receiver_id == current_user.id).distinct()

    # Combine unique user IDs
    other_user_ids = {row[0] for row in sent_to_users.union(received_from_users)}

    conversations = []
    for user_id in other_user_ids:
        other_user = User.query.get(user_id)
        if not other_user:
            continue

        # Get the last message in the conversation
        last_message = Message.query.filter(
            or_(
                and_(Message.sender_id == current_user.id, Message.receiver_id == user_id),
                and_(Message.sender_id == user_id, Message.receiver_id == current_user.id)
            )
        ).order_by(Message.timestamp.desc()).first()

        # Count unread messages from this user
        unread_count = Message.query.filter(
            Message.sender_id == user_id,
            Message.receiver_id == current_user.id,
            Message.is_read == False
        ).count()

        if last_message:
            conversations.append({
                "other_user": {
                    "id": other_user.id,
                    "username": other_user.username
                },
                "last_message": {
                    "content": last_message.content,
                    "timestamp": last_message.timestamp.isoformat(),
                    "sender_id": last_message.sender_id
                },
                "unread_count": unread_count
            })

    # Sort conversations by the timestamp of the last message
    conversations.sort(key=lambda x: x["last_message"]["timestamp"], reverse=True)

    return jsonify(conversations)

# Get messages within a specific conversation (with another user)
@message_bp.route("/conversations/<int:other_user_id>", methods=["GET"])
@login_required
def get_messages(other_user_id):
    # Mark messages from the other user as read
    Message.query.filter(
        Message.sender_id == other_user_id,
        Message.receiver_id == current_user.id,
        Message.is_read == False
    ).update({"is_read": True})
    db.session.commit()

    # Fetch messages
    messages = Message.query.filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == other_user_id),
            and_(Message.sender_id == other_user_id, Message.receiver_id == current_user.id)
        )
    ).order_by(Message.timestamp.asc()).all()

    messages_data = [
        {
            "id": msg.id,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat(),
            "sender_id": msg.sender_id,
            "receiver_id": msg.receiver_id,
            "is_read": msg.is_read
        } for msg in messages
    ]

    return jsonify(messages_data)

# Send a new message
@message_bp.route("/", methods=["POST"])
@login_required
def send_message():
    data = request.json
    receiver_id = data.get("receiver_id")
    content = data.get("content")
    # advertisement_id = data.get("advertisement_id") # Optional: if linking to ad

    if not receiver_id or not content:
        return jsonify({"error": "Missing receiver_id or content"}), 400

    receiver = User.query.get(receiver_id)
    if not receiver:
        return jsonify({"error": "Receiver user not found"}), 404

    if receiver_id == current_user.id:
        return jsonify({"error": "Cannot send message to yourself"}), 400

    new_message = Message(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        content=content
        # advertisement_id=advertisement_id # Optional
    )
    db.session.add(new_message)
    db.session.commit()

    return jsonify({
        "message": "Message sent successfully",
        "sent_message": {
            "id": new_message.id,
            "content": new_message.content,
            "timestamp": new_message.timestamp.isoformat(),
            "sender_id": new_message.sender_id,
            "receiver_id": new_message.receiver_id
        }
    }), 201

