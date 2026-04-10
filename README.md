# 🔍 AskMyData
### Natural Language → SQL → Insights · AI-Powered Data Query Tool

<div align="center">

**Built by [Swarleen Bhamra](https://www.swarleen.com)**

[![🚀 Live App](https://img.shields.io/badge/🚀%20Live%20App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://cyberquery-ai.streamlit.app/)
[![Portfolio](https://img.shields.io/badge/🌐%20swarleen.com-1B3A6B?style=for-the-badge)](https://www.swarleen.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/swarleenbhamra/)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Swarleen)

> 💡 **Right-click the Live App badge → Open in new tab**

</div>

---

## 🚀 Try the App

<div align="center">

### 👇 Click below to open the live app

<a href="https://cyberquery-ai.streamlit.app/" target="_blank">
  <img src="https://img.shields.io/badge/▶%20Open%20AskMyData-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Open AskMyData"/>
</a>

**[https://cyberquery-ai.streamlit.app/](https://cyberquery-ai.streamlit.app/)**

> 💡 Right-click → Open in new tab to keep this page open

</div>

---

## 💡 The Idea

Most people interact with data through dashboards — static views built in advance for questions someone already thought to ask.

**AskMyData flips that.**

Type any question in plain English. The app understands what you're asking, writes the SQL, runs it against a real database, and explains what it found — in seconds. No SQL knowledge required. No pre-built reports. No waiting for an analyst.

> *"Which department had the most critical incidents last quarter?"*
> *"What's the average time to resolve high severity incidents?"*
> *"Show me all ransomware incidents in the Finance department."*

Any question. Instant answer. Plain English explanation.

---

## ⚙️ How It Works — Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                           │
│              Streamlit Web App · Python · Light Theme           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │  Natural language question
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LLM LAYER                                  │
│         Large Language Model · Natural Language Understanding   │
│                                                                 │
│  Input:  User question + database schema                        │
│  Output: Valid SQLite query                                     │
│                                                                 │
│  Prompt engineering ensures:                                    │
│  → SELECT only (no destructive queries)                         │
│  → Exact column name matching                                   │
│  → SQLite-compatible syntax                                     │
│  → Context-aware query construction                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │  Generated SQL query
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                 │
│              SQLite · In-Memory Database · Pandas               │
│                                                                 │
│  → Excel dataset loaded into SQLite on app start               │
│  → SQL executed against in-memory database                      │
│  → Results returned as structured dataframe                     │
│  → Auto chart generated for numeric results                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │  Query results
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INSIGHT LAYER                                │
│         LLM · Analytical Reasoning · Plain English Output       │
│                                                                 │
│  Input:  User question + SQL + results                          │
│  Output: 2-3 sentence executive-level insight                   │
│                                                                 │
│  Explains: What the data means · Patterns · Recommendations     │
└─────────────────────────────────────────────────────────────────┘
                         │
                         │  Answer + insight + chart
                         ▼
                    👤 User sees results
```

---

## 🧠 The AI Layer — What Makes It Work

This isn't a keyword matcher or a rule-based query builder. It uses a **Large Language Model (LLM)** for two distinct tasks:

### 1. Natural Language to SQL
The LLM receives the user's question alongside the full database schema — column names, data types, and valid values. It reasons about what the user is asking, maps it to the correct columns and filters, and generates a syntactically valid SQLite query.

**Prompt engineering handles:**
- Safety — only SELECT queries are permitted, never destructive operations
- Accuracy — exact column names enforced, correct data types respected
- Context — date formats, text comparisons, and aggregation logic handled correctly
- Edge cases — ambiguous questions are resolved using schema context

### 2. Result Interpretation
Once the query runs and results are returned, the LLM receives the original question, the SQL, and the result set. It synthesises these into a 2-3 sentence analytical insight written for a non-technical audience — specific numbers, pattern observations, and one actionable recommendation.

**This is the difference between data and insight.**

---

## 🗂️ The Dataset

**200 cybersecurity incidents · 18 dimensions · Jan 2024 – Apr 2025**

| Dimension | Values |
|---|---|
| Incident Type | Phishing, Malware, Ransomware, Unauthorized Access, DDoS, Insider Threat, Data Exfiltration, Credential Compromise, Vulnerability Exploit, Social Engineering |
| Severity | Critical / High / Medium / Low |
| Status | Open / In Progress / Resolved / Closed |
| Department | IT, Finance, HR, Operations, Legal, Marketing, Engineering, Compliance |
| Region | North America, Asia Pacific, Europe, Latin America |
| Attack Vector | Email, Network, Web Application, Insider, Physical, Third Party, Cloud |
| Control Gap | MFA Not Enforced, Patch Management Delay, Excessive Privileges, and more |
| Financial Impact | CAD dollar value per incident |
| SLA Performance | Met vs Breached by severity tier |
| Root Cause | Human Error, System Vulnerability, Process Gap, Third Party, Unknown |

---

## ✨ Features

**🔍 Natural language query**
Type any business question in plain English — no SQL knowledge needed

**📊 Embedded live dashboard**
Full interactive Power BI dashboard embedded directly in the app — explore visually before querying

**💡 AI-generated insights**
Every query result comes with a plain English analytical explanation written for non-technical stakeholders

**⚡ 10 example prompts**
One-click example questions to explore the dataset instantly

**📈 Auto chart generation**
Numeric results automatically render as bar charts for quick visual interpretation

**🔒 Secure by design**
API key stored in encrypted secrets vault 

---

## 🚀 Run It Locally

```bash
git clone https://github.com/Swarleen/askmydata
cd askmydata
pip install -r requirements.txt
streamlit run app.py
```

Add your API key to `.streamlit/secrets.toml`:
```toml
ANTHROPIC_API_KEY = "your-api-key-here"
```

Open `http://localhost:8501`

---

## ☁️ Deploy on Streamlit Cloud

1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io) → connect GitHub → select repo

---

## 🧰 Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![LLM](https://img.shields.io/badge/LLM-Natural%20Language%20Processing-1B3A6B?style=for-the-badge)
![Prompt Engineering](https://img.shields.io/badge/Prompt%20Engineering-FF6B35?style=for-the-badge)
![Excel](https://img.shields.io/badge/Microsoft%20Excel-217346?style=for-the-badge&logo=microsoft-excel&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)
![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)

**Key concepts applied:**
- Large Language Model (LLM) integration for natural language understanding
- Prompt engineering for safe, accurate SQL generation
- In-memory relational database query execution
- LLM-powered result interpretation and insight generation
- Secure secret management for API credentials
- Streamlit session state management for interactive UX

---

## 👩‍💻 About

**Swarleen Bhamra** — Business Analyst & Data Analyst based in Toronto, ON.

I build data solutions that sit at the intersection of analytics, AI, and business intelligence — from Power BI dashboards and audit analytics tools to AI-powered applications that make data accessible to everyone.

<div align="center">

| | |
|---|---|
| 🌐 Portfolio | [swarleen.com](https://www.swarleen.com) |
| 💼 LinkedIn | [linkedin.com/in/swarleenbhamra](https://www.linkedin.com/in/swarleenbhamra/) |
| 📊 Power BI Dashboards | [github.com/Swarleen/PowerBI-Portfolio](https://github.com/Swarleen/PowerBI-Portfolio) |
| 🐙 GitHub | [github.com/Swarleen](https://github.com/Swarleen) |

</div>

> 💼 Open to Business Analyst, Data Analyst, and Technology Analytics roles in Toronto.
> If this project resonates with what your team is building — let's connect.

---

<div align="center">
<sub>Dataset is fictional and created for portfolio demonstration purposes only.</sub>
</div>
