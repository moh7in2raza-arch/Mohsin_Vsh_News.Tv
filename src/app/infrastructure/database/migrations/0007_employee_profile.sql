ALTER TABLE employees
    ADD COLUMN IF NOT EXISTS cnic TEXT NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS designation TEXT NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS salary NUMERIC(14,2) NOT NULL DEFAULT 0;

ALTER TABLE employees
    ADD CONSTRAINT employees_salary_nonnegative CHECK (salary >= 0);

CREATE UNIQUE INDEX IF NOT EXISTS employees_cnic_unique_nonblank
    ON employees (cnic) WHERE cnic <> '';

INSERT INTO permissions (code)
VALUES ('employee.view'), ('employee.manage')
ON CONFLICT (code) DO NOTHING;

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r JOIN permissions p
  ON p.code IN ('employee.view', 'employee.manage')
WHERE r.name = 'Admin'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, permission_id)
SELECT rp.role_id, pv.id
FROM role_permissions rp
JOIN permissions pm ON pm.id = rp.permission_id
JOIN permissions pv ON pv.code = 'employee.view'
WHERE pm.code = 'employee.manage'
ON CONFLICT DO NOTHING;
