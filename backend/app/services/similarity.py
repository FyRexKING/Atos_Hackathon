"""
Similarity search service using Qdrant vector database.
Finds similar tickets based on embeddings.
"""
import hashlib
import os
from typing import List, Tuple
from app.schemas.ticket import SimilarTicket, SimilarityOutput
from sqlalchemy.orm import Session
from app.db.database import Ticket


class SimilarityService:
    """Service for finding similar tickets using vector embeddings."""

    def __init__(self):
        """Initialize similarity service."""
        self.qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        self.qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        self.collection_name = os.getenv("QDRANT_COLLECTION", "tickets")
        self.embedding_dim = 384  # Dimension for mock embeddings

        # Try to connect to Qdrant, but make it optional for development
        self.qdrant_available = self._check_qdrant_connection()

    def _check_qdrant_connection(self) -> bool:
        """Check if Qdrant is available."""
        try:
            from qdrant_client import QdrantClient
            try:
                client = QdrantClient(host=self.qdrant_host, port=self.qdrant_port)
                client.get_collections()
                return True
            except Exception:
                return False
        except ImportError:
            return False

    def search_similar(self, title: str, description: str, db: Session) -> SimilarityOutput:
        """
        Search for similar tickets using Qdrant or fallback to database search.

        Args:
            title: Ticket title
            description: Ticket description
            db: Database session

        Returns:
            SimilarityOutput with similar tickets and average similarity score
        """
        if self.qdrant_available:
            return self._search_qdrant(title, description, db)
        else:
            return self._search_database(title, description, db)

    def _search_qdrant(self, title: str, description: str, db: Session) -> SimilarityOutput:
        """Search using Qdrant vector database."""
        try:
            from qdrant_client import QdrantClient

            client = QdrantClient(host=self.qdrant_host, port=self.qdrant_port)

            # Generate embedding for query
            query_embedding = self._generate_embedding(title, description)

            # Search for similar vectors
            search_result = client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=3
            )

            similar_tickets = []
            total_score = 0.0

            for hit in search_result:
                ticket_id = hit.id
                score = hit.score

                # Get ticket details from database
                ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
                if ticket:
                    similar_tickets.append(
                        SimilarTicket(
                            ticket_id=ticket.id,
                            title=ticket.title,
                            category=ticket.category,
                            similarity_score=float(score),
                            status=ticket.status
                        )
                    )
                    total_score += score

            avg_similarity = total_score / len(similar_tickets) if similar_tickets else 0.0

            return SimilarityOutput(
                similar_tickets=similar_tickets,
                avg_similarity=float(avg_similarity)
            )

        except Exception as e:
            print(f"Qdrant search failed, falling back to database: {e}")
            return self._search_database(title, description, db)

    def _search_database(self, title: str, description: str, db: Session) -> SimilarityOutput:
        """
        Fallback search using database (original implementation).

        Args:
            title: Ticket title
            description: Ticket description
            db: Database session

        Returns:
            SimilarityOutput with similar tickets
        """
        # Generate embedding for the input ticket
        query_embedding = self._generate_embedding(title, description)

        # Query all tickets from database
        tickets = db.query(Ticket).all()

        if not tickets:
            return SimilarityOutput(similar_tickets=[], avg_similarity=0.0)

        # Calculate similarity scores for all tickets
        similarities = []
        for ticket in tickets:
            ticket_embedding = self._generate_embedding(ticket.title, ticket.description)
            score = self._cosine_similarity(query_embedding, ticket_embedding)
            similarities.append((ticket, score))

        # Sort by similarity score descending and get top 3
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_3 = similarities[:3]

        # Build response
        similar_tickets = [
            SimilarTicket(
                ticket_id=ticket.id,
                title=ticket.title,
                category=ticket.category,
                similarity_score=float(score),
                status=ticket.status
            )
            for ticket, score in top_3
        ]

        avg_similarity = sum(score for _, score in top_3) / len(top_3) if top_3 else 0.0

        return SimilarityOutput(
            similar_tickets=similar_tickets,
            avg_similarity=float(avg_similarity)
        )

    def _generate_embedding(self, title: str, description: str) -> List[float]:
        """
        Generate embedding for text.

        This is a mock implementation using hashing.
        In production, use actual embedding models (Sentence Transformers, Gemini Embeddings, etc.)

        Args:
            title: Ticket title
            description: Ticket description

        Returns:
            List of floats representing the embedding
        """
        # Combine title and description
        text = (title + " " + description).lower()

        # Use hash-based mock embedding
        embedding = []
        for i in range(self.embedding_dim):
            # Create a deterministic embedding based on text and index
            h = hashlib.sha256(f"{text}{i}".encode()).hexdigest()
            # Convert hex to float between -1 and 1
            value = (int(h[:8], 16) % 200 - 100) / 100.0
            embedding.append(value)

        return embedding

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity score (0-1)
        """
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a ** 2 for a in vec1) ** 0.5
        norm2 = sum(b ** 2 for b in vec2) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)
        # Normalize to 0-1 range
        return (similarity + 1) / 2

    def store_embedding(self, ticket_id: int, title: str, description: str) -> bool:
        """
        Store ticket embedding in Qdrant (optional).

        Args:
            ticket_id: ID of the ticket
            title: Ticket title
            description: Ticket description

        Returns:
            True if stored successfully, False otherwise
        """
        if not self.qdrant_available:
            return False

        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import PointStruct

            client = QdrantClient(host=self.qdrant_host, port=self.qdrant_port)

            # Check if collection exists, create if not
            collections = client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if self.collection_name not in collection_names:
                client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config={"size": self.embedding_dim, "distance": "Cosine"}
                )

            # Generate and store embedding
            embedding = self._generate_embedding(title, description)
            point = PointStruct(
                id=ticket_id,
                vector=embedding,
                payload={"title": title, "description": description}
            )

            # Use upsert which handles both insert and update
            client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )

            return True

        except Exception as e:
            print(f"Error storing embedding in Qdrant: {e}")
            return False
