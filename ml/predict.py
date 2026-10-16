# Educational baseline rules for the first working version.
# Replace with a validated, trained model in ml/train_model.py before presenting
# predictive performance as a genuine machine-learning result.

def predict_transaction(amount, merchant, location, channel):
    probability = 0.03
    if amount >= 20000:
        probability += 0.50
    elif amount >= 10000:
        probability += 0.25
    if str(merchant).lower() in {"electronics", "jewellery", "jewelry"}:
        probability += 0.20
    if str(channel).lower() in {"online", "web", "mobile"}:
        probability += 0.10
    probability = min(probability, 0.99)
    decision = "Suspicious" if probability >= 0.50 else "Normal"
    return round(probability, 4), decision
