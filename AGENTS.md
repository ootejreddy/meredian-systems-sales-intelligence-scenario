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

## Key Business Rules

- Q1 is FINAL — all numbers are actual
- Q2 is IN PROGRESS as of May 2 2026 — 32 days into quarter
- At-risk = pipeline coverage below 75% of quota
- Pipeline coverage = (closed won + active pipeline) / quota \* 100
- Active pipeline stages: Negotiation, Proposal, Discovery
- Q2 quota EXISTS — use quota_q2_2026 from Q2_REPS table

## Key Numbers

- Q1 total closed won: $6,041,000
- Q2 closed won so far: $518,000
- Q2 active pipeline: $5,198,000
- Q1 closed won at same point day 32: $1,260,000
- Q2 is 59% behind Q1 pace at same point
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

- CCO was burned by hallucinations — every answer shows source SQL
- Flag when Q2 looks low because it is only 32 days in
- Use pipeline coverage not attainment alone for Q2 risk
- Response format: ANSWER / DATA / FLAG
- At-risk threshold: pipeline coverage below 75%
