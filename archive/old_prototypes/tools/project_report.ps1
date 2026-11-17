# tools\project_report.ps1
# Read-only status report for C:\Mohsin_Vsh_News.tv
# Writes docs\project_status_report.md and prints it. Changes nothing.
# Run from the project root, in the VS Code terminal with .venv activated:
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\project_report.ps1
# Add -SkipDb to skip the database section (no password prompt).

param([switch]$SkipDb)

$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$out = New-Object System.Collections.Generic.List[string]
function Add-Line([string]$t) { $out.Add($t) }
function Add-Section([string]$t) { $out.Add(""); $out.Add("## $t"); $out.Add("") }
function Add-Block($lines) {
    $out.Add('```')
    foreach ($l in @($lines)) { $out.Add([string]$l) }
    $out.Add('```')
}

Add-Line "# Mohsin_Vsh_News.tv - project status report"
Add-Line ""
Add-Line "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm')  |  Folder: $root"

# 1. Tools -------------------------------------------------------------------
Add-Section "1. Tools"
$tools = @()
$tools += "python : " + ((python --version 2>&1) -join ' ')
$cmd = Get-Command python -ErrorAction SilentlyContinue
if ($cmd) { $tools += "python path : " + $cmd.Source }
$tools += "psql   : " + ((psql --version 2>&1) -join ' ')
$iscc = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
$tools += "ISCC.exe at default path : " + (Test-Path $iscc)
$prev = [Console]::OutputEncoding
try {
    [Console]::OutputEncoding = [Text.Encoding]::Unicode
    $wsl = wsl -l -v 2>&1
} finally { [Console]::OutputEncoding = $prev }
$tools += "wsl:"
$tools += ($wsl | ForEach-Object { "  $_" })
Add-Block $tools

Add-Line ""
Add-Line "Key packages in the active environment:"
$pk = python -m pip list --format=freeze 2>&1 |
    Where-Object { $_ -match '^(PySide6==|psycopg|argon2|pytest==|python-dotenv|pyinstaller|xlrd|openpyxl)' }
Add-Block $pk

# 2. Git ---------------------------------------------------------------------
Add-Section "2. Git"
$git = @()
$git += "branch : " + ((git branch --show-current 2>&1) -join ' ')
$git += "tags   : " + ((git tag 2>&1) -join ', ')
$git += ".venv ignored : " + ((git check-ignore .venv 2>&1) -join ' ')
$git += ""
$git += "last commits:"
$git += (git log --oneline -n 10 2>&1 | ForEach-Object { "  $_" })
$git += ""
$git += "uncommitted changes (git status --short):"
$st = git status --short 2>&1
if ($st) { $git += ($st | ForEach-Object { "  $_" }) } else { $git += "  (clean)" }
Add-Block $git

# 3. Files -------------------------------------------------------------------
Add-Section "3. Files (src, tests, tools, docs)"
$files = foreach ($d in 'src','tests','tools','docs') {
    if (Test-Path $d) {
        Get-ChildItem $d -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -notmatch '__pycache__|\.pytest_cache' }
    }
}
$rows = $files | ForEach-Object {
    $rel = $_.FullName.Substring($root.Length + 1)
    $state = if ($_.Length -eq 0) { 'EMPTY' } else { 'has content' }
    '{0,-72} {1,7} bytes  {2}' -f $rel, $_.Length, $state
}
Add-Block $rows
$empty = @($files | Where-Object { $_.Length -eq 0 }).Count
Add-Line ""
Add-Line "Total files: $(@($files).Count)  |  empty: $empty  |  with content: $(@($files).Count - $empty)"

# 4. Migrations --------------------------------------------------------------
Add-Section "4. SQL files"
$sql = Get-ChildItem -Recurse -Filter *.sql -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch '\\\.venv\\|\\archive\\' } |
    ForEach-Object { '{0,-80} {1,7} bytes' -f $_.FullName.Substring($root.Length + 1), $_.Length }
Add-Block $sql

# 5. Tests -------------------------------------------------------------------
Add-Section "5. Tests (pytest -q)"
$t = python -m pytest -q 2>&1 | Select-Object -Last 15
Add-Block $t

# 6. Database ----------------------------------------------------------------
Add-Section "6. Database erp_office (read-only queries, as erp_app)"
if ($SkipDb) {
    Add-Line "(skipped with -SkipDb)"
} else {
    $tmp = Join-Path $env:TEMP "project_report_queries.sql"
    @"
\echo --- schema_version
SELECT version, name, applied_at FROM schema_version ORDER BY version;
\echo --- tables and owners
SELECT tablename, tableowner FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;
\echo --- accounts columns
SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'accounts' ORDER BY ordinal_position;
\echo --- row counts
SELECT 'accounts' AS table_name, count(*) FROM accounts
UNION ALL SELECT 'users', count(*) FROM users
UNION ALL SELECT 'roles', count(*) FROM roles
UNION ALL SELECT 'permissions', count(*) FROM permissions;
"@ | Set-Content -Path $tmp -Encoding ASCII
    Write-Host "psql will ask for the erp_app password (typing is hidden)."
    $db = psql -U erp_app -d erp_office -f $tmp 2>&1
    Remove-Item $tmp -ErrorAction SilentlyContinue
    Add-Block $db
}

# Write ----------------------------------------------------------------------
New-Item -ItemType Directory -Force docs | Out-Null
$target = Join-Path $root "docs\project_status_report.md"
$out | Set-Content -Path $target -Encoding UTF8
$out | ForEach-Object { Write-Host $_ }
Write-Host ""
Write-Host "Report written to $target"
