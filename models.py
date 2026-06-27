from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Contact(db.Model):

    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)

    wa_id = db.Column(db.String(30), unique=True, nullable=False)

    name = db.Column(db.String(200))

    first_seen = db.Column(db.DateTime, default=datetime.utcnow)

    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    total_messages = db.Column(db.Integer, default=0)


class Message(db.Model):

    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)

    message_id = db.Column(db.String(150), unique=True)

    contact_id = db.Column(
        db.Integer,
        db.ForeignKey("contacts.id")
    )

    direction = db.Column(db.String(20))

    message_type = db.Column(db.String(50))

    message_text = db.Column(db.Text)

    timestamp = db.Column(db.String(50))

    raw_json = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
