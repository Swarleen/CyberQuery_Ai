import streamlit as st
import pandas as pd
import sqlite3
import anthropic
import re

st.set_page_config(
    page_title="AskMyData — Natural Language to SQL",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #F5F7FA; }
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E2E8F0; }

    .hero-title { font-size: 2rem; font-weight: 700; color: #1B3A6B; margin-bottom: 0.2rem; }
    .hero-sub { font-size: 0.95rem; color: #64748B; margin-bottom: 1.5rem; }

    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .metric-val { font-size: 1.8rem; font-weight: 700; color: #1B3A6B; }
    .metric-label { font-size: 0.72rem; color: #94A3B8; margin-top: 0.2rem; text-transform: uppercase; letter-spacing: 0.05em; }

    .sql-box {
        background: #F8FAFC;
        border: 1px solid #162d54;
        border-left: 4px solid #1B3A6B;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        font-family: monospace;
        font-size: 0.85rem;
        color: #1B3A6B;
        white-space: pre-wrap;
        margin: 1rem 0;
    }
    .insight-box {
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-left: 4px solid #3B82F6;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        color: #1E3A5F;
        font-size: 0.9rem;
        line-height: 1.6;
        margin: 1rem 0;
    }
    .section-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.5rem;
    }
    .footer-text {
        text-align: center;
        color: #94A3B8;
        font-size: 0.75rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #E2E8F0;
    }
    div[data-testid="stMarkdownContainer"] p { color: #334155; }
    h1, h2, h3 { color: #1B3A6B !important; }
    label { color: #64748B !important; font-size: 0.85rem !important; }
    .stTextInput > div > div > input {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
        font-size: 1rem !important;
    }
    .stButton > button {
        background-color: #1B3A6B !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 2rem !important;
    }
    .stButton > button:hover { background-color: #162d54 !important; color: #FFFFFF !important; }
    .stButton > button span { color: #FFFFFF !important; }
    .stButton > button p { color: #FFFFFF !important; }
    .example-btn button {
        background-color: #1B3A6B !important;
        color: #FFFFFF !important;
        border: 1px solid #1B3A6B !important;
        font-size: 0.78rem !important;
        padding: 0.3rem 0.6rem !important;
        border-radius: 20px !important;
        font-weight: 400 !important;
    }
    .example-btn button:hover { background-color: #162d54 !important; border-color: #162d54 !important; color: #FFFFFF !important; }
    .example-btn button span { color: #FFFFFF !important; }
    .example-btn button p { color: #FFFFFF !important; }
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
    "Which region has the highest critical incidents?",
    "What percentage of incidents are recurring?",
    "Show total financial impact by severity",
]

if "question_input" not in st.session_state:
    st.session_state.question_input = ""

def set_example(q):
    st.session_state.question_input = q

with st.sidebar:
    st.markdown("### 🔍 AskMyData")
    st.markdown("<p style='color:#64748B;font-size:0.85rem;'>Natural Language → SQL → Insights</p>", unsafe_allow_html=True)
    st.divider()

    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        help="Get your free API key at console.anthropic.com"
    )

    st.divider()
    st.markdown("<p style='color:#94A3B8;font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;'>Dataset</p>", unsafe_allow_html=True)
    st.markdown("<p style='color:#334155;font-size:0.82rem;'>200 cybersecurity incidents<br>18 dimensions · Jan 2024 – Apr 2025</p>", unsafe_allow_html=True)

    st.divider()
    st.markdown("<p style='color:#94A3B8;font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;'>Try asking about</p>", unsafe_allow_html=True)
    topics = ["Severity trends", "SLA performance", "Financial impact", "Attack vectors", "Control gaps", "Department risk"]
    for t in topics:
        st.markdown(f"<p style='color:#1B3A6B;font-size:0.82rem;margin:0;'>→ {t}</p>", unsafe_allow_html=True)

    st.divider()
    st.markdown("<p style='color:#94A3B8;font-size:0.75rem;'>Built by <a href='https://www.swarleen.com' style='color:#1B3A6B;font-weight:600;'>Swarleen Bhamra</a></p>", unsafe_allow_html=True)

conn, df = load_data_to_sqlite()
schema = get_schema()

st.markdown('<div class="hero-title">🔍 AskMyData</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Ask any question about your cybersecurity incidents in plain English. AI writes the SQL, runs it, and explains what it found.</div>', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)
total = len(df)
critical = len(df[df['Severity'] == 'Critical'])
open_inc = len(df[df['Status'] == 'Open'])
sla_breached = len(df[df['SLA_Met'] == 'No'])
total_impact = df['Financial_Impact_CAD'].sum()

with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-val">{total}</div><div class="metric-label">Total Incidents</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-val" style="color:#E63946;">{critical}</div><div class="metric-label">Critical</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-val" style="color:#F4A261;">{open_inc}</div><div class="metric-label">Open</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card"><div class="metric-val" style="color:#E63946;">{sla_breached}</div><div class="metric-label">SLA Breached</div></div>', unsafe_allow_html=True)
with col5:
    st.markdown(f'<div class="metric-card"><div class="metric-val" style="color:#2A9D8F;">${total_impact:,.0f}</div><div class="metric-label">Total Impact (CAD)</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-label">Ask a question</div>', unsafe_allow_html=True)

st.markdown('<div class="section-label" style="margin-bottom:0.3rem;">Or try one of these</div>', unsafe_allow_html=True)

cols = st.columns(5)
for i, example in enumerate(EXAMPLE_QUESTIONS[:5]):
    with cols[i]:
        st.markdown('<div class="example-btn">', unsafe_allow_html=True)
        st.button(example, key=f"ex_{i}", use_container_width=True, on_click=set_example, args=(example,))
        st.markdown('</div>', unsafe_allow_html=True)

cols2 = st.columns(5)
for i, example in enumerate(EXAMPLE_QUESTIONS[5:]):
    with cols2[i]:
        st.markdown('<div class="example-btn">', unsafe_allow_html=True)
        st.button(example, key=f"ex2_{i}", use_container_width=True, on_click=set_example, args=(example,))
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

user_question = st.text_input(
    "Your question",
    key="question_input",
    placeholder="e.g. Which department had the most critical incidents last quarter?",
    label_visibility="collapsed"
)

run_query = st.button("🔍  Run Query")

if run_query and user_question:
    if not api_key:
        st.error("⚠️ Please enter your Anthropic API key in the sidebar to continue.")
    else:
        try:
            client = anthropic.Anthropic(api_key=api_key)

            with st.spinner("Generating SQL..."):
                sql_query = generate_sql(user_question, schema, client)

            st.markdown('<div class="section-label" style="margin-top:1.5rem;">Generated SQL</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sql-box">{sql_query}</div>', unsafe_allow_html=True)

            try:
                results = pd.read_sql_query(sql_query, conn)

                st.markdown(f'<div class="section-label" style="margin-top:1rem;">Results — {len(results)} row{"s" if len(results) != 1 else ""}</div>', unsafe_allow_html=True)

                if results.empty:
                    st.info("No results found for this query.")
                else:
                    st.dataframe(results, use_container_width=True, hide_index=True)

                    with st.spinner("Generating insight..."):
                        insight = generate_insight(user_question, sql_query, results, client)

                    st.markdown('<div class="section-label" style="margin-top:1rem;">AI Insight</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="insight-box">💡 {insight}</div>', unsafe_allow_html=True)

                    if len(results) > 1 and results.select_dtypes(include='number').shape[1] > 0:
                        numeric_cols = results.select_dtypes(include='number').columns.tolist()
                        if numeric_cols and len(results) <= 20:
                            try:
                                chart_col = numeric_cols[0]
                                label_col = [c for c in results.columns if c not in numeric_cols]
                                if label_col:
                                    chart_df = results.set_index(label_col[0])[chart_col]
                                    st.markdown('<div class="section-label" style="margin-top:1rem;">Quick Chart</div>', unsafe_allow_html=True)
                                    st.bar_chart(chart_df)
                            except Exception:
                                pass

            except Exception as e:
                st.error(f"SQL error: {str(e)} — try rephrasing your question.")

        except Exception as e:
            st.error(f"API error: {str(e)}")

elif run_query and not user_question:
    st.warning("Please enter a question first.")

with st.expander("📐 View Database Schema"):
    st.code(schema, language="sql")

st.markdown("""
<div class="footer-text">
    AskMyData · Built by <a href='https://www.swarleen.com' style='color:#1B3A6B;'>Swarleen Bhamra</a> ·
    <a href='https://www.linkedin.com/in/swarleenbhamra/' style='color:#1B3A6B;'>LinkedIn</a> ·
    <a href='https://github.com/Swarleen' style='color:#1B3A6B;'>GitHub</a><br>
    Dataset is fictional and for portfolio demonstration purposes only.
</div>
""", unsafe_allow_html=True)
