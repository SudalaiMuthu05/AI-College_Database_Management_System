# AI-College_Database_Management_System

## 🎓 CampusBuddy
### Connecting the Campus with Intelligent Database Conversations

> 🏢 **This project was developed as part of my internship at TANSAM.**

CampusBuddy is a locally powered AI-driven SQL assistant that allows users to query a campus database using natural language. Instead of writing complex SQL queries, users can simply ask questions in plain English — and CampusBuddy intelligently converts them into optimized PostgreSQL queries and returns structured results.

---

## 🚀 Project Overview

CampusBuddy is a research-inspired AI database agent that bridges natural language understanding and structured data retrieval — making campus data accessible to everyone, regardless of their technical background.

At its core, CampusBuddy eliminates the barrier between users and complex relational databases. Whether you're an administrator trying to pull enrollment statistics, a faculty member checking student performance, or a staff member querying departmental records — CampusBuddy lets you simply *ask* instead of *query*.

### 🔍 How It Works
The user types a plain English question (e.g., *"How many students are enrolled in Computer Science this semester?"*). CampusBuddy's AI engine, powered by a locally hosted Mistral model via Ollama, interprets the intent behind the question and translates it into a precise, optimized PostgreSQL query. The query is then validated through a secure SQL layer before execution, and the results are returned in a clean, structured format through the web interface.

### 🎯 Key Objectives
- **Democratize data access** — No SQL knowledge required to interact with the campus database
- **Ensure data security** — All queries pass through a validation and sanitization layer to prevent injection attacks
- **Maintain privacy** — The entire AI pipeline runs locally, meaning no data is sent to external servers or third-party APIs
- **Scale for real-world use** — Built and tested on a PostgreSQL database containing 200,000+ records, ensuring performance under realistic academic data loads

### 🌐 Real-World Relevance
Campus databases are notoriously complex — spanning students, faculty, courses, grades, departments, attendance, and more. Traditional systems require technical staff to retrieve even basic reports. CampusBuddy reimagines this workflow by introducing conversational AI as a middleware layer, making institutional data more transparent, accessible, and actionable for everyone on campus.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| 🧠 AI Model | Ollama + Mistral (Local LLM) |
| 🐘 Database | PostgreSQL (200,000+ records) |
| ⚙️ Backend | Flask (Python) |
| 🎨 Frontend | Modern Animated UI |
| 🔐 Security | SQL Validation & Sanitization Layer |

---

## 📸 Screenshot (UI)
![image_alt](https://github.com/SudalaiMuthu05/AI-College_Database_Management_System/blob/9d44097db689d7e344c4a9a6181e49f88be49b1f/Screenshot%20(337).png)
