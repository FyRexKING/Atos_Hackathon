"""
High-quality seed tickets for system learning.
These represent real-world support cases with proper resolutions.
Automatically loaded when database initializes.
"""

QUALITY_TICKETS = [
    {
        "title": "Cannot reset password - email not received",
        "description": "I clicked 'Forgot Password' but never received the reset email. I've checked spam folder. Account shows last login was 2 weeks ago.",
        "category": "auth",
        "priority": "high",
        "impact": "high",
        "resolution": "User email had unsubscribed from password reset emails due to bulk mail filter. Manually reset password via admin panel and educated user on email filtering. Added user to whitelist for future resets.",
        "status": "resolved",
        "resolved_by": "admin",
    },
    {
        "title": "Double charge on subscription renewal",
        "description": "I was charged $99.99 twice on March 15th for my Pro plan renewal. I only expected one charge. My credit card statement shows two identical transactions.",
        "category": "billing",
        "priority": "high",
        "impact": "medium",
        "resolution": "Found duplicate charge due to user submitting form twice rapidly. Refunded $99.99 to original payment method. Added client-side button disable to prevent double submissions.",
        "status": "resolved",
        "resolved_by": "admin",
    },
    {
        "title": "API timeout on bulk data export",
        "description": "Getting '504 Gateway Timeout' when trying to export 50,000 records via /api/export endpoint. Same operation worked fine last month with 30,000 records. No recent changes to my code.",
        "category": "api",
        "priority": "high",
        "impact": "high",
        "resolution": "Database query was missing index on export_date column. Added composite index on (user_id, export_date). Export now completes in 2.3s instead of 45s. User informed of query optimization.",
        "status": "resolved",
        "resolved_by": "admin",
    },
    {
        "title": "Database connection timeout during peak hours",
        "description": "Between 9-10 AM PST, we're seeing 'Database connection pool exhausted' errors. This happens every weekday. Our application is trying to scale but hitting connection limits.",
        "category": "infra",
        "priority": "high",
        "impact": "high",
        "resolution": "Increased connection pool size from 20 to 50. Implemented connection pooling on application side. Connection timeout errors reduced by 95%. Recommend monitoring peak hour usage.",
        "status": "resolved",
        "resolved_by": "admin",
    },
    {
        "title": "Two-factor authentication not working after password change",
        "description": "Changed my password yesterday and now 2FA won't authenticate. I get 'Invalid token' error even though I'm using correct authenticator app codes. Previously worked fine.",
        "category": "auth",
        "priority": "critical",
        "impact": "high",
        "resolution": "2FA tokens are time-sensitive and syncing issue occurred after password change. User re-registered authenticator app (removed old device, added new). Used backup codes to regain access during process.",
        "status": "resolved",
        "resolved_by": "admin",
    },
    {
        "title": "Data not syncing across multiple devices",
        "description": "Created a project on my laptop but it's not showing on my phone. I waited 5 minutes. Other users report same issue. Data seems to be locally stored but not reaching the server.",
        "category": "general",
        "priority": "high",
        "impact": "high",
        "resolution": "Sync service was failing silently due to rate limit on mobile app. Backend returning 429s but app not retrying. Updated app to implement exponential backoff. Data now syncs within 2 seconds.",
        "status": "resolved",
        "resolved_by": "admin",
    },
    {
        "title": "Permission denied error when editing team documents",
        "description": "Team lead added me to 'Editors' group but I still can't edit documents. Other editors can edit fine. Error message says 'Permission Denied for resource'.",
        "category": "account",
        "priority": "medium",
        "impact": "medium",
        "resolution": "User had inherited 'Viewer' role from default team policy. New role wasn't overriding old permissions due to role precedence bug. Admin manually cleared old role. Could edit after 2-minute cache refresh.",
        "status": "resolved",
        "resolved_by": "admin",
    },
    {
        "title": "Notifications disabled for important alerts",
        "description": "I'm subscribed to email alerts for critical issues but stopped receiving them 3 days ago. No settings changed on my end. Other notification types still work (reminders, updates).",
        "category": "general",
        "priority": "high",
        "impact": "medium",
        "resolution": "Notification service had a bug filtering by alert severity after system update. Queue had 50,000 unprocessed messages. Restarted notificiation service and reprocessed queue. Issue won't recur after patch deployed.",
        "status": "resolved",
        "resolved_by": "admin",
    },
    {
        "title": "Unable to upload files larger than 10MB",
        "description": "Trying to upload a 25MB video file through the web interface. Get error 'File too large'. But according to docs, limit should be 1GB.",
        "category": "api",
        "priority": "medium",
        "impact": "medium",
        "resolution": "Nginx reverse proxy had hardcoded 10MB limit that wasn't documented. Updated nginx client_max_body_size to 1GB to match application setting. Users can now upload large files.",
        "status": "resolved",
        "resolved_by": "admin",
    },
    {
        "title": "Search returns no results for special characters in queries",
        "description": "Searching for 'C++' returns no results even though we have many C++ tutorials. But searching 'csharp' works fine. Special characters seem to be the issue.",
        "category": "general",
        "priority": "medium",
        "impact": "low",
        "resolution": "Search indexer was stripping special characters before storing them. Reconfigured Elasticsearch analyzer to preserve special chars. Full reindex took 2 hours. Searches now match documents with C++, C#, etc.",
        "status": "resolved",
        "resolved_by": "admin",
    },
]


def add_quality_tickets_to_db(db):
    """
    Add high-quality seed tickets to database for learning.
    Only adds if tickets don't already exist (idempotent).
    """
    from app.db.database import Ticket
    from datetime import datetime, timedelta
    
    # Check if tickets already seeded
    existing_count = db.query(Ticket).filter(
        Ticket.title.in_([t["title"] for t in QUALITY_TICKETS])
    ).count()
    
    if existing_count > 0:
        print(f"✓ Quality tickets already seeded ({existing_count} found)")
        return
    
    # Add tickets with varied creation times
    now = datetime.utcnow()
    for i, ticket_data in enumerate(QUALITY_TICKETS):
        # Stagger creation times over past 30 days
        created_at = now - timedelta(days=30 - (i * 3))
        
        ticket = Ticket(
            title=ticket_data["title"],
            description=ticket_data["description"],
            category=ticket_data["category"],
            priority=ticket_data["priority"],
            impact=ticket_data["impact"],
            status=ticket_data["status"],
            resolution=ticket_data.get("resolution"),
            confidence_score=0.75 if ticket_data["status"] == "resolved" else 0.60,  # Good confidence for quality tickets
            decision="auto_resolve" if ticket_data["status"] == "resolved" else "human_review",
            created_at=created_at,
            resolved_at=created_at + timedelta(hours=4, minutes=30) if ticket_data["status"] == "resolved" else None,
        )
        db.add(ticket)
    
    db.commit()
    print(f"✓ Added {len(QUALITY_TICKETS)} high-quality seed tickets")
    
    return len(QUALITY_TICKETS)
