-- ==============================
-- 🧭 INVENTORY DATABASE INSPECTION SCRIPT
-- ==============================

-- 1️⃣ Show all tables in the database
.headers on
.mode column
.print '📋 All tables in the database:'
.tables

-- 2️⃣ Show structure (schema) of each table
.print '\n🧱 USERS TABLE STRUCTURE:'
.schema users

.print '\n📦 ITEMS TABLE STRUCTURE:'
.schema items

-- 3️⃣ Show all records from users table
.print '\n👤 USERS TABLE DATA:'
SELECT * FROM users;

-- 4️⃣ Show all records from items table
.print '\n📦 ITEMS TABLE DATA:'
SELECT * FROM items;

-- 5️⃣ Show record counts
.print '\n📊 TOTAL USERS:'
SELECT COUNT(*) AS total_users FROM users;

.print '\n📊 TOTAL ITEMS:'
SELECT COUNT(*) AS total_items FROM items;



-- ==============================
-- END OF SCRIPT
-- ==============================
