# DocGen AI 🚀

**AI-powered professional document generator for small businesses.**

Turn your rough notes, data, and ideas into polished business documents in seconds.

## Features

- 📄 **5 Document Types**: Proposals, Invoices, Reports, SOPs, Contracts
- 🤖 **AI-Powered**: Uses Google Gemini to generate professional content
- 📥 **PDF Export**: Download any document as a clean PDF
- ✏️ **Edit & Customize**: Modify generated documents before downloading
- 📚 **Document History**: All your documents saved and accessible
- 💰 **Free to Start**: Uses free-tier APIs and SQLite database

## Quick Start

### 1. Prerequisites

- Python 3.10+ installed
- A free [Google Gemini API key](https://aistudio.google.com/apikey) (optional for demo mode)

### 2. Setup

```bash
# Clone or navigate to the project
cd docgen-ai

# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (Mac/Linux)
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure

```bash
# Copy the example env file
copy .env.example .env

# Edit .env and add your Gemini API key
# GEMINI_API_KEY=your-key-here
```

> **Note**: The app works in demo mode without an API key, but real AI generation requires a free Gemini key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey).

### 4. Run

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000** in your browser. That's it! 🎉

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/documents/generate` | Generate a new document |
| GET | `/api/documents/` | List all documents |
| GET | `/api/documents/{id}` | Get a specific document |
| PUT | `/api/documents/{id}` | Update a document |
| DELETE | `/api/documents/{id}` | Delete a document |
| GET | `/api/documents/{id}/pdf` | Download as PDF |
| GET | `/api/documents/{id}/html` | Get raw HTML |
| GET | `/api/health` | Health check |

## Tech Stack

- **Backend**: Python + FastAPI
- **AI**: Google Gemini 2.0 Flash
- **Database**: SQLite + SQLAlchemy
- **PDF**: WeasyPrint
- **Frontend**: Vanilla HTML/CSS/JS

## Project Structure

```
docgen-ai/
├── app/
│   ├── main.py           # FastAPI app entry point
│   ├── config.py         # Configuration
│   ├── database.py       # Database setup
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic schemas
│   ├── routers/
│   │   └── documents.py  # API endpoints
│   └── services/
│       ├── ai_service.py # AI generation logic
│       └── pdf_service.py# PDF generation
├── frontend/
│   ├── index.html        # Main UI
│   ├── styles.css        # Styling
│   └── app.js            # Frontend logic
├── requirements.txt
├── .env.example
└── README.md
```

## Roadmap to Revenue

1. ✅ MVP with core document generation
2. 🔲 Add user authentication & accounts
3. 🔲 Add Stripe payments (freemium: 3 free docs/month)
4. 🔲 Custom templates & branding
5. 🔲 Team/organization plans
6. 🔲 File upload support (Excel, CSV → reports)
7. 🔲 Launch on Product Hunt & Indie Hackers

## License

MIT
