# Meridian Sales Intelligence — Cortex Code Context

## Project Overview

Snowflake Cortex Agent for sales pipeline Q&A.
Deloitte FDE take-home assignment — Meridian Systems scenario.
Deadline: Wednesday May 19 2026 3pm.

## Snowflake Connection

Role: MERIDIAN_ENGINEER
Database: MERIDIAN_SALES
Schema: GOLD
Warehouse: COMPUTE_WH
Stage: MERIDIAN_SALES.GOLD.MERIDIAN_STAGE

## Tables in MERIDIAN_SALES.GOLD

Q1_DEALS — 88 rows
Columns: deal_id, account_name, segment, region, rep_id,
stage, deal_value, close_date, created_date,
product_line, loss_reason
Stages: Closed Won, Closed Lost, Proposal, Discovery, Prospecting
Period: Jan 1 to Mar 31 2026 — FINAL

Q2_DEALS — 92 rows
Same columns as Q1_DEALS
Stages: Closed Won, Closed Lost, Proposal, Discovery, Negotiation
NOTE: Negotiation is NEW in Q2 — does not exist in Q1
Period: Apr 1 to Jun 30 2026 — IN PROGRESS as of May 2 2026
IMPORTANT: Pipeline deals have EXPECTED close dates not actual

Q1_REPS — 10 rows
Columns: rep_id, rep_name, segment, region,
quota_q1_2026, manager, hire_date

Q2_REPS — 10 rows
Same as Q1_REPS plus quota_q2_2026

## Business Definitions

- Bookings = total deal value of all Closed Won deals in a period — actual signed revenue, not pipeline
- Attainment = closed won / quota * 100 — what a rep has actually booked as % of target
- Attainment is the complete picture for Q1 (final) but misleading for Q2 (only 32 days in)
- Quota coverage = (closed won + active pipeline) / quota * 100 — correct risk signal for Q2
- Active pipeline = deals in Negotiation, Proposal, or Discovery stages — excludes Closed Won and Closed Lost
- At-risk = quota coverage below 75%
- Pace = closed won bookings by a specific day cutoff within a quarter — used to compare progress across quarters at the same point in time
- Day 32 = calendar day 32 of a quarter. Q1 day 32 = Feb 1 2026. Q2 day 32 = May 2 2026. Used as the comparison point between Q1 and Q2.
- Behind Q1 pace = (Q2 day32 bookings / Q1 day32 bookings - 1) * 100. Current value: (518K / 1260K - 1) * 100 = -59%. Negative means Q2 is behind.
- 75% at-risk threshold = industry standard early-quarter risk signal. Below 75% quota coverage means a rep cannot hit quota even if all pipeline converts, which is statistically unlikely. Not a Meridian-specific rule.

## Key Business Rules

- Q1 is FINAL — all numbers are actual
- Q2 is IN PROGRESS as of May 2 2026 — 32 days into quarter
- Q2 quota EXISTS — use quota_q2_2026 from Q2_REPS table
- For Q2 risk, always use quota coverage — attainment alone is misleading at 32 days

## Key Numbers

- Q1 total bookings: $6,041,000
- Q2 bookings so far: $518,000
- Q2 active pipeline: $5,198,000
- Q1 bookings at day 32 (Feb 1): $1,260,000
- Q2 is 59% behind Q1 pace at day 32: (518K / 1260K - 1) * 100
- High risk reps: Priya Patel 74%, Kevin Marsh 74%,
  Danielle Torres 65%, Aisha Williams 63%
- Tom Bradley is LOW risk at 99% — do NOT flag him as at risk

## What We Are Building

1. sql/01_create_database.sql
2. sql/02_create_tables.sql
3. sql/03_load_data.sql
4. sql/04_create_views.sql
5. semantic/meridian_semantic.yaml
6. agent/agent_config.sql
7. app/streamlit_app.py
8. tests/test_quota_calculations.py
9. evals/golden_qa.json + evals/run_evals.py

## Coding Standards

- Always use MERIDIAN_SALES.GOLD schema prefix in SQL
- Use CREATE OR REPLACE for all DDL
- Add COMMENT on all tables and views
- Never hardcode passwords — use externalbrowser auth
- Pin all Python package versions
- Use MERIDIAN_ENGINEER role

## Trust Rules for the Agent System Prompt

- Every number must come from SQL — never estimate, recall, or generate a number
- If the data cannot answer the question, say what is missing — do not guess
- Never lead with Q2 attainment — always lead with quota coverage, attainment is secondary
- When Q2 attainment looks low, explain it: Q2 is only 32 days in — quota coverage is the correct signal
- When citing Q2 pipeline values, flag that these are expected close dates, not actual closed revenue
- When Negotiation stage deals are present, call it a positive signal — deals further along than Q1 was at same point
- 75% threshold is industry-standard: below it means a rep cannot hit quota even if all pipeline converts
- When comparing Q1 vs Q2, state the formula: (Q2 day32 / Q1 day32 - 1) * 100 and note Q2 is still in progress
- Flag all assumptions explicitly in the FLAG section
- Response format: ANSWER / DATA / FLAG
