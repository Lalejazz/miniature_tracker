# Miniature Tracker

A web application to track your Warhammer miniature collection and painting progress.

## Features (MVP)
- Track miniatures with basic information (name, faction, model type)
- Monitor painting status progression:
  - Want to Buy
  - Purchased
  - Assembled
  - Primed
  - Game Ready
  - Parade Ready

## Tech Stack
- **Backend**: Python FastAPI
- **Frontend**: React with TypeScript
- **Database**: JSON file storage (for MVP)
- **Hosting**: Netlify/Vercel

## Project Structure
```
miniature_tracker/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI app
│   │   ├── models.py       # Data models
│   │   ├── crud.py         # Database operations
│   │   └── tests/          # Backend tests
│   ├── data/               # JSON storage
│   └── pyproject.toml      # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   ├── public/
│   └── package.json
└── README.md
```

## Development Setup

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## API Endpoints (Planned)
- `GET /miniatures` - List all miniatures
- `POST /miniatures` - Add new miniature
- `PUT /miniatures/{id}` - Update miniature
- `DELETE /miniatures/{id}` - Delete miniature

## Development Principles
- TDD: Tests first, then implementation
- KISS: Simple solutions over complex ones
- YAGNI: Build only what we need now 