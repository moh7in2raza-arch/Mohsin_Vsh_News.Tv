CREATE TABLE company_settings (
    id BOOLEAN PRIMARY KEY DEFAULT TRUE CHECK (id),
    company_name TEXT NOT NULL,
    address TEXT NOT NULL DEFAULT '',
    phone TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL DEFAULT '',
    website TEXT NOT NULL DEFAULT '',
    logo_path TEXT,
    tax_number TEXT
);

CREATE TABLE fiscal_periods (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_closed BOOLEAN NOT NULL DEFAULT FALSE
);
