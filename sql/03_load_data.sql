-- ============================================================
-- MERIDIAN SALES INTELLIGENCE — Stage Upload & Data Loading
-- Database: MERIDIAN_SALES | Schema: GOLD
-- ============================================================

-- ------------------------------------------------------------
-- STEP 1: Upload CSV files to internal stage
-- Run these from SnowSQL or a Snowflake client that supports PUT
-- ------------------------------------------------------------
PUT file://data/q1_deals.csv @MERIDIAN_SALES.GOLD.MERIDIAN_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://data/q1_reps.csv @MERIDIAN_SALES.GOLD.MERIDIAN_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://data/q2_deals.csv @MERIDIAN_SALES.GOLD.MERIDIAN_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://data/q2_reps.csv @MERIDIAN_SALES.GOLD.MERIDIAN_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;

-- Verify uploads
LIST @MERIDIAN_SALES.GOLD.MERIDIAN_STAGE;

-- ------------------------------------------------------------
-- STEP 2: Load data into tables
-- ------------------------------------------------------------
COPY INTO MERIDIAN_SALES.GOLD.Q1_DEALS
FROM @MERIDIAN_SALES.GOLD.MERIDIAN_STAGE/q1_deals.csv
FILE_FORMAT = (FORMAT_NAME = 'MERIDIAN_SALES.GOLD.MERIDIAN_CSV_FORMAT')
ON_ERROR = ABORT_STATEMENT;

COPY INTO MERIDIAN_SALES.GOLD.Q2_DEALS
FROM @MERIDIAN_SALES.GOLD.MERIDIAN_STAGE/q2_deals.csv
FILE_FORMAT = (FORMAT_NAME = 'MERIDIAN_SALES.GOLD.MERIDIAN_CSV_FORMAT')
ON_ERROR = ABORT_STATEMENT;

COPY INTO MERIDIAN_SALES.GOLD.Q1_REPS
FROM @MERIDIAN_SALES.GOLD.MERIDIAN_STAGE/q1_reps.csv
FILE_FORMAT = (FORMAT_NAME = 'MERIDIAN_SALES.GOLD.MERIDIAN_CSV_FORMAT')
ON_ERROR = ABORT_STATEMENT;

COPY INTO MERIDIAN_SALES.GOLD.Q2_REPS
FROM @MERIDIAN_SALES.GOLD.MERIDIAN_STAGE/q2_reps.csv
FILE_FORMAT = (FORMAT_NAME = 'MERIDIAN_SALES.GOLD.MERIDIAN_CSV_FORMAT')
ON_ERROR = ABORT_STATEMENT;

-- ------------------------------------------------------------
-- STEP 3: Verify row counts
-- Expected: Q1_DEALS=88, Q2_DEALS=92, Q1_REPS=10, Q2_REPS=10
-- ------------------------------------------------------------
SELECT 'Q1_DEALS' AS table_name, COUNT(*) AS row_count FROM MERIDIAN_SALES.GOLD.Q1_DEALS
UNION ALL
SELECT 'Q2_DEALS', COUNT(*) FROM MERIDIAN_SALES.GOLD.Q2_DEALS
UNION ALL
SELECT 'Q1_REPS', COUNT(*) FROM MERIDIAN_SALES.GOLD.Q1_REPS
UNION ALL
SELECT 'Q2_REPS', COUNT(*) FROM MERIDIAN_SALES.GOLD.Q2_REPS;
