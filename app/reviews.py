from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.auth import login_required
from app.models import Review, Transaction

reviews_bp = Blueprint("reviews", __name__)

@reviews_bp.route("/reviews")
@login_required
def queue():
    user_id = int(session["user_id"])
    rows = Review.query.join(Transaction, Review.transaction_id == Transaction.transaction_id).filter(
        Transaction.owner_id == user_id).order_by(Review.review_id.desc()).all()
    return render_template("reviews.html", reviews=rows)

@reviews_bp.route("/reviews/<int:review_id>", methods=["POST"])
@login_required
def update_review(review_id):
    user_id = int(session["user_id"])
    review = Review.query.join(Transaction, Review.transaction_id == Transaction.transaction_id).filter(
        Review.review_id == review_id, Transaction.owner_id == user_id).first()
    if not review:
        flash("Review not found.", "danger")
        return redirect(url_for("reviews.queue"))
    status = request.form.get("status")
    if status not in {"Pending", "Confirmed Fraud", "Legitimate"}:
        flash("Invalid review status.", "danger")
        return redirect(url_for("reviews.queue"))
    review.status = status
    review.remarks = request.form.get("remarks", "").strip()
    review.reviewer_id = user_id
    db.session.commit()
    flash("Review updated.", "success")
    return redirect(url_for("reviews.queue"))
