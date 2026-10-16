from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from sqlalchemy import UniqueConstraint

class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="analyst")
    reviews = db.relationship("Review", backref="reviewer", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Customer(db.Model):
    __tablename__ = "customers"
    __table_args__ = (UniqueConstraint("owner_id", "account_no", name="uq_customer_owner_account"),)
    customer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    account_no = db.Column(db.String(50), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False, index=True)
    city = db.Column(db.String(100))
    transactions = db.relationship("Transaction", backref="customer", lazy=True)

class Transaction(db.Model):
    __tablename__ = "transactions"
    transaction_id = db.Column(db.String(50), primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.customer_id"), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False, index=True)
    transaction_time = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    merchant = db.Column(db.String(120))
    location = db.Column(db.String(120))
    channel = db.Column(db.String(50))
    prediction = db.relationship("FraudPrediction", backref="transaction", uselist=False, cascade="all, delete-orphan")
    reviews = db.relationship("Review", backref="transaction", lazy=True, cascade="all, delete-orphan")

class FraudPrediction(db.Model):
    __tablename__ = "fraud_predictions"
    prediction_id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(50), db.ForeignKey("transactions.transaction_id"), nullable=False, unique=True)
    fraud_probability = db.Column(db.Float, nullable=False)
    decision = db.Column(db.String(30), nullable=False)
    predicted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Review(db.Model):
    __tablename__ = "reviews"
    review_id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(50), db.ForeignKey("transactions.transaction_id"), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="Pending")
    remarks = db.Column(db.Text)
    reviewed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
