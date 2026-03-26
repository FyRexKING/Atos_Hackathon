# AI Support Ticket System - Backend API

A production-ready FastAPI backend for an AI-powered support ticket system with Human-in-the-Loop (HITL) processing.

## Features

✅ **Smart Ticket Classification** - Uses Gemini API to classify tickets into category, priority, and impact
✅ **Similarity Search** - Finds similar tickets using vector embeddings and Qdrant
✅ **Confidence Scoring** - Calculates resolution confidence based on multiple factors
✅ **Intelligent Routing** - Auto-resolves high-confidence tickets or routes to humans
✅ **AI-Powered Resolutions** - Generates suggested resolutions using Gemini
✅ **Human-in-the-Loop** - SQLite database for human review queue
✅ **RESTful API** - Clean OpenAPI/Swagger documentation
✅ **Production-Ready** - Error handling, logging, and modular architecture

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app initialization
│   ├── routes/
│   │   └── ticket.py           # API endpoints
│   ├── services/
│   │   ├── classifier.py       # Gemini classification
│   │   ├── similarity.py       # Qdrant similarity search
│   │   ├── confidence.py       # Confidence scoring
│   │   ├── resolver.py         # Resolution generation
│   │   └── pipeline.py         # Main orchestration
│   ├── schemas/
│   │   └── ticket.py           # Pydantic models
│   └── db/
│       └── database.py         # SQLAlchemy models
├── requirements.txt            # Dependencies
├── .env                        # Environment variables
└── README.md                   # This file
```

## Installation

### 1. Clone and Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Edit `.env` and add your Gemini API key:

```env
GEMINI_API_KEY=your_key_here
QDRANT_HOST=localhost
QDRANT_PORT=6333
DATABASE_URL=sqlite:///./tickets.db
DEBUG=True
```

### 4. Run the Server

```bash
uvicorn app.main:app --reload
```

API will be available at `http://localhost:8000`

## API Endpoints

### Create and Process Ticket

**POST** `/api/ticket`

Request:
```json
{
  "title": "Cannot login to account",
  "description": "I've tried multiple times but keep getting an authentication error. The email and password are correct."
}
```

Response:
```json
{
  "ticket_id": 1,
  "title": "Cannot login to account",
  "classification": {
    "category": "auth",
    "priority": "high",
    "impact": "high"
  },
  "similarity": {
    "similar_tickets": [
      {
        "ticket_id": 1,
        "title": "Cannot login to account",
        "category": "auth",
        "similarity_score": 0.95,
        "status": "resolved"
      }
    ],
    "avg_similarity": 0.95
  },
  "confidence": {
    "score": 0.82,
    "similarity_weight": 0.475,
    "category_match_weight": 0.3,
    "impact_penalty_weight": 0.05
  },
  "decision": "human_review",
  "explanation": "Matched similar ticket #1 (score: 0.95) | Category: auth, Priority: high, Impact: high | Confidence: 0.82 → Routed to human review (high priority/impact)",
  "resolution": null,
  "status": "pending_review"
}
```

### Get Pending Tickets

**GET** `/api/tickets/pending`

Returns all tickets awaiting human review.

### Get Ticket by ID

**GET** `/api/ticket/{ticket_id}`

Retrieve a specific ticket's details.

### Resolve Ticket (Human)

**PATCH** `/api/ticket/{ticket_id}/resolve`

Request:
```json
{
  "resolution": "Password reset completed. User can now login."
}
```

### Reject Ticket

**PATCH** `/api/ticket/{ticket_id}/reject`

Request:
```json
{
  "reason": "Insufficient information to resolve"
}
```

### Get Statistics

**GET** `/api/stats`

Returns system statistics:
```json
{
  "total_tickets": 5,
  "resolved": 1,
  "pending_review": 3,
  "rejected": 1,
  "auto_resolved": 1,
  "avg_confidence": 0.82
}
```

### Health Check

**GET** `/health`

Returns service status.

## Classification Logic

Tickets are classified into:

**Categories:**
- `auth` - Authentication and login issues
- `billing` - Payment and invoice problems
- `infra` - Infrastructure and services
- `ui` - User interface issues
- `api` - API errors

**Priority Levels:**
- `low` - Can wait
- `medium` - Address soon
- `high` - Urgent

**Impact Levels:**
- `low` - Minor inconvenience
- `medium` - Affects workflow
- `high` - Service unavailable

## Decision Logic

The system makes decisions based on:

1. **Priority/Impact Check** - If either is HIGH → route to human
2. **Confidence Threshold** - If confidence ≥ 0.75 → auto-resolve
3. **Default** - Otherwise → route to human

### Confidence Formula

```
confidence = similarity_score × 0.5 + category_match × 0.3 + (1 - impact_penalty) × 0.2

Impact Penalty:
- low = 0.0
- medium = 0.1
- high = 0.3
```

## Services Overview

### Classifier Service
- Uses Gemini 2.0 Flash API for structured classification
- Falls back to keyword-based mock classification if API unavailable
- Handles JSON parsing errors gracefully

### Similarity Service
- Generates embeddings using deterministic hashing (mock implementation)
- Searches database for similar tickets
- Returns top 3 matches with cosine similarity scores
- Optional Qdrant integration for production scalability

### Confidence Service
- Combines similarity, category match, and impact factors
- Weights each factor according to importance
- Normalizes score between 0 and 1

### Resolver Service
- Generates contextual resolutions using Gemini Pro
- Provides category-based mock resolutions when API unavailable
- Returns resolution with explanation

### Pipeline Service
- Orchestrates all services
- Implements decision logic
- Stores tickets in database for human review
- Generates detailed explanations for all decisions

## Sample Data

The system automatically creates 5 sample tickets on startup for testing:

1. **Cannot login to account** - Auth issue (high priority)
2. **Billing discrepancy in invoice** - Billing issue (high impact)
3. **API returning 500 errors** - API issue (high priority)
4. **UI button not responsive** - UI issue (medium priority)
5. **Database connection timeout** - Infrastructure issue (high priority)

## Error Handling

- API validation with Pydantic
- Graceful fallbacks when Gemini API unavailable
- Safe JSON parsing with error recovery
- Database transaction rollback on errors
- HTTP exception handling with meaningful messages

## Testing with curl

```bash
# Create and process a ticket
curl -X POST http://localhost:8000/api/ticket \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Cannot login to account",
    "description": "I cannot access my account despite entering correct credentials"
  }'

# Get pending tickets
curl http://localhost:8000/api/tickets/pending

# Get statistics
curl http://localhost:8000/api/stats

# Access API documentation
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

## Environment Variables

```env
# Gemini API Configuration
GEMINI_API_KEY=your_api_key  # Required for full functionality

# Qdrant Configuration (optional)
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=tickets

# Database Configuration
DATABASE_URL=sqlite:///./tickets.db

# App Configuration
DEBUG=True/False
```

## Production Deployment

### Performance Optimization

1. **Database** - Use PostgreSQL instead of SQLite
2. **Embeddings** - Integrate Sentence Transformers or Gemini Embeddings API
3. **Caching** - Add Redis for caching similar tickets
4. **Queue** - Use Celery for async resolution generation
5. **Monitoring** - Add logging and metrics collection

### Recommended Setup

```python
# Use PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/tickets

# Use production server
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app

# Add database migrations with Alembic
alembic init migrations
alembic upgrade head
```

## Dependencies

- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **sqlalchemy** - ORM
- **pydantic** - Data validation
- **requests** - HTTP client for Gemini API
- **qdrant-client** - Vector database (optional)
- **python-dotenv** - Environment configuration

## License

This is a production-ready template. Customize as needed for your use case.

## Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review sample tickets for expected behavior
3. Check environment variables are properly set
4. Verify Gemini API key is valid
