# 🛡️ CyberQuery AI — Natural Language to SQL
### Ask your cybersecurity data anything. In plain English. by [Swarleen Bhamra](https://www.swarleen.com)

[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Claude AI](https://img.shields.io/badge/Powered%20by-Claude%20AI-1B3A6B?style=for-the-badge)](https://anthropic.com)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Portfolio](https://img.shields.io/badge/swarleen.com-1B3A6B?style=for-the-badge)](https://www.swarleen.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/swarleenbhamra/)

---

## 💡 The Project

Most people interact with data through dashboards — static views built in advance for questions someone already thought to ask.

This app flips that. Ask any question in plain English. The AI converts it to SQL, runs it against a real database, returns the results, and explains what they mean — in seconds.

No SQL knowledge required. No pre-built reports. Just questions and answers.

Built on a 200-incident cybersecurity dataset using **Claude AI** (Anthropic) for natural language understanding and **SQLite** for query execution.

---

## ✨ What It Does

```
User types:  "Which department had the most critical incidents?"
                            ↓
         Claude converts to SQL query
                            ↓
        SQLite executes against real data
                            ↓
         Results returned as a dataframe
                            ↓
      Claude explains the findings in plain English
                            ↓
         Auto chart generated where relevant
```

---

## 🗂️ The Dataset

200 cybersecurity incidents · 18 dimensions · Jan 2024 – Apr 2025

Covers incident type, severity, status, department, region, attack vector, time to detect, time to resolve, SLA performance, control gaps, financial impact, root cause, recurrence, and regulatory reportability.

---

## 🚀 Run It Locally

```bash
git clone https://github.com/Swarleen/cyberquery-ai
cd cyberquery-ai
pip install -r requirements.txt
streamlit run app.py
```

Then open your browser at `http://localhost:8501`

You'll need an **Anthropic API key** — get one free at [console.anthropic.com](https://console.anthropic.com)

---

## ☁️ Deploy on Streamlit Cloud (Free)

1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repo → `app.py` as the main file
5. Add your Anthropic API key in Secrets: `ANTHROPIC_API_KEY = "sk-ant-..."`
6. Deploy — live in 2 minutes

---

## 🧰 Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Claude AI](https://img.shields.io/badge/Claude%20AI-1B3A6B?style=for-the-badge)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Excel](https://img.shields.io/badge/Microsoft%20Excel-217346?style=for-the-badge&logo=microsoft-excel&logoColor=white)

---

## 👩‍💻 About

**Swarleen Bhamra** — Business Analyst & Data Analyst based in Toronto, ON.

- 🌐 [swarleen.com](https://www.swarleen.com)
- 💼 [LinkedIn](https://www.linkedin.com/in/swarleenbhamra/)
- 📊 [Portfolio](https://github.com/Swarleen/PowerBI-Portfolio)

> Open to Business Analyst, Data Analyst, and Technology Audit Analytics roles in Toronto.

---

*Dataset is fictional and for portfolio demonstration purposes only.*
