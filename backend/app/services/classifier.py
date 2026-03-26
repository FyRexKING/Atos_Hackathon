"""
Classification service using Gemini API.
Classifies tickets into category, priority, and impact.
"""
import json
import os
import requests
from typing import Dict, Any
from app.schemas.ticket import ClassificationOutput


class ClassificationService:
    """Service for classifying tickets using Gemini Flash API."""

    def __init__(self):
        """Initialize with Gemini API key."""
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    def classify(self, title: str, description: str) -> ClassificationOutput:
        """
        Classify a ticket using Gemini API.

        Args:
            title: Ticket title
            description: Ticket description

        Returns:
            ClassificationOutput with category, priority, impact

        Raises:
            ValueError: If API call fails or response is invalid
        """
        if not self.api_key:
            return self._get_mock_classification(title, description)

        prompt = self._build_prompt(title, description)

        try:
            response = requests.post(
                self.base_url,
                params={"key": self.api_key},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=10
            )
            response.raise_for_status()

            result = response.json()

            # Extract text from Gemini response
            if "candidates" in result and len(result["candidates"]) > 0:
                text_content = result["candidates"][0]["content"]["parts"][0]["text"]
                classification_data = self._parse_json_response(text_content)
                return ClassificationOutput(**classification_data)

            raise ValueError("Invalid Gemini API response structure")

        except requests.exceptions.RequestException as e:
            print(f"Gemini API error: {e}. Using mock classification.")
            return self._get_mock_classification(title, description)

    def _build_prompt(self, title: str, description: str) -> str:
        """Build the classification prompt for Gemini."""
        return f"""Classify the following support ticket into category, priority, and impact.

Ticket Title: {title}
Ticket Description: {description}

Respond with ONLY valid JSON (no markdown, no extra text) in this exact format:
{{
    "category": "auth | billing | infra | ui | api",
    "priority": "low | medium | high",
    "impact": "low | medium | high"
}}

Rules:
- category: Choose the most relevant category (authentication, billing, infrastructure, user interface, API)
- priority: Assess based on urgency (low=can wait, medium=should address soon, high=urgent)
- impact: Assess user impact (low=minor inconvenience, medium=affects workflow, high=service unavailable)
"""

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """
        Parse JSON from Gemini response safely.

        Args:
            text: Raw text response from Gemini

        Returns:
            Parsed JSON dictionary

        Raises:
            ValueError: If JSON parsing fails
        """
        try:
            # Try to find JSON in the response (might be wrapped in markdown)
            if "```" in text:
                # Extract JSON from markdown code block
                start = text.find("```") + 3
                if text[start:start+4] == "json":
                    start += 4
                end = text.rfind("```")
                text = text[start:end].strip()

            data = json.loads(text)

            # Validate required fields
            required_fields = {"category", "priority", "impact"}
            if not required_fields.issubset(set(data.keys())):
                raise ValueError(f"Missing required fields. Got: {data.keys()}")

            # Validate values
            valid_categories = {"auth", "billing", "infra", "ui", "api"}
            valid_levels = {"low", "medium", "high"}

            data["category"] = data["category"].lower()
            data["priority"] = data["priority"].lower()
            data["impact"] = data["impact"].lower()

            if data["category"] not in valid_categories:
                raise ValueError(f"Invalid category: {data['category']}")
            if data["priority"] not in valid_levels:
                raise ValueError(f"Invalid priority: {data['priority']}")
            if data["impact"] not in valid_levels:
                raise ValueError(f"Invalid impact: {data['impact']}")

            return data

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            raise ValueError(f"Failed to parse classification response: {e}")

    def _get_mock_classification(self, title: str, description: str) -> ClassificationOutput:
        """
        Get mock classification based on keywords (used when API is unavailable).

        Args:
            title: Ticket title
            description: Ticket description

        Returns:
            Mock ClassificationOutput
        """
        text = (title + " " + description).lower()

        # Simple keyword-based mock classification
        if any(word in text for word in ["login", "auth", "password", "account", "permission"]):
            category = "auth"
        elif any(word in text for word in ["billing", "invoice", "payment", "charge", "price"]):
            category = "billing"
        elif any(word in text for word in ["database", "server", "infrastructure", "timeout", "connection"]):
            category = "infra"
        elif any(word in text for word in ["button", "ui", "interface", "display", "click"]):
            category = "ui"
        elif any(word in text for word in ["api", "endpoint", "500", "error", "response"]):
            category = "api"
        else:
            category = "api"

        # Mock priority based on urgency words
        if any(word in text for word in ["urgent", "critical", "cannot", "broken", "down"]):
            priority = "high"
        elif any(word in text for word in ["slow", "issue", "problem"]):
            priority = "medium"
        else:
            priority = "low"

        # Mock impact
        if priority == "high":
            impact = "high"
        elif priority == "medium":
            impact = "medium"
        else:
            impact = "low"

        return ClassificationOutput(category=category, priority=priority, impact=impact)
