-- BACK UP bank_fraud_db before running this migration.
-- This migration intentionally leaves existing records owner_id = NULL. They will not
-- appear in any user's dashboard until an administrator explicitly assigns ownership.
-- Run once against the existing MySQL database.

ALTER TABLE customers
  ADD COLUMN owner_id INT NULL,
  ADD INDEX ix_customers_owner_id (owner_id),
  ADD CONSTRAINT fk_customers_owner_id_users
    FOREIGN KEY (owner_id) REFERENCES users(user_id);

-- MySQL normally names the unique index for account_no "account_no". Check with
-- SHOW INDEX FROM customers; and replace that index name below if yours differs.
ALTER TABLE customers
  DROP INDEX account_no,
  ADD CONSTRAINT uq_customer_owner_account UNIQUE (owner_id, account_no);

ALTER TABLE transactions
  ADD COLUMN owner_id INT NULL,
  ADD INDEX ix_transactions_owner_id (owner_id),
  ADD CONSTRAINT fk_transactions_owner_id_users
    FOREIGN KEY (owner_id) REFERENCES users(user_id);

-- After migration, the app assigns owner_id for all new uploads. Do not set ownership
-- for old rows unless you have verified which user owns each row.
