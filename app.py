import json
import os
import requests

from flask import Flask, request, render_template

from config import Config
from models import db, Contact, Message

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()


# ------------------------
# Email
# ------------------------

def send_email(subject, body):

    if not Config.RESEND_API_KEY:
        print("RESEND_API_KEY missing")
        return

    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {Config.RESEND_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "from": "onboarding@resend.dev",
            "to": [Config.TO_EMAIL],
            "subject": subject,
            "text": body
        },
        timeout=20
    )

    print(response.status_code)
    print(response.text)


# ------------------------
# Dashboard
# ------------------------

@app.route("/")
def dashboard():

    messages = Message.query.order_by(
        Message.created_at.desc()
    ).limit(50).all()

    total_contacts = Contact.query.count()
    total_messages = Message.query.count()

    return render_template(
        "dashboard.html",
        messages=messages,
        total_contacts=total_contacts,
        total_messages=total_messages
    )


# ------------------------
# Webhook Verify
# ------------------------

@app.route("/webhook", methods=["GET"])
def verify():

    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if (
        mode == "subscribe"
        and token == Config.VERIFY_TOKEN
    ):
        return challenge, 200

    return "Verification failed", 403


# ------------------------
# Receive Messages
# ------------------------

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json()

    print(json.dumps(data, indent=2))

    try:

        value = data["entry"][0]["changes"][0]["value"]

        if "messages" not in value:
            return "OK", 200

        msg = value["messages"][0]

        wa_id = msg["from"]

        contacts = value.get("contacts", [])

        if contacts:
            name = contacts[0]["profile"]["name"]
        else:
            name = wa_id

        contact = Contact.query.filter_by(
            wa_id=wa_id
        ).first()

        if contact is None:

            contact = Contact(
                wa_id=wa_id,
                phone=wa_id,
                name=name,
                total_messages=1
            )

            db.session.add(contact)

        else:

            contact.name = name
            contact.total_messages += 1

        text = ""

        if msg["type"] == "text":
            text = msg["text"]["body"]

        elif msg["type"] == "button":
            text = msg["button"]["text"]

        else:
            text = f"<{msg['type']}>"

        message = Message(
            message_id=msg["id"],
            contact=contact,
            message_type=msg["type"],
            message_text=text,
            timestamp=msg["timestamp"],
            raw_json=json.dumps(msg)
        )

        db.session.add(message)

        db.session.commit()

        send_email(
            f"WhatsApp: {name}",
            text
        )

    except Exception as e:

        db.session.rollback()

        print(e)

    return "OK", 200


if __name__ == "__main__":
    app.run()
