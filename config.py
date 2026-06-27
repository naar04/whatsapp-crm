import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    # Render sometimes provides postgres:// instead of postgresql://
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            "postgres://",
            "postgresql://",
            1
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

    RESEND_API_KEY = os.getenv("RESEND_API_KEY")

    TO_EMAIL = os.getenv("TO_EMAIL")
