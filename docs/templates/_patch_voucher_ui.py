from pathlib import Path
from datetime import datetime
import re, shutil, subprocess, sys

root = Path.cwd()
app = root / "src" / "vsh_acc" / "app.py"
acct = root / "src" / "vsh_acc" / "accounting.py"
db = root / "data" / "vsh_accounting.db"

if not app.exists() or not acct.exists() or not db.exists():
    raise SystemExit("STOP: app.py, accounting.py, or the actual database is missing.")

import sqlite3
con = sqlite3.connect(db)
cols = {r[1] for r in con.execute("PRAGMA table_info(vouchers)")}
required = {"payee", "cheque_no", "cheque_date", "amount_in_words",
            "prepared_by_name", "verified_by_name", "received_by_name",
            "checked_by_name", "approved_by_name"}
con.close()
if not required.issubset(cols):
    raise SystemExit("STOP: required voucher columns are missing. Do not patch.")

backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backups = []
for p in (app, acct):
    b = backup_dir / f"{p.stem}_before_voucher_ui_{stamp}.py"
    shutil.copy2(p, b)
    backups.append((p, b))
print("Source backups:")
for p, b in backups:
    print(" ", b)

def replace_function(source, name, new_text):
    pattern = rf"(?ms)^    def {re.escape(name)}\b.*?(?=^    def |\Z)"
    result, n = re.subn(pattern, lambda m: new_text.rstrip() + "\n\n", source, count=1)
    if n != 1:
        raise RuntimeError(f"Could not safely locate function {name}")
    return result

try:
    a = acct.read_text(encoding="utf-8-sig")
    a = replace_function(a, "_insert_voucher", '''    def _insert_voucher(self, type_id, prefix, voucher_date, narration, lines,
                        reference_no, reversal_of=None, voucher_fields=None) -> int:
        """Insert a voucher and its lines; amounts supplied in rupees."""
        _check_date(voucher_date)
        if not narration or not narration.strip():
            raise AccountingError("Narration zaroori hai")
        fields = dict(voucher_fields or {})
        allowed = {
            "payee", "cheque_no", "cheque_date", "amount_in_words",
            "prepared_by_name", "verified_by_name", "received_by_name",
            "checked_by_name", "approved_by_name"
        }
        fields = {k: (str(v).strip() if v is not None else None)
                  for k, v in fields.items() if k in allowed}
        try:
            with self.conn:
                number = self._next_number(type_id, prefix, voucher_date[:4])
                base_cols = ["voucher_no", "voucher_type_id", "voucher_date",
                             "narration", "reference_no", "created_by", "reversal_of"]
                base_vals = [number, type_id, voucher_date, narration.strip(),
                             reference_no, self.user.id, reversal_of]
                cols = {r[1] for r in self.conn.execute("PRAGMA table_info(vouchers)")}
                extra = {k: v for k, v in fields.items() if k in cols}
                all_cols = base_cols + list(extra)
                all_vals = base_vals + list(extra.values())
                sql = ("INSERT INTO vouchers (" + ", ".join(all_cols) + ") VALUES (" +
                       ", ".join("?" for _ in all_cols) + ")")
                vid = self.conn.execute(sql, all_vals).lastrowid
                for i, ln in enumerate(lines, 1):
                    self.conn.execute(
                        "INSERT INTO voucher_lines(voucher_id, line_no, account_id, debit, credit, line_narration) "
                        "VALUES (?,?,?,?,?,?)",
                        (vid, i, self._account_id(ln["account"]),
                         to_paisa(ln.get("debit", 0)),
                         to_paisa(ln.get("credit", 0)), ln.get("narration"))
                    )
                return vid
        except sqlite3.IntegrityError as exc:
            raise AccountingError(str(exc)) from None''')

    a = replace_function(a, "create_voucher", '''    def create_voucher(self, type_code: str, voucher_date: str, narration: str, lines: list,
                       reference_no: str | None = None, payee: str | None = None,
                       cheque_no: str | None = None, cheque_date: str | None = None,
                       amount_in_words: str | None = None,
                       prepared_by_name: str | None = None,
                       verified_by_name: str | None = None,
                       received_by_name: str | None = None,
                       checked_by_name: str | None = None,
                       approved_by_name: str | None = None) -> int:
        require_permission(self.user, "voucher.create")
        t = self._type_row(type_code)
        self._check_type_allowed(t["id"])
        fields = {
            "payee": payee, "cheque_no": cheque_no, "cheque_date": cheque_date,
            "amount_in_words": amount_in_words, "prepared_by_name": prepared_by_name,
            "verified_by_name": verified_by_name, "received_by_name": received_by_name,
            "checked_by_name": checked_by_name, "approved_by_name": approved_by_name,
        }
        return self._insert_voucher(t["id"], t["prefix"], voucher_date, narration, lines,
                                    reference_no, voucher_fields=fields)''')
    acct.write_text(a, encoding="utf-8", newline="\n")

    s = app.read_text(encoding="utf-8-sig")

    s = replace_function(s, "add_voucher_tab", '''    def add_voucher_tab(self):
        page = QWidget()
        outer = QVBoxLayout(page)
        form = QFormLayout()

        self.v_type = QComboBox()
        for row in self.conn.execute("SELECT code, name FROM voucher_types ORDER BY id"):
            self.v_type.addItem(f"{row['code']} - {row['name']}", row["code"])

        self.v_date = QDateEdit()
        self.v_date.setCalendarPopup(True)
        self.v_date.setDate(QDate.currentDate())

        self.v_payee = QLineEdit()
        self.v_cheque_no = QLineEdit()
        self.v_cheque_date = QDateEdit()
        self.v_cheque_date.setCalendarPopup(True)
        self.v_cheque_date.setDate(QDate.currentDate())
        self.v_cheque_date.setSpecialValueText("Not specified")
        self.v_cheque_date.setDate(QDate(1900, 1, 1))
        self.v_reference = QLineEdit()
        self.v_narration = QLineEdit()
        self.v_narration.setPlaceholderText("Particulars / purpose of payment")
        self.v_debit = QLineEdit()
        self.v_credit = QLineEdit()
        self.v_debit.setPlaceholderText("Existing posting account code")
        self.v_credit.setPlaceholderText("Existing posting account code")
        self.v_amount = QDoubleSpinBox()
        self.v_amount.setRange(0.01, 999999999999.99)
        self.v_amount.setDecimals(2)
        self.v_amount.setValue(1.00)

        self.v_prepared = QLineEdit()
        self.v_verified = QLineEdit()
        self.v_received = QLineEdit()
        self.v_checked = QLineEdit()
        self.v_approved = QLineEdit()

        form.addRow("Voucher type:", self.v_type)
        form.addRow("Voucher date:", self.v_date)
        form.addRow("Payee:", self.v_payee)
        form.addRow("Cheque number:", self.v_cheque_no)
        form.addRow("Cheque date:", self.v_cheque_date)
        form.addRow("Reference number:", self.v_reference)
        form.addRow("Particulars / narration:", self.v_narration)
        form.addRow("Debit account code:", self.v_debit)
        form.addRow("Credit account code:", self.v_credit)
        form.addRow("Amount (PKR):", self.v_amount)
        form.addRow("Prepared by:", self.v_prepared)
        form.addRow("Verified by:", self.v_verified)
        form.addRow("Received by:", self.v_received)
        form.addRow("Checked by:", self.v_checked)
        form.addRow("Approved by:", self.v_approved)
        outer.addLayout(form)

        note = QLabel(
            "Creates a draft voucher with one debit line and one credit line. "
            "Use existing posting accounts, not group accounts. "
            "A draft is not a posted accounting transaction."
        )
        note.setWordWrap(True)
        outer.addWidget(note)
        btn = QPushButton("Create Voucher and Preview")
        btn.clicked.connect(self.create_voucher)
        outer.addWidget(btn)
        outer.addStretch(1)
        self.tabs.addTab(page, "Voucher Entry")''')

    s = replace_function(s, "create_voucher", '''    def create_voucher(self):
        try:
            amount = f"{self.v_amount.value():.2f}"
            cheque_date = self.v_cheque_date.date().toString("yyyy-MM-dd")
            if self.v_cheque_date.date() == QDate(1900, 1, 1):
                cheque_date = None
            voucher_id = self.accounting.create_voucher(
                type_code=self.v_type.currentData(),
                voucher_date=self.v_date.date().toString("yyyy-MM-dd"),
                narration=self.v_narration.text().strip(),
                reference_no=self.v_reference.text().strip() or None,
                payee=self.v_payee.text().strip() or None,
                cheque_no=self.v_cheque_no.text().strip() or None,
                cheque_date=cheque_date,
                prepared_by_name=self.v_prepared.text().strip() or None,
                verified_by_name=self.v_verified.text().strip() or None,
                received_by_name=self.v_received.text().strip() or None,
                checked_by_name=self.v_checked.text().strip() or None,
                approved_by_name=self.v_approved.text().strip() or None,
                lines=[
                    {"account": self.v_debit.text().strip(),
                     "debit": amount, "credit": "0",
                     "narration": self.v_narration.text().strip()},
                    {"account": self.v_credit.text().strip(),
                     "debit": "0", "credit": amount,
                     "narration": self.v_narration.text().strip()},
                ],
            )
            QMessageBox.information(
                self, "Voucher Created",
                "Draft voucher saved successfully. It has not been posted."
            )
            self.v_narration.clear()
            self.refresh_vouchers_if_available()
            self.show_voucher_preview(voucher_id)
        except Exception as exc:
            show_error(self, "Voucher could not be created", exc)''')

    s = replace_function(s, "show_voucher_preview", '''    def show_voucher_preview(self, voucher_id):
        """Printable VSH NEWS payment voucher using saved database fields."""
        try:
            from pathlib import Path
            from datetime import datetime
            v = self.accounting.get_voucher(int(voucher_id))
            type_row = self.conn.execute(
                "SELECT name FROM voucher_types WHERE id = ?", (v["voucher_type_id"],)
            ).fetchone()
            type_name = type_row["name"] if type_row else "Voucher"

            esc = lambda value: html.escape(str(value or ""))
            money = lambda value: f"{int(value or 0) / 100:,.2f}"
            total_debit = sum(int(line.get("debit") or 0) for line in v.get("lines", []))
            total_credit = sum(int(line.get("credit") or 0) for line in v.get("lines", []))

            def words_under_1000(n):
                ones = ["Zero", "One", "Two", "Three", "Four", "Five", "Six",
                        "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve",
                        "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen",
                        "Eighteen", "Nineteen"]
                tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty",
                        "Seventy", "Eighty", "Ninety"]
                out = []
                if n >= 100:
                    out.extend([ones[n // 100], "Hundred"])
                    n %= 100
                if n >= 20:
                    out.append(tens[n // 10])
                    n %= 10
                if n:
                    out.append(ones[n])
                return " ".join(out)

            def number_words(n):
                if n == 0:
                    return "Zero"
                parts = []
                for scale, label in [(10000000, "Crore"), (100000, "Lac"),
                                     (1000, "Thousand"), (1, "")]:
                    q, n = divmod(n, scale)
                    if q:
                        if scale == 1:
                            parts.append(words_under_1000(q))
                        else:
                            parts.append(words_under_1000(q) + " " + label)
                return " ".join(parts)

            total_paisa = total_debit or total_credit
            rupees, paisa = divmod(total_paisa, 100)
            amount_words = v.get("amount_in_words") or (
                number_words(rupees) + " Rupees and " +
                number_words(paisa) + " Paisa"
            )

            line_html = []
            for i, line in enumerate(v.get("lines", []), 1):
                description = line.get("line_narration") or v.get("narration") or ""
                line_html.append(
                    "<tr>"
                    f"<td>{i}</td>"
                    f"<td>{esc(line.get('account_code'))}</td>"
                    f"<td>{esc(description)}</td>"
                    f"<td class='num'>{money(line.get('debit'))}</td>"
                    f"<td class='num'>{money(line.get('credit'))}</td>"
                    "</tr>"
                )
            while len(line_html) < 5:
                line_html.append("<tr><td>&nbsp;</td><td></td><td></td><td></td><td></td></tr>")

            cheque_date = v.get("cheque_date") or ""
            reference = v.get("reference_no") or ""
            logo_html = ""
            candidates = [
                Path.cwd() / "assets" / "Logo.png",
                Path.cwd() / "assets" / "vsh_news_logo.png",
                Path.cwd() / "Logo.png",
                Path(__file__).resolve().parent / "assets" / "Logo.png",
                Path(__file__).resolve().parent / "assets" / "vsh_news_logo.png",
            ]
            logo = next((p for p in candidates if p.is_file()), None)
            if logo:
                logo_html = f"<div class='logo'>{esc(logo.name)}</div>"

            html_doc = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
@page {{ size: A4; margin: 12mm; }}
body {{ font-family: Arial, sans-serif; color:#172033; font-size:9pt; }}
.brand {{ background:#12345a; color:white; padding:14px; text-align:center; }}
.brand h1 {{ font-size:17pt; margin:0; }}
.brand div {{ margin-top:4px; font-size:9pt; }}
.vtitle {{ text-align:center; color:#12345a; font-size:15pt; margin:14px 0 8px; }}
table {{ width:100%; border-collapse:collapse; margin:7px 0; }}
td, th {{ border:1px solid #aab6c5; padding:6px; vertical-align:top; }}
.meta td {{ width:50%; }}
th {{ background:#e7eef6; color:#12345a; }}
.num {{ text-align:right; white-space:nowrap; }}
.totals td {{ font-weight:bold; background:#eef3f8; }}
.words {{ border:1px solid #aab6c5; padding:8px; margin-top:10px; }}
.signatures {{ margin-top:34px; }}
.signatures td {{ border:0; border-top:1px solid #53657a; text-align:center; width:20%; padding-top:6px; }}
.footer {{ margin-top:14px; color:#53657a; font-size:8pt; }}
</style></head><body>
<div class="brand">
<h1>Visionary Baluchistan Media Corporation (Pvt) Ltd</h1>
<div>VSH NEWS</div>
</div>
<div class="vtitle">{esc(type_name)} / PAYMENT VOUCHER</div>
<table class="meta">
<tr><td><b>Voucher No:</b> {esc(v.get('voucher_no'))}</td>
<td><b>Voucher Date:</b> {esc(v.get('voucher_date'))}</td></tr>
<tr><td><b>Cheque No:</b> {esc(v.get('cheque_no') or '-')}</td>
<td><b>Cheque Date:</b> {esc(cheque_date or '-')}</td></tr>
<tr><td colspan="2"><b>Payee:</b> {esc(v.get('payee') or '-')}</td></tr>
<tr><td colspan="2"><b>Particulars:</b> {esc(v.get('narration'))}</td></tr>
<tr><td><b>Reference:</b> {esc(reference or '-')}</td>
<td><b>Status:</b> {esc(v.get('status'))}</td></tr>
</table>
<table>
<thead><tr><th style="width:7%">Sr.</th><th style="width:16%">A/c Code</th>
<th>Description / Particulars</th><th>Debit (PKR)</th><th>Credit (PKR)</th></tr></thead>
<tbody>{''.join(line_html)}
<tr class="totals"><td colspan="3">TOTAL</td>
<td class="num">{money(total_debit)}</td><td class="num">{money(total_credit)}</td></tr>
</tbody></table>
<div class="words"><b>Amount in Words:</b> {esc(amount_words)}</div>
<table class="signatures"><tr>
<td>{esc(v.get('prepared_by_name') or '')}<br><b>Prepared By</b></td>
<td>{esc(v.get('verified_by_name') or '')}<br><b>Verified By</b></td>
<td>{esc(v.get('received_by_name') or '')}<br><b>Received By</b></td>
<td>{esc(v.get('checked_by_name') or '')}<br><b>Checked By</b></td>
<td>{esc(v.get('approved_by_name') or '')}<br><b>Approved By</b></td>
</tr></table>
<div class="footer">Printing Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
&nbsp;&nbsp; | &nbsp;&nbsp; VSH NEWS Accounting</div>
</body></html>"""

            document = QTextDocument(self)
            document.setHtml(html_doc)
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            dialog = QPrintPreviewDialog(printer, self)
            dialog.setWindowTitle(f"Voucher Preview - {v.get('voucher_no', '')}")
            dialog.resize(1000, 750)
            def render_preview(target_printer):
                if hasattr(document, "print_"):
                    document.print_(target_printer)
                else:
                    document.print(target_printer)
            dialog.paintRequested.connect(render_preview)
            dialog.exec()
        except Exception as exc:
            show_error(self, "Voucher preview could not be opened", exc)''')

    app.write_text(s, encoding="utf-8", newline="\n")

    result = subprocess.run(
        [str(root / ".venv" / "Scripts" / "python.exe"), "-m", "py_compile",
         str(app), str(acct)],
        capture_output=True, text=True
    )
    if result.returncode:
        raise RuntimeError("Python compile failed:\n" + result.stdout + result.stderr)

    print("\nSUCCESS: source files patched and Python syntax check passed.")
    print("Database was not modified by this patch.")
    print("NOTE: Existing vouchers are unchanged; new fields apply to new vouchers.")
except Exception as exc:
    print("\nPATCH FAILED:", exc)
    for original, backup in backups:
        shutil.copy2(backup, original)
        print("Restored:", original)
    sys.exit(1)
