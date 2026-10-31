-- =============================================================================
-- LabLine Database Cleanup Script
-- Safely purges legacy demo accounts, hardcoded credentials, and demo names
-- Verifies the authorized administrator credential:
-- 1. Administrator: nithin@gmail.com / 12345678
-- =============================================================================

-- 1. Delete legacy demo accounts by email
DELETE FROM users 
WHERE email IN ('admin@labline.com', 'yashasrao@gmail.com', 'nithinshetty1166@gmail.com');

-- 2. Delete legacy demo accounts by name (preserving nithin@gmail.com)
DELETE FROM users 
WHERE (name LIKE '%Nitish Kumar%' OR name LIKE '%Varshith Gowda%' OR name LIKE '%Aryan Sharma%')
  AND email != 'nithin@gmail.com';

-- 3. Update any legacy phlebotomist demo names
UPDATE phlebotomists 
SET name = 'Vijay Nair' 
WHERE name = 'Varshith Gowda';

-- 4. Remove any other administrator accounts so only nithin@gmail.com remains
DELETE FROM users 
WHERE role = 'admin' 
  AND email != 'nithin@gmail.com';

-- 5. Verify authorized accounts
SELECT id, name, email, role, created_at 
FROM users 
WHERE role = 'admin';
