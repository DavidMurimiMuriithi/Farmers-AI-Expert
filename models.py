# models.py
from datetime import datetime
from extensions import db # Import the 'db' instance from your main file

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=True)  # Optional if you capture user names
    question_text = db.Column(db.Text, nullable=False)
    reply_text = db.Column(db.Text, nullable=True)
    document_url = db.Column(db.String(255), nullable=True)  # Optional URL for an attached document
    image_url = db.Column(db.String(255), nullable=True)     # Optional URL for an attached image
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    replied_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<Question {self.id} - {self.question_text[:20]}...>"
