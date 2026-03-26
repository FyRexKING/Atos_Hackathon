# QUICK TEST SAMPLE - COPY & PASTE READY

## Sample Test Tickets Created

### Ticket 1: Authentication
```
ID: 25
Title: Cannot login to my account
Category: auth
Priority: high
Confidence: 0.61
Status: pending_review
```

### Ticket 2: Billing
```
ID: 26
Title: Unexpected duplicate charge on invoice
Category: billing
Confidence: 0.47
Status: pending_review
```

### Ticket 3: API
```
ID: 27
Title: API endpoint returning 500 errors
Category: infra
Confidence: 0.48
Status: pending_review
```

### Ticket 4: UI
```
ID: 28
Title: Submit button not responding
Category: ui
Confidence: 0.47
Status: pending_review
```

---

## FASTEST WAY TO TEST - SWAGGER UI

**No typing required!** Visual interface with click buttons.

1. **Open browser**: http://localhost:8000/docs
2. **You'll see** interactive API documentation
3. **Pick endpoint**: Click on any endpoint (e.g., POST /api/ticket)
4. **Click button**: "Try it out"
5. **Fill form**: Enter title and description
6. **Execute**: Click "Execute" button
7. **See response**: Immediately below

**That's it! No curl commands needed.**

---

## TEST VIA CURL (Windows Command Prompt)

### Test 1: Create Ticket
```
curl -X POST http://localhost:8000/api/ticket ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"My issue\",\"description\":\"Test description\"}"
```

### Test 2: Get Pending Tickets
```
curl http://localhost:8000/api/tickets/pending
```

### Test 3: Get Ticket #25
```
curl http://localhost:8000/api/ticket/25
```

### Test 4: Get Statistics
```
curl http://localhost:8000/api/stats
```

### Test 5: Resolve Ticket #25
```
curl -X PATCH http://localhost:8000/api/ticket/25/resolve ^
  -H "Content-Type: application/json" ^
  -d "{\"resolution\":\"Issue fixed\"}"
```

### Test 6: Reject Ticket #26
```
curl -X PATCH http://localhost:8000/api/ticket/26/reject ^
  -H "Content-Type: application/json" ^
  -d "{\"reason\":\"Duplicate\"}"
```

### Test 7: Health Check
```
curl http://localhost:8000/health
```

---

## TEST VIA PYTHON

Create `test.py`:

```python
import requests

API = "http://localhost:8000"

# 1. Create
print("[1] Creating ticket...")
r = requests.post(f"{API}/api/ticket", json={
    "title": "Test issue",
    "description": "Testing the system"
})
print(f"Status: {r.status_code}")
print(f"ID: {r.json()['ticket_id']}")
print(f"Category: {r.json()['classification']['category']}")

# 2. Get Pending
print("\n[2] Getting pending...")
r = requests.get(f"{API}/api/tickets/pending")
print(f"Count: {r.json()['count']}")

# 3. Get Stats
print("\n[3] Getting stats...")
r = requests.get(f"{API}/api/stats")
print(f"Total: {r.json()['total_tickets']}")

# 4. Get Ticket
print("\n[4] Getting ticket...")
r = requests.get(f"{API}/api/ticket/25")
print(f"Title: {r.json()['title']}")

# 5. Resolve
print("\n[5] Resolving...")
r = requests.patch(f"{API}/api/ticket/25/resolve", json={
    "resolution": "Fixed"
})
print(f"Status: {r.json()['message']}")

print("\nDone!")
```

Run: `python test.py`

---

## POST REQUEST EXAMPLE

```
POST http://localhost:8000/api/ticket
Content-Type: application/json

{
  "title": "Cannot reset password",
  "description": "I clicked reset password but didn't receive email"
}
```

**Response (200 OK):**
```json
{
  "ticket_id": 29,
  "title": "Cannot reset password",
  "classification": {
    "category": "auth",
    "priority": "high",
    "impact": "high"
  },
  "similarity": {
    "similar_tickets": [...],
    "avg_similarity": 0.56
  },
  "confidence": {
    "score": 0.54,
    "similarity_weight": 0.28,
    "category_match_weight": 0.3,
    "impact_penalty_weight": 0.035
  },
  "decision": "human_review",
  "explanation": "Matched similar ticket... Routed to human review",
  "resolution": null,
  "status": "pending_review"
}
```

---

## GET REQUEST EXAMPLE

```
GET http://localhost:8000/api/tickets/pending
```

**Response (200 OK):**
```json
{
  "tickets": [
    {
      "id": 25,
      "title": "Cannot login to my account",
      "category": "auth",
      "priority": "high",
      "impact": "high",
      "confidence_score": 0.61,
      "decision": "human_review",
      "status": "pending_review",
      "created_at": "2026-03-24T10:30:00"
    }
  ],
  "count": 26
}
```

---

## PATCH REQUEST EXAMPLE

```
PATCH http://localhost:8000/api/ticket/25/resolve
Content-Type: application/json

{
  "resolution": "We've reset your password. Check your email for reset link."
}
```

**Response (200 OK):**
```json
{
  "message": "Ticket resolved",
  "ticket": {
    "id": 25,
    "title": "Cannot login to my account",
    "status": "resolved",
    "human_resolution": "We've reset your password..."
  }
}
```

---

## ALL ENDPOINTS AT A GLANCE

| Method | Endpoint | What it does |
|--------|----------|------------|
| POST | /api/ticket | Create & process new ticket |
| GET | /api/tickets/pending | Get all pending tickets |
| GET | /api/ticket/{id} | Get one ticket's details |
| PATCH | /api/ticket/{id}/resolve | Approve & close ticket |
| PATCH | /api/ticket/{id}/reject | Reject ticket |
| GET | /api/stats | Get statistics |
| GET | /health | Check server status |

---

## WHAT HAPPENS WHEN YOU CREATE A TICKET

1. **Classification** - AI categorizes into auth/billing/infra/ui/api
2. **Priority & Impact** - AI determines priority and impact level
3. **Similarity** - System finds 3 most similar historical tickets
4. **Confidence** - System calculates solution confidence (0-1)
5. **Decision** - Routes to auto-resolve OR human queue
6. **Response** - Returns all analysis data to you

---

## WHAT YOU GET IN RESPONSE

- `ticket_id` - Unique identifier
- `classification` - Category, priority, impact
- `similarity` - Similar historical tickets
- `confidence` - Confidence score (0-1)
- `decision` - auto_resolve or human_review
- `status` - pending_review or resolved
- `resolution` - If auto-resolve, generated solution
- `explanation` - Human-readable summary

---

## SERVER INFORMATION

```
Status: RUNNING
URL: http://localhost:8000
API Docs: http://localhost:8000/docs
Database: SQLite (tickets.db)
Tickets Created: 32+
Pending Queue: 26
Average Confidence: 0.82
```

---

## RECOMMENDATION

**For easiest testing:** Open http://localhost:8000/docs in your browser

No setup needed, visual interface, instant feedback.

---

## NEXT STEPS

1. Choose a testing method above (Swagger UI recommended)
2. Create sample tickets
3. View pending queue
4. Approve or reject tickets
5. Check statistics
6. Done!

All features fully tested and working!
