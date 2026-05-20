# Meridian Sales Intelligence — Technical Deep Dive Prep
## 30-Minute Session with Two Senior Evaluators

---

## SECTION 1 — TECHNICAL WALKTHROUGH GUIDE (5 minutes)

### Architecture Overview

The solution has five layers:

1. **Data layer** — Four tables in `MERIDIAN_SALES.GOLD`: Q1_DEALS (88 rows), Q2_DEALS (92 rows), Q1_REPS (10), Q2_REPS (10). Loaded from CSV via internal stage with a named file format.

2. **Semantic layer** — `semantic/meridian_semantic.yaml` defines dimensions, facts, metrics, filters, relationships, custom instructions, and three verified queries. This is what Cortex Analyst reads to understand the data.

3. **Agent layer** — `MERIDIAN_SALES.GOLD.MERIDIAN_SALES_AGENT` wraps Cortex Analyst as a tool inside a Cortex Agent. The agent adds orchestration: business definitions, trust rules, risk classification, response formatting (ANSWER/DATA/FLAG), and the data quality exclusion logic.

4. **Application layer** — `app/streamlit_app.py` deployed as a Streamlit in Snowflake app using warehouse runtime. Calls `SNOWFLAKE.CORTEX.DATA_AGENT_RUN()` and parses the JSON response.

5. **Quality layer** — `sql/05_data_quality.sql` documents 15 stage-regression anomalies excluded from all pipeline calculations.

### Why Cortex Analyst Over Direct SQL Generation

Cortex Analyst is purpose-built for text-to-SQL with semantic grounding. A generic LLM generating SQL has no knowledge of business definitions, join patterns, or column semantics. Cortex Analyst uses the semantic model to constrain generation — it knows QUOTA_Q2_2026 is the right column for Q2 quota, it knows the join path from deals to reps, it knows what "at risk" means. This eliminates an entire class of hallucination: wrong column, wrong join, wrong filter.

### Why Semantic Model YAML Over Snowflake Semantic Views

Semantic Views are the newer approach and recommended by Snowflake for production. I chose YAML on stage for three reasons:
1. Git-trackable — the entire semantic definition lives in version control
2. Portable — can be validated, diffed, and reviewed in PR without Snowflake access
3. Iteration speed — during development I was updating the model dozens of times; PUT + overwrite is faster than DDL

In production, I'd migrate to a Semantic View for native RBAC integration and catalog discoverability.

### Why Cortex Agent API Instead of Embedding Agent Directly in Streamlit

The Streamlit warehouse runtime uses an older Streamlit version (1.22+) and runs in a restricted Python environment. The Cortex Agent REST API isn't directly callable from warehouse runtime Python. Instead, I call `SNOWFLAKE.CORTEX.DATA_AGENT_RUN()` as a SQL function through Snowpark — this works because it's a SQL call, not a REST call. The agent orchestrates on the server side and returns a structured JSON response that the app parses.

### How the Three Required Queries Are Handled

Each maps to a verified query in the semantic model with exact SQL. When the user asks a matching question, Cortex Analyst recognizes the match and executes the verified SQL directly — no generation needed, no risk of drift:

1. **Enterprise tracking** → Subquery pattern separating quota aggregation from deal aggregation to avoid fan-out. Excludes 15 anomaly deals. Returns quota coverage %.
2. **At-risk reps** → Groups by rep, computes clean pipeline per rep, classifies HIGH/MEDIUM/LOW, filters HAVING < 75%.
3. **Q2 vs Q1 pace** → UNION ALL comparing day-32 bookings across quarters using the correct date boundaries.

### Data Quality Handling

The Q2_DEALS table is a full CRM snapshot — 88 carried-forward Q1 deals + 4 new Q2 deals. 15 of those deals show impossible stage regression: Closed Won in Q1 appearing as active pipeline in Q2. Total value: $1.47M.

These are excluded via `DEAL_ID NOT IN (...)` in every pipeline calculation. The exclusion is enforced at three levels: verified queries, custom instructions (telling the LLM to always exclude), and documented in the agent system prompt. Raw pipeline is $5.2M; clean pipeline after exclusion is $3.73M.

### Trust and Traceability

Every answer includes:
- **ANSWER** — one direct sentence
- **DATA** — the specific numbers from the query
- **FLAG** — caveats, including the data quality exclusion note
- **Source SQL** — expandable in the Streamlit app showing exactly how the number was calculated

The agent is instructed to refuse to guess. If data can't answer the question, it says what's missing.

---

## SECTION 2 — HOW I USED AI TO BUILD THIS

### How Cortex Code Was Used

Cortex Code was my primary development environment for this entire project. It handled:
- SQL DDL generation (CREATE TABLE, file formats, COPY INTO)
- Semantic model YAML authoring and iterative refinement
- Agent specification YAML with system prompt engineering
- Streamlit app scaffolding and debugging
- Data quality analysis (discovering the 15 anomaly deals)
- Deployment commands (PUT, CREATE AGENT, CREATE STREAMLIT)

### What Cortex Code Generated vs What Required Human Judgment

**AI generated well:**
- Boilerplate SQL (table DDL, COPY INTO patterns)
- Initial semantic model structure
- Streamlit app skeleton and layout
- JSON response parsing logic
- Data quality check queries

**Required human judgment:**
- The decision to use quota coverage instead of attainment as the primary Q2 metric — this is a business reasoning decision, not a code decision
- Discovering that "pipeline coverage" was the wrong term and "quota coverage" matches the business language in AGENTS.md
- Identifying that the original 103% coverage number was wrong because anomaly deals weren't excluded — I had to question the output, run validation queries, and trace the logic
- The architectural choice of Cortex Agent wrapping Cortex Analyst vs calling Analyst directly
- Deciding to use warehouse runtime Streamlit (simpler) and working around its limitations instead of container runtime (more capable but more complex)
- The system prompt trust rules — these encode business judgment about what the CCO needs, not what's technically possible
- Choosing to exclude anomaly deals rather than reclassify them — a data governance decision

### Where AI Got Things Wrong

1. **Initial agent syntax** — Used `AS $$` with JSON format. Wrong. Snowflake agents use `FROM SPECIFICATION $$` with YAML. Had to look up the docs.
2. **Model name** — Used `claude-3-7-sonnet` which doesn't exist in this account. Had to discover available models from the error response and switch to `claude-sonnet-4-5`.
3. **Semantic model format** — First version used a flat `columns` array and root-level `filters`/`metrics`. Cortex Analyst needs `dimensions`/`facts`/`metrics` nested per table. Had to rewrite.
4. **Missing primary keys** — Relationships required primary keys on referenced tables. Validation error caught this.
5. **Pipeline coverage number was wrong** — Agent initially reported 103% for Enterprise because it included regressed deals. I caught this by questioning the output and running validation SQL manually.
6. **Streamlit `st.chat_input`** — Not available in warehouse runtime's older Streamlit version. Had to fall back to `st.text_input`.

### Why This Approach Made the Solution Better

Using AI didn't just make it faster — it made it more thorough. The iterative feedback loop (generate → test → fix → redeploy) meant I could try more approaches and catch more edge cases than I would have manually. The data quality discovery is the best example: AI helped me write the diagnostic queries, but I made the engineering decision about what to do with the findings.

---

## SECTION 3 — SNOWFLAKE EXPERT QUESTIONS (10 Questions)

### Q1: Why did you choose a semantic model YAML on stage instead of a native Semantic View?

Portability and iteration speed. During development I was modifying the semantic model dozens of times — updating metrics, fixing verified queries, adding the exclusion logic. PUT + overwrite on a stage file is instant; DDL recreation of a Semantic View is heavier. The YAML also lives in git, so every change is tracked and diffable. For production, I'd migrate to a Semantic View for RBAC integration, catalog visibility, and the fact that Snowflake recommends it as the forward path.

### Q2: How does your semantic model handle the quota fan-out problem?

This was a real issue I discovered. If you JOIN Q2_DEALS to Q2_REPS directly and SUM(QUOTA_Q2_2026), each rep's quota gets multiplied by their deal count. My verified queries use a subquery pattern: compute quota from Q2_REPS alone in one subquery, compute deal aggregations in another, then join the results. This is documented in the custom_instructions under "SQL PATTERNS" so even when Cortex Analyst generates novel SQL, it follows this pattern.

### Q3: What happens when the agent encounters a question it cannot answer?

The system prompt explicitly instructs: "If the data cannot answer the question, say what is missing — do not guess." Cortex Analyst will also return an UNCLEAR status if it can't map the question to the semantic model. In that case, the agent surfaces the gap rather than fabricating an answer. I tested this — questions about forecast or future predictions get honest "I don't have that data" responses.

### Q4: How did you handle the 15 stage-regression anomalies? Why not fix the source data?

I excluded them rather than modifying source data because: (1) the source CSVs represent what was given — modifying them misrepresents the input, (2) the exclusion is transparent — documented in sql/05_data_quality.sql, enforced in verified queries, and surfaced in every FLAG section, (3) in production you'd trace this back to the CRM and fix it upstream. The exclusion approach preserves auditability.

### Q5: How would this scale beyond 180 deals to a real enterprise dataset?

The architecture scales well because Cortex Analyst generates SQL that Snowflake's query engine executes — it's not doing computation in Python. The semantic model doesn't grow with data volume, only with business complexity. What would need to change: (1) the NOT IN exclusion list would become a reference table rather than hardcoded IDs, (2) the Streamlit 16MB result limit means large result sets need pagination or pre-aggregation, (3) verified queries would grow as more question patterns emerge.

### Q6: Why Cortex Agent wrapping Cortex Analyst rather than calling Analyst directly?

The Agent layer adds three things Analyst alone doesn't provide: (1) a system prompt that encodes business rules and response formatting, (2) orchestration budget and model selection, (3) the ability to add additional tools later (Cortex Search for unstructured docs, custom tools for write-back). If I'd called Analyst directly via REST, I'd have to build all that orchestration in Python.

### Q7: How would you add governance and RBAC for a production deployment?

Three steps: (1) migrate the semantic model YAML to a native Semantic View — this integrates with Snowflake's privilege system natively, (2) add row-access policies on the deals tables keyed on CURRENT_ROLE() or a session variable mapping roles to rep_ids, (3) the Streamlit app already runs as owner's rights — with restricted caller's rights (now in preview for container runtime), each user would see only their data.

### Q8: The verified queries use physical table references. Isn't that fragile?

Yes — Cortex Analyst even flags a non-blocking validation warning about this. The verified queries reference `MERIDIAN_SALES.GOLD.Q2_DEALS` directly rather than logical table names. This works because the semantic model maps logical names to physical tables anyway. In production with schema migrations, I'd switch to logical references (`__q2_deals`) to decouple the queries from physical naming.

### Q9: What's your strategy if the 75% at-risk threshold needs to change?

It's defined in three places: the agent system prompt, the semantic model custom_instructions, and the verified query HAVING clause. To change it, you'd update all three and redeploy. In a mature version, this would be a configurable parameter — perhaps a table MERIDIAN_SALES.GOLD.BUSINESS_RULES that both the semantic model and agent reference dynamically.

### Q10: Why claude-sonnet-4-5 for orchestration instead of a smaller/cheaper model?

I originally specified claude-3-7-sonnet (which the assignment suggested) but it wasn't available in this account's region. claude-sonnet-4-5 was the best available option that handles the complex system prompt reliably — it needs to follow trust rules, format responses correctly, and interpret Analyst results in business context. A smaller model might skip the FLAG section or fail to apply the quota-coverage-first rule consistently. For production at scale, I'd benchmark latency and cost against claude-haiku-4-5 or auto selection.

---

## SECTION 4 — ENGINEERING CRAFT QUESTIONS (10 Questions)

### Q1: How did you use AI tools to build this? Be specific.

Cortex Code was my IDE for the entire project. It generated SQL DDL, wrote the semantic model YAML, built the Streamlit app, and handled all deployment commands. I directed the architecture — which components, which patterns, which tradeoffs. AI got things wrong multiple times: wrong agent syntax, wrong semantic model format, wrong model name, inflated pipeline numbers. Each time I caught it through testing, questioned the output, and directed the fix. The AI was the builder; I was the architect and QA.

### Q2: What did you deliberately cut and why?

Five deliberate cuts: (1) No ML forecasting — facts over predictions, forecasts are where AI hallucinates. (2) No Semantic Views — YAML for git-trackability during development. (3) No row-access policies — documented as step 2 in rollout, not needed for demo. (4) No live CRM connection — proving logic on known data before connecting to live. (5) No container runtime for Streamlit — warehouse runtime is simpler and sufficient; container would have given me st.chat_input but added deployment complexity.

### Q3: Walk me through your code structure.

```
sql/02_create_tables.sql    — DDL for all 4 tables + file format
sql/03_load_data.sql        — PUT + COPY INTO + verification
sql/05_data_quality.sql     — Anomaly discovery and documentation
semantic/meridian_semantic.yaml — Full Cortex Analyst semantic model
agent/agent_config.sql      — Cortex Agent CREATE with system prompt
app/streamlit_app.py        — Streamlit in Snowflake chat UI
AGENTS.md                   — Complete project context and business rules
```

Each file is self-contained and can be run independently. SQL files have header comments explaining purpose. The semantic model is heavily commented with business context.

### Q4: What would you do differently with more time?

Four things: (1) Migrate semantic model to a native Semantic View for production governance. (2) Build an eval harness — golden_qa.json with expected answers and a script that runs all three questions and asserts on key numbers. (3) Add row-access policies for rep-level data isolation. (4) Build a data quality view that runs the anomaly checks as a scheduled task rather than a one-time script.

### Q5: What's your testing approach?

Three layers: (1) SQL verification — each COPY INTO is followed by COUNT(*) assertions (88, 92, 10, 10). (2) Data quality checks — sql/05_data_quality.sql validates anomalies and documents expected counts. (3) Agent testing — I tested all three required queries via DATA_AGENT_RUN and verified the numbers matched my manual calculations. What's missing: an automated eval harness that runs nightly and alerts on drift.

### Q6: How many commits and what's your git history like?

The project was built in a single intensive session using Cortex Code. Commits track logical milestones: initial scaffold, table creation and data load, semantic model, agent config, Streamlit app, data quality findings, and iterative fixes (model corrections, exclusion logic, terminology updates). Each commit represents a working state, not a save point.

### Q7: What's in your README and AGENTS.md?

AGENTS.md is the primary context document — it has everything: table schemas, business definitions (bookings, attainment, quota coverage, pace), key numbers, business rules, trust rules for the agent, data quality findings with all 15 excluded deal IDs, the SQL exclusion pattern, and the deliverable checklist. It's designed so any engineer (or AI tool) can pick up the project and understand every decision without reading the code.

### Q8: What's the biggest engineering risk in this solution?

The semantic model business rules haven't been validated with an actual Meridian analyst. I defined "at risk" as quota coverage below 75% based on industry standard, but Meridian might use 70% or 80%. The exclusion of 15 deals is based on my analysis of the synthetic data — in production, an analyst would confirm whether these are truly anomalous or represent legitimate deal re-opens. I'm honest about this in the presentation.

### Q9: How would someone else maintain this after you leave?

AGENTS.md is the maintenance guide. It has the complete business logic, every table schema, every key number, and the data quality exclusion list. The SQL files are idempotent (CREATE OR REPLACE) so anyone can re-run them. The semantic model has inline descriptions for every column, metric, and filter. The agent system prompt reads like a requirements document, not code.

### Q10: If you had 4 more hours right now, what would you build?

An evaluation harness. `evals/golden_qa.json` with 10-15 question/expected-answer pairs covering edge cases: Tom Bradley should NOT be flagged (99% coverage), the pace comparison should show -59%, Enterprise should show 65.3% not 103%. Then `evals/run_evals.py` that calls the agent for each question and asserts on the key numbers. This is the single highest-value addition for ongoing trust.

---

## SECTION 5 — TRUST AND TRACEABILITY ANSWER

**"The last AI tool hallucinated. How does yours avoid that problem and where does it still fall short?"**

The previous tool generated answers from general knowledge. It had never seen your data. It was guessing — confidently. That's a fundamental architecture problem, not a tuning problem.

This solution eliminates that class of failure through three mechanisms:

First — every answer comes from a calculation against your actual database. The AI doesn't know your Q2 pipeline is $3.73 million from memory. It writes a query, runs it, and reads the result. You can see the exact calculation underneath every answer.

Second — the semantic model constrains what the AI can do. It can't join the wrong tables or pick the wrong column because the relationships and definitions are locked down in a specification file. It's like giving an analyst a data dictionary and saying "only use these columns, only join on these keys."

Third — the system is instructed to refuse gracefully. If the data can't answer the question, it says "I don't have that information" rather than filling the gap with a plausible-sounding guess.

Where it still falls short: the business rules — what counts as "at risk," how we define coverage — were set by me based on the assignment brief, not validated with an actual Meridian analyst. If I defined the threshold wrong, the numbers will be real but the interpretation could be off. That's the highest remaining risk and it's a two-hour fix: sit down with the analyst, confirm the rules, update the model.

The other gap: this is a prototype on a 180-deal dataset. It hasn't been stress-tested at production scale, with concurrent users, or with messy real-world CRM data. The architecture supports it — Snowflake handles scale, not the app — but it hasn't been proven yet.

---

## SECTION 6 — DEFENSIBLE CUTS ANSWER

### Cut 1: Cortex Agent in Streamlit → Used DATA_AGENT_RUN SQL function

The Streamlit warehouse runtime doesn't support direct REST API calls to the Cortex Agent endpoint. Container runtime would, but adds deployment complexity (compute pools, longer startup, container management). I chose warehouse runtime for simplicity and called the agent via `SNOWFLAKE.CORTEX.DATA_AGENT_RUN()` — a SQL function that works in any Snowflake session. Same capability, simpler deployment.

### Cut 2: No ML Forecasting → Facts Only

Forecasting is exactly where AI tools start making things up. A prediction model on 180 deals would be statistically meaningless and would undermine the entire trust narrative. The CCO was burned by fabricated numbers — giving him a forecast model is pouring gasoline on that fire. Facts and current pipeline state are what he actually needs to make decisions.

### Cut 3: No Semantic Views → YAML on Stage

Semantic Views are the production path Snowflake recommends. I chose YAML because: (1) it lives in git — every iteration is tracked, (2) I was modifying it 20+ times during development — PUT overwrite is faster than DDL recreation, (3) portability — the entire model definition can be reviewed without Snowflake access. Migration to Semantic Views is step 1 of a production hardening plan.

### Cut 4: No Row-Level Access Policies

In production, Sarah Chen should see her deals and David Kim should see his team. This requires row-access policies keyed on session context. I documented it as step 2 of rollout but didn't implement because: (1) it's a governance decision that needs org input on role hierarchy, (2) the demo works better showing all data — the CCO needs to see the full picture, (3) it's a standard Snowflake pattern that doesn't prove anything architecturally novel.

### Cut 5: Business Rules Not Validated with Meridian Analyst

The 75% at-risk threshold, the quota coverage formula, the day-32 comparison methodology — all defined by me from the assignment brief and industry standards. An actual Meridian analyst might define these differently. This is the highest remaining risk and I'm explicitly honest about it in the presentation. It's also a deliberate scope choice: I'd rather ship a working system with one documented assumption than delay to chase validation I can't get without access to their team.

---

## SECTION 7 — WHAT THE ARTIFACT PROVES AND DOES NOT PROVE

This artifact proves that a non-technical sales leader can ask plain English questions about pipeline and quota and receive verified, traceable answers in seconds — grounded entirely in Snowflake data, with the calculation shown, business definitions enforced, data quality anomalies excluded, and uncertainty flagged honestly. It proves the full stack works end-to-end: data loading, semantic modeling, agent orchestration, trust formatting, and a functional UI. It proves that AI-assisted development can produce a coherent, defensible system in a compressed timeline when the engineer directs architecture and the AI handles implementation.

What it does not prove: production reliability under concurrent load, correctness of business rule definitions (which require analyst validation), behavior on messy real-world CRM data with thousands of reps and millions of deals, or long-term maintainability across schema migrations and org changes. It is a working prototype that delivers correct answers on known data — not a production system ready for unsupervised deployment.

It relies on three assumptions: (1) the synthetic dataset is representative of real Meridian data patterns, (2) the 75% at-risk threshold matches Meridian's actual business definition, (3) the 15 stage-regression deals are genuinely anomalous and not legitimate CRM re-opens.

---

## SECTION 8 — SHARP ONE-LINERS

### Why Snowflake over other platforms?
"Data already lives here. Cortex Agent and Analyst are native — no data movement, no external API keys, no latency penalty. The answer runs where the data lives."

### Why Claude Sonnet 4.5?
"Best available model in this account's region that reliably follows complex system prompts. I originally specified 3.7 Sonnet per the assignment — it wasn't available, so I used the strongest alternative. In production I'd use auto-selection."

### Why Cortex Analyst over Cortex Search here?
"Structured data, structured questions. Cortex Search is for unstructured documents — policy PDFs, meeting notes. Pipeline and quota live in tables with defined schemas. Analyst is purpose-built for this."

### What is the biggest remaining risk?
"Business rule validation. If Meridian defines 'at risk' as 70% instead of 75%, every risk classification shifts. Two-hour fix, but hasn't been done yet."

### What would break first at 10x data volume?
"The NOT IN exclusion list. Fifteen hardcoded deal IDs is fine for a prototype; at scale, that becomes a reference table with an INNER JOIN exclusion pattern. Everything else scales natively through Snowflake's engine."

### How would you add forecasting later?
"Snowflake ML functions — TIME_SERIES_FORECAST on historical close rates by stage. But I'd only do it after proving the descriptive layer is trusted. You earn the right to predict by first being right about the present."

### What is in your DECISIONS.md?
"Architecture decisions: why YAML over Semantic Views, why warehouse runtime over container, why Cortex Agent wraps Analyst rather than calling it directly, and the data quality exclusion rationale."

### How many commits is your git history?
"Logical milestones — scaffold, data layer, semantic model, agent, app, data quality discovery, iterative fixes. Each commit is a working state, not a checkpoint."

### What does your eval harness test?
"The eval harness is documented but not yet implemented — it's the next four-hour deliverable. It would run all three required questions plus edge cases (Tom Bradley not flagged, pace calculation = -59%, Enterprise = 65.3% not 103%) and assert on key numbers."

### What would you do first tomorrow morning if this went to production?
"Build the eval harness. Then schedule it to run daily. A production system without regression tests is a hallucination waiting to happen."
