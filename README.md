<<<<<<< HEAD
# 📄 AI Resume Analyzer & ATS Optimizer

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supported-4169E1?style=flat&logo=postgresql&logoColor=white)](https://postgresql.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An enterprise-grade, portfolio-ready web application designed to parse resumes across formats (`PDF`, `DOCX`, `DOC`, `TXT`, `PNG`, `JPG`, `JPEG`), evaluate ATS scoring alignment, generate tailored cover letters, build dynamic interview preparation roadmaps, and provide side-by-side resume comparison matrix capabilities.

---

## 🌟 Core Features

- **Multi-Format ATS Parsing**: Multi-bucket skill extraction (`Languages`, `Frameworks`, `Databases`, `Tools`, `Concepts`), contact information isolation, and single-card object grouping for work experience, projects, and education.
- **Job Description Matcher**: Automated keyword overlap scoring, gap assessment, and tailored learning roadmaps.
- **Side-by-Side Resume Comparison**: Compare two uploaded resumes to analyze ATS differences, skill overlaps, and experience contrast.
- **Tailored Cover Letter Generator**: Custom cover letter generation supporting multiple executive tones (`Formal`, `Modern`, `Executive`, `Startup`, `Technical`).
- **Interactive Interview Preparation**: Batch-based dynamic Q&A practice with continuous pagination (`#1-#5`, `#6-#10`, `#11-#15`).
- **Multi-Format Export Engine**: Download parsed resumes and analysis reports in `JSON`, `Markdown`, and `HTML` formats.
- **Progressive Web App (PWA)**: Web App Manifest and Service Worker support for offline asset caching and home screen installation.

---

## 🛠 Tech Stack

- **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Flask-Migrate
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **AI Engine**: Groq API (`llama-3.3-70b-versatile`) with offline fallback parser
- **Frontend**: HTML5, Vanilla CSS3 (Glassmorphism), JavaScript (ES6+), Bootstrap 5, FontAwesome 6, Chart.js

---

## 🚀 Quick Start (Local Development)

### 1. Clone Repository & Setup Environment
```bash
git clone https://github.com/<your-username>/resume-analyzer.git
cd resume-analyzer

python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure `.env` File
Create a `.env` file in the root directory:
```env
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-12345
GROQ_API_KEY=your-groq-api-key-here
MAX_CONTENT_LENGTH=10485760
```

### 3. Run Development Server
```bash
python app.py
```
Open `http://127.0.0.1:5000` in your web browser.

---

## 🌐 Deploying to Render & GitHub

### Step 1: Push Project to GitHub
```bash
git init
git add .
git commit -m "Initial production release"
git branch -M main
git remote add origin https://github.com/<your-username>/resume-analyzer.git
git push -u origin main
```

### Step 2: Deploy on Render
1. Log in to [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** -> **Blueprint**.
3. Connect your GitHub repository `resume-analyzer`.
4. Render will automatically detect `render.yaml` and provision:
   - **Web Service**: `ai-resume-analyzer` (`gunicorn app:app`)
   - **PostgreSQL Database**: `resume-analyzer-db`
5. Under Environment Variables, set:
   - `GROQ_API_KEY`: Your Groq API key.
   - `FLASK_ENV`: `production`

---

## 🔒 Security & Hardening

- Production HTTP Security Headers (`X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, `Referrer-Policy`)
- Strict CSRF Form Token Validation
- File Upload Type & Size Restrictions (10 MB Limit)
- Parameterized Database Queries via SQLAlchemy ORM
- Secure Session Cookie Flags (`HttpOnly`, `SameSite=Lax`)

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
=======
# AI-Resume-Analyzer
>>>>>>> 22be800d5e279191bf6bf762f9b962e13ad20f43
