from datetime import datetime
from app.extensions import db


class ActionLog(db.Model):
    __tablename__ = "action_logs"

    id = db.Column(db.Integer, primary_key=True)
    action_type = db.Column(db.String(100))
    entity_type = db.Column(db.String(100))
    description = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=True)
    source = db.Column(db.String(50)) #alice
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<ActionLog {self.action_type} {self.entity_type}>"