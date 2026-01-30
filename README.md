# GitHub Repository Analyzer

AI-powered tool to analyze GitHub repositories and generate interview prep materials.

## Features
- 📖 Project explanations
- 📄 Resume bullet points
- 🎓 Viva questions
- 💼 Interview Q&A
- 💬 AI Chatbot
- 📥 Export (TXT, DOCX, PDF)

## Live Demo
🔗 https://github-analyzer-dev.vercel.app

## Tech Stack
**Frontend:** React, Tailwind CSS, Vite  
**Backend:** FastAPI, Python, Groq AI  
**Deploy:** Vercel + Render

## Local Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
# Create .env with GROQ_API_KEY
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables
```
GROQ_API_KEY=your_groq_key
GITHUB_TOKEN=your_github_token (optional)
```

## Usage
1. Enter GitHub repo URL
2. Click "Analyze Repository"
3. View results in tabs
4. Download or chat about the repo

## API Endpoints
- `POST /api/analyze-repo` - Analyze repository
- `POST /api/chat` - Chat about repository
- `POST /api/export-docx` - Export as Word
- `POST /api/export-pdf` - Export as PDF
