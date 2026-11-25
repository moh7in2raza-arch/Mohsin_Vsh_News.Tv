# VSH NEWS TV ERP PROJECT BIBLE

## Current Status
- GitHub Synced
- 29/29 Tests Passed
- PostgreSQL Working
- Employees Table Clean
- Departments Configured
- Accounts Configured

## Approved Templates

All PDF
All XLS/XLSX
All DOCX

are approved master templates.

## Dashboard Rules

- Logged-in user photo
- Employee photo from local folder
- KPI cards
- Attendance status
- Database status
- Quick actions

## Attendance Rules

Source:
iVMS-4200

Import:
CSV
XLS
XLSX

## Photo Rules

Source:

data/photos/

## Voucher Rules

Description
A/C Code
Debit
Credit

Grid based entry

Debit = Credit

## Release Plan

Employee Module
HR Letters
Vouchers
Reports
Ledgers
Attendance
Dashboard
EXE
Setup
Release

## Chart Of Accounts Source

File:

docs/decisions/source_data/Accounts.xls

Source Type:

Approved Business Data Source

Used By:

- Payment Voucher
- Receipt Voucher
- Journal Voucher
- Contra Voucher
- General Ledger
- Account Ledger
- Trial Balance
- Financial Reports

Rule:

Do not manually create account heads.

Use Account Code + Account Name from Accounts.xls.
