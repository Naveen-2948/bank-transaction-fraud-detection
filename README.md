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

## Existing database update

The application calls `db.create_all()`, which creates missing tables but does not alter existing tables. If you already ran an older version, back up your database and apply a migration before running this version. For a fresh student database, the simplest path is to create a new empty database and start the app again. Existing transaction/customer rows have no owner and should not be assigned to a user without confirming who owns them.

For an existing MySQL database, back it up first and review `migrations/2026_10_user_owned_data_mysql.sql`. It adds nullable owner columns so legacy rows remain unassigned and invisible to user dashboards, and replaces the global account-number uniqueness rule with per-user uniqueness. Check the actual unique index name on `customers.account_no` before running the script. Do not blindly assign historical rows to the first user.

## Important model limitation
The first runnable application uses transparent demo rules for scoring so the end-to-end flow works without inventing training labels. These scores are not a validated fraud model and must not be used for real banking decisions. `ml/train_model.py` trains a Random Forest only when you provide an authorized, representative labelled file at `data/labelled_transactions.csv` with columns `amount, merchant, location, channel, is_fraud`. Evaluate it using an appropriate holdout set and fraud-sensitive metrics before use.

## Security note
This is a student prototype, not production banking software. Add CSRF protection, rate limiting, audit logs, migrations, secure cookie settings, stronger admin provisioning, and comprehensive validation before any real deployment.
