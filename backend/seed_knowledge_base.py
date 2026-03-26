#!/usr/bin/env python
"""
Seed the Knowledge Base with real-world support issues and solutions.
Run this once to populate the KB.
"""

from app.db.database import SessionLocal, KnowledgeBase, init_db
from datetime import datetime

def seed_knowledge_base():
    """Populate KB with real-world issues and solutions."""
    init_db()
    db = SessionLocal()
    
    try:
        # Check if KB already seeded
        existing_count = db.query(KnowledgeBase).count()
        if existing_count > 0:
            print(f"✓ Knowledge Base already seeded with {existing_count} articles. Skipping.")
            return
        
        kb_articles = [
            # Authentication Issues
            {
                "title": "How to Reset a Forgotten Password",
                "content": """
If you've forgotten your password, follow these steps to reset it:

1. Click on the login page
2. Look for "Forgot Password?" link below the password field
3. Enter your email address or username
4. Check your email for a reset link (usually arrives within 5 minutes)
5. Click the link and create a new password
6. Password must be at least 8 characters with uppercase, lowercase, and numbers
7. Try logging in with your new password

If you don't receive the email:
- Check your spam/junk folder
- Make sure you're using the correct email
- Wait 5 minutes before requesting a new link
- Contact support if still having issues
""",
                "category": "auth",
                "tags": ["password", "reset", "forgot", "login", "access"],
                "solution_steps": [
                    "Click 'Forgot Password?' on login page",
                    "Enter email/username",
                    "Check email for reset link (5 min)",
                    "Create new password (8+ chars, mixed case + numbers)",
                    "Log in with new password"
                ],
                "related_categories": ["auth", "account"]
            },
            {
                "title": "Account Locked After Multiple Failed Login Attempts",
                "content": """
Your account has been locked for security reasons after several failed login attempts.

Why this happens:
- Protection against unauthorized access attempts
- Standard security practice for sensitive accounts
- Automatic unlock after 30 minutes of inactivity

What to do:
1. Wait 30 minutes - the account will auto-unlock
2. Ensure you're using correct credentials
3. Check CAPS LOCK is not on
4. Try logging in from a different device
5. Clear browser cookies and try again
6. If you still can't access, use password reset

Prevention:
- Use password manager to avoid typos
- Keep credentials secure
- Enable two-factor authentication for added security
""",
                "category": "auth",
                "tags": ["locked", "failed", "attempts", "security", "access"],
                "solution_steps": [
                    "Wait 30 minutes for auto-unlock",
                    "Verify correct username/password",
                    "Clear browser cache and cookies",
                    "Try from different device",
                    "Use password reset if needed"
                ],
                "related_categories": ["auth", "security"]
            },
            
            # Billing Issues
            {
                "title": "Payment Failed - Transaction Declined",
                "content": """
Your payment was declined by the payment processor. Here's how to resolve it:

Common Reasons:
1. Insufficient funds in account
2. Card has expired
3. Billing address doesn't match card records
4. Card issuer flagged as suspicious
5. Payment gateway temporarily unavailable

Steps to Fix:
1. Check your bank account has sufficient funds
2. Verify card hasn't expired (check MM/YY on card)
3. Confirm billing address matches card records exactly
4. Contact your bank to see if they blocked the transaction
5. Try a different payment method if available
6. Wait 5 minutes and retry
7. Use a different card from a different issuer

For Recurring Billing:
- Update your card details in account settings
- Select "Update Payment Method"
- Enter new card information
- Save and retry billing

Still having issues?
- Contact your bank to approve transactions with us
- Use manual payment processing
- Request invoice for offline payment
""",
                "category": "billing",
                "tags": ["payment", "declined", "card", "transaction", "money"],
                "solution_steps": [
                    "Check account has sufficient funds",
                    "Verify card hasn't expired",
                    "Confirm billing address matches exactly",
                    "Contact bank to approve transaction",
                    "Try different card/payment method",
                    "Update payment method in account settings",
                    "Request invoice for offline payment"
                ],
                "related_categories": ["billing", "payments", "account"]
            },
            {
                "title": "Invoice Discrepancies - Duplicate Charges",
                "content": """
If you notice duplicate charges or incorrect amounts on your invoice:

First Steps:
1. Check your bank/credit card statement for actual charges
2. Count how many charges match our company name
3. Note the dates and amounts
4. Check your email for confirmation receipts

Possible Reasons:
- Payment retried after initial failure
- Browser refresh during checkout created duplicate
- Subscription renewed + manual payment on same day
- Billing cycle changed and previous payment not refunded

How to Get a Refund:
1. Log into your account and go to Billing > Invoices
2. Click "dispute" on the duplicate charge
3. Provide evidence (screenshots, dates)
4. Include transaction IDs from your bank
5. Submit dispute ticket

Timeline:
- Disputes reviewed within 2 business days
- Refunds processed within 5-7 business days
- Refunds appear in your bank account 2-3 business days after processing

Preventing Future Duplicates:
- Wait for payment confirmation before closing browser
- Set up auto-billing instead of manual payments
- Update subscription before payment fails
""",
                "category": "billing",
                "tags": ["duplicate", "charge", "invoice", "refund", "billing"],
                "solution_steps": [
                    "Verify charges on bank statement",
                    "Login to account and check Invoices",
                    "Click 'dispute' on duplicate charge",
                    "Provide transaction IDs and proof",
                    "Submit dispute ticket",
                    "Wait for 2-day review, 5-7 day refund"
                ],
                "related_categories": ["billing", "payments", "refund"]
            },
            
            # Infrastructure/System Issues
            {
                "title": "Service Timeout or Slow Performance",
                "content": """
If the service is running slowly or timing out:

Quick Diagnostics:
1. Check your internet connection speed (speedtest.net)
2. Try from a different network (mobile hotspot)
3. Clear browser cache and cookies
4. Try a different browser (Chrome, Firefox, Safari)
5. Check if other services/websites load normally

If only our service is slow:
1. Try accessing from incognito/private mode
2. Disable browser extensions temporarily
3. Check browser console for errors (F12 > Console)
4. Try from a different device

Server-Side Issues:
- Check status page: status.company.com
- Check if you see "503 Service Unavailable"
- Check if region is experiencing issues
- Wait 5-15 minutes for service recovery

If Problem Persists:
1. Send us the exact error message (screenshot)
2. Include your internet speed test results
3. Tell us your timezone and when issue started
4. Provide browser type and version
5. Let us investigate on backend

Workarounds While We Fix:
- Try again in 5 minutes
- Use API directly if available
- Bulk operations may need to be queued
- Scheduled maintenance may cause temporary slowness
""",
                "category": "infra",
                "tags": ["slow", "timeout", "performance", "speed", "loading"],
                "solution_steps": [
                    "Check internet speed (speedtest.net)",
                    "Try from different network (mobile hotspot)",
                    "Clear browser cache and cookies",
                    "Try different browser",
                    "Check status page: status.company.com",
                    "Try incognito/private mode",
                    "Disable browser extensions",
                    "Check console for errors (F12)"
                ],
                "related_categories": ["infra", "technical", "performance"]
            },
            {
                "title": "System Outage or Complete Service Unavailability",
                "content": """
If you cannot access the service at all:

EMERGENCY RESPONSE:
1. Check status.company.com immediately
2. Check our Twitter @CompanyStatus for updates
3. Check your email for incident notification
4. Do NOT keep refreshing - it adds load
5. Subscribe to status page for real-time updates

What We're Doing:
1. Our engineering team is investigating (within 2 minutes)
2. Major incidents get emergency response from all teams
3. We have failover systems activating automatically
4. Status page updates every 5-10 minutes
5. Customer communication sent to all registered emails

Your Data is Safe:
- All data is backed up multiple times
- Automated backups every 6 hours
- Failed transactions are never processed
- No data loss on our systems

Timeline Expectations:
- 15 minutes: Most common issues resolved
- 1 hour: Majority of complex issues resolved
- 4+ hours: Major infrastructure failures (rare)
- Critical: Enterprise support contacted directly

What NOT to Do:
- Don't submit multiple support tickets (we see first one)
- Don't keep logging in/out
- Don't change account settings during outage
- Don't assume data is lost

Post-Outage:
- Service restored and fully operational
- Status page marked as "Resolved"
- Root cause analysis posted to status page
- Compensation applied per SLA
""",
                "category": "infra",
                "tags": ["outage", "down", "unavailable", "offline", "critical", "emergency"],
                "solution_steps": [
                    "Check status.company.com for updates",
                    "Follow @CompanyStatus on Twitter",
                    "Check email for incident notification",
                    "Wait for automated recovery (usually <30 min)",
                    "Do NOT keep refreshing",
                    "Subscribe to status page updates",
                    "Contact premium support if urgent"
                ],
                "related_categories": ["infra", "critical", "emergency"]
            },
            
            # Account & General Issues
            {
                "title": "Cannot Find or Access My Data",
                "content": """
If you can't find your data or access your account:

Data Search:
1. Use the search box at top of page
2. Try different keywords (exact words vs partial)
3. Filter by date range uploaded
4. Check different categories/folders
5. Clear search and try again
6. Use browser search (Ctrl+F) on results page

Data Organization:
1. Data might be in a different folder than expected
2. Check "Recent" section for latest uploads
3. Check "Archived" section if old data
4. Check if shared with you by someone else
5. Check "Trash" if recently deleted

Account Access:
1. Verify you're logged into correct account
2. You might have multiple accounts
3. Contact admin of shared workspace
4. Check email for account invites
5. Accept any pending workspace invites

Deleted Data Recovery:
1. Check Trash/Recycle bin
2. Deleted data available for 30 days
3. Click "Restore" to recover
4. After 30 days, permanent deletion occurs
5. Contact support for data older than 30 days

Still Can't Find It:
- Provide exact date when data was added
- Describe what the data contained
- Tell us how you uploaded it
- We can search server logs
""",
                "category": "general",
                "tags": ["data", "missing", "find", "search", "access", "lost"],
                "solution_steps": [
                    "Use search function with keywords",
                    "Try different date ranges",
                    "Check different categories/folders",
                    "Verify logged into correct account",
                    "Check shared workspace invites",
                    "Check Trash for deleted data (30 days)",
                    "Provide specific details to support"
                ],
                "related_categories": ["account", "data", "general"]
            },
            {
                "title": "Permission Denied - Cannot Edit or Delete Data",
                "content": """
If you're getting "Permission Denied" error:

Understand Permission Levels:
1. **View Only**: Can see data but not edit
2. **Edit**: Can view and modify data
3. **Admin**: Can edit, delete, and manage users
4. **Owner**: Full control including deletion

How to Check Your Permissions:
1. Open the item/folder
2. Click Settings or Info icon
3. Look for "Permissions" or "Sharing" section
4. See what level you have

If You Don't Have Permission:
1. Contact the workspace owner or admin
2. Ask for elevated permissions
3. They can upgrade you in Settings > Team Members
4. Takes effect immediately after upgrade

If You're the Owner/Admin:
1. Go to Settings > Team Members
2. Find the person in the list
3. Click their row to see permissions
4. Change permission level
5. Click Save
6. They'll see new permissions on next action

Sharing Settings:
1. Only owner can delete the item
2. Admins can delete but owner can restore
3. Editors cannot delete
4. Viewers cannot edit or delete
5. Public links have view-only access

For Workspace-Wide Changes:
- Owner: Go to Settings > Workspace
- Select default permission level for new members
- Changes apply to new additions only
- Existing members keep current level
""",
                "category": "account",
                "tags": ["permission", "denied", "access", "edit", "delete", "admin"],
                "solution_steps": [
                    "Check permission level in Settings",
                    "Ask owner/admin for higher permission",
                    "Owner goes to Settings > Team Members",
                    "Select member and change permission",
                    "Save changes",
                    "Permission takes effect immediately"
                ],
                "related_categories": ["account", "permissions", "admin"]
            },
            {
                "title": "Receive Too Many or Irrelevant Notifications",
                "content": """
If you're getting unwanted notifications:

Notification Settings:
1. Go to Settings > Notifications
2. Toggle each notification type on/off
3. Choose delivery method: Email, In-App, Both
4. Set frequency: Instant, Daily Digest, Weekly

By Type:
- Work item updates: Get notified when items change
- Comments: Get notified when mentioned
- Team messages: Get all messages or mentions only
- Billing alerts: Invoice and payment notifications
- Security alerts: Login activity and permission changes

Email Notifications:
1. Settings > Email Preferences
2. Uncheck boxes for unwanted categories
3. Set digest frequency (real-time vs daily)
4. Whitelist/blacklist specific contacts
5. Use "Do Not Disturb" during hours

Unsubscribe from Email:
1. Click "Unsubscribe" at bottom of any email
2. Remove yourself from mailing list
3. Can resubscribe in Settings later
4. Some system alerts can't be disabled

Disable All Notifications:
1. Settings > Notifications
2. Toggle "All Notifications" OFF
3. You won't receive any notifications
4. Critical security alerts still sent

Quiet Hours:
1. Settings > Do Not Disturb
2. Set time period (e.g., 6 PM - 9 AM)
3. Notifications queued and delivered after hours
4. Except for critical/security alerts
""",
                "category": "general",
                "tags": ["notifications", "email", "alert", "settings", "spam"],
                "solution_steps": [
                    "Go to Settings > Notifications",
                    "Toggle notification types on/off",
                    "Choose: Email, In-App, or Both",
                    "Set frequency: Instant or Digest",
                    "Set Do Not Disturb hours if desired",
                    "Uncheck specific categories",
                    "Save preferences"
                ],
                "related_categories": ["account", "settings", "general"]
            }
        ]
        
        for article in kb_articles:
            kb = KnowledgeBase(
                title=article["title"],
                content=article["content"],
                category=article["category"],
                tags=article.get("tags", []),
                solution_steps=article.get("solution_steps", []),
                related_categories=article.get("related_categories", []),
                is_active=True
            )
            db.add(kb)
        
        db.commit()
        print(f"✓ Successfully seeded Knowledge Base with {len(kb_articles)} articles")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error seeding Knowledge Base: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_knowledge_base()
