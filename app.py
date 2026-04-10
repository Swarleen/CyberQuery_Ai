import streamlit as st
import pandas as pd
import sqlite3
import anthropic
import re
import os
from datetime import datetime

st.set_page_config(
    page_title="CyberQuery AI — Natural Language to SQL",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { background-color: #0F1923; }
    .stApp { background-color: #0F1923; }
    
    [data-testid="stSidebar"] {
        background-color: #1A2B3C;
    }
    
    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 0.2rem;
    }
    .hero-sub {
        font-size: 1rem;
        color: #7a8ea8;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #1A2B3C;
        border: 1px solid #2a4a7f;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        text-align: center;
    }
    .metric-val {
        font-size: 1.8rem;
        font-weight: 700;
        color: #F2C811;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #7a8ea8;
        margin-top: 0.2rem;
    }
    .sql-box {
        background: #162030;
        border: 1px solid #2a4a7f;
        border-left: 4px solid #F2C811;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        font-family: monospace;
        font-size: 0.85rem;
        color: #F2C811;
        white-space: pre-wrap;
        margin: 1rem 0;
    }
    .insight-box {
        background: #1A2B3C;
        border: 1px solid #2a4a7f;
        border-left: 4px solid #4ECDC4;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        color: #E8E8E8;
        font-size: 0.9rem;
        line-height: 1.6;
        margin: 1rem 0;
    }
    .example-chip {
        display: inline-block;
        background: #1A2B3C;
        border: 1px solid #2a4a7f;
        border-radius: 20px;
        padding: 0.3rem 0.8rem;
        font-size: 0.8rem;
        color: #7ab3ff;
        margin: 0.2rem;
        cursor: pointer;
    }
    .stTextInput > div > div > input {
        background-color: #1A2B3C !important;
        color: #FFFFFF !important;
        border: 1px solid #2a4a7f !important;
        border-radius: 8px !important;
        font-size: 1rem !important;
    }
    .stButton > button {
        background-color: #F2C811 !important;
        color: #0F1923 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 2rem !important;
        font-size: 1rem !important;
    }
    .stButton > button:hover {
        background-color: #e6b800 !important;
    }
    .stDataFrame {
        background-color: #1A2B3C !important;
    }
    div[data-testid="stMarkdownContainer"] p {
        color: #E8E8E8;
    }
    .stSelectbox > div > div {
        background-color: #1A2B3C !important;
        color: #FFFFFF !important;
        border: 1px solid #2a4a7f !important;
    }
    h1, h2, h3 { color: #FFFFFF !important; }
    .stAlert { background-color: #1A2B3C !important; }
    label { color: #7a8ea8 !important; }
    .footer-text {
        text-align: center;
        color: #3a5a7a;
        font-size: 0.75rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #1A2B3C;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_data_to_sqlite():
    df = pd.read_excel("Cybersecurity_Incidents.xlsx")
    df.columns = [c.strip() for c in df.columns]
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    df.to_sql("incidents", conn, if_exists="replace", index=False)
    return conn, df


@st.cache_data
def get_schema():
    return """
    Table: incidents
    Columns:
    - Incident_ID (TEXT): Unique identifier e.g. INC-0001
    - Reported_Date (TEXT): Date reported e.g. 2024-03-15
    - Incident_Type (TEXT): Phishing, Malware, Ransomware, Unauthorized Access, DDoS Attack, Insider Threat, Data Exfiltration, Credential Compromise, Vulnerability Exploit, Social Engineering
    - Severity (TEXT): Critical, High, Medium, Low
    - Status (TEXT): Open, In Progress, Resolved, Closed
    - Department_Affected (TEXT): IT, Finance, HR, Operations, Legal, Marketing, Engineering, Compliance
    - Region (TEXT): North America, Asia Pacific, Europe, Latin America
    - Attack_Vector (TEXT): Email, Network, Web Application, Insider, Physical, Third Party, Cloud
    - Time_to_Detect_Hours (INTEGER): Hours to detect
    - Time_to_Resolve_Hours (INTEGER): Hours to resolve
    - SLA_Met (TEXT): Yes or No
    - Resolved_Date (TEXT): Date resolved
    - Control_Gap_Identified (TEXT): MFA Not Enforced, Patch Management Delay, Excessive Privileges, No Encryption, Weak Password Policy, Missing DLP Controls, Insufficient Logging, No Security Awareness Training
    - Resolution_Team (TEXT): SOC Team, IR Team, Network Security, Identity & Access, Endpoint Security, Cloud Security
    - Financial_Impact_CAD (INTEGER): Financial impact in CAD dollars
    - Recurrence (TEXT): Yes or No
    - Root_Cause (TEXT): Human Error, System Vulnerability, Process Gap, Third Party, Unknown
    - Regulatory_Reportable (TEXT): Yes or No
    """


def generate_sql(question, schema, client):
    prompt = f"""You are an expert SQL analyst. Convert the user's natural language question into a valid SQLite SQL query.

Database schema:
{schema}

Rules:
- Only use SELECT statements — never INSERT, UPDATE, DELETE, DROP
- Use proper SQLite syntax
- For date comparisons use string comparison since dates are stored as TEXT (format: YYYY-MM-DD)
- Always use exact column names from the schema
- Return ONLY the raw SQL query with no explanation, no markdown, no backticks
- If counting, always include meaningful labels in the output
- For financial values, they are in CAD dollars

User question: {question}

SQL Query:"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    sql = message.content[0].text.strip()
    sql = re.sub(r'```sql\s*', '', sql)
    sql = re.sub(r'```\s*', '', sql)
    return sql.strip()


def generate_insight(question, sql, results_df, client):
    results_preview = results_df.head(20).to_string() if not results_df.empty else "No results returned"
    prompt = f"""You are a cybersecurity analyst presenting findings to a non-technical executive.

The user asked: "{question}"

SQL executed: {sql}

Results:
{results_preview}

Write a concise 2-3 sentence analytical insight explaining what these results mean, any patterns worth noting, and one recommendation or observation. 
Be specific with numbers from the results. Write in plain English — no jargon, no SQL references. Sound like a human analyst, not a bot."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()


EXAMPLE_QUESTIONS = [
    "How many critical incidents are still open?",
    "Which department has the most incidents?",
    "What is the average time to resolve high severity incidents?",
    "Which attack vector causes the most financial damage?",
    "How many incidents breached their SLA?",
    "What are the top 3 control gaps by incident count?",
    "Show me all ransomware incidents in Finance",
    "Which region has the highest number of critical incidents?",
    "What percentage of incidents are recurring?",
    "Show total financial impact by severity",
]

with st.sidebar:
    st.markdown("### 🛡️ CyberQuery AI")
    st.markdown("<p style='color:#7a8ea8;font-size:0.85rem;'>Natural Language → SQL → Insights</p>", unsafe_allow_html=True)
    st.divider()

    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        help="Get your API key from console.anthropic.com"
    )

    st.divider()
    st.markdown("<p style='color:#7a8ea8;font-size:0.8rem;'>📊 Dataset</p>", unsafe_allow_html=True)
    st.markdown("<p style='color:#E8E8E8;font-size:0.8rem;'>200 cybersecurity incidents<br>18 dimensions<br>Jan 2024 – Apr 2025</p>", unsafe_allow_html=True)

    st.divider()
    st.markdown("<p style='color:#7a8ea8;font-size:0.8rem;'>💡 Try asking about:</p>", unsafe_allow_html=True)
    topics = ["Severity trends", "SLA performance", "Financial impact", "Attack vectors", "Control gaps", "Department risk"]
    for t in topics:
        st.markdown(f"<span style='color:#4ECDC4;font-size:0.8rem;'>→ {t}</span>", unsafe_allow_html=True)

    st.divider()
    st.markdown("<p style='color:#3a5a7a;font-size:0.75rem;'>Built by <a href='https://www.swarleen.com' style='color:#F2C811;'>Swarleen Bhamra</a></p>", unsafe_allow_html=True)

conn, df = load_data_to_sqlite()
schema = get_schema()

st.markdown('<div class="hero-title">🛡️ CyberQuery AI</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Ask any question about your cybersecurity incidents in plain English. AI converts it to SQL and explains the results.</div>', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)
total = len(df)
critical = len(df[df['Severity'] == 'Critical'])
open_inc = len(df[df['Status'] == 'Open'])
sla_breached = len(df[df['SLA_Met'] == 'No'])
total_impact = df['Financial_Impact_CAD'].sum()

with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-val">{total}</div><div class="metric-label">Total Incidents</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-val" style="color:#FF4444;">{critical}</div><div class="metric-label">Critical</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-val" style="color:#FF8800;">{open_inc}</div><div class="metric-label">Open</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card"><div class="metric-val" style="color:#E63946;">{sla_breached}</div><div class="metric-label">SLA Breached</div></div>', unsafe_allow_html=True)
with col5:
    st.markdown(f'<div class="metric-card"><div class="metric-val" style="color:#4ECDC4;">${total_impact:,.0f}</div><div class="metric-label">Total Impact (CAD)</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("#### 💬 Ask a question about your incidents")

st.markdown("<p style='color:#7a8ea8;font-size:0.85rem;'>Try one of these:</p>", unsafe_allow_html=True)
cols = st.columns(5)
selected_example = None
for i, example in enumerate(EXAMPLE_QUESTIONS[:5]):
    with cols[i]:
        if st.button(example, key=f"ex_{i}", use_container_width=True):
            selected_example = example

cols2 = st.columns(5)
for i, example in enumerate(EXAMPLE_QUESTIONS[5:]):
    with cols2[i]:
        if st.button(example, key=f"ex2_{i}", use_container_width=True):
            selected_example = example

st.markdown("<br>", unsafe_allow_html=True)

if selected_example:
    question = selected_example
else:
    question = ""

user_question = st.text_input(
    "Your question",
    value=question,
    placeholder="e.g. Which department had the most critical incidents last quarter?",
    label_visibility="collapsed"
)

run_query = st.button("🔍 Run Query", use_container_width=False)

if run_query and user_question:
    if not api_key:
        st.error("⚠️ Please enter your Anthropic API key in the sidebar to use AI features.")
    else:
        try:
            client = anthropic.Anthropic(api_key=api_key)

            with st.spinner("🤖 Generating SQL..."):
                sql_query = generate_sql(user_question, schema, client)

            st.markdown("#### 📝 Generated SQL")
            st.markdown(f'<div class="sql-box">{sql_query}</div>', unsafe_allow_html=True)

            try:
                results = pd.read_sql_query(sql_query, conn)

                st.markdown(f"#### 📊 Results — {len(results)} row{'s' if len(results) != 1 else ''} returned")

                if results.empty:
                    st.info("No results found for this query.")
                else:
                    st.dataframe(
                        results,
                        use_container_width=True,
                        hide_index=True
                    )

                    with st.spinner("💡 Generating insight..."):
                        insight = generate_insight(user_question, sql_query, results, client)

                    st.markdown("#### 💡 AI Insight")
                    st.markdown(f'<div class="insight-box">💡 {insight}</div>', unsafe_allow_html=True)

                    if len(results) > 1 and results.select_dtypes(include='number').shape[1] > 0:
                        numeric_cols = results.select_dtypes(include='number').columns.tolist()
                        if numeric_cols and len(results) <= 20:
                            try:
                                chart_col = numeric_cols[0]
                                label_col = results.columns[0] if results.columns[0] not in numeric_cols else results.columns[-1]
                                if label_col != chart_col:
                                    chart_df = results.set_index(label_col)[chart_col]
                                    st.markdown("#### 📈 Quick Chart")
                                    st.bar_chart(chart_df)
                            except Exception:
                                pass

            except Exception as e:
                st.error(f"SQL execution error: {str(e)}")
                st.markdown("The AI generated a query that couldn't run. Try rephrasing your question.")

        except Exception as e:
            st.error(f"API error: {str(e)}")

elif run_query and not user_question:
    st.warning("Please enter a question first.")

with st.expander("📐 View Database Schema"):
    st.code(schema, language="sql")

st.markdown("""
<div class="footer-text">
    CyberQuery AI · Built by <a href='https://www.swarleen.com' style='color:#F2C811;'>Swarleen Bhamra</a> · 
    <a href='https://www.linkedin.com/in/swarleenbhamra/' style='color:#F2C811;'>LinkedIn</a> · 
    <a href='https://github.com/Swarleen' style='color:#F2C811;'>GitHub</a><br>
    Dataset is fictional and for portfolio demonstration purposes only.
</div>
""", unsafe_allow_html=True)
