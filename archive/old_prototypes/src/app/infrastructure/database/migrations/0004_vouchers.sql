CREATE TABLE voucher_headers (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    voucher_no TEXT NOT NULL UNIQUE,

    voucher_date DATE NOT NULL,

    narration TEXT,

    status TEXT NOT NULL DEFAULT 'Draft'
);

CREATE TABLE voucher_lines (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    voucher_id BIGINT
        REFERENCES voucher_headers(id),

    account_id BIGINT
        REFERENCES accounts(id),

    debit NUMERIC(14,2) DEFAULT 0,

    credit NUMERIC(14,2) DEFAULT 0
);