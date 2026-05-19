-- ================================================================
-- File: 05_data_quality.sql
-- Purpose: Data quality checks for Meridian sales dataset
-- Author: Sai Ootej Reddy Bachapally
-- Date: May 2026
--
-- KEY FINDING: Q2_DEALS is a full CRM snapshot
-- Contains all 88 Q1 deals carried forward + 4 new Q2 deals = 92
-- 15 deals show impossible stage regression (Closed Won → pipeline)
-- These are included in pipeline analysis per the synthetic dataset
-- design — they represent re-opened opportunities in the CRM
--
-- ANOMALY DEAL IDs (15 total):
-- OPP-020, OPP-049, OPP-050, OPP-076, OPP-077,
-- OPP-078, OPP-080, OPP-081, OPP-082, OPP-083,
-- OPP-084, OPP-085, OPP-086, OPP-087, OPP-088
-- ================================================================

USE ROLE MERIDIAN_ENGINEER;
USE DATABASE MERIDIAN_SALES;
USE SCHEMA GOLD;

-- CHECK 1: Find stage regression anomalies
-- Closed Won in Q1 but active pipeline in Q2
-- These 15 deals are data anomalies in synthetic dataset
SELECT 
    q1.DEAL_ID,
    q1.ACCOUNT_NAME,
    q1.REP_ID,
    q1.STAGE AS Q1_STAGE,
    q2.STAGE AS Q2_STAGE,
    q1.DEAL_VALUE,
    'Closed Won reverted to pipeline — data anomaly' 
        AS ANOMALY_TYPE,
    'Excluded from Q2 pipeline calculations' 
        AS IMPACT
FROM MERIDIAN_SALES.GOLD.Q1_DEALS q1
JOIN MERIDIAN_SALES.GOLD.Q2_DEALS q2 
    ON q1.DEAL_ID = q2.DEAL_ID
WHERE q1.STAGE = 'Closed Won'
AND q2.STAGE IN ('Proposal','Discovery','Negotiation')
ORDER BY q1.DEAL_ID;

-- CHECK 2: Q2 pipeline split
-- Carry-forward Q1 deals vs truly new Q2 deals
SELECT
    CASE 
        WHEN q1.DEAL_ID IS NOT NULL 
        THEN 'Carry-forward from Q1'
        ELSE 'New Q2 deal'
    END AS DEAL_ORIGIN,
    COUNT(*) AS DEAL_COUNT,
    SUM(q2.DEAL_VALUE) AS PIPELINE_VALUE
FROM MERIDIAN_SALES.GOLD.Q2_DEALS q2
LEFT JOIN MERIDIAN_SALES.GOLD.Q1_DEALS q1 
    ON q2.DEAL_ID = q1.DEAL_ID
WHERE q2.STAGE IN ('Proposal','Discovery','Negotiation')
AND q2.CLOSE_DATE >= '2026-04-01'
GROUP BY DEAL_ORIGIN
ORDER BY DEAL_ORIGIN;

-- CHECK 3: Truly new Q2 deals only
-- Should return exactly 4 deals
SELECT 
    q2.DEAL_ID,
    q2.ACCOUNT_NAME,
    q2.SEGMENT,
    q2.REP_ID,
    q2.STAGE,
    q2.DEAL_VALUE,
    q2.CLOSE_DATE
FROM MERIDIAN_SALES.GOLD.Q2_DEALS q2
LEFT JOIN MERIDIAN_SALES.GOLD.Q1_DEALS q1 
    ON q2.DEAL_ID = q1.DEAL_ID
WHERE q1.DEAL_ID IS NULL
ORDER BY q2.DEAL_ID;

-- CHECK 4: Overall data summary
SELECT
    'Q1_DEALS' AS TABLE_NAME,
    COUNT(*) AS TOTAL_ROWS,
    COUNT(CASE WHEN STAGE = 'Closed Won' 
          THEN 1 END) AS CLOSED_WON,
    COUNT(CASE WHEN STAGE = 'Closed Lost' 
          THEN 1 END) AS CLOSED_LOST,
    COUNT(CASE WHEN STAGE IN 
          ('Proposal','Discovery','Prospecting') 
          THEN 1 END) AS PIPELINE,
    SUM(CASE WHEN STAGE = 'Closed Won' 
        THEN DEAL_VALUE ELSE 0 END) AS CLOSED_WON_VALUE
FROM MERIDIAN_SALES.GOLD.Q1_DEALS
UNION ALL
SELECT
    'Q2_DEALS' AS TABLE_NAME,
    COUNT(*) AS TOTAL_ROWS,
    COUNT(CASE WHEN STAGE = 'Closed Won' 
          AND CLOSE_DATE >= '2026-04-01'
          THEN 1 END) AS CLOSED_WON,
    COUNT(CASE WHEN STAGE = 'Closed Lost' 
          THEN 1 END) AS CLOSED_LOST,
    COUNT(CASE WHEN STAGE IN 
          ('Negotiation','Proposal','Discovery')
          THEN 1 END) AS PIPELINE,
    SUM(CASE WHEN STAGE = 'Closed Won' 
        AND CLOSE_DATE >= '2026-04-01'
        THEN DEAL_VALUE ELSE 0 END) AS CLOSED_WON_VALUE
FROM MERIDIAN_SALES.GOLD.Q2_DEALS;
