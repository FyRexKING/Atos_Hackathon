import sys
import threading
import time
import requests
from fastapi.testclient import TestClient
from app.main import app

# Use TestClient for direct app testing (no server needed)
client = TestClient(app)

def run_tests():
    print("\n" + "="*70)
    print("AI SUPPORT TICKET SYSTEM - UNIT TEST SUITE")
    print("="*70 + "\n")
    
    passed = 0
    total = 0
    
    # Test 1: Health Check
    print("[1/10] Testing Health Check...")
    total += 1
    try:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        print("     Status: PASS")
        passed += 1
    except Exception as e:
        print(f"     Status: FAIL - {e}")
    
    # Test 2: Root Endpoint  
    print("[2/10] Testing Root Endpoint...")
    total += 1
    try:
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        print("     Status: PASS")
        passed += 1
    except Exception as e:
        print(f"     Status: FAIL - {e}")
    
    # Test 3: Create Auth Ticket
    print("[3/10] Testing Auth Ticket Creation...")
    total += 1
    try:
        response = client.post("/api/ticket", json={
            "title": "Cannot login to account",
            "description": "I cannot access my account with correct password"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["classification"]["category"] == "auth"
        assert "decision" in data
        print("     Status: PASS (category: {})".format(data["classification"]["category"]))
        passed += 1
    except Exception as e:
        print(f"     Status: FAIL - {e}")
    
    # Test 4: Create Billing Ticket
    print("[4/10] Testing Billing Ticket Creation...")
    total += 1
    try:
        response = client.post("/api/ticket", json={
            "title": "Billing discrepancy in invoice",
            "description": "The monthly invoice shows double the expected amount"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["classification"]["category"] == "billing"
        print("     Status: PASS (category: {})".format(data["classification"]["category"]))
        passed += 1
    except Exception as e:
        print(f"     Status: FAIL - {e}")
    
    # Test 5: Create API Error Ticket
    print("[5/10] Testing API Error Ticket Creation...")
    total += 1
    try:
        response = client.post("/api/ticket", json={
            "title": "API returning 500 errors",
            "description": "The /api/users endpoint returning HTTP 500"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["classification"]["category"] == "api"
        print("     Status: PASS (category: {})".format(data["classification"]["category"]))
        passed += 1
    except Exception as e:
        print(f"     Status: FAIL - {e}")
    
    # Test 6: Verify Confidence Scoring
    print("[6/10] Testing Confidence Scoring...")
    total += 1
    try:
        response = client.post("/api/ticket", json={
            "title": "Cannot login",
            "description": "I cannot access my account"
        })
        assert response.status_code == 200
        data = response.json()
        confidence = data["confidence"]["score"]
        assert 0 <= confidence <= 1
        print("     Status: PASS (confidence: {:.2f})".format(confidence))
        passed += 1
    except Exception as e:
        print(f"     Status: FAIL - {e}")
    
    # Test 7: Get Pending Tickets
    print("[7/10] Testing Get Pending Tickets...")
    total += 1
    try:
        response = client.get("/api/tickets/pending")
        assert response.status_code == 200
        data = response.json()
        assert "tickets" in data
        assert "count" in data
        print("     Status: PASS (found {} pending tickets)".format(data["count"]))
        passed += 1
    except Exception as e:
        print(f"     Status: FAIL - {e}")
    
    # Test 8: Get Statistics
    print("[8/10] Testing Statistics Endpoint...")
    total += 1
    try:
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_tickets" in data
        assert "resolved" in data
        assert "pending_review" in data
        print("     Status: PASS (total: {}, resolved: {})".format(
            data["total_tickets"], data["resolved"]))
        passed += 1
    except Exception as e:
        print(f"     Status: FAIL - {e}")
    
    # Test 9: Input Validation
    print("[9/10] Testing Input Validation...")
    total += 1
    try:
        response = client.post("/api/ticket", json={
            "title": "x"  # Too short
        })
        assert response.status_code == 422  # Validation error
        print("     Status: PASS (validation error caught)")
        passed += 1
    except Exception as e:
        print(f"     Status: FAIL - {e}")
    
    # Test 10: Decision Logic
    print("[10/10] Testing Decision Logic...")
    total += 1
    try:
        response = client.post("/api/ticket", json={
            "title": "Cannot login to account",
            "description": "I cannot access my account"
        })
        assert response.status_code == 200
        data = response.json()
        decision = data["decision"]
        assert decision in ["auto_resolve", "human_review"]
        explanation = data["explanation"]
        assert len(explanation) > 0
        print("     Status: PASS (decision: {})".format(decision))
        passed += 1
    except Exception as e:
        print(f"     Status: FAIL - {e}")
    
    # Summary
    print("\n" + "="*70)
    print("TEST RESULTS")
    print("="*70)
    print("Tests Passed: {}/{}".format(passed, total))
    if passed == total:
        print("Status: ALL TESTS PASSED!")
    else:
        print("Status: SOME TESTS FAILED")
    print("="*70 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
