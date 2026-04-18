from datetime import datetime


from app.extensions import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    #color = db.Column(db.String(20), default="#3498db")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    tasks = db.relationship(
        "Task",
        backref="category",
        lazy=True
    )

    __table_args__ = (
        db.UniqueConstraint("user_id", "name", name="uq_user_category_name"),
    )

    def __repr__(self):
        return f"<Category {self.name}>"