# scan_latest.ps1 - read-only project scan
$P = "C:\Mohsin_Vsh_News.tv"
Set-Location $P
$out = Join-Path $P "docs\scan_latest.md"

& {
  "# Latest scan - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"

  "`n## 1. Git"
  git config --global --add safe.directory C:/Mohsin_Vsh_News.tv 2>$null
  "branch: $(git rev-parse --abbrev-ref HEAD)"
  git log -8 --format="%h | %ad | %s" --date=short
  "`n-- uncommitted --"
  git status --short

  "`n## 2. Migrations (files)"
  Get-ChildItem "$P\src\app\infrastructure\database\migrations\*.sql" |
    Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize | Out-String

  "## 3. Voucher template / ADR files"
  foreach ($d in "docs\templates\vouchers", "docs\adr", "docs\decisions") {
    "-- $d --"
    if (Test-Path "$P\$d") {
      Get-ChildItem "$P\$d" -Recurse -File |
        Select-Object FullName, Length, LastWriteTime | Format-Table -AutoSize | Out-String
    } else { "(folder nahi mila)" }
  }

  "## 4. Tests"
  & "$P\.venv\Scripts\python.exe" -m pytest -q 2>&1 | Select-Object -Last 8

  "`n## 5. Database (read-only)"
  $py = Join-Path $env:TEMP "scan_db.py"
  @'
import os
from dotenv import load_dotenv
import psycopg
load_dotenv(r"C:\Mohsin_Vsh_News.tv\.env")
c = psycopg.connect(host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"), user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"))
cur = c.cursor()
cur.execute("select version, name, applied_at from schema_version order by version")
print("schema_version:")
for r in cur.fetchall(): print("  ", r)
for t in ("voucher_headers", "voucher_lines", "company_settings"):
    cur.execute("select column_name, data_type from information_schema.columns "
                "where table_schema='public' and table_name=%s order by ordinal_position", (t,))
    print(f"\n{t}:")
    for r in cur.fetchall(): print("  ", r[0], "-", r[1])
for t in ("accounts", "users", "voucher_headers", "voucher_lines"):
    cur.execute(f"select count(*) from {t}")
    print(f"rows {t}:", cur.fetchone()[0])
'@ | Set-Content $py -Encoding UTF8
  & "$P\.venv\Scripts\python.exe" $py 2>&1
  Remove-Item $py -ErrorAction SilentlyContinue

  "`n## 6. Purani project_report.ps1 (full report)"
  powershell -NoProfile -ExecutionPolicy Bypass -File "$P\tools\project_report.ps1"
  "(docs\project_status_report.md dobara likhi gayi)"
} *>&1 | Tee-Object -FilePath $out

Write-Host "`nDone. Output: $out"
