-- ============================================================
-- MERIDIAN SALES INTELLIGENCE — Cortex Agent Configuration
-- Database: MERIDIAN_SALES | Schema: GOLD
-- ============================================================

-- ------------------------------------------------------------
-- STEP 1: Upload semantic model YAML to stage
-- ------------------------------------------------------------
PUT file://semantic/meridian_semantic.yaml
  @MERIDIAN_SALES.GOLD.MERIDIAN_STAGE
  AUTO_COMPRESS=FALSE OVERWRITE=TRUE;

-- Verify upload
LIST @MERIDIAN_SALES.GOLD.MERIDIAN_STAGE;

-- ------------------------------------------------------------
-- STEP 2: Grant required privileges (run as ACCOUNTADMIN)
-- ------------------------------------------------------------
-- USE ROLE ACCOUNTADMIN;
-- GRANT CREATE AGENT ON SCHEMA MERIDIAN_SALES.GOLD TO ROLE MERIDIAN_ENGINEER;
-- USE ROLE MERIDIAN_ENGINEER;

-- ------------------------------------------------------------
-- STEP 3: Create the Cortex Agent
-- ------------------------------------------------------------
CREATE OR REPLACE AGENT MERIDIAN_SALES.GOLD.MERIDIAN_SALES_AGENT
COMMENT = 'Meridian Systems sales intelligence agent. Answers plain English questions about pipeline and quota. Every answer shows the SQL behind it for full traceability.'
FROM SPECIFICATION
$$
models:
  orchestration: claude-sonnet-4-5

orchestration:
  budget:
    seconds: 60
    tokens: 16000

instructions:
  response: |
    You are a trusted sales intelligence assistant for Meridian Systems. You help sales leaders get fast accurate answers about pipeline and quota.

    CONTEXT:
    - Q1 Jan-Mar 2026 is FINAL — all numbers are actual
    - Q2 Apr-Jun 2026 is IN PROGRESS as of May 2 2026
    - Q2 is only 32 days into the quarter
    - Q2 pipeline deals have EXPECTED close dates not actual
    - Negotiation stage exists in Q2 but NOT in Q1

    TRUST RULES:
    1. Every answer must show the actual numbers from the data
    2. Never say based on your data without showing specifics
    3. If Q2 attainment looks low explain why — Q2 is only 32 days in as of May 2
    4. Use pipeline coverage not attainment alone for Q2 risk
    5. Pipeline coverage = (closed won + active pipeline) / quota * 100
    6. At-risk means pipeline coverage below 75 percent
    7. Flag any assumption you are making explicitly
    8. Give direct answers — not hedges or redirects
    9. When comparing Q1 vs Q2 note Q2 is still in progress

    RESPONSE FORMAT:
    ANSWER: direct one sentence answer
    DATA: the specific numbers that support it
    FLAG: important caveats or context — omit if none

    RISK DEFINITIONS:
    HIGH RISK: pipeline coverage below 75 percent
    MEDIUM RISK: pipeline coverage 75 to 90 percent
    LOW RISK: pipeline coverage above 90 percent
  orchestration: "Use Analyst1 for all questions about deals, pipeline, quota, reps, revenue, bookings, and risk."
  sample_questions:
    - question: "How is the Enterprise segment tracking against quota this quarter?"
    - question: "Which reps are at risk of missing Q2?"
    - question: "How does Q2 attainment compare to where we were at the same point in Q1?"

tools:
  - tool_spec:
      type: "cortex_analyst_text_to_sql"
      name: "Analyst1"
      description: "Converts natural language questions about sales pipeline, quota attainment, and rep performance into SQL queries against the Meridian Sales data model."

tool_resources:
  Analyst1:
    semantic_model_file: "@MERIDIAN_SALES.GOLD.MERIDIAN_STAGE/meridian_semantic.yaml"
    execution_environment:
      warehouse: "COMPUTE_WH"
$$;

-- ------------------------------------------------------------
-- STEP 4: Verify agent exists
-- ------------------------------------------------------------
SHOW AGENTS IN SCHEMA MERIDIAN_SALES.GOLD;

-- ------------------------------------------------------------
-- STEP 5: Grant usage to MERIDIAN_ENGINEER role
-- ------------------------------------------------------------
GRANT USAGE ON AGENT MERIDIAN_SALES.GOLD.MERIDIAN_SALES_AGENT
TO ROLE MERIDIAN_ENGINEER;

-- ------------------------------------------------------------
-- STEP 6: Test the agent with the 3 required questions
-- ------------------------------------------------------------

-- Test 1: Enterprise segment tracking
SELECT SNOWFLAKE.CORTEX.DATA_AGENT_RUN(
  'MERIDIAN_SALES.GOLD.MERIDIAN_SALES_AGENT',
  '{"messages": [{"role": "user", "content": [{"type": "text", "text": "How is the Enterprise segment tracking against quota this quarter?"}]}]}'
) AS response;

-- Test 2: At-risk reps
SELECT SNOWFLAKE.CORTEX.DATA_AGENT_RUN(
  'MERIDIAN_SALES.GOLD.MERIDIAN_SALES_AGENT',
  '{"messages": [{"role": "user", "content": [{"type": "text", "text": "Which reps are at risk of missing Q2?"}]}]}'
) AS response;

-- Test 3: Q2 vs Q1 comparison
SELECT SNOWFLAKE.CORTEX.DATA_AGENT_RUN(
  'MERIDIAN_SALES.GOLD.MERIDIAN_SALES_AGENT',
  '{"messages": [{"role": "user", "content": [{"type": "text", "text": "How does Q2 compare to Q1 at the same point?"}]}]}'
) AS response;
