# src/models/message.py
from .user import db # Use the existing db instance
from datetime import datetime

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False, nullable=False)

    # Foreign Keys
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    # Optional: Link message to a specific ad conversation
    # advertisement_id = db.Column(db.Integer, db.ForeignKey("advertisement.id"), nullable=True)

    # Relationships
    sender = db.relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = db.relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")
    # advertisement = db.relationship("Advertisement") # If linking to ads

    def __repr__(self):
        return f"<Message from {self.sender_id} to {self.receiver_id} at {self.timestamp}>"

