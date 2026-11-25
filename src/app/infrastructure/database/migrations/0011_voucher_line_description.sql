ALTER TABLE voucher_lines
    ADD COLUMN IF NOT EXISTS description TEXT;
