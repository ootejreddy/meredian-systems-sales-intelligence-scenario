# Meridian Sales Intelligence — Process Flow
## How Your Data Becomes a Trusted Answer

---

## The Big Picture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │     │                 │     │                 │
│   YOUR SALES    │────▶│   DATA IS       │────▶│  BUSINESS RULES │────▶│  INTELLIGENCE   │────▶│   YOU ASK A     │
│   DATA          │     │   VERIFIED      │     │  ARE APPLIED    │     │  LAYER          │     │   QUESTION      │
│                 │     │   & CLEANED     │     │                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
                                                                                                         │
                                                                                                         ▼
                                                                                                ┌─────────────────┐
                                                                                                │                 │
                                                                                                │  TRUSTED ANSWER │
                                                                                                │  WITH PROOF     │
                                                                                                │                 │
                                                                                                └─────────────────┘
```

Every answer you receive has passed through all five steps.
Nothing is guessed. Nothing is estimated. Every number is calculated directly from your data.

---

## Step 1 — Your Sales Data

**What it is:** Your CRM sales records — the same data your analyst works with.

**What's included:**

| Dataset | Period | Status | What It Contains |
|---------|--------|--------|-----------------|
| Q1 Deals | Jan – Mar 2026 | Final | 88 deals — all closed, all actual revenue |
| Q2 Deals | Apr – Jun 2026 | In Progress | 92 deals — mix of closed and open pipeline |
| Rep Roster | Q1 & Q2 | Current | 10 reps with quota targets per quarter |

**Key numbers at this stage:**
- Q1 total bookings: **$6.04 million** (final)
- Q2 closed so far: **$518 thousand** (32 days into quarter)
- Q2 open pipeline: **$5.2 million** (before cleaning)

---

## Step 2 — Data Is Verified and Cleaned

**What we do:** Before any analysis runs, the data is checked for problems.

**What we found:**

15 deals appeared in an impossible state — they were marked as "closed and won" in Q1 but showed up again as open pipeline in Q2. In a real business, this cannot happen. Once revenue is booked, a deal doesn't un-close itself.

**What we did about it:**

- Identified all 15 problematic deals (total value: **$1.47 million**)
- Removed them from all pipeline calculations
- Documented exactly which deals were removed and why
- Every answer that uses pipeline data tells you this cleaning was applied

**After cleaning:**

| Metric | Before Cleaning | After Cleaning |
|--------|----------------|----------------|
| Q2 Active Pipeline | $5.20M | **$3.73M** |
| Enterprise Quota Coverage | 103% (misleading) | **65.3%** (accurate) |

Without this step, the system would have told you Enterprise is fine. They're not — they're at high risk.

---

## Step 3 — Business Rules Are Applied

**What it is:** The system is taught how your business thinks about sales performance.

**Rules built in:**

| Concept | Definition | Why It Matters |
|---------|------------|----------------|
| Bookings | Closed and signed revenue only | Never confuses pipeline with actual revenue |
| Quota Coverage | (Closed deals + open pipeline) ÷ quota | The right way to measure risk mid-quarter |
| At-Risk | Quota coverage below 75% | Industry standard — if coverage is below 75%, a rep cannot hit target even if every open deal closes |
| Attainment | Closed deals ÷ quota | Only useful for completed quarters — misleading at 32 days in |

**Why this matters to you:**

The system won't confuse "closed revenue" with "expected pipeline." It won't tell you a rep is safe when they're actually at risk. It uses the right metric for the right situation — and tells you which one it's using.

---

## Step 4 — The Intelligence Layer

**What it does:** Reads your question, goes directly to your data, runs the calculation, and brings back the answer.

**How it works — in plain terms:**

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│   You ask: "Which reps are at risk of missing Q2?"       │
│                                                          │
│         ▼                                                │
│                                                          │
│   System checks: What does "at risk" mean?               │
│   → Quota coverage below 75%                             │
│                                                          │
│         ▼                                                │
│                                                          │
│   System calculates: For each rep, add up their          │
│   closed deals + open pipeline, divide by their          │
│   target, exclude the 15 bad deals                       │
│                                                          │
│         ▼                                                │
│                                                          │
│   System returns: 5 reps below 75%                       │
│   Shows the exact calculation used                       │
│   Flags that Q2 is only 32 days in                       │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**What it does NOT do:**
- Does not predict the future
- Does not form opinions
- Does not fill in gaps with guesses
- If it doesn't have the data to answer, it says so

---

## Step 5 — Your Dashboard

**What you see:**

### Live Metrics (always visible at the top)

| Q1 Total Bookings | Q2 Closed Won | Q2 Active Pipeline | Reps At High Risk |
|---|---|---|---|
| $6.04M (Final) | $518K (As of May 2) | $3.73M (Cleaned) | 5 of 10 |

### Ask Any Question

Type a question in plain English. For example:
- "How is Enterprise tracking against quota?"
- "Which reps are at risk?"
- "How does Q2 compare to Q1 at the same point?"

### Every Answer Includes Three Parts

| Part | What It Shows | Why |
|------|--------------|-----|
| **ANSWER** | One clear sentence | So you get the headline immediately |
| **DATA** | The specific numbers | So you can see exactly what's behind it |
| **FLAG** | Honest caveats | So you know what to watch out for |

### Proof Is Always Available

Under every answer, you can expand "View source" — this shows exactly how the number was calculated from your data. The same steps your analyst would take, just faster.

---

## Trust Built In At Every Step

| Step | Safeguard | What It Prevents |
|------|-----------|-----------------|
| Data Loading | Row count verification | Missing or duplicate records |
| Data Cleaning | 15 anomaly deals excluded | Misleading pipeline numbers |
| Business Rules | Definitions locked in | Inconsistent interpretations |
| Calculation | Reads directly from your database | Made-up numbers |
| Answer | Shows its work | Unverifiable claims |
| Caveats | Flags uncertainty honestly | False confidence |

**The system is designed to be caught checking its work — not to look impressive.**

---

## What Happens Next — Three Steps to Go Live

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  STEP 1                    STEP 2                   STEP 3      │
│  ────────                  ────────                 ────────    │
│                                                                 │
│  Validation Session        Access Controls          Live CRM    │
│                                                                 │
│  2 hours with your         Each rep sees their      Connect to  │
│  data analyst to           own pipeline.            your CRM    │
│  confirm business          Managers see their       for real-   │
│  rules match how           team. No one sees        time data   │
│  your team actually        what they shouldn't.     instead of  │
│  operates.                                          quarterly   │
│                                                     snapshots.  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

No six-month project. No committee. The system works today on your data.
These three steps make it production-ready for your full team.

---

*Document prepared for Meridian Systems CCO — May 2026*
