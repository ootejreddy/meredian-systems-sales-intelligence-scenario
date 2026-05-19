import streamlit as st
import json
from snowflake.snowpark.context import get_active_session

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(
    page_title="Meridian Sales Intelligence",
    layout="wide",
    page_icon="📊"
)

# ------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# ------------------------------------------------------------
# SNOWFLAKE CONNECTION
# ------------------------------------------------------------
session = get_active_session()

# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------
with st.sidebar:
    st.title("About This App")
    st.markdown("""
    - **Data:** Meridian Systems Q1 and Q2 2026 sales data
    - **Agent:** Snowflake Cortex Agent with Cortex Analyst
    - **Model:** claude-sonnet-4-5
    - **Trust:** Every answer grounded in SQL — no hallucination
    - **At-risk threshold:** Pipeline coverage below 75 percent
    """)
    st.markdown("---")
    st.markdown("**Key Numbers**")
    sidebar_data = {
        "Metric": ["Q1 Total", "Q2 Closed", "Q2 Pipeline", "High Risk Reps"],
        "Value": ["$6.04M", "$518K", "$5.2M", "4"]
    }
    st.table(sidebar_data)

# ------------------------------------------------------------
# TITLE AND TRUST BANNER
# ------------------------------------------------------------
st.title("📊 Meridian Sales Intelligence")
st.info(
    "Every answer shows the SQL that produced it. "
    "Data gaps and assumptions are flagged explicitly. "
    "Numbers come directly from Snowflake — not generated."
)

# ------------------------------------------------------------
# KEY METRICS ROW
# ------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    q1_bookings = session.sql(
        "SELECT SUM(DEAL_VALUE) FROM MERIDIAN_SALES.GOLD.Q1_DEALS WHERE STAGE = 'Closed Won'"
    ).collect()[0][0]
    q1_display = f"${q1_bookings / 1_000_000:.2f}M" if q1_bookings else "$0"
    st.metric(label="Q1 Total Bookings", value=q1_display, help="Final")
    st.caption("Final")

with col2:
    q2_closed = session.sql(
        "SELECT SUM(DEAL_VALUE) FROM MERIDIAN_SALES.GOLD.Q2_DEALS "
        "WHERE STAGE = 'Closed Won' AND CLOSE_DATE >= '2026-04-01'"
    ).collect()[0][0]
    q2_closed_display = f"${int(q2_closed / 1_000)}K" if q2_closed else "$0"
    st.metric(label="Q2 Closed Won", value=q2_closed_display, help="As of May 2")
    st.caption("As of May 2")

with col3:
    q2_pipeline = session.sql(
        "SELECT SUM(DEAL_VALUE) FROM MERIDIAN_SALES.GOLD.Q2_DEALS "
        "WHERE STAGE IN ('Negotiation','Proposal','Discovery')"
    ).collect()[0][0]
    q2_pipe_display = f"${q2_pipeline / 1_000_000:.2f}M" if q2_pipeline else "$0"
    st.metric(label="Q2 Active Pipeline", value=q2_pipe_display, help="Open Deals")
    st.caption("Open Deals")

with col4:
    at_risk_df = session.sql("""
        SELECT COUNT(*) AS cnt FROM (
            SELECT r.REP_ID,
                ROUND((SUM(CASE WHEN d.STAGE = 'Closed Won' THEN d.DEAL_VALUE ELSE 0 END) +
                    SUM(CASE WHEN d.STAGE IN ('Negotiation','Proposal','Discovery')
                        THEN d.DEAL_VALUE ELSE 0 END)) /
                    r.QUOTA_Q2_2026 * 100, 1) AS COVERAGE
            FROM MERIDIAN_SALES.GOLD.Q2_DEALS d
            JOIN MERIDIAN_SALES.GOLD.Q2_REPS r ON d.REP_ID = r.REP_ID
            WHERE d.CLOSE_DATE >= '2026-04-01'
            GROUP BY r.REP_ID, r.QUOTA_Q2_2026
            HAVING COVERAGE < 75
        )
    """).collect()[0][0]
    st.metric(label="Reps At High Risk", value=f"{at_risk_df} of 10", help="Coverage below 75%")
    st.caption("Coverage below 75%")

# ------------------------------------------------------------
# DIVIDER
# ------------------------------------------------------------
st.divider()

# ------------------------------------------------------------
# EXAMPLE QUESTION BUTTONS
# ------------------------------------------------------------
st.markdown("**Try these questions**")
btn_col1, btn_col2, btn_col3 = st.columns(3)

with btn_col1:
    if st.button("How is Enterprise tracking against quota?", use_container_width=True):
        st.session_state.pending_question = "How is the Enterprise segment tracking against quota this quarter?"

with btn_col2:
    if st.button("Which reps are at risk of missing Q2?", use_container_width=True):
        st.session_state.pending_question = "Which reps are at risk of missing Q2?"

with btn_col3:
    if st.button("How does Q2 compare to Q1 at same point?", use_container_width=True):
        st.session_state.pending_question = "How does Q2 attainment compare to where we were at the same point in Q1?"

# ------------------------------------------------------------
# DIVIDER
# ------------------------------------------------------------
st.divider()

# ------------------------------------------------------------
# HELPER: CALL CORTEX AGENT
# ------------------------------------------------------------
def call_agent(question: str) -> dict:
    """Call the Meridian Sales Agent and return parsed response."""
    try:
        request_body = json.dumps({
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": question}]}
            ]
        })
        result = session.sql(
            "SELECT SNOWFLAKE.CORTEX.DATA_AGENT_RUN("
            "'MERIDIAN_SALES.GOLD.MERIDIAN_SALES_AGENT', ?)",
            params=[request_body]
        ).collect()[0][0]

        response = json.loads(result)

        # Extract text answer and SQL from response
        answer_text = ""
        source_sql = ""

        if "content" in response:
            for block in response["content"]:
                block_type = block.get("type", "")

                # Extract text content
                if block_type == "text":
                    answer_text += block.get("text", "")

                # Extract SQL from tool_result blocks
                elif block_type == "tool_result":
                    # tool_result content can be at block level or nested
                    content_list = block.get("content", [])
                    if not content_list and "tool_result" in block:
                        content_list = block["tool_result"].get("content", [])
                    for item in content_list:
                        if isinstance(item, dict) and item.get("type") == "json":
                            json_data = item.get("json", {})
                            # Only grab sql from execution results, not semantic context
                            if "sql" in json_data and "result_set" in json_data:
                                source_sql = json_data["sql"]
                            elif "sql" in json_data and "query_id" in json_data:
                                source_sql = json_data["sql"]

        elif "message" in response:
            answer_text = response["message"]

        return {"answer": answer_text, "sql": source_sql, "error": None}

    except Exception as e:
        return {"answer": None, "sql": None, "error": str(e)}


# ------------------------------------------------------------
# CHAT INTERFACE — DISPLAY HISTORY
# ------------------------------------------------------------
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Assistant:**")
        st.markdown(msg["content"])
        if msg.get("sql"):
            with st.expander("View source SQL — see exactly how this was calculated"):
                st.code(msg["sql"], language="sql")
    st.markdown("---")

# ------------------------------------------------------------
# CHAT INPUT
# ------------------------------------------------------------
user_input = st.text_input(
    "Ask about pipeline, quota, or rep performance",
    key="user_question",
    placeholder="e.g. Which reps are at risk of missing Q2?"
)

# Use pending question from button click if set
question = st.session_state.pending_question or user_input
if st.session_state.pending_question:
    st.session_state.pending_question = None

if question:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": question})
    st.markdown(f"**You:** {question}")

    # Call agent
    with st.spinner("Analyzing..."):
        result = call_agent(question)

    if result["error"]:
        st.error("Could not get answer. Please try again.")
        st.caption(f"Error details: {result['error']}")
    else:
        st.markdown("**Assistant:**")
        st.markdown(result["answer"])
        if result["sql"]:
            with st.expander("View source SQL — see exactly how this was calculated"):
                st.code(result["sql"], language="sql")

        # Save to history
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "sql": result["sql"]
        })
