# Bank Transaction Fraud Detection & Analytics Dashboard

## Setup (Windows / VS Code)
1. Open this folder in VS Code.
2. Create and activate a Python 3.11 virtual environment:
   ```powershell
   py -3.11 -m venv .venv
   & .\.venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
4. Create a MySQL database:
   ```sql
   CREATE DATABASE bank_fraud_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
5. Copy `.env.example` to `.env` and set your actual MySQL password and a private secret key. Never commit `.env`.
6. Start the app:
   ```powershell
   python run.py
   ```
7. Open http://127.0.0.1:5000/register and create an analyst account. Each account starts with an empty dashboard. Use **Upload transactions** to upload your own CSV. `data/sample_transactions.csv` is an optional sample file that you can choose manually; it is not automatically loaded.

## CSV upload columns
`transaction_id, customer_name, account_no, city, transaction_time, amount, merchant, location, channel`
Evaluate it using an appropriate holdout set and fraud-sensitive metrics before use.

## Security note
This is a student prototype, not production banking software. Add CSRF protection, rate limiting, audit logs, migrations, secure cookie settings, stronger admin provisioning, and comprehensive validation before any real deployment.
