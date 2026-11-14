# Builds the installer, enforcing ADR-0001 sections 1-3. Run from anywhere:
#   powershell -ExecutionPolicy Bypass -File tools\build_exe.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root
$py = Join-Path $root "venv\Scripts\python.exe"

# --- ADR-0001 s.2: Python 3.12, 64-bit
if (-not (Test-Path $py)) { throw "venv not found at $py" }
$info = (& $py -c "import sys,struct;print(sys.version_info[0],sys.version_info[1],struct.calcsize('P')*8)").Trim()
if ($info -ne "3 12 64") { throw "ADR-0001 requires Python 3.12 64-bit (found: $info)" }

# --- ADR-0001 s.1: WSL2 (warn only; it is a platform requirement, not a build one)
$wsl = ((& wsl.exe -l -v 2>&1 | Out-String) -replace "`0", "")
if ($wsl -notmatch "\s2\s*(\r?\n|$)") { Write-Warning "WSL2 distribution not detected (ADR-0001 s.1)" }

# --- ADR-0001 s.3: Inno Setup compiler path
$required = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
$existing = "C:\Users\HP\Downloads\VSH_Accounting\Inno Setup 6\ISCC.exe"
if (Test-Path $required) { $iscc = $required }
elseif (Test-Path $existing) {
    $iscc = $existing
    Write-Warning "ISCC found only at the legacy location; ADR-0001 s.3 requires: $required"
} else { throw "ISCC.exe not found at the ADR-0001 path: $required" }

Write-Host "== tests" -ForegroundColor Cyan
& $py -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "Tests failed - build stopped" }

Write-Host "== PyInstaller" -ForegroundColor Cyan
& $py -m PyInstaller build\vsh_erp.spec --noconfirm --distpath dist --workpath build\work
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }

Write-Host "== Inno Setup" -ForegroundColor Cyan
& $iscc build\installer.iss
if ($LASTEXITCODE -ne 0) { throw "ISCC failed" }

Write-Host "Done: dist\installer\ERPOffice-Setup.exe" -ForegroundColor Green
Name: "{autodesktop}\ERP Office"; Filename: "{app}\ERPOffice.exe"
