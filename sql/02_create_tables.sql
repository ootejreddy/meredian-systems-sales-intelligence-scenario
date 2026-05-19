-- ============================================================
-- MERIDIAN SALES INTELLIGENCE — File Format & Table DDL
-- Database: MERIDIAN_SALES | Schema: GOLD
-- ============================================================

-- ------------------------------------------------------------
-- FILE FORMAT
-- ------------------------------------------------------------
CREATE OR REPLACE FILE FORMAT MERIDIAN_SALES.GOLD.MERIDIAN_CSV_FORMAT
  TYPE = CSV
  SKIP_HEADER = 1
  FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  NULL_IF = ('', 'NULL')
  EMPTY_FIELD_AS_NULL = TRUE;

-- ------------------------------------------------------------
-- TABLE: Q1_DEALS
-- ------------------------------------------------------------
CREATE OR REPLACE TABLE MERIDIAN_SALES.GOLD.Q1_DEALS (
  DEAL_ID VARCHAR(20),
  ACCOUNT_NAME VARCHAR(100),
  SEGMENT VARCHAR(20),
  REGION VARCHAR(20),
  REP_ID VARCHAR(10),
  STAGE VARCHAR(20),
  DEAL_VALUE NUMBER(12,2),
  CLOSE_DATE DATE,
  CREATED_DATE DATE,
  PRODUCT_LINE VARCHAR(50),
  LOSS_REASON VARCHAR(100)
)
COMMENT = 'Q1 2026 deals Jan-Mar. Final — all data is actual closed revenue.';

-- ------------------------------------------------------------
-- TABLE: Q2_DEALS
-- ------------------------------------------------------------
CREATE OR REPLACE TABLE MERIDIAN_SALES.GOLD.Q2_DEALS (
  DEAL_ID VARCHAR(20),
  ACCOUNT_NAME VARCHAR(100),
  SEGMENT VARCHAR(20),
  REGION VARCHAR(20),
  REP_ID VARCHAR(10),
  STAGE VARCHAR(20),
  DEAL_VALUE NUMBER(12,2),
  CLOSE_DATE DATE,
  CREATED_DATE DATE,
  PRODUCT_LINE VARCHAR(50),
  LOSS_REASON VARCHAR(100)
)
COMMENT = 'Q2 2026 deals Apr-Jun. In progress as of May 2 2026. Pipeline deals have EXPECTED close dates not actual.';

-- ------------------------------------------------------------
-- TABLE: Q1_REPS
-- ------------------------------------------------------------
CREATE OR REPLACE TABLE MERIDIAN_SALES.GOLD.Q1_REPS (
  REP_ID VARCHAR(10),
  REP_NAME VARCHAR(50),
  SEGMENT VARCHAR(20),
  REGION VARCHAR(20),
  QUOTA_Q1_2026 NUMBER(12,2),
  MANAGER VARCHAR(50),
  HIRE_DATE DATE
)
COMMENT = 'Sales rep details with Q1 2026 quota targets.';

-- ------------------------------------------------------------
-- TABLE: Q2_REPS
-- ------------------------------------------------------------
CREATE OR REPLACE TABLE MERIDIAN_SALES.GOLD.Q2_REPS (
  REP_ID VARCHAR(10),
  REP_NAME VARCHAR(50),
  SEGMENT VARCHAR(20),
  REGION VARCHAR(20),
  QUOTA_Q1_2026 NUMBER(12,2),
  QUOTA_Q2_2026 NUMBER(12,2),
  MANAGER VARCHAR(50),
  HIRE_DATE DATE
)
COMMENT = 'Sales rep details with both Q1 and Q2 2026 quota targets.';
