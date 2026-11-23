
INSERT INTO company_settings (id, company_name, address, phone, email, website, logo_path, tax_number)
VALUES (
    TRUE,
    'Visionary Baluchistan Media Corporation Pvt Ltd',
    'Vsh News TV Station Office: Uzma Arcade, Suite 201, 2nd Floor, Khayaban-e-Iqbal, Block 7, Clifton, Karachi.',
    '92-21-35308112, 92-21-35308113, 92-21-35308114',
    'info@vshnews.tv',
    'www.vshnews.tv',
    'assets/vsh_logo.png.png',
    ''
)
ON CONFLICT (id) DO UPDATE SET
    company_name = EXCLUDED.company_name,
    address = EXCLUDED.address,
    phone = EXCLUDED.phone;

ALTER TABLE voucher_headers
    ADD COLUMN IF NOT EXISTS cheque_no TEXT NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS cheque_date DATE NULL,
    ADD COLUMN IF NOT EXISTS party_name TEXT NOT NULL DEFAULT '';
