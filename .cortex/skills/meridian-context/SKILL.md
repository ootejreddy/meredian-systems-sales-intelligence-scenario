---
name: meridian-context
description: >
  Meridian Systems sales intelligence project context.
  Use when generating SQL, semantic models, or agent config
  for the Meridian FDE assignment.
tools:
  - snowflake_sql
  - cortex_analyst
---

# When to Use
- Any SQL generation for MERIDIAN_SALES database
- Creating or editing the semantic model YAML
- Configuring the Cortex Agent
- Building the Streamlit app

# Key Context
- Q1 is final, Q2 is in progress as of May 2 2026
- Q2 pipeline deals have EXPECTED close dates
- Always use MERIDIAN_SALES.GOLD schema prefix
- At-risk threshold is 75% pipeline coverage
- Negotiation stage only exists in Q2 not Q1

# SQL Best Practices for This Project
- Use CREATE OR REPLACE for all DDL
- Add COMMENT = '...' on every table
- Use DATE not TIMESTAMP for close_date and created_date
- Always qualify table names with full schema path
- Add SELECT COUNT(*) after every COPY INTO to verify load
