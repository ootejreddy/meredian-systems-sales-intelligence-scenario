# Architecture Decisions

## What I Built

<!-- One paragraph: the minimal vertical slice that demonstrates the full
     Cortex Agent loop end-to-end. What is working, what a reviewer can
     click through. -->

---

## Defensible Cuts

<!--
List each scope cut as: What | Why it was safe to skip
Example:
- No auth on Streamlit UI | Single-user local demo; not a production service
- No incremental data load | CSV is static for the assignment; COPY INTO is idempotent
-->

| Cut | Rationale |
|-----|-----------|
| | |

---

## Risk Accepted

<!--
Honest list of shortcuts that would need remediation before production:
- hardcoded warehouse size
- no row-level security
- semantic model not versioned
etc.
-->

| Risk | What Would Fix It |
|------|-------------------|
| | |
