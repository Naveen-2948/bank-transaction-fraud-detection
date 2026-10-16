from flask import Blueprint, render_template, redirect, url_for, session
from sqlalchemy import func
from app import db
from app.auth import login_required
from app.models import Transaction, FraudPrediction, Review

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.login"))

@main_bp.route("/dashboard")
@login_required
def dashboard():
    from collections import Counter, defaultdict
    from datetime import date, timedelta

    user_id = int(session["user_id"])
    user_transactions = Transaction.query.filter_by(owner_id=user_id)
    total = user_transactions.count()
    flagged = db.session.query(func.count(FraudPrediction.prediction_id)).join(
        Transaction, Transaction.transaction_id == FraudPrediction.transaction_id
    ).filter(Transaction.owner_id == user_id, FraudPrediction.decision == "Suspicious").scalar() or 0
    suspicious_amount = db.session.query(func.coalesce(func.sum(Transaction.amount), 0)).join(
        FraudPrediction, Transaction.transaction_id == FraudPrediction.transaction_id
    ).filter(Transaction.owner_id == user_id, FraudPrediction.decision == "Suspicious").scalar()
    pending = db.session.query(func.count(Review.review_id)).join(
        Transaction, Review.transaction_id == Transaction.transaction_id
    ).filter(Transaction.owner_id == user_id, Review.status == "Pending").scalar() or 0
    recent = user_transactions.order_by(Transaction.transaction_time.desc()).limit(8).all()
    all_transactions = user_transactions.order_by(Transaction.transaction_time.asc()).all()

    daily_counts = Counter()
    decision_counts = Counter()
    channel_counts = defaultdict(lambda: {"total": 0, "suspicious": 0})
    merchant_counts = Counter()
    today = date.today()
    for offset in range(29, -1, -1):
        daily_counts[(today - timedelta(days=offset)).isoformat()] = 0

    for tx in all_transactions:
        tx_day = tx.transaction_time.date().isoformat()
        if tx_day in daily_counts:
            daily_counts[tx_day] += 1
        decision = tx.prediction.decision if tx.prediction else "Not predicted"
        decision_counts[decision] += 1
        channel = (tx.channel or "Unknown").strip() or "Unknown"
        channel_counts[channel]["total"] += 1
        if decision == "Suspicious":
            channel_counts[channel]["suspicious"] += 1
            merchant = (tx.merchant or "Unknown").strip() or "Unknown"
            merchant_counts[merchant] += 1

    chart_daily_labels = list(daily_counts.keys())
    chart_daily_values = list(daily_counts.values())
    chart_decision_labels = list(decision_counts.keys()) or ["No data"]
    chart_decision_values = list(decision_counts.values()) or [0]
    chart_channel_labels = list(channel_counts.keys()) or ["No data"]
    chart_channel_values = [channel_counts[ch]["suspicious"] for ch in chart_channel_labels]
    top_merchants = merchant_counts.most_common(8)
    chart_merchant_labels = [merchant for merchant, _ in top_merchants] or ["No suspicious merchants"]
    chart_merchant_values = [count for _, count in top_merchants] or [0]

    return render_template(
        "dashboard.html", total=total, flagged=flagged,
        suspicious_amount=suspicious_amount, pending=pending, recent=recent,
        chart_daily_labels=chart_daily_labels, chart_daily_values=chart_daily_values,
        chart_decision_labels=chart_decision_labels, chart_decision_values=chart_decision_values,
        chart_channel_labels=chart_channel_labels, chart_channel_values=chart_channel_values,
        chart_merchant_labels=chart_merchant_labels, chart_merchant_values=chart_merchant_values,
    )
