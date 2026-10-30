-- =============================================================================
-- LabLine Database Cleanup Script
-- Safely purges legacy demo accounts, hardcoded credentials, and demo names
-- =============================================================================

-- 1. Delete legacy demo accounts by email
DELETE FROM users 
WHERE email IN ('admin@labline.com', 'yashasrao@gmail.com');

-- 2. Delete legacy demo accounts by name (preserving the single admin nithinshetty1166@gmail.com)
DELETE FROM users 
WHERE (name LIKE '%Nitish Kumar%' OR name LIKE '%Varshith Gowda%' OR name LIKE '%Aryan Sharma%')
  AND email != 'nithinshetty1166@gmail.com';

-- 3. Update any legacy phlebotomist demo names
UPDATE phlebotomists 
SET name = 'Vijay Nair' 
WHERE name = 'Varshith Gowda';

-- 4. Remove any other administrator accounts so exactly one administrator remains
DELETE FROM users 
WHERE role = 'admin' 
  AND email != 'nithinshetty1166@gmail.com';

-- 5. Verify single administrator account
SELECT id, name, email, role, created_at 
FROM users 
WHERE role = 'admin';
