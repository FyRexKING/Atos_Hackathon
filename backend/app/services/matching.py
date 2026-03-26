"""
Hybrid Matching Service - Combines semantic (Gemini embeddings) and keyword (TF-IDF) matching.
Finds similar historical tickets and relevant KB articles.
"""

from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from app.db.database import Ticket, KnowledgeBase
from datetime import datetime, timedelta
import google.generativeai as genai
import os
import logging
import time
from functools import lru_cache
from hashlib import md5

logger = logging.getLogger(__name__)


class HybridMatchingService:
    """
    Combines semantic similarity (Gemini) with keyword-based similarity (TF-IDF).
    Finds similar historical tickets and relevant KB articles.
    """

    def __init__(self):
        """Initialize with Gemini API if available, otherwise use keyword-only matching."""
        api_key = os.getenv("GEMINI_API_KEY")
        self.use_semantic = False
        self.rate_limited = False
        self.rate_limit_until = None
        self.semantic_cache = {}  # Cache embeddings to avoid repeated calls
        self.request_count = 0
        self.max_requests_per_minute = 60  # Free tier limit
        self.request_timestamps = []
        
        if api_key:
            try:
                genai.configure(api_key=api_key)
                # Test the API with a simple embedding
                test_response = genai.embed_content(
                    model="models/gemini-embedding-001",
                    content="test"
                )
                if test_response and 'embedding' in test_response:
                    self.use_semantic = True
                    self.model = "models/gemini-embedding-001"
                    logger.info("✅ Gemini API configured successfully - semantic matching ENABLED")
                    print("✅ Gemini API configured successfully - semantic matching ENABLED")
                else:
                    logger.warning("⚠️  Gemini API test failed - using keyword-only matching")
                    print("⚠️  Gemini API test failed - using keyword-only matching")
                    self.use_semantic = False
            except Exception as e:
                logger.error(f"❌ Gemini API initialization error: {str(e)}")
                print(f"❌ Gemini API initialization error: {str(e)}")
                print("⚠️  Using keyword-only matching")
                self.use_semantic = False
        else:
            logger.warning("⚠️  GEMINI_API_KEY not set - using keyword-only matching")
            print("⚠️  GEMINI_API_KEY not set - using keyword-only matching")

    def _check_rate_limit(self) -> bool:
        """Check if we've hit rate limit."""
        if self.rate_limited:
            if datetime.utcnow() < self.rate_limit_until:
                return True
            else:
                self.rate_limited = False
                self.rate_limit_until = None
                logger.info("✅ Rate limit recovery - semantic matching re-enabled")
        return False

    def _handle_rate_limit(self, wait_minutes: int = 1):
        """Handle rate limiting by backing off."""
        self.rate_limited = True
        self.rate_limit_until = datetime.utcnow() + timedelta(minutes=wait_minutes)
        logger.warning(f"⚠️  Rate limited - falling back to keyword-only for {wait_minutes} minute(s)")
        print(f"⚠️  Gemini API rate limited - using keyword-only matching for {wait_minutes}m")

    def get_semantic_embedding(self, text: str) -> List[float]:
        """Get semantic embedding from Gemini with caching and rate limit handling."""
        if not self.use_semantic or self._check_rate_limit():
            return None
        
        # Check cache first
        text_hash = md5(text.encode()).hexdigest()
        if text_hash in self.semantic_cache:
            return self.semantic_cache[text_hash]
            
        try:
            response = genai.embed_content(
                model=self.model,
                content=text
            )
            embedding = response['embedding']
            self.semantic_cache[text_hash] = embedding  # Cache for future use
            return embedding
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "Too Many Requests" in error_str:
                logger.warning("❌ Gemini API rate limit hit (429)")
                self._handle_rate_limit(wait_minutes=1)
            elif "403" in error_str or "Forbidden" in error_str:
                logger.error("❌ Gemini API forbidden - check API key")
                self.use_semantic = False
            else:
                logger.error(f"Gemini embedding error: {error_str}")
            return None

    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity using cosine distance of embeddings.
        Returns 0-1 score. Falls back to 0 if Gemini not available or rate limited.
        """
        if not self.use_semantic or self._check_rate_limit():
            return 0.0  # Skip semantic if disabled or rate limited
            
        try:
            emb1 = self.get_semantic_embedding(text1)
            emb2 = self.get_semantic_embedding(text2)
            
            if emb1 is None or emb2 is None:
                return 0.0
            
            similarity = cosine_similarity(
                [emb1],
                [emb2]
            )[0][0]
            return float(similarity)
        except Exception as e:
            logger.error(f"Semantic similarity calculation error: {str(e)}")
            return 0.0

    def calculate_keyword_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate keyword similarity using TF-IDF cosine similarity.
        Returns 0-1 score.
        """
        try:
            vectorizer = TfidfVectorizer(
                lowercase=True,
                stop_words='english',
                max_features=100
            )
            
            # Create TF-IDF vectors
            vectors = vectorizer.fit_transform([text1, text2])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(vectors[0], vectors[1])[0][0]
            return float(similarity)
        except Exception as e:
            print(f"Error in keyword similarity: {str(e)}")
            return 0.0

    def calculate_hybrid_similarity(self, text1: str, text2: str, 
                                  semantic_weight: float = 0.6,
                                  keyword_weight: float = 0.4) -> float:
        """
        Calculate hybrid similarity: 60% semantic, 40% keyword.
        Falls back to pure keyword when semantic unavailable.
        Returns 0-1 score where 1 is perfect match.
        """
        if not self.use_semantic:
            # Use pure keyword matching when semantic unavailable
            return self.calculate_keyword_similarity(text1, text2)
        
        semantic = self.calculate_semantic_similarity(text1, text2)
        keyword = self.calculate_keyword_similarity(text1, text2)
        
        # Log the detailed scoring for debugging
        logger.debug(f"Hybrid similarity - Semantic: {semantic:.3f}, Keyword: {keyword:.3f}")
        
        hybrid = (semantic * semantic_weight) + (keyword * keyword_weight)
        return min(1.0, max(0.0, hybrid))  # Clamp to 0-1

    def find_similar_historical_tickets(
        self,
        db: Session,
        ticket_title: str,
        ticket_description: str,
        limit: int = 5,
        days_back: int = 90
    ) -> List[Dict]:
        """
        Find similar historical resolved tickets.
        Only considers resolved tickets from last 90 days.
        Returns top N matches with similarity scores.
        """
        try:
            matching_type = "HYBRID (Semantic + Keyword)" if self.use_semantic else "KEYWORD (TF-IDF only)"
            logger.info(f"🔍 Finding similar tickets using: {matching_type}")
            
            # Get resolved tickets from last 90 days
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            historical_tickets = db.query(Ticket).filter(
                Ticket.status == "resolved",
                Ticket.resolved_at >= cutoff_date,
                Ticket.resolution.isnot(None)
            ).all()

            if not historical_tickets:
                logger.info("No historical resolved tickets found")
                return []

            combined_query = f"{ticket_title} {ticket_description}"
            matches = []

            for hist_ticket in historical_tickets:
                hist_combined = f"{hist_ticket.title} {hist_ticket.description}"
                
                # Calculate hybrid similarity
                similarity = self.calculate_hybrid_similarity(
                    combined_query,
                    hist_combined,
                    semantic_weight=0.6,
                    keyword_weight=0.4
                )

                if similarity > 0.3:  # Only return if above threshold
                    matches.append({
                        "ticket_id": hist_ticket.id,
                        "title": hist_ticket.title,
                        "similarity_score": round(similarity, 3),
                        "category": hist_ticket.category,
                        "priority": hist_ticket.priority,
                        "status": hist_ticket.status,  # Added missing status field
                        "resolution": hist_ticket.resolution,
                        "resolved_date": hist_ticket.resolved_at.isoformat() if hist_ticket.resolved_at else None
                    })

            # Sort by similarity score and return top N
            matches = sorted(matches, key=lambda x: x["similarity_score"], reverse=True)
            found_count = len(matches[:limit])
            logger.info(f"✅ Found {found_count} similar tickets (showing top {min(found_count, limit)})")
            return matches[:limit]

        except Exception as e:
            logger.error(f"Error finding similar tickets: {str(e)}")
            return []

    def find_relevant_kb_articles(
        self,
        db: Session,
        ticket_title: str,
        ticket_description: str,
        ticket_category: str,
        limit: int = 5
    ) -> List[Dict]:
        """
        Find relevant KB articles using hybrid matching.
        Considers category match and semantic/keyword similarity.
        Returns top N KB articles with relevance scores.
        """
        try:
            matching_type = "HYBRID (Semantic + Keyword)" if self.use_semantic else "KEYWORD (TF-IDF only)"
            logger.info(f"📚 Finding KB articles using: {matching_type}")
            
            # Get active KB articles
            kb_articles = db.query(KnowledgeBase).filter(
                KnowledgeBase.is_active == True
            ).all()

            if not kb_articles:
                logger.info("No active KB articles found")
                return []

            combined_query = f"{ticket_title} {ticket_description}"
            matches = []

            for article in kb_articles:
                # Combine article title and content for matching
                article_text = f"{article.title} {article.content}"
                
                # Calculate hybrid similarity
                similarity = self.calculate_hybrid_similarity(
                    combined_query,
                    article_text,
                    semantic_weight=0.6,
                    keyword_weight=0.4
                )

                # Boost score if category matches
                category_boost = 0.1 if article.category == ticket_category else 0.0
                final_score = min(1.0, similarity + category_boost)

                if final_score > 0.3:  # Only return if above threshold
                    matches.append({
                        "kb_id": article.id,
                        "title": article.title,
                        "relevance_score": round(final_score, 3),
                        "category": article.category,
                        "tags": article.tags or [],
                        "solution_steps": article.solution_steps or [],
                        "url": f"/kb/{article.id}"  # Frontend can link to KB article
                    })

            # Sort by relevance score and return top N
            matches = sorted(matches, key=lambda x: x["relevance_score"], reverse=True)
            found_count = len(matches[:limit])
            logger.info(f"✅ Found {found_count} relevant KB articles (showing top {min(found_count, limit)})")
            return matches[:limit]

        except Exception as e:
            logger.error(f"Error finding KB articles: {str(e)}")
            return []

    def get_full_recommendations(
        self,
        db: Session,
        ticket_title: str,
        ticket_description: str,
        ticket_category: str
    ) -> Dict:
        """
        Get comprehensive recommendations including:
        - Similar historical tickets
        - Relevant KB articles
        Returns dict with all recommendations and metadata.
        """
        historical_matches = self.find_similar_historical_tickets(
            db, ticket_title, ticket_description, limit=3
        )
        
        kb_matches = self.find_relevant_kb_articles(
            db, ticket_title, ticket_description, ticket_category, limit=3
        )

        return {
            "historical_tickets": historical_matches,
            "kb_articles": kb_matches,
            "has_historical_match": len(historical_matches) > 0,
            "has_kb_match": len(kb_matches) > 0,
            "is_new_issue_type": len(historical_matches) == 0 and len(kb_matches) == 0
        }
