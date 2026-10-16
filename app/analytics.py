import csv
from io import StringIO
from flask import Blueprint, Response, session
from app import db
from app.auth import login_required
from app.models import Transaction, FraudPrediction

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/reports.csv")
@login_required
def export_report():
    user_id = int(session["user_id"])
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["transaction_id", "transaction_time", "amount", "merchant", "location", "channel", "fraud_probability", "decision"])
    rows = db.session.query(Transaction, FraudPrediction).outerjoin(
        FraudPrediction, Transaction.transaction_id == FraudPrediction.transaction_id
    ).filter(Transaction.owner_id == user_id).order_by(Transaction.transaction_time.desc()).all()
    for tx, pred in rows:
        # Export the original transaction ID without the internal per-user namespace.
        source_id = tx.transaction_id.split("_", 1)[1] if "_" in tx.transaction_id else tx.transaction_id
        writer.writerow([source_id, tx.transaction_time, tx.amount, tx.merchant, tx.location, tx.channel,
                         pred.fraud_probability if pred else "", pred.decision if pred else "Not predicted"])
    return Response(output.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=fraud_report.csv"})
