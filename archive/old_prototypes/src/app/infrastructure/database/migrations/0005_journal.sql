CREATE TABLE journal_entries (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    voucher_id BIGINT NOT NULL
        REFERENCES voucher_headers(id),

    posted_by BIGINT
        REFERENCES users(id),

    posted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE journal_lines (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    entry_id BIGINT NOT NULL
        REFERENCES journal_entries(id),

    account_id BIGINT NOT NULL
        REFERENCES accounts(id),

    debit NUMERIC(14,2) NOT NULL DEFAULT 0,

    credit NUMERIC(14,2) NOT NULL DEFAULT 0
);

CREATE TABLE audit_log (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    user_id BIGINT
        REFERENCES users(id),

    action TEXT NOT NULL,

    entity TEXT,

    entity_id BIGINT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);