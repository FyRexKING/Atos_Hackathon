# Quick Testing Guide - AI Ticket System

## Setup: Ensure Both Servers Running

```bash
# Terminal 1: Backend
cd /home/beluga/ATOS/backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd /home/beluga/ATOS/frontend
npm run dev
# Should start on http://localhost:5174
```

---

## Test Scenario 1: Auto-Resolution (≥0.80 Confidence)

### Setup
1. Open frontend on http://localhost:5174
2. Log in as CLIENT
3. Navigate to TicketForm

### Test Steps
1. **Submit ticket**:
   - Title: "Cannot reset password for my account"
   - Description: "I've tried resetting my password three times. I get the reset email but clicking the link does nothing. The link works when I copy-paste it into a new tab though."

2. **Expected Result**:
   ```
   ✓ Category: "auth" (authentication)
   ✓ Priority: "medium" (or "low")
   ✓ Confidence: ≥ 0.80 (high match with password reset patterns)
   ✓ Status: "resolved" (auto-resolved)
   ✓ Decision: "Auto Resolved"
   ```

3. **Client Dashboard Check**:
   - Ticket details show **green section**: "Your Ticket Has Been Resolved"
   - Resolution text visible (e.g., "Password reset email link issue detected...")
   - Status badge shows "Auto Resolved"

---

## Test Scenario 2: Human Review (< 0.80 Confidence)

### Test Steps
1. **Submit ticket**:
   - Title: "Strange behavior in our custom API integration"
   - Description: "After deploying version 3.2, our internal dashboards are showing intermittent timeouts. Only affects certain queries. We've checked logs but nothing obvious."

2. **Expected Result**:
   ```
   ✓ Category: "api"
   ✓ Priority: "medium"
   ✓ Confidence: < 0.80 (novel/complex issue)
   ✓ Status: "pending_review"
   ✓ Decision: "Human Review"
   ```

3. **Admin Dashboard Check**:
   - Ticket appears in "Pending Review" queue
   - ApprovalPanel shows three action buttons

---

## Test Scenario 3: Admin Assign to Team

### Test Steps
1. **In Admin Dashboard**, select the pending ticket from Scenario 2
2. **Click "Assign Team"** button
3. **Fill form**:
   - Team: Select "Engineering"
   - Note: "This looks like v3.2 deployment issue. Check recent commits."
4. **Click "Assign"**

### Expected Result
```
✓ Ticket status changes to "assigned"
✓ assigned_team set to "Engineering"
✓ Success message: "Ticket assigned to Engineering!"
✓ Ticket removed from admin queue (now assigned, not pending)
✓ Client sees blue box: "Assigned to Engineering team"
```

---

## Test Scenario 4: Admin Reject with Message

### Test Steps
1. **In Admin Dashboard**, select any pending ticket
2. **Click "Reject"** button
3. **Fill form**:
   - Message: "We are unable to process this request as it falls outside our support scope. Please contact our enterprise support team for custom integrations."
4. **Click "Confirm Rejection"**

### Expected Result
```
✓ Ticket status changes to "rejected"
✓ rejection_message saved
✓ Success message: "Ticket rejected - message sent to client!"
✓ Client sees red box with exact rejection message
✓ No resolution offered (just rejection reason)
```

---

## Test Scenario 5: Admin Approve AI Resolution

### Test Steps
1. **Create and auto-resolve a ticket** (Scenario 1)
2. **Switch to Admin Dashboard**
3. **Look for an "Approve AI" button** next to the auto-resolved ticket
   - *Note: This button should ONLY appear for auto-resolved tickets*
4. **Click "Approve AI"**
5. **Optional note field**, click "Confirm Approval"

### Expected Result
```
✓ Ticket status changes to "resolved"
✓ resolution_source set to "ai"
✓ Success message: "AI resolution approved and finalized!"
✓ Ticket locked (no further admin actions available)
✓ Client sees green box with resolution text
```

---

## Database Verification

### Check Columns Exist
```bash
cd /home/beluga/ATOS/backend

# Option 1: Check database directly
sqlite3 tickets.db ".schema tickets" | grep -E "assigned_team|rejection_message|resolution_source"

# Option 2: Run migration (safe, idempotent)
python migrate_db.py
```

### Check Fields in Sample Tickets
```bash
sqlite3 tickets.db
> SELECT id, status, assigned_team, rejection_message, resolution_source FROM tickets LIMIT 5;
```

---

## API Endpoint Testing (cURL)

### 1. Assign to Team
```bash
curl -X POST http://localhost:8000/api/admin/ticket/1/assign \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"team": "Engineering", "note": "Deployment issue detected"}'
```

### 2. Reject Ticket
```bash
curl -X POST http://localhost:8000/api/admin/ticket/1/reject \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Unable to process at this time"}'
```

### 3. Approve AI Resolution
```bash
curl -X POST http://localhost:8000/api/admin/ticket/1/approve-ai \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"note": "Looks good"}'
```

---

## Debugging Tips

### If Auto-Resolution Doesn't Trigger
1. Check confidence score in response (should be ≥ 0.80)
2. Check priority/impact (should NOT be "high")
3. Log in to admin and verify ticket appears in queue, not resolved list

### If Assign/Reject Buttons Don't Work
1. Make sure you're logged in as ADMIN role
2. Check browser console for API errors (F12 → Console tab)
3. Verify backend is running on port 8000

### If Changes Don't Show
1. **Backend**: Restart uvicorn (Ctrl+C, then restart)
2. **Frontend**: Clear browser cache (Ctrl+Shift+Del) or use incognito mode
3. Check Network tab in DevTools to see actual API responses

---

## Success Indicators

When everything works:
1. ✅ 0.80+ confidence → auto-resolved, shows on client dashboard
2. ✅ < 0.80 confidence → pending review in admin queue
3. ✅ Admin can assign, reject, or approve with single clicks
4. ✅ All changes reflected immediately on client/admin dashboards
5. ✅ Database updated with correct `assigned_team`, `rejection_message`, `resolution_source`
6. ✅ Clients see appropriate sections (green for resolved, red for rejected, blue for assigned)

---

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| "Admin access required" error | Not logged in as admin | Create admin account or promote user |
| Assign button not appearing | Ticket not in pending_review status | Ensure ticket needs admin action |
| No green box on client dashboard | Ticket not auto-resolved | Check confidence score |
| Database columns don't exist | Migration not run | Run `python migrate_db.py` |
| Port 8000/5174 already in use | Server already running | Kill existing process or use different port |

---

**Ready to test? Start with Test Scenario 1 for the happy path!**
