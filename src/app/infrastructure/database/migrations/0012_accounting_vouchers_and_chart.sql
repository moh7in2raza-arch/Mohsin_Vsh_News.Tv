-- Accounting groups and headers are parents for the existing flat chart.
CREATE TABLE IF NOT EXISTS account_groups (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (
        type IN ('Asset', 'Liability', 'Equity', 'Income', 'Expense')
    ),
    normal_balance CHAR(1) NOT NULL CHECK (
        normal_balance IN ('D', 'C')
    ),
    UNIQUE (id, type)
);

CREATE TABLE IF NOT EXISTS account_headers (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (
        type IN ('Asset', 'Liability', 'Equity', 'Income', 'Expense')
    ),
    group_id BIGINT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (id, type),
    UNIQUE (group_id, name),
    FOREIGN KEY (group_id, type) REFERENCES account_groups(id, type)
);

ALTER TABLE accounts
    ADD COLUMN IF NOT EXISTS header_id BIGINT;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'accounts_header_type_fkey'
          AND conrelid = 'accounts'::regclass
    ) THEN
        ALTER TABLE accounts
            ADD CONSTRAINT accounts_header_type_fkey
            FOREIGN KEY (header_id, type)
            REFERENCES account_headers (id, type);
    END IF;
END;
$$;

INSERT INTO account_groups (code, name, type, normal_balance)
VALUES
    ('ASSET', 'Assets', 'Asset', 'D'),
    ('LIABILITY', 'Liabilities', 'Liability', 'C'),
    ('EQUITY', 'Equity', 'Equity', 'C'),
    ('INCOME', 'Income', 'Income', 'C'),
    ('EXPENSE', 'Expenses', 'Expense', 'D')
ON CONFLICT (code) DO NOTHING;

INSERT INTO account_headers (code, name, type, group_id)
SELECT h.code, h.name, h.type, g.id
FROM (VALUES
    ('ASSET_CASH', 'Cash and Bank', 'Asset', 'ASSET'),
    ('ASSET_RECEIVABLES', 'Accounts Receivable', 'Asset', 'ASSET'),
    ('ASSET_INVENTORY', 'Inventory', 'Asset', 'ASSET'),
    ('ASSET_FIXED', 'Fixed Assets', 'Asset', 'ASSET'),
    ('ASSET_OTHER', 'Other Assets', 'Asset', 'ASSET'),
    ('LIABILITY_PAYABLES', 'Accounts Payable', 'Liability', 'LIABILITY'),
    ('LIABILITY_ACCRUED', 'Accrued Expenses', 'Liability', 'LIABILITY'),
    ('LIABILITY_LOANS', 'Loans Payable', 'Liability', 'LIABILITY'),
    ('LIABILITY_OTHER', 'Other Liabilities', 'Liability', 'LIABILITY'),
    ('EQUITY_OWNER', 'Owner Capital', 'Equity', 'EQUITY'),
    ('EQUITY_RETAINED', 'Retained Earnings', 'Equity', 'EQUITY'),
    ('EQUITY_OTHER', 'Other Equity', 'Equity', 'EQUITY'),
    ('INCOME_SALES', 'Sales Revenue', 'Income', 'INCOME'),
    ('INCOME_SERVICE', 'Service Revenue', 'Income', 'INCOME'),
    ('INCOME_OTHER', 'Other Income', 'Income', 'INCOME'),
    ('EXPENSE_SALARY', 'Salary Expense', 'Expense', 'EXPENSE'),
    ('EXPENSE_RENT', 'Rent Expense', 'Expense', 'EXPENSE'),
    ('EXPENSE_UTILITIES', 'Utilities Expense', 'Expense', 'EXPENSE'),
    ('EXPENSE_OFFICE', 'Office Expense', 'Expense', 'EXPENSE'),
    ('EXPENSE_TRANSPORT', 'Transport Expense', 'Expense', 'EXPENSE'),
    ('EXPENSE_MISC', 'Miscellaneous Expense', 'Expense', 'EXPENSE'),
    ('EXPENSE_OTHER', 'Other Expenses', 'Expense', 'EXPENSE')
) AS h(code, name, type, group_code)
JOIN account_groups g ON g.code = h.group_code
ON CONFLICT (code) DO NOTHING;

-- Seed the requested posting accounts only when an equivalent name and type
-- are not already present. Existing account ids, balances, and names are kept.
INSERT INTO accounts (code, name, type, normal_balance, is_active, header_id)
SELECT s.code, s.name, s.type, s.normal_balance, TRUE, h.id
FROM (VALUES
    ('1000', 'Cash in Hand', 'Asset', 'D', 'ASSET_CASH'),
    ('1015', 'Cash at Bank', 'Asset', 'D', 'ASSET_CASH'),
    ('1100', 'Accounts Receivable', 'Asset', 'D', 'ASSET_RECEIVABLES'),
    ('1200', 'Inventory', 'Asset', 'D', 'ASSET_INVENTORY'),
    ('1500', 'Fixed Assets', 'Asset', 'D', 'ASSET_FIXED'),
    ('2000', 'Accounts Payable', 'Liability', 'C', 'LIABILITY_PAYABLES'),
    ('2010', 'Accrued Expenses', 'Liability', 'C', 'LIABILITY_ACCRUED'),
    ('2200', 'Loans Payable', 'Liability', 'C', 'LIABILITY_LOANS'),
    ('3200', 'Owner Capital', 'Equity', 'C', 'EQUITY_OWNER'),
    ('3100', 'Retained Earnings', 'Equity', 'C', 'EQUITY_RETAINED'),
    ('4200', 'Sales Revenue', 'Income', 'C', 'INCOME_SALES'),
    ('4300', 'Service Revenue', 'Income', 'C', 'INCOME_SERVICE'),
    ('4100', 'Other Income', 'Income', 'C', 'INCOME_OTHER'),
    ('5010', 'Salary Expense', 'Expense', 'D', 'EXPENSE_SALARY'),
    ('5100', 'Rent Expense', 'Expense', 'D', 'EXPENSE_RENT'),
    ('5200', 'Utilities Expense', 'Expense', 'D', 'EXPENSE_UTILITIES'),
    ('5300', 'Office Expense', 'Expense', 'D', 'EXPENSE_OFFICE'),
    ('5400', 'Transport Expense', 'Expense', 'D', 'EXPENSE_TRANSPORT'),
    ('5500', 'Miscellaneous Expense', 'Expense', 'D', 'EXPENSE_MISC')
) AS s(code, name, type, normal_balance, header_code)
JOIN account_headers h ON h.code = s.header_code AND h.type = s.type
WHERE NOT EXISTS (
    SELECT 1 FROM accounts existing
    WHERE lower(existing.name) = lower(s.name)
      AND existing.type = s.type
)
ON CONFLICT (code) DO NOTHING;

-- Attach all legacy accounts to a matching header without renaming them.
UPDATE accounts a
SET header_id = h.id
FROM account_headers h
WHERE h.code = CASE a.type
    WHEN 'Asset' THEN CASE lower(a.name)
        WHEN 'cash in hand' THEN 'ASSET_CASH'
        WHEN 'bank' THEN 'ASSET_CASH'
        WHEN 'cash at bank' THEN 'ASSET_CASH'
        WHEN 'accounts receivable' THEN 'ASSET_RECEIVABLES'
        WHEN 'inventory' THEN 'ASSET_INVENTORY'
        WHEN 'fixed assets' THEN 'ASSET_FIXED'
        ELSE 'ASSET_OTHER'
    END
    WHEN 'Liability' THEN CASE lower(a.name)
        WHEN 'accounts payable' THEN 'LIABILITY_PAYABLES'
        WHEN 'salaries payable' THEN 'LIABILITY_ACCRUED'
        WHEN 'accrued expenses' THEN 'LIABILITY_ACCRUED'
        WHEN 'loans payable' THEN 'LIABILITY_LOANS'
        ELSE 'LIABILITY_OTHER'
    END
    WHEN 'Equity' THEN CASE lower(a.name)
        WHEN 'owner''s capital' THEN 'EQUITY_OWNER'
        WHEN 'owner capital' THEN 'EQUITY_OWNER'
        WHEN 'retained earnings' THEN 'EQUITY_RETAINED'
        ELSE 'EQUITY_OTHER'
    END
    WHEN 'Income' THEN CASE lower(a.name)
        WHEN 'sales revenue' THEN 'INCOME_SALES'
        WHEN 'service income' THEN 'INCOME_SERVICE'
        WHEN 'service revenue' THEN 'INCOME_SERVICE'
        WHEN 'other income' THEN 'INCOME_OTHER'
        ELSE 'INCOME_OTHER'
    END
    WHEN 'Expense' THEN CASE lower(a.name)
        WHEN 'salaries expense' THEN 'EXPENSE_SALARY'
        WHEN 'salary expense' THEN 'EXPENSE_SALARY'
        WHEN 'rent expense' THEN 'EXPENSE_RENT'
        WHEN 'utilities expense' THEN 'EXPENSE_UTILITIES'
        WHEN 'office expense' THEN 'EXPENSE_OFFICE'
        WHEN 'transport expense' THEN 'EXPENSE_TRANSPORT'
        WHEN 'miscellaneous expense' THEN 'EXPENSE_MISC'
        ELSE 'EXPENSE_OTHER'
    END
END
AND h.type = a.type
AND a.header_id IS DISTINCT FROM h.id;

ALTER TABLE accounts
    ALTER COLUMN header_id SET NOT NULL;

ALTER TABLE voucher_headers
    ADD COLUMN IF NOT EXISTS voucher_type TEXT NOT NULL DEFAULT 'Journal',
    ADD COLUMN IF NOT EXISTS reference_no TEXT NOT NULL DEFAULT '';

ALTER TABLE voucher_headers
    DROP CONSTRAINT IF EXISTS voucher_status_valid,
    ADD CONSTRAINT voucher_status_valid CHECK (
        status IN ('Draft', 'Submitted', 'Approved', 'Posted', 'Reversed', 'Deleted')
    );

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'voucher_type_valid'
          AND conrelid = 'voucher_headers'::regclass
    ) THEN
        ALTER TABLE voucher_headers
            ADD CONSTRAINT voucher_type_valid CHECK (
                voucher_type IN ('Journal', 'Payment', 'Receipt',
                                 'Contra', 'Sales', 'Purchase')
            );
    END IF;
END;
$$;

INSERT INTO permissions (code)
VALUES ('voucher.delete_draft')
ON CONFLICT (code) DO NOTHING;

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
JOIN permissions p ON p.code = 'voucher.delete_draft'
WHERE r.name IN ('Clerk', 'Accountant', 'Admin')
ON CONFLICT DO NOTHING;

-- Fiscal years run from July 1 through June 30. Do not overlap an existing
-- user-configured period or replace its name/dates.
DO $$
DECLARE
    fiscal_start DATE;
    fiscal_end DATE;
    fiscal_name TEXT;
BEGIN
    fiscal_start := make_date(
        EXTRACT(YEAR FROM current_date)::INTEGER
            - CASE WHEN EXTRACT(MONTH FROM current_date) < 7 THEN 1 ELSE 0 END,
        7, 1
    );
    fiscal_end := make_date(EXTRACT(YEAR FROM fiscal_start)::INTEGER + 1, 6, 30);
    fiscal_name := 'FY'
        || EXTRACT(YEAR FROM fiscal_start)::INTEGER::TEXT
        || '-'
        || right(EXTRACT(YEAR FROM fiscal_end)::INTEGER::TEXT, 2);

    IF NOT EXISTS (
        SELECT 1 FROM fiscal_periods
        WHERE start_date <= fiscal_end AND end_date >= fiscal_start
    ) THEN
        INSERT INTO fiscal_periods (name, start_date, end_date, is_closed)
        VALUES (fiscal_name, fiscal_start, fiscal_end, FALSE)
        ON CONFLICT (name) DO NOTHING;
    END IF;
END;
$$;
