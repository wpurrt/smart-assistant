from datetime import datetime


from app.extensions import db


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)

    is_done = db.Column(db.Boolean, default=False, nullable=False)

    priority = db.Column(db.String(20), default="medium", nullable=False)  # low, medium, high
    deadline = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.now)
    completed_at = db.Column(db.DateTime, nullable=True)

    file_path = db.Column(db.String(255))
    file_type = db.Column(db.String(50))

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)

    def __repr__(self):
        return f"<Task {self.title}>"