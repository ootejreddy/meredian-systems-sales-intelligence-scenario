# Meridian Systems — Sales Intelligence

> Snowflake Cortex Agent take-home assignment

---

## What This Does

<!-- 2-3 sentences: the problem, the solution, what a user can ask -->

## Architecture

<!-- Diagram or bulleted flow:
     CSV data → Snowflake tables → Cortex Analyst semantic model
     → Cortex Agent SQL tool → Streamlit chat UI
-->

## How To Run

### Prerequisites
- Python 3.11+
- Snowflake account with Cortex Analyst enabled
- `snowsql` CLI (for DDL setup)

### Steps

```bash
# 1. Clone and install
git clone <repo>
cd meredian-systems-sales-intelligence-scenario
cp .env.example .env          # fill in your credentials
make install

# 2. Load data into Snowflake
#    Place CSVs in data/ first, then:
make setup

# 3. Run the app
make run
```

---

## Key Decisions

<!-- What you chose and why — link to DECISIONS.md for full rationale -->

## What I Did Not Build

<!-- Honest list of scope cuts: what's missing and why it's OK -->

## What I Would Do Next

<!-- Top 3-5 improvements if given more time -->

## Time Spent

| Phase | Hours |
|-------|-------|
| Schema design & DDL | |
| Semantic model (YAML) | |
| Agent configuration | |
| Streamlit app | |
| Tests & evals | |
| Docs & polish | |
| **Total** | |
