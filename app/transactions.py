from datetime import datetime
from decimal import Decimal
from pathlib import Path
import tempfile
import pandas as pd
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from werkzeug.utils import secure_filename
from app import db
from app.auth import login_required
from app.models import Customer, Transaction, FraudPrediction, Review
from ml.predict import predict_transaction

transactions_bp = Blueprint("transactions", __name__)
REQUIRED_COLUMNS = {"transaction_id", "customer_name", "account_no", "city", "transaction_time",
                    "amount", "merchant", "location", "channel"}

@transactions_bp.route("/transactions")
@login_required
def list_transactions():
    rows = Transaction.query.filter_by(owner_id=int(session["user_id"])).order_by(
        Transaction.transaction_time.desc()).limit(500).all()
    return render_template("transactions.html", transactions=rows)

@transactions_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        file = request.files.get("file")
        if not file or not file.filename:
            flash("Choose a CSV file.", "danger")
            return redirect(url_for("transactions.upload"))
        if Path(file.filename).suffix.lower() != ".csv":
            flash("Only CSV files are accepted.", "danger")
            return redirect(url_for("transactions.upload"))

        # Use a unique temporary path so simultaneous uploads never overwrite each other.
        upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
        upload_dir.mkdir(parents=True, exist_ok=True)
        safe_name = secure_filename(file.filename) or "upload.csv"
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(prefix="upload_", suffix=".csv", dir=upload_dir, delete=False) as temp:
                temp_path = Path(temp.name)
                file.save(temp)
            frame = pd.read_csv(temp_path)
            missing = REQUIRED_COLUMNS - set(frame.columns)
            if missing:
                raise ValueError("Missing columns: " + ", ".join(sorted(missing)))
            if frame.empty:
                raise ValueError("The CSV file contains no transactions.")

            user_id = int(session["user_id"])
            created = 0
            skipped = 0
            for _, row in frame.iterrows():
                source_tid = str(row["transaction_id"]).strip()
                if not source_tid or source_tid.lower() == "nan":
                    skipped += 1
                    continue
                # The DB primary key is namespaced per user so different users may upload
                # files containing the same source transaction IDs without collisions.
                if len(source_tid) > 40:
                    skipped += 1
                    continue
                tid = f"u{user_id}_{source_tid}"
                if db.session.get(Transaction, tid):
                    skipped += 1
                    continue
                try:
                    amount = Decimal(str(row["amount"]))
                    if not amount.is_finite() or amount < 0:
                        skipped += 1
                        continue
                    account_no = str(row["account_no"]).strip()
                    if not account_no or account_no.lower() == "nan":
                        skipped += 1
                        continue
                    tx_time = pd.to_datetime(row["transaction_time"], errors="raise").to_pydatetime()
                except (ValueError, TypeError, ArithmeticError):
                    skipped += 1
                    continue

                customer = Customer.query.filter_by(owner_id=user_id, account_no=account_no).first()
                if not customer:
                    customer = Customer(
                        owner_id=user_id,
                        name=str(row["customer_name"]).strip()[:120] or "Unknown",
                        account_no=account_no[:50],
                        city=str(row["city"]).strip()[:100],
                    )
                    db.session.add(customer)
                    db.session.flush()
                tx = Transaction(
                    transaction_id=tid, customer_id=customer.customer_id, owner_id=user_id,
                    transaction_time=tx_time, amount=amount,
                    merchant=str(row["merchant"])[:120], location=str(row["location"])[:120],
                    channel=str(row["channel"])[:50],
                )
                db.session.add(tx)
                db.session.flush()
                probability, decision = predict_transaction(float(amount), str(row["merchant"]),
                                                            str(row["location"]), str(row["channel"]))
                db.session.add(FraudPrediction(transaction_id=tid, fraud_probability=probability, decision=decision))
                if decision == "Suspicious":
                    db.session.add(Review(transaction_id=tid, reviewer_id=user_id, status="Pending",
                                          remarks="Automatically queued for review."))
                created += 1
            db.session.commit()
            flash(f"Imported {created} transactions for your account. Skipped {skipped} invalid or duplicate rows.", "success")
        except Exception as exc:
            db.session.rollback()
            current_app.logger.exception("CSV import failed")
            flash(f"Could not import CSV: {exc}", "danger")
        finally:
            if temp_path:
                try:
                    temp_path.unlink(missing_ok=True)
                except OSError:
                    pass
        return redirect(url_for("transactions.list_transactions"))
    return render_template("upload.html")

@transactions_bp.route("/predict/<transaction_id>", methods=["POST"])
@login_required
def predict_one(transaction_id):
    user_id = int(session["user_id"])
    tx = Transaction.query.filter_by(transaction_id=transaction_id, owner_id=user_id).first()
    if not tx:
        flash("Transaction not found.", "danger")
    else:
        probability, decision = predict_transaction(float(tx.amount), tx.merchant or "", tx.location or "", tx.channel or "")
        pred = FraudPrediction.query.filter_by(transaction_id=transaction_id).first()
        if pred:
            pred.fraud_probability, pred.decision, pred.predicted_at = probability, decision, datetime.utcnow()
        else:
            db.session.add(FraudPrediction(transaction_id=transaction_id, fraud_probability=probability, decision=decision))
        db.session.commit()
        flash("Prediction refreshed.", "success")
    return redirect(url_for("transactions.list_transactions"))
