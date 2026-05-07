# DrishtiAI — Patient Safety Signal Intelligence

Real-time social listening platform that monitors Twitter, Reddit, and online forums for patient-reported adverse drug events and safety signals — surfacing risks weeks before they appear in formal pharmacovigilance reports.

## What It Does
- Ingests tweets and posts mentioning drugs, symptoms, and conditions in real time
- Runs a 4-stage biomedical NLP pipeline: entity extraction → sentiment → adverse event detection → PII flagging
- Detects adverse drug events with confidence scoring and explainable AI (SHAP-style reasoning)
- Automatically masks PII/PHI in all dashboard views — DPDP Act compliant by design
- Agentic source discovery — AI agent searches the web for new patient communities and forums automatically
- Live dashboard with signal feed, trend charts, and one-click source onboarding

## AI Pipeline
| Stage | Model / Tool | Purpose |
|-------|-------------|---------|
| Named Entity Recognition | scispaCy `en_core_sci_sm` | Extract drugs, symptoms, conditions |
| Sentiment Analysis | cardiffnlp/twitter-roberta-base-sentiment | Social media-aware sentiment |
| Adverse Event Detection | Rule-based classifier + sentiment signals | Flag safety-critical posts |
| PII/PHI Flagging | Microsoft Presidio | Detect and mask personal identifiers |
| Source Discovery | DuckDuckGo Search Agent | Auto-discover new monitoring sources |

## Tech Stack
Python, FastAPI, PostgreSQL, Redis, scispaCy, cardiffnlp RoBERTa, Microsoft Presidio, Streamlit, Plotly, twitterapi.io, PRAW, DuckDuckGo Search, APScheduler, Docker Compose

## Architecture
Twitter / Reddit / Forums
↓
Source Engine (plugin architecture)
↓
PostgreSQL (raw posts)
↓
NLP Pipeline (scispaCy → RoBERTa → Presidio)
↓
Signal Intelligence (adverse events + SHAP explanations)
↓
Streamlit Dashboard

## Setup

### Prerequisites
- Docker Desktop
- Python 3.10+

### Run
```bash
# Start database and Redis
docker compose up -d

# Install dependencies
cd backend
pip install -r requirements.txt
pip install https://s3-us-west-2.amazonaws.com/ai2-s3-scispacy/releases/v0.5.4/en_core_sci_sm-0.5.4.tar.gz

# Add your API keys
cp .env.example .env
# Edit .env and add TWITTER_API_KEY

# Start API server
uvicorn main:app --reload

# Start dashboard (new terminal)
venv\Scripts\python.exe -m streamlit run dashboard.py
```

### Environment Variables
- DATABASE_URL=postgresql://drishti:drishti123@127.0.0.1:5433/drishtidb
- REDIS_URL=redis://localhost:6379
- TWITTER_API_KEY=your_twitterapi_io_key
- REDDIT_CLIENT_ID=your_reddit_client_id
- REDDIT_CLIENT_SECRET=your_reddit_client_secret

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ingest/test` | Fetch posts from Twitter |
| POST | `/process` | Run NLP pipeline on unprocessed posts |
| GET | `/signals/feed` | Signal feed with full NLP results |
| GET | `/signals/stats` | Summary statistics |
| GET | `/signals/trends` | Trend data for charts |
| GET | `/discover` | Agentic source discovery |

## India-Specific Design
- PII detection includes Aadhaar number patterns
- Adverse event classifier handles Hinglish and Indian drug brand names
- DPDP Act compliant — no raw author data stored, all PII masked
- Designed for CDSCO/PvPI integration for post-market surveillance

## Contributors
- Himanshu Menghani — https://github.com/524himanshu
- Sweety Saha — https://github.com/sahasweety

## Hackathon
AI for Bharat 2026 — Theme 6: Real-Time Social Listening for Patient Experience & Safety Signals
PAN IIT Bangalore Alumni Association × Government of Karnataka
