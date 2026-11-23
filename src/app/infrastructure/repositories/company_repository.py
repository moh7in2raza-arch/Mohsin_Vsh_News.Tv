from src.app.infrastructure.repositories._sql import fetch_one


class CompanyRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_settings(self) -> dict | None:
        return fetch_one(
            self.conn,
            """SELECT company_name, address, phone, email, website, logo_path, tax_number
               FROM company_settings WHERE id = TRUE""",
        )

    def save_settings(
        self,
        company_name: str,
        address: str,
        phone: str,
        email: str = "",
        website: str = "",
        logo_path: str | None = None,
        tax_number: str | None = None,
    ) -> dict:
        row = fetch_one(
            self.conn,
            """INSERT INTO company_settings
                   (id, company_name, address, phone, email, website, logo_path, tax_number)
               VALUES (TRUE, %s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT (id) DO UPDATE SET
                   company_name = EXCLUDED.company_name,
                   address = EXCLUDED.address,
                   phone = EXCLUDED.phone,
                   email = EXCLUDED.email,
                   website = EXCLUDED.website,
                   logo_path = COALESCE(EXCLUDED.logo_path, company_settings.logo_path),
                   tax_number = EXCLUDED.tax_number
               RETURNING company_name, address, phone, email, website, logo_path, tax_number""",
            (company_name, address, phone, email, website, logo_path, tax_number),
        )
        return row or {}
