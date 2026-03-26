"""
Recommendations Engine - Generates comprehensive action plans for support agents.
Combines KB articles, historical tickets, and AI suggestions into step-by-step guides.
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.db.database import Ticket, KnowledgeBase, RecommendedSolution
from app.services.matching import HybridMatchingService
from datetime import datetime
import json


class RecommendationsEngine:
    """
    Generates comprehensive recommendations including:
    - Step-by-step action plans
    - Relevant KB articles with links
    - Similar historical ticket resolutions
    - Suggested solutions ranked by confidence
    """

    def __init__(self):
        self.matching = HybridMatchingService()

    def generate_action_plan(
        self,
        db: Session,
        ticket_title: str,
        ticket_description: str,
        ticket_category: str,
        confidence_score: float,
        is_high_impact: bool = False
    ) -> Dict:
        """
        Generate comprehensive recommendations and action plan for a ticket.
        Returns dict with solutions, steps, and explainability.
        """
        
        # Get all matching data
        recommendations = self.matching.get_full_recommendations(
            db, ticket_title, ticket_description, ticket_category
        )

        # Generate the action plan
        action_plan = self._build_action_plan(
            ticket_title,
            ticket_description,
            ticket_category,
            recommendations,
            is_high_impact
        )

        # Get top solutions ranked by confidence
        suggested_solutions = self._build_suggested_solutions(
            recommendations,
            confidence_score,
            ticket_category
        )

        # Build explainability narrative
        explainability = self._build_explainability(
            ticket_category,
            confidence_score,
            recommendations,
            is_high_impact
        )

        return {
            "confidence_score": round(confidence_score, 3),
            "is_high_impact": is_high_impact,
            "is_new_issue_type": recommendations["is_new_issue_type"],
            "action_plan": action_plan,
            "suggested_solutions": suggested_solutions,
            "explainability": explainability,
            "historical_matches": recommendations["historical_tickets"],
            "kb_articles": recommendations["kb_articles"],
            "recommended_team": self._recommend_team(ticket_category),
            "escalation_required": confidence_score < 0.8 or is_high_impact
        }

    def _build_action_plan(
        self,
        title: str,
        description: str,
        category: str,
        recommendations: Dict,
        is_high_impact: bool
    ) -> Dict:
        """Build step-by-step action plan for the support agent."""
        
        steps = []

        # Step 1: Understand the issue
        steps.append({
            "step": 1,
            "action": "Understand the Issue",
            "details": f"Ticket: {title}\n{description}",
            "priority": "critical"
        })

        # Step 2: Check for similar resolved tickets
        if recommendations["historical_tickets"]:
            top_match = recommendations["historical_tickets"][0]
            steps.append({
                "step": 2,
                "action": "Review Similar Historical Ticket",
                "details": f"Similar Ticket #{top_match['ticket_id']}: '{top_match['title']}' (Match: {top_match['similarity_score']*100:.0f}%)\nResolution Applied: {top_match['resolution'][:200]}...",
                "reference_id": top_match["ticket_id"],
                "priority": "high"
            })

        # Step 3: Check KB articles
        if recommendations["kb_articles"]:
            top_kb = recommendations["kb_articles"][0]
            steps.append({
                "step": 3,
                "action": "Review Knowledge Base Articles",
                "details": f"Most Relevant: '{top_kb['title']}' (Relevance: {top_kb['relevance_score']*100:.0f}%)\n\nSolution Steps:\n" + "\n".join([f"  {i+1}. {s}" for i, s in enumerate(top_kb['solution_steps'][:3])]),
                "reference_id": top_kb["kb_id"],
                "priority": "high"
            })

        # Step 4: If new issue type
        if recommendations["is_new_issue_type"]:
            steps.append({
                "step": len(steps) + 1,
                "action": "FLAG: New Issue Type Detected",
                "details": "This issue doesn't match historical tickets or KB articles. Document the resolution for future reference.",
                "priority": "critical"
            })

        # Step 5: Categorize and prioritize
        steps.append({
            "step": len(steps) + 1,
            "action": "Categorize Issue",
            "details": f"Category: {category}\nEscalation Required: Yes (confidence < 80% threshold)\nHigh Impact: {'Yes' if is_high_impact else 'No'}",
            "priority": "high"
        })

        # Step 6: Create resolution
        steps.append({
            "step": len(steps) + 1,
            "action": "Create Resolution",
            "details": "Based on the above research, create a detailed response with:\n1. Root cause explanation\n2. Step-by-step solution\n3. Prevention tips\n4. Follow-up support offer",
            "priority": "critical"
        })

        return {
            "total_steps": len(steps),
            "steps": steps,
            "estimated_time": "5-15 minutes",
            "difficulty": "Medium" if recommendations["is_new_issue_type"] else "Low"
        }

    def _build_suggested_solutions(
        self,
        recommendations: Dict,
        confidence_score: float,
        category: str = None
    ) -> List[Dict]:
        """Build ranked list of suggested solutions."""
        
        solutions = []

        # Rank 1: Historical ticket solution (if exists)
        if recommendations["historical_tickets"]:
            for i, ticket in enumerate(recommendations["historical_tickets"][:3]):
                solutions.append({
                    "rank": len(solutions) + 1,
                    "type": "historical_match",
                    "title": f"Similar Ticket Resolution (Ticket #{ticket['ticket_id']})",
                    "confidence": round(ticket["similarity_score"], 3),
                    "solution": f"Similar issue was resolved as: {ticket['resolution'][:200]}...",
                    "action_steps": [
                        f"1. Apply resolution from Ticket #{ticket['ticket_id']}",
                        "2. Adapt for current ticket specifics",
                        "3. Test with customer",
                        "4. Document any variations"
                    ],
                    "source": f"Historical Ticket #{ticket['ticket_id']}"
                })

        # Rank 2: KB article solutions
        if recommendations["kb_articles"]:
            for i, article in enumerate(recommendations["kb_articles"][:3]):
                solutions.append({
                    "rank": len(solutions) + 1,
                    "type": "kb_article",
                    "title": f"KB Article: {article['title']}",
                    "confidence": round(article["relevance_score"], 3),
                    "solution": f"Follow the documented solution in KB article #{article['kb_id']}",
                    "action_steps": article["solution_steps"][:5],  # Top 5 steps
                    "source": f"KB Article #{article['kb_id']}"
                })

        # Always provide a category-based AI suggestion
        general_suggestion = self._generate_category_suggestion(category, confidence_score)
        if general_suggestion:
            solutions.append(general_suggestion)

        return sorted(solutions, key=lambda x: x["confidence"], reverse=True)

    def _build_explainability(
        self,
        category: str,
        confidence_score: float,
        recommendations: Dict,
        is_high_impact: bool
    ) -> Dict:
        """Build explainability narrative showing AI reasoning."""
        
        facts = []
        
        # Fact 1: Classification confidence
        facts.append({
            "fact": "Classification Confidence",
            "value": f"{confidence_score*100:.0f}%",
            "explanation": "Based on AI analysis of ticket title, description, and category."
        })

        # Fact 2: Auto-resolution eligibility
        can_auto_resolve = confidence_score >= 0.8 and not is_high_impact
        facts.append({
            "fact": "Auto-Resolution Eligible",
            "value": "Yes" if can_auto_resolve else "No",
            "explanation": f"Confidence {'≥ 80%' if confidence_score >= 0.8 else '< 80%'}" + 
                        (f" and High Impact: {is_high_impact}" if is_high_impact else "")
        })

        # Fact 3: Similar historical tickets
        if recommendations["historical_tickets"]:
            facts.append({
                "fact": "Similar Historical Tickets Found",
                "value": f"{len(recommendations['historical_tickets'])} match(es)",
                "explanation": f"Best match: {recommendations['historical_tickets'][0]['title']} ({recommendations['historical_tickets'][0]['similarity_score']*100:.0f}% similar)"
            })
        else:
            facts.append({
                "fact": "Similar Historical Tickets",
                "value": "None found",
                "explanation": "This issue doesn't match previously resolved tickets."
            })

        # Fact 4: KB article coverage
        if recommendations["kb_articles"]:
            facts.append({
                "fact": "Relevant KB Articles Found",
                "value": f"{len(recommendations['kb_articles'])} article(s)",
                "explanation": f"Best match: {recommendations['kb_articles'][0]['title']} ({recommendations['kb_articles'][0]['relevance_score']*100:.0f}% relevant)"
            })
        else:
            facts.append({
                "fact": "KB Coverage",
                "value": "No existing articles",
                "explanation": "Knowledge base doesn't have documented solution for this issue type."
            })

        # Fact 5: High-impact status
        facts.append({
            "fact": "High-Impact Ticket",
            "value": "Yes" if is_high_impact else "No",
            "explanation": "Escalated for human review due to system criticality or customer impact."
        })

        return {
            "summary": self._build_explainability_summary(
                confidence_score, is_high_impact, recommendations
            ),
            "facts": facts,
            "reasoning_chain": [
                "1. Analyzed ticket text and metadata",
                "2. Searched historical ticket database",
                "3. Searched knowledge base articles",
                "4. Calculated confidence score",
                "5. Applied escalation rules",
                "6. Generated recommendations"
            ]
        }

    def _build_explainability_summary(
        self,
        confidence_score: float,
        is_high_impact: bool,
        recommendations: Dict
    ) -> str:
        """Build one-sentence explainability summary."""
        
        if is_high_impact:
            return "HIGH-IMPACT TICKET: Automatically escalated due to system criticality or customer value. Requires agent review regardless of confidence score."
        
        if confidence_score >= 0.8:
            if recommendations["has_historical_match"]:
                return f"READY FOR AUTO-RESOLUTION: {confidence_score*100:.0f}% confident. Similar historical ticket found with proven resolution."
            else:
                return f"READY FOR AUTO-RESOLUTION: {confidence_score*100:.0f}% confident based on KB articles and AI analysis."
        
        if confidence_score >= 0.6:
            if recommendations["is_new_issue_type"]:
                return f"ESCALATE WITH CAUTION: {confidence_score*100:.0f}% confident but NEW issue type. Lacks historical precedent. Requires agent judgment."
            else:
                return f"ESCALATE FOR REVIEW: {confidence_score*100:.0f}% confident. Recommend agent verify before applying auto-resolution."
        
        return f"ESCALATE FOR INVESTIGATION: {confidence_score*100:.0f}% confident. Issue is ambiguous or rare. Requires full agent investigation."

    def _generate_category_suggestion(self, category: str, confidence_score: float) -> Dict:
        """Generate general category-based troubleshooting suggestion."""
        
        category_guides = {
            "auth": {
                "title": "Authentication Troubleshooting",
                "solution": "Start with standard auth troubleshooting: verify credentials, check account status, confirm no IP restrictions.",
                "steps": [
                    "1. Verify email and password are correct",
                    "2. Check if account is locked or disabled",
                    "3. Clear browser cache/cookies and retry",
                    "4. Confirm no geographic restrictions applied",
                    "5. Reset password if needed",
                    "6. Check 2FA settings if applicable"
                ]
            },
            "billing": {
                "title": "Billing & Payment Support",
                "solution": "Review payment method, transaction history, and invoice details. Verify billing address and card info.",
                "steps": [
                    "1. Check payment method on file",
                    "2. Review recent transactions",
                    "3. Verify billing address matches payment method",
                    "4. Check for card expiration or limit issues",
                    "5. Review invoice details",
                    "6. Contact payment processor if needed"
                ]
            },
            "infra": {
                "title": "Infrastructure & System Support",
                "solution": "Check system status, server logs, and resource utilization. Verify connectivity and dependencies.",
                "steps": [
                    "1. Check system/service status page",
                    "2. Review server logs for errors",
                    "3. Verify resource utilization (CPU, memory, disk)",
                    "4. Test connectivity to dependencies",
                    "5. Check recent deployments or changes",
                    "6. Restart services if safe to do so"
                ]
            },
            "api": {
                "title": "API & Integration Support",
                "solution": "Verify API credentials, endpoint correctness, request format, and authentication headers.",
                "steps": [
                    "1. Verify API credentials and permissions",
                    "2. Check endpoint URL is correct",
                    "3. Validate request headers and authentication",
                    "4. Review request payload format",
                    "5. Check response status and error messages",
                    "6. Test with Postman or curl"
                ]
            },
            "ui": {
                "title": "User Interface & Frontend Support",
                "solution": "Check browser compatibility, clear cache, verify JavaScript, and test across browsers.",
                "steps": [
                    "1. Clear browser cache and cookies",
                    "2. Try in incognito/private mode",
                    "3. Test in different browser",
                    "4. Check browser console for errors",
                    "5. Verify JavaScript is enabled",
                    "6. Try different device/OS"
                ]
            },
            "general": {
                "title": "General Support",
                "solution": "Gather more information about the issue and apply troubleshooting basics.",
                "steps": [
                    "1. Gather detailed issue description",
                    "2. Identify exact error messages",
                    "3. Check when issue started",
                    "4. Verify no recent changes",
                    "5. Try basic troubleshooting (restart, refresh)",
                    "6. Escalate to specialist if needed"
                ]
            }
        }
        
        guide = category_guides.get(category or "general", category_guides["general"])
        
        return {
            "rank": 999,  # Will be re-ranked after sorting
            "type": "ai_suggestion",
            "title": guide["title"],
            "confidence": round(max(confidence_score * 0.7, 0.5), 3),  # General baseline confidence
            "solution": guide["solution"],
            "action_steps": guide["steps"],
            "source": "AI-Generated Category Guide"
        }

    def _recommend_team(self, category: str) -> str:
        """Recommend which team should handle this ticket."""
        
        team_mapping = {
            "auth": "Account & Security Team",
            "billing": "Billing & Finance Team",
            "infra": "Infrastructure & Systems Team",
            "ui": "Product & UX Team",
            "api": "Engineering & API Team",
            "general": "General Support Team"
        }
        
        return team_mapping.get(category, "General Support Team")

    def save_recommendations(
        self,
        db: Session,
        ticket_id: int,
        recommendations: Dict
    ) -> None:
        """Save recommendations to database for audit trail."""
        
        try:
            # For each suggested solution, create a database record
            for solution in recommendations.get("suggested_solutions", []):
                rec = RecommendedSolution(
                    ticket_id=ticket_id,
                    solution_type=solution["type"],
                    solution_content=solution["solution"],
                    relevance_score=solution["confidence"],
                    action_steps=solution["action_steps"],
                    reference_id=solution.get("reference_id")
                )
                db.add(rec)
            
            db.commit()
        except Exception as e:
            print(f"Error saving recommendations: {str(e)}")
            db.rollback()
