-- 0009: restrict account.manage to Accountant and Admin (forward-only)
DELETE FROM role_permissions
WHERE role_id IN (SELECT id FROM roles WHERE name IN ('Clerk', 'Approver'))
  AND permission_id = (SELECT id FROM permissions WHERE code = 'account.manage');
