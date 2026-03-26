# COMPLETE API TESTING GUIDE

## Server Status
- **Status**: RUNNING
- **URL**: http://localhost:8000
- **Port**: 8000
- **Database**: SQLite (tickets.db)

---

## SAMPLE TEST TICKETS CREATED

### Ticket 1: Authentication Issue
```
ID: 25
Title: Cannot login to my account
Category: auth
Priority: high
Impact: high
Confidence: 0.61
Decision: human_review
Status: pending_review
```

### Ticket 2: Billing Issue
```
ID: 26
Title: Unexpected duplicate charge on invoice
Category: billing
Priority: low
Impact: low
Confidence: 0.47
Decision: human_review
Status: pending_review
```

### Ticket 3: API Error
```
ID: 27
Title: API endpoint returning 500 errors
Category: infra
Priority: low
Impact: low
Confidence: 0.48
Decision: human_review
Status: pending_review
```

### Ticket 4: UI Issue
```
ID: 28
Title: Submit button not responding on contact form
Category: ui
Priority: low
Impact: low
Confidence: 0.47
Decision: human_review
Status: pending_review
```

---

## METHOD 1: INTERACTIVE SWAGGER UI (RECOMMENDED)

**EASIEST WAY TO TEST:**

1. Open browser and go to: **http://localhost:8000/docs**
2. You will see all endpoints listed
3. Click on any endpoint to expand it
4. Click "Try it out" button
5. Fill in the form with test data (if needed)
6. Click "Execute" button
7. See the response immediately

**No coding required!** Just visual forms and buttons.

---

## METHOD 2: USING CURL IN TERMINAL

Copy and paste these commands in Command Prompt or PowerShell:

### Test 1: Create a New Ticket (POST)
```bash
curl -X POST http://localhost:8000/api/ticket ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"Test ticket\",\"description\":\"This is a test\"}"
```

### Test 2: Get All Pending Tickets (GET)
```bash
curl http://localhost:8000/api/tickets/pending
```

### Test 3: Get Specific Ticket (GET)
```bash
curl http://localhost:8000/api/ticket/25
```

### Test 4: Get System Statistics (GET)
```bash
curl http://localhost:8000/api/stats
```

### Test 5: Resolve a Ticket (PATCH)
```bash
curl -X PATCH http://localhost:8000/api/ticket/25/resolve ^
  -H "Content-Type: application/json" ^
  -d "{\"resolution\":\"Issue resolved\"}"
```

### Test 6: Reject a Ticket (PATCH)
```bash
curl -X PATCH http://localhost:8000/api/ticket/26/reject ^
  -H "Content-Type: application/json" ^
  -d "{\"reason\":\"Duplicate ticket\"}"
```

### Test 7: Health Check (GET)
```bash
curl http://localhost:8000/health
```

---

## METHOD 3: USING PYTHON

Create file `test_api.py`:

```python
import requests

BASE_URL = "http://localhost:8000"

# Test 1: Create Ticket
print("[1] Creating ticket...")
resp = requests.post(f"{BASE_URL}/api/ticket", json={
    "title": "Cannot login",
    "description": "Cannot access account"
})
data = resp.json()
print(f"  Ticket ID: {data['ticket_id']}")
print(f"  Category: {data['classification']['category']}")
print(f"  Confidence: {data['confidence']['score']:.2f}")
print(f"  Decision: {data['decision']}")

# Test 2: Get Pending Tickets
print("\n[2] Getting pending tickets...")
resp = requests.get(f"{BASE_URL}/api/tickets/pending")
data = resp.json()
print(f"  Total pending: {data['count']}")

# Test 3: Get Stats
print("\n[3] Getting statistics...")
resp = requests.get(f"{BASE_URL}/api/stats")
stats = resp.json()
print(f"  Total tickets: {stats['total_tickets']}")
print(f"  Resolved: {stats['resolved']}")
print(f"  Pending: {stats['pending_review']}")

# Test 4: Get Specific Ticket
print("\n[4] Getting ticket #25...")
resp = requests.get(f"{BASE_URL}/api/ticket/25")
ticket = resp.json()
print(f"  Title: {ticket['title']}")
print(f"  Status: {ticket['status']}")

# Test 5: Resolve Ticket
print("\n[5] Resolving ticket #25...")
resp = requests.patch(f"{BASE_URL}/api/ticket/25/resolve", json={
    "resolution": "Issue has been resolved"
})
print(f"  Status: {resp.json()['message']}")

print("\n[SUCCESS] All tests completed!")
```

Run with: `python test_api.py`

---

## ALL ENDPOINTS REFERENCE

| Endpoint | Method | Purpose | Response |
|----------|--------|---------|----------|
| `/api/ticket` | POST | Create ticket | 200 + ticket object |
| `/api/tickets/pending` | GET | Get pending queue | 200 + array of tickets |
| `/api/ticket/{id}` | GET | Get ticket by ID | 200 + ticket object |
| `/api/ticket/{id}/resolve` | PATCH | Resolve ticket | 200 + updated ticket |
| `/api/ticket/{id}/reject` | PATCH | Reject ticket | 200 + updated ticket |
| `/api/stats` | GET | Get statistics | 200 + stats object |
| `/health` | GET | Health check | 200 + status |

---

## RESPONSE EXAMPLES

### POST /api/ticket - Response
```json
{
  "ticket_id": 25,
  "title": "Cannot login to my account",
  "classification": {
    "category": "auth",
    "priority": "high",
    "impact": "high"
  },
  "similarity": {
    "similar_tickets": [
      {
        "ticket_id": 18,
        "title": "Cannot login to account",
        "category": "auth",
        "similarity_score": 0.89,
        "status": "resolved"
      }
    ],
    "avg_similarity": 0.89
  },
  "confidence": {
    "score": 0.78,
    "similarity_weight": 0.445,
    "category_match_weight": 0.3,
    "impact_penalty_weight": 0.035
  },
  "decision": "human_review",
  "explanation": "Matched similar ticket #18... Routed to human review",
  "resolution": null,
  "status": "pending_review"
}
```

### GET /api/tickets/pending - Response
```json
{
  "tickets": [
    {
      "id": 25,
      "title": "Cannot login to my account",
      "category": "auth",
      "priority": "high",
      "impact": "high",
      "confidence_score": 0.78,
      "decision": "human_review",
      "status": "pending_review",
      "created_at": "2026-03-24T10:30:00"
    }
  ],
  "count": 22
}
```

### GET /api/stats - Response
```json
{
  "total_tickets": 32,
  "resolved": 1,
  "pending_review": 22,
  "rejected": 2,
  "auto_resolved": 1,
  "avg_confidence": 0.82
}
```

### PATCH /api/ticket/{id}/resolve - Response
```json
{
  "message": "Ticket resolved",
  "ticket": {
    "id": 25,
    "status": "resolved",
    "human_resolution": "Issue resolved by human agent"
  }
}
```

---

## TESTING WORKFLOW

### Step-by-Step Testing

1. **Create a Ticket**
   - Use POST /api/ticket
   - Provide title and description
   - Note the ticket ID returned

2. **Verify Pending Queue**
   - Use GET /api/tickets/pending
   - Should see your new ticket

3. **Get Ticket Details**
   - Use GET /api/ticket/{id}
   - Replace {id} with ticket ID from step 1

4. **Check Statistics**
   - Use GET /api/stats
   - Should show total_tickets increased

5. **Resolve the Ticket**
   - Use PATCH /api/ticket/{id}/resolve
   - Provide resolution message
   - Status should change to "resolved"

6. **Verify Update**
   - Use GET /api/ticket/{id}
   - Confirm status is "resolved"

7. **Check Final Statistics**
   - Use GET /api/stats
   - resolved count should increase

---

## QUICK COMMAND REFERENCE

Create ticket:
```
curl -X POST http://localhost:8000/api/ticket -H "Content-Type: application/json" -d "{\"title\":\"...\",\"description\":\"...\"}"
```

Get pending:
```
curl http://localhost:8000/api/tickets/pending
```

Get ticket:
```
curl http://localhost:8000/api/ticket/ID
```

Get stats:
```
curl http://localhost:8000/api/stats
```

Resolve:
```
curl -X PATCH http://localhost:8000/api/ticket/ID/resolve -H "Content-Type: application/json" -d "{\"resolution\":\"...\"}"
```

Reject:
```
curl -X PATCH http://localhost:8000/api/ticket/ID/reject -H "Content-Type: application/json" -d "{\"reason\":\"...\"}"
```

Health:
```
curl http://localhost:8000/health
```

---

## IMPORTANT NOTES

- **Base URL**: http://localhost:8000
- **Content-Type**: application/json (for POST/PATCH requests)
- **Status Codes**: 200 = success, 404 = not found, 422 = validation error
- **Database**: SQLite (auto-created, persists data)
- **Sample Tickets**: Pre-loaded (tickets 1-5)
- **New Tickets**: Continue from ID 25+

---

## NEXT STEPS

1. **Recommended**: Open http://localhost:8000/docs (best experience)
2. **Alternative**: Use curl commands above
3. **Advanced**: Use Python requests library
4. **Full Docs**: See README.md and EXAMPLES.md files

---

**Server is ready for testing!** All endpoints are live and functional.
