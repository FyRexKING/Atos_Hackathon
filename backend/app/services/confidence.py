"""
Confidence scoring service.
Calculates confidence score based on similarity, category match, and impact.
"""
from app.schemas.ticket import ConfidenceOutput, ClassificationOutput, SimilarityOutput


class ConfidenceService:
    """Service for calculating ticket resolution confidence scores."""

    @staticmethod
    def calculate_confidence(
        classification: ClassificationOutput,
        similarity: SimilarityOutput
    ) -> ConfidenceOutput:
        """
        Calculate confidence score for ticket resolution.

        Formula:
        confidence = similarity_score * 0.5 + category_match * 0.3 + (1 - impact_penalty) * 0.2

        Impact penalty:
        - low = 0
        - medium = 0.1
        - high = 0.3

        Args:
            classification: Classification output
            similarity: Similarity search output

        Returns:
            ConfidenceOutput with calculated scores
        """

        # Get similarity score (average of top similar tickets)
        similarity_score = similarity.avg_similarity

        # Calculate category match score
        # If we found similar tickets with matching category, boost the score
        category_match = 0.0
        if similarity.similar_tickets:
            matching_categories = sum(
                1 for ticket in similarity.similar_tickets
                if ticket.category == classification.category
            )
            category_match = matching_categories / len(similarity.similar_tickets)

        # Calculate impact penalty
        impact_penalty = ConfidenceService._get_impact_penalty(classification.impact)

        # Apply weights
        weights = {
            "similarity": 0.5,
            "category_match": 0.3,
            "impact_penalty": 0.2
        }

        confidence_score = (
            similarity_score * weights["similarity"] +
            category_match * weights["category_match"] +
            (1 - impact_penalty) * weights["impact_penalty"]
        )

        # Clamp score between 0 and 1
        confidence_score = max(0.0, min(1.0, confidence_score))

        return ConfidenceOutput(
            score=float(confidence_score),
            similarity_weight=float(similarity_score * weights["similarity"]),
            category_match_weight=float(category_match * weights["category_match"]),
            impact_penalty_weight=float((1 - impact_penalty) * weights["impact_penalty"])
        )

    @staticmethod
    def _get_impact_penalty(impact: str) -> float:
        """
        Get impact penalty factor.

        Args:
            impact: Impact level (low, medium, high)

        Returns:
            Penalty factor (0-0.3)
        """
        penalties = {
            "low": 0.0,
            "medium": 0.1,
            "high": 0.3
        }
        return penalties.get(impact.lower(), 0.1)
