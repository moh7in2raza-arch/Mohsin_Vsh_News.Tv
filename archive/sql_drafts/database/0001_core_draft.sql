-- =====================================================
-- 0001_core.sql
-- ERP Foundation
-- Security, Company, Fiscal Periods, Chart of Accounts
-- PostgreSQL
-- =====================================================

CREATE EXTENSION IF NOT EXISTS btree_gist;

-- =====================================================
-- USERS
-- =====================================================

CREATE TABLE users (
    id                   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username             TEXT NOT NULL UNIQUE,
    full_name            TEXT NOT NULL,
    password_hash        TEXT NOT NULL,
    is_active            BOOLEAN NOT NULL DEFAULT TRUE,
    failed_attempts      INTEGER NOT NULL DEFAULT 0,
    locked_until         TIMESTAMPTZ,
    must_change_password BOOLEAN NOT NULL DEFAULT TRUE,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ
);

-- =====================================================
-- ROLES
-- =====================================================

CREATE TABLE roles (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- =====================================================
-- PERMISSIONS
-- =====================================================

CREATE TABLE permissions (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code TEXT NOT NULL UNIQUE
);

-- =====================================================
-- ROLE PERMISSIONS
-- =====================================================

CREATE TABLE role_permissions (
    role_id BIGINT NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id BIGINT NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

-- =====================================================
-- USER ROLES
-- =====================================================

CREATE TABLE user_roles (
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id BIGINT NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- =====================================================
-- COMPANY SETTINGS
-- Single Record Table
-- =====================================================

CREATE TABLE company_settings (
    id BOOLEAN PRIMARY KEY DEFAULT TRUE CHECK (id),
    company_name TEXT NOT NULL,
    address TEXT NOT NULL DEFAULT '',
    phone TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL DEFAULT '',
    website TEXT NOT NULL DEFAULT '',
    logo_path TEXT,
    tax_number TEXT,
    gst_rate NUMERIC(5,2) DEFAULT 0
        CHECK (gst_rate BETWEEN 0 AND 100)
);

-- =====================================================
-- FISCAL PERIODS
-- No overlap allowed
-- =====================================================

CREATE TABLE fiscal_periods (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_closed BOOLEAN NOT NULL DEFAULT FALSE,
    CHECK (end_date > start_date),

    EXCLUDE USING gist (
        daterange(start_date, end_date, '[]') WITH &&
    )
);

-- =====================================================
-- ACCOUNT GROUPS
-- =====================================================

CREATE TABLE account_groups (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    code TEXT NOT NULL UNIQUE,

    name TEXT NOT NULL,

    type TEXT NOT NULL CHECK (
        type IN (
            'Asset',
            'Liability',
            'Equity',
            'Income',
            'Expense'
        )
    ),

    parent_id BIGINT,

    UNIQUE (id, type),

    FOREIGN KEY (parent_id, type)
        REFERENCES account_groups(id, type)
);

-- =====================================================
-- ACCOUNTS
-- =====================================================

CREATE TABLE accounts (

    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    code TEXT NOT NULL UNIQUE,

    name TEXT NOT NULL,

    group_id BIGINT NOT NULL,

    type TEXT NOT NULL CHECK (
        type IN (
            'Asset',
            'Liability',
            'Equity',
            'Income',
            'Expense'
        )
    ),

    normal_balance CHAR(1) NOT NULL
        CHECK (normal_balance IN ('D','C')),

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    CHECK (
        (type IN ('Asset','Expense') AND normal_balance='D')
        OR
        (type IN ('Liability','Equity','Income') AND normal_balance='C')
    ),

    FOREIGN KEY (group_id, type)
        REFERENCES account_groups(id, type)
);

-- =====================================================
-- DEPARTMENTS (HR)
-- =====================================================

CREATE TABLE departments (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- =====================================================
-- EMPLOYEES (HR Foundation)
-- =====================================================

CREATE TABLE employees (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    employee_code TEXT NOT NULL UNIQUE,

    full_name TEXT NOT NULL,

    email TEXT,

    phone TEXT,

    department_id BIGINT
        REFERENCES departments(id),

    joining_date DATE NOT NULL,

    status TEXT NOT NULL DEFAULT 'Active'
        CHECK (
            status IN (
                'Active',
                'Inactive',
                'Resigned',
                'Terminated'
            )
        ),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =====================================================
-- ROLES SEED
-- =====================================================

INSERT INTO roles(name)
VALUES
('Clerk'),
('Accountant'),
('Approver'),
('Admin'),
('HR');

-- =====================================================
-- PERMISSIONS SEED
-- =====================================================

INSERT INTO permissions(code)
VALUES

('voucher.create'),
('voucher.edit_draft'),
('voucher.submit'),
('voucher.approve'),
('voucher.post'),
('voucher.reverse'),

('report.view'),

('mapping.manage'),

('user.manage'),
('backup.run'),

('settings.manage'),
('chart.manage'),
('period.manage'),

('staff.view'),
('staff.manage'),
('staff.change_status'),

('letter.generate'),
('letter.template_manage');

-- =====================================================
-- ROLE PERMISSIONS SEED
-- =====================================================

INSERT INTO role_permissions(role_id, permission_id)

SELECT r.id, p.id
FROM (
VALUES

('Clerk','voucher.create'),
('Clerk','voucher.edit_draft'),
('Clerk','voucher.submit'),
('Clerk','report.view'),

('Accountant','voucher.create'),
('Accountant','voucher.edit_draft'),
('Accountant','voucher.submit'),
('Accountant','voucher.post'),
('Accountant','voucher.reverse'),
('Accountant','report.view'),

('Approver','voucher.approve'),
('Approver','voucher.reverse'),
('Approver','mapping.manage'),
('Approver','report.view'),

('Admin','user.manage'),
('Admin','backup.run'),
('Admin','report.view'),
('Admin','settings.manage'),
('Admin','chart.manage'),
('Admin','period.manage'),

('HR','staff.view'),
('HR','staff.manage'),
('HR','staff.change_status'),
('HR','letter.generate'),
('HR','letter.template_manage'),
('HR','report.view')

) AS M(role_name, perm_code)

JOIN roles r
ON r.name = M.role_name

JOIN permissions p
ON p.code = M.perm_code;

-- =====================================================
-- VERIFICATION
-- =====================================================

SELECT COUNT(*) AS roles_count
FROM roles;

SELECT COUNT(*) AS permissions_count
FROM permissions;

SELECT COUNT(*) AS role_permissions_count
FROM role_permissions;