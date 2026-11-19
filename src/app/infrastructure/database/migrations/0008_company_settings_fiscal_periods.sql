CREATE TABLE IF NOT EXISTS company_settings (
    id BOOLEAN PRIMARY KEY DEFAULT TRUE CHECK (id),
    company_name TEXT NOT NULL,
    address TEXT NOT NULL DEFAULT '',
    phone TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL DEFAULT '',
    website TEXT NOT NULL DEFAULT '',
    logo_path TEXT,
    tax_number TEXT
);

CREATE TABLE IF NOT EXISTS fiscal_periods (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_closed BOOLEAN NOT NULL DEFAULT FALSE
);

INSERT INTO permissions (code)
VALUES
    ('voucher.view'),
    ('account.view'),
    ('account.manage'),
    ('report.view')
ON CONFLICT (code) DO NOTHING;

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles AS r
CROSS JOIN permissions AS p
WHERE r.name IN ('Clerk', 'Accountant', 'Approver', 'Admin')
  AND p.code IN ('voucher.view', 'account.view', 'account.manage', 'report.view')
ON CONFLICT DO NOTHING;
