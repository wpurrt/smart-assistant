from datetime import datetime


from app.extensions import db


class UserAliceLink(db.Model):
    __tablename__ = "user_alice_links"
    id = db.Column(db.Integer, primary_key=True)
    link_code = db.Column(db.String(12), unique=True, nullable=False, index=True)
    yandex_user_id = db.Column(db.String(255), unique=True, nullable=True)
    is_linked = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    linked_at = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)

    def __repr__(self):
        return f"<UserAliceLink user_id={self.user_id} linked={self.is_linked}>"