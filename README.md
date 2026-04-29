# AssignmentForge – AI Assignment Generator

## 🚀 Quick Start

### 1. Start the Backend
```bash
cd backend
python main.py
```
Backend runs at: http://localhost:8000

### 2. Start the Frontend
```bash
cd frontend
npm run dev
```
Frontend runs at: http://localhost:5173

---

## 📁 Project Structure
```
assignmentforge/
├── backend/
│   ├── main.py          # FastAPI server
│   ├── generator.py     # AI content generation (OpenAI GPT-4)
│   ├── docx_builder.py  # Word document builder
│   └── database.py      # SQLite history storage
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── views/
│   │       ├── GenerateView.jsx
│   │       ├── PreviewView.jsx
│   │       └── HistoryView.jsx
│   └── vite.config.js
└── README.md
```

## 🔑 OpenAI API Key
Enter your OpenAI API key in the sidebar of the app.
Without a key, the app generates demo/preview content.

Get a key at: https://platform.openai.com/api-keys

## 📄 Supported Assignment Types
| Type | Course | Description |
|------|--------|-------------|
| Content Aggregators Research | SMALT | A1 |
| Social Media Aggregators Critique | SMALT | A2 |
| Social Media Listening Tools | SMALT | A3 |
| Goals & Objectives | CA-CNTOR | A1 Part 1 |
| Target Audience | CA-CNTOR | A1 Part 2 |
| Content Plan & Viral | CA-CNTOR | A1 Part 3 |
| Social Profiles Outreach-Ready | CA-CNTOR | A2 |
| Influencer Outreach | CA-CNTOR | A3 |
| Final Project Report | CA-CNTOR | A4 |

## 🛠 Tech Stack
- **Frontend**: React 18 + Vite + Axios
- **Backend**: FastAPI + Python 3.11
- **AI**: OpenAI GPT-4o
- **Documents**: python-docx (Word)
- **Database**: SQLite
