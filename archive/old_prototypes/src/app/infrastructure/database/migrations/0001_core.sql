CREATE TABLE users (
    id                   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username             TEXT NOT NULL UNIQUE,
    full_name            TEXT NOT NULL,
    password_hash        TEXT NOT NULL,
    is_active            BOOLEAN NOT NULL DEFAULT TRUE,
    failed_attempts      INTEGER NOT NULL DEFAULT 0,
    locked_until         TIMESTAMPTZ,
    must_change_password BOOLEAN NOT NULL DEFAULT TRUE,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE roles (
    id   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE permissions (
    id   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code TEXT NOT NULL UNIQUE
);

CREATE TABLE role_permissions (
    role_id       BIGINT NOT NULL REFERENCES roles(id),
    permission_id BIGINT NOT NULL REFERENCES permissions(id),
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE user_roles (
    user_id BIGINT NOT NULL REFERENCES users(id),
    role_id BIGINT NOT NULL REFERENCES roles(id),
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE accounts (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code           TEXT NOT NULL UNIQUE,
    name           TEXT NOT NULL,
    type           TEXT NOT NULL
                   CHECK (type IN ('Asset','Liability','Equity','Income','Expense')),
    normal_balance CHAR(1) NOT NULL CHECK (normal_balance IN ('D','C')),
    is_active      BOOLEAN NOT NULL DEFAULT TRUE,
    CHECK (
        (type IN ('Asset','Expense') AND normal_balance = 'D') OR
        (type IN ('Liability','Equity','Income') AND normal_balance = 'C')
    )
);

INSERT INTO roles (name) VALUES ('Clerk'), ('Accountant'), ('Approver'), ('Admin');

INSERT INTO permissions (code) VALUES
    ('voucher.create'), ('voucher.edit_draft'), ('voucher.submit'),
    ('voucher.approve'), ('voucher.post'), ('voucher.reverse'),
    ('report.view'), ('mapping.manage'), ('user.manage'), ('backup.run');

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM (VALUES
    ('Clerk','voucher.create'), ('Clerk','voucher.edit_draft'),
    ('Clerk','voucher.submit'), ('Clerk','report.view'),
    ('Accountant','voucher.create'), ('Accountant','voucher.edit_draft'),
    ('Accountant','voucher.submit'), ('Accountant','voucher.post'),
    ('Accountant','voucher.reverse'), ('Accountant','report.view'),
    ('Approver','voucher.approve'), ('Approver','voucher.reverse'),
    ('Approver','mapping.manage'), ('Approver','report.view'),
    ('Admin','user.manage'), ('Admin','backup.run'), ('Admin','report.view')
) AS m(role_name, perm_code)
JOIN roles r ON r.name = m.role_name
JOIN permissions p ON p.code = m.perm_code;
