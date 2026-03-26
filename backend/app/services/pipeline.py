"""
Main processing pipeline for ticket classification and resolution.
Orchestrates all services: classification, similarity, confidence, resolution, and recommendations.
Uses LangGraph for state management and conditional flow.
"""
from typing import TypedDict, Optional, List
from sqlalchemy.orm import Session
from langgraph.graph import StateGraph, END
from app.schemas.ticket import (
    TicketInput,
    TicketResponse,
    ClassificationOutput,
    SimilarityOutput,
    ConfidenceOutput,
    ResolutionOutput,
    SimilarTicket
)
from app.services.classifier import ClassificationService
from app.services.matching import HybridMatchingService
from app.services.confidence import ConfidenceService
from app.services.resolver import ResolverService
from app.services.recommendations import RecommendationsEngine
from app.db.database import Ticket
from datetime import datetime


class TicketState(TypedDict):
    """State schema for the ticket processing graph."""
    ticket_input: TicketInput
    db: Session
    current_user: Optional[any]  # The authenticated user
    classification: Optional[ClassificationOutput]
    similarity: Optional[SimilarityOutput]
    kb_articles: Optional[List[dict]]  # KB articles from hybrid matching
    is_new_issue_type: Optional[bool]  # Whether this is a new/novel issue
    confidence: Optional[ConfidenceOutput]
    decision: Optional[str]
    resolution: Optional[ResolutionOutput]
    ticket_db: Optional[Ticket]
    status: Optional[str]
    explanation: Optional[str]
    is_high_impact: Optional[bool]  # Flag for critical issues
    recommendations: Optional[dict]  # AI recommendations for escalation


class TicketPipeline:
    """
    Main pipeline for processing support tickets using LangGraph.
    Handles classification, similarity search, confidence scoring, and resolution.
    """

    def __init__(self):
        """Initialize pipeline with all services and build the graph."""
        self.classifier = ClassificationService()
        self.hybrid_matching = HybridMatchingService()  # FIXED: Use HybridMatchingService
        self.confidence = ConfidenceService()
        self.resolver = ResolverService()
        self.recommendations = RecommendationsEngine()

        # Build the LangGraph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(TicketState)

        # Add nodes
        workflow.add_node("classify_ticket", self._classify_ticket)
        workflow.add_node("search_similar", self._search_similar)
        workflow.add_node("calculate_confidence", self._calculate_confidence)
        workflow.add_node("make_decision", self._make_decision)
        workflow.add_node("generate_recommendations", self._generate_recommendations)
        workflow.add_node("generate_resolution", self._generate_resolution)
        workflow.add_node("store_ticket", self._store_ticket)

        # Define the flow
        workflow.set_entry_point("classify_ticket")
        workflow.add_edge("classify_ticket", "search_similar")
        workflow.add_edge("search_similar", "calculate_confidence")
        workflow.add_edge("calculate_confidence", "make_decision")

        # Conditional edges based on decision
        workflow.add_conditional_edges(
            "make_decision",
            self._route_decision,
            {
                "auto_resolve": "generate_resolution",
                "human_review": "generate_recommendations",
            }
        )

        workflow.add_edge("generate_recommendations", "store_ticket")
        workflow.add_edge("generate_resolution", "store_ticket")
        workflow.add_edge("store_ticket", END)

        return workflow.compile()

    def process_ticket(
        self,
        ticket_input: TicketInput,
        db: Session,
        current_user
    ) -> TicketResponse:
        """
        Process a support ticket through the LangGraph pipeline.

        Args:
            ticket_input: Input ticket with title and description
            db: Database session
            current_user: The authenticated user creating the ticket

        Returns:
            TicketResponse with full processing results
        """
        # Initialize state
        initial_state: TicketState = {
            "ticket_input": ticket_input,
            "db": db,
            "current_user": current_user,
            "classification": None,
            "similarity": None,
            "confidence": None,
            "decision": None,
            "resolution": None,
            "ticket_db": None,
            "status": None,
            "explanation": None,
            "is_high_impact": False,
            "recommendations": None,
        }

        # Run the graph
        final_state = self.graph.invoke(initial_state)

        # Generate explanation
        explanation = self._generate_explanation(final_state)

        # Build response
        response = TicketResponse(
            ticket_id=final_state.get("ticket_db").id if final_state.get("ticket_db") else None,
            title=ticket_input.title,
            classification=final_state["classification"],
            similarity=final_state["similarity"],
            confidence=final_state["confidence"],
            decision=final_state["decision"],
            explanation=explanation,
            resolution=final_state.get("resolution"),
            status=final_state["status"]
        )

        return response

    # Node functions for LangGraph
    def _classify_ticket(self, state: TicketState) -> TicketState:
        """Classify the ticket using the classifier service."""
        classification = self.classifier.classify(
            state["ticket_input"].title,
            state["ticket_input"].description
        )
        return {**state, "classification": classification}

    def _search_similar(self, state: TicketState) -> TicketState:
        """FIXED: Search for similar tickets using HybridMatchingService (semantic + keyword)."""
        try:
            matching_results = self.hybrid_matching.get_full_recommendations(
                state["db"],
                state["ticket_input"].title,
                state["ticket_input"].description,
                state["classification"].category
            )
            # Convert to SimilarityOutput format for backwards compatibility
            from app.schemas.ticket import SimilarityOutput, SimilarTicket
            
            similar_tickets = []
            total_score = 0.0
            
            for ticket in matching_results.get("historical_tickets", []):
                similar_tickets.append(SimilarTicket(
                    ticket_id=ticket["ticket_id"],
                    title=ticket["title"],
                    category=ticket["category"],
                    similarity_score=ticket["similarity_score"],
                    status=ticket["status"]
                ))
                total_score += ticket["similarity_score"]
            
            avg_similarity = total_score / len(similar_tickets) if similar_tickets else 0.0
            
            similarity = SimilarityOutput(
                similar_tickets=similar_tickets,
                avg_similarity=avg_similarity
            )
            
            state["similarity"] = similarity
            state["kb_articles"] = matching_results.get("kb_articles", [])
            state["is_new_issue_type"] = matching_results.get("is_new_issue_type", False)
        except Exception as e:
            print(f"Hybrid matching error: {e}")
            state["similarity"] = SimilarityOutput(similar_tickets=[], avg_similarity=0.0)
            state["kb_articles"] = []
            state["is_new_issue_type"] = True
        
        return state

    def _calculate_confidence(self, state: TicketState) -> TicketState:
        """FIXED: Calculate confidence with proper boost from matching results."""
        from app.schemas.ticket import ConfidenceOutput
        
        # Base confidence from category classification
        base_score = 0.60
        
        # Boost from historical ticket matches (up to +0.20)
        match_boost = 0.0
        if state["similarity"].similar_tickets:
            best_match = state["similarity"].similar_tickets[0]
            match_boost = min(0.20, best_match.similarity_score * 0.25)
        
        # Boost from KB article matches (up to +0.15)
        kb_boost = 0.0
        if state.get("kb_articles"):
            best_kb = state["kb_articles"][0]
            kb_boost = min(0.15, best_kb.get("relevance_score", 0) * 0.20)
        
        # Penalty for new issue type (-0.10)
        new_issue_penalty = 0.10 if state.get("is_new_issue_type") else 0.0
        
        # Penalty for high impact (-0.15)
        impact_penalty = 0.15 if state["classification"].impact == "high" else 0.0
        
        # Final confidence calculation
        final_score = base_score + match_boost + kb_boost - new_issue_penalty - impact_penalty
        final_score = max(0.0, min(1.0, final_score))  # Clamp to [0, 1]
        
        confidence = ConfidenceOutput(
            score=float(final_score),
            similarity_weight=float(match_boost),
            category_match_weight=float(kb_boost),
            impact_penalty_weight=float(impact_penalty)
        )
        return {**state, "confidence": confidence}

    def _make_decision(self, state: TicketState) -> TicketState:
        """Make decision based on classification and confidence."""
        decision, status, is_high_impact = self._make_decision_logic(
            state["classification"],
            state["confidence"],
            state["ticket_input"]
        )
        return {**state, "decision": decision, "status": status, "is_high_impact": is_high_impact}

    def _generate_resolution(self, state: TicketState) -> TicketState:
        """Generate resolution for auto-resolve tickets."""
        resolution = self.resolver.generate_resolution(
            state["ticket_input"].title,
            state["ticket_input"].description,
            state["classification"].category,
            state["classification"].priority
        )
        return {**state, "resolution": resolution}

    def _generate_recommendations(self, state: TicketState) -> TicketState:
        """
        Generate comprehensive recommendations for human review tickets.
        Includes action plans, KB articles, similar tickets, and team recommendations.
        """
        recommendations = self.recommendations.generate_action_plan(
            db=state["db"],
            ticket_title=state["ticket_input"].title,
            ticket_description=state["ticket_input"].description,
            ticket_category=state["classification"].category,
            confidence_score=state["confidence"].score,
            is_high_impact=state["is_high_impact"]
        )
        return {**state, "recommendations": recommendations}

    def _store_ticket(self, state: TicketState) -> TicketState:
        """Store ticket in database for human review."""
        ticket_db = self._store_ticket_db(
            state["ticket_input"],
            state["classification"],
            state["similarity"],
            state["confidence"],
            state["decision"],
            state["db"],
            state["current_user"],
            state.get("recommendations")  # Pass recommendations if available
        )
        return {**state, "ticket_db": ticket_db}

    def _route_decision(self, state: TicketState) -> str:
        """Route to next node based on decision."""
        return state["decision"]

    # Helper methods
    def _make_decision_logic(
        self,
        classification: ClassificationOutput,
        confidence: ConfidenceOutput,
        ticket_input: TicketInput
    ) -> tuple[str, str, bool]:
        """
        Make decision on ticket resolution with policy gates and high-impact detection.

        Policy Rules:
        1. If HIGH-IMPACT (system critical, multiple customers, etc.) → ALWAYS human_review + escalate
        2. If priority == high OR impact == high → ALWAYS human_review (no exceptions)
        3. If confidence < 0.80 → human_review (threshold enforcement)
        4. If confidence >= 0.80 AND low/medium priority AND not high-impact → auto_resolve
        5. Default → human_review

        High-Impact Detection:
        - Keywords indicating system down: "down", "offline", "unavailable", "critical", "outage"
        - Multiple affected: "multiple", "everyone", "all users", "many"
        - Revenue impact: "payment", "billing", "transaction" + "failed", "blocked"

        Args:
            classification: Classification output
            confidence: Confidence scoring output
            ticket_input: Original ticket input

        Returns:
            Tuple of (decision, status, is_high_impact) where:
            - decision: "auto_resolve" or "human_review"
            - status: "resolved" or "pending_review"
            - is_high_impact: Whether this is a critical ticket
        """
        
        # Detect high-impact tickets
        is_high_impact = self._detect_high_impact(ticket_input, classification)
        
        # Policy Rule 1: HIGH-IMPACT always escalates
        if is_high_impact:
            return "human_review", "pending_review", True

        # Policy Rule 2: CRITICAL - High priority or high impact always requires human review
        if classification.priority == "high" or classification.impact == "high":
            return "human_review", "pending_review", False

        # Policy Rule 3: Confidence threshold enforcement (0.80 minimum for auto-resolve)
        if confidence.score < 0.80:
            return "human_review", "pending_review", False

        # Policy Rule 4: Low/medium priority + confidence >= 0.80 → auto-resolve
        if confidence.score >= 0.80:
            return "auto_resolve", "resolved", False

        # Fallback to human review
        return "human_review", "pending_review", False

    def _detect_high_impact(
        self,
        ticket_input: TicketInput,
        classification: ClassificationOutput
    ) -> bool:
        """
        Detect if this is a high-impact critical ticket.
        Examples: system outage, multiple customers affected, revenue-impacting.
        """
        combined_text = f"{ticket_input.title} {ticket_input.description}".lower()
        
        # Critical system indicators
        system_down_keywords = ["system down", "offline", "unavailable", "outage", "critical", "emergency", "disaster", "no access"]
        if any(keyword in combined_text for keyword in system_down_keywords):
            return True
        
        # Multiple customers affected
        multi_customer_keywords = ["multiple users", "all customers", "everyone", "many users", "widespread", "global"]
        if any(keyword in combined_text for keyword in multi_customer_keywords):
            return True
        
        # Revenue/billing impact
        if "payment" in combined_text or "billing" in combined_text or "transaction" in combined_text:
            revenue_keywords = ["failed", "blocked", "stuck", "not processing", "error"]
            if any(keyword in combined_text for keyword in revenue_keywords):
                return True
        
        # Data loss/security
        if "data" in combined_text and ("lost" in combined_text or "deleted" in combined_text or "breach" in combined_text):
            return True
        
        return False

    def _generate_explanation(self, state: TicketState) -> str:
        """
        Generate human-readable explanation of the decision.

        Args:
            state: Final state after processing

        Returns:
            Explanation string
        """
        classification = state["classification"]
        similarity = state["similarity"]
        confidence = state["confidence"]
        decision = state["decision"]

        parts = []

        # Add similarity info
        if similarity.similar_tickets:
            top_match = similarity.similar_tickets[0]
            parts.append(
                f"Matched similar ticket #{top_match.ticket_id} "
                f"(score: {top_match.similarity_score:.2f})"
            )
        else:
            parts.append("No similar tickets found")

        # Add classification info
        parts.append(
            f"Category: {classification.category}, "
            f"Priority: {classification.priority}, "
            f"Impact: {classification.impact}"
        )

        # Add confidence info
        parts.append(f"Confidence: {confidence.score:.2f}")

        # Add decision info
        if decision == "auto_resolve":
            parts.append("Auto-resolved due to high confidence")
        else:
            parts.append("Requires human review")

        return " | ".join(parts)

    def _generate_explanation_from_data(
        self,
        classification: ClassificationOutput,
        similarity: SimilarityOutput,
        confidence: ConfidenceOutput,
        decision: str
    ) -> str:
        """
        Generate human-readable explanation from individual data components.

        Args:
            classification: Classification output
            similarity: Similarity search results
            confidence: Confidence scoring
            decision: Decision made

        Returns:
            Explanation string
        """
        parts = []

        # Add similarity info
        if similarity.similar_tickets:
            top_match = similarity.similar_tickets[0]
            parts.append(
                f"Matched similar ticket #{top_match.ticket_id} "
                f"(score: {top_match.similarity_score:.2f})"
            )
        else:
            parts.append("No similar tickets found")

        # Add classification info
        parts.append(
            f"Category: {classification.category}, "
            f"Priority: {classification.priority}, "
            f"Impact: {classification.impact}"
        )

        # Add confidence info
        parts.append(f"Confidence: {confidence.score:.2f}")

        # Add decision info
        if decision == "auto_resolve":
            parts.append("Auto-resolved due to high confidence")
        else:
            parts.append("Requires human review")

        return " | ".join(parts)

    def _store_ticket_db(
        self,
        ticket_input: TicketInput,
        classification: ClassificationOutput,
        similarity: SimilarityOutput,
        confidence: ConfidenceOutput,
        decision: str,
        db: Session,
        current_user,
        recommendations: Optional[dict] = None
    ) -> Ticket:
        """Store ticket in database with recommendations if available."""
        # Generate explanation for this ticket
        explanation = self._generate_explanation_from_data(
            classification, similarity, confidence, decision
        )

        ticket = Ticket(
            title=ticket_input.title,
            description=ticket_input.description,
            category=classification.category,
            priority=classification.priority,
            impact=classification.impact,
            confidence_score=confidence.score,
            decision=decision,
            status="resolved" if decision == "auto_resolve" else "pending_review",
            user_id=current_user.id,
            # Store full AI analysis
            ai_explanation=explanation,
            similarity_data={
                "similar_tickets": [
                    {
                        "ticket_id": t.ticket_id,
                        "title": t.title,
                        "category": t.category,
                        "similarity_score": t.similarity_score,
                        "status": t.status
                    } for t in similarity.similar_tickets
                ],
                "avg_similarity": similarity.avg_similarity
            },
            confidence_breakdown={
                "score": confidence.score,
                "similarity_weight": confidence.similarity_weight,
                "category_match_weight": confidence.category_match_weight,
                "impact_penalty_weight": confidence.impact_penalty_weight
            }
        )
        
        # Add recommendations if available (for human review tickets)
        if recommendations:
            # Store as JSON in the ticket for reference
            ticket.similarity_data = {
                **ticket.similarity_data,
                "recommendations": {
                    "action_plan": recommendations.get("action_plan"),
                    "suggested_solutions": recommendations.get("suggested_solutions"),
                    "recommended_team": recommendations.get("recommended_team"),
                    "is_new_issue_type": recommendations.get("is_new_issue_type")
                }
            }
        
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        
        # Save individual recommendations to database
        if recommendations:
            self.recommendations.save_recommendations(db, ticket.id, recommendations)
        
        return ticket
