# ReactLens Backend

Python/FastAPI backend for the ReactLens technical debt analysis tool.

## Setup (Mac)

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# Edit .env and add your tokens:
#   GITHUB_TOKEN=your_github_personal_access_token
#   ANTHROPIC_API_KEY=your_anthropic_api_key
```

## Run

```bash
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

## Test

```bash
# Run all tests
pytest tests/ -v

# Run only unit tests
pytest tests/test_analyser.py -v

# Run only API tests
pytest tests/test_main.py -v
```

## API

### POST /api/analyse

**Request:**
```json
{
  "repo_url": "https://github.com/owner/repo",
  "github_token": "optional",
  "anthropic_key": "optional"
}
```

**Response:**
```json
{
  "repo_name": "repo",
  "total_files": 12,
  "high_debt_count": 3,
  "medium_debt_count": 5,
  "low_debt_count": 4,
  "components": [...],
  "ai_summary": "...",
  "ai_top_issues": ["..."],
  "ai_remediation_plan": ["Step 1: ...", "Step 2: ...", "Step 3: ..."],
  "ai_overall_score": 42,
  "ai_score_label": "Moderate"
}
```

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app + routes
│   ├── analyser.py          # Static analysis engine (8 metrics)
│   ├── github_client.py     # GitHub API integration
│   └── ai_recommender.py   # Anthropic API integration
├── tests/
│   ├── test_analyser.py     # Unit tests (40 tests)
│   └── test_main.py         # API integration tests (12 tests)
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```
