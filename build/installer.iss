; Compiled by tools\build_exe.ps1 (Inno Setup 6.3+ per ADR-0001)
[Setup]
AppName=ERP Office Management
AppVersion=0.1.0
DefaultDirName={autopf}\ERP Office
DefaultGroupName=ERP Office
OutputDir=..\dist\installer
OutputBaseFilename=ERPOffice-Setup
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin

[Files]
Source: "..\dist\ERPOffice\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion
; Settings file is created once and never overwritten or removed on upgrade
Source: "..\.env.example"; DestDir: "{app}"; DestName: ".env"; Flags: onlyifdoesntexist uninsneveruninstall

[Icons]
Name: "{group}\ERP Office"; Filename: "{app}\ERPOffice.exe"
Name: "{autodesktop}\ERP Office"; Filename: "{app}\ERPOffice.exe"
