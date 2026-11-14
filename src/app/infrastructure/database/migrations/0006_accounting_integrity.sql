-- Voucher numbering and ownership
CREATE SEQUENCE IF NOT EXISTS voucher_no_seq;

ALTER TABLE voucher_headers
    ADD COLUMN IF NOT EXISTS created_by BIGINT REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

ALTER TABLE voucher_headers
    ADD CONSTRAINT voucher_status_valid
    CHECK (status IN ('Draft','Submitted','Approved','Posted','Reversed'));

-- Voucher lines: mandatory columns, one side per line, no negatives
UPDATE voucher_lines SET debit = 0 WHERE debit IS NULL;
UPDATE voucher_lines SET credit = 0 WHERE credit IS NULL;
ALTER TABLE voucher_lines
    ALTER COLUMN voucher_id SET NOT NULL,
    ALTER COLUMN account_id SET NOT NULL,
    ALTER COLUMN debit SET NOT NULL,
    ALTER COLUMN credit SET NOT NULL;
ALTER TABLE voucher_lines
    ADD CONSTRAINT voucher_line_one_side
    CHECK (debit >= 0 AND credit >= 0 AND (debit > 0) <> (credit > 0));
ALTER TABLE journal_lines
    ADD CONSTRAINT journal_line_one_side
    CHECK (debit >= 0 AND credit >= 0 AND (debit > 0) <> (credit > 0));

-- Journal entries: posting vs reversal, each voucher posted/reversed once
ALTER TABLE journal_entries
    ADD COLUMN kind TEXT NOT NULL DEFAULT 'Posting'
        CHECK (kind IN ('Posting','Reversal')),
    ADD COLUMN reverses_entry_id BIGINT REFERENCES journal_entries(id);
CREATE UNIQUE INDEX one_posting_per_voucher
    ON journal_entries (voucher_id) WHERE kind = 'Posting';
CREATE UNIQUE INDEX one_reversal_per_entry
    ON journal_entries (reverses_entry_id) WHERE reverses_entry_id IS NOT NULL;

CREATE INDEX voucher_lines_voucher_idx ON voucher_lines (voucher_id);
CREATE INDEX journal_lines_account_idx ON journal_lines (account_id);
CREATE INDEX journal_lines_entry_idx ON journal_lines (entry_id);
CREATE INDEX audit_log_created_idx ON audit_log (created_at);

-- Ledger and audit are append-only: corrections are made by reversal
CREATE FUNCTION forbid_change() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION '% on % is not allowed (append-only table)', TG_OP, TG_TABLE_NAME;
END;
$$;
CREATE TRIGGER journal_entries_append_only
    BEFORE UPDATE OR DELETE ON journal_entries
    FOR EACH ROW EXECUTE FUNCTION forbid_change();
CREATE TRIGGER journal_lines_append_only
    BEFORE UPDATE OR DELETE ON journal_lines
    FOR EACH ROW EXECUTE FUNCTION forbid_change();
CREATE TRIGGER audit_log_append_only
    BEFORE UPDATE OR DELETE ON audit_log
    FOR EACH ROW EXECUTE FUNCTION forbid_change();
    