# DrishtiAI — Patient Safety Signal Intelligence

Real-time social listening platform that monitors Twitter, Reddit, and online forums for patient-reported adverse drug events and safety signals.

## What It Does
- Ingests tweets and posts mentioning drugs, symptoms, and conditions
- Runs biomedical NLP to extract entities (drugs, symptoms, conditions)
- Detects adverse drug events with confidence scoring and SHAP explanations
- Flags PII/PHI in posts and masks content automatically
- Displays signals in a real-time dashboard with trend charts

## Tech Stack
Python, FastAPI, PostgreSQL, Redis, scispaCy, cardiffnlp sentiment model, Microsoft Presidio, Streamlit, Plotly, twitterapi.io, Docker Compose

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

# Copy env file and add your API keys
cp .env.example .env

# Start API server
uvicorn main:app --reload

# Start dashboard (new terminal)
venv\Scripts\python.exe -m streamlit run dashboard.py
```

### API Endpoints
- `POST /ingest/test` — fetch posts from Twitter
- `POST /process` — run NLP pipeline on unprocessed posts
- `GET /signals/feed` — signal feed with full NLP results
- `GET /signals/stats` — summary statistics
- `GET /signals/trends` — trend data for charts

## 👨‍💻 Contributors
- https://github.com/524himanshu/
- https://github.com/sahasweety

## Team
DrishtiAI — AI for Bharat 2026, Theme 6
