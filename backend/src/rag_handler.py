"""
RAG Handler for FAQ-based question answering
Uses simple similarity search to find relevant FAQ answers
"""

import json
import logging
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger("rag_handler")


class FAQRetriever:
    def __init__(self, faq_file_path: str):
        """Initialize FAQ retriever with company knowledge base"""
        self.faq_data = self._load_faq_data(faq_file_path)
        self.faq_entries = self._prepare_faq_entries()
        logger.info(f"Loaded {len(self.faq_entries)} FAQ entries")

    def _load_faq_data(self, file_path: str) -> Dict[str, Any]:
        """Load FAQ data from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading FAQ data: {e}")
            return {}

    def _prepare_faq_entries(self) -> List[Dict[str, str]]:
        """Prepare FAQ entries for search"""
        entries = []

        # Add main FAQs
        for faq in self.faq_data.get('faq', []):
            entries.append({
                'question': faq['question'],
                'answer': faq['answer'],
                'category': 'faq'
            })

        # Add product information as searchable content
        for product in self.faq_data.get('products', []):
            entries.append({
                'question': f"What is {product['name']}? Tell me about {product['name']}",
                'answer': f"{product['name']}: {product['description']}. Key features: {', '.join(product['key_features'][:3])}. Best for: {product['target_audience']}",
                'category': 'product'
            })

        # Add pricing information
        for pricing in self.faq_data.get('pricing', []):
            entries.append({
                'question': f"What is the pricing for {pricing['product']}? How much does {pricing['product']} cost?",
                'answer': f"{pricing['product']} - {pricing['model']}: {pricing['details']}",
                'category': 'pricing'
            })

        return entries

    def _simple_similarity(self, query: str, text: str) -> float:
        """
        Enhanced keyword-based similarity score with better matching
        """
        query_lower = query.lower()
        text_lower = text.lower()

        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'is', 'are', 'what', 'how', 'do', 'does', 'can', 'will', 'about', 'for', 'with', 'to', 'of', 'in', 'on'}

        query_words = [w for w in query_lower.split() if w not in stop_words and len(w) > 2]
        text_words = [w for w in text_lower.split() if len(w) > 2]

        if not query_words:
            return 0.0

        # Calculate word overlap
        query_set = set(query_words)
        text_set = set(text_words)
        overlap = query_set.intersection(text_set)

        # Base similarity
        similarity = len(overlap) / len(query_set) if query_set else 0.0

        # Bonus for key terms
        key_terms = {
            'pricing': (['price', 'pricing', 'cost', 'commission', 'fee', 'charge'], 0.3),
            'onboarding': (['onboard', 'start', 'signup', 'register', 'join', 'get started'], 0.3),
            'delivery': (['delivery', 'deliver', 'fleet', 'rider', 'executive'], 0.2),
            'payment': (['payment', 'settle', 'money', 'pay', 'fund'], 0.2),
            'support': (['support', 'help', 'assist', 'service'], 0.2),
            'partner': (['partner', 'partnership', 'collaborate'], 0.2),
        }

        for key, (terms, bonus) in key_terms.items():
            if any(term in query_lower for term in terms):
                if any(term in text_lower for term in terms):
                    similarity += bonus

        # Bonus for partial word matches (like "price" matching "pricing")
        for q_word in query_words:
            if len(q_word) > 3:
                if any(q_word in t_word or t_word in q_word for t_word in text_words):
                    similarity += 0.1

        return min(similarity, 1.5)

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for relevant FAQ entries
        Returns top_k most relevant entries
        """
        if not query or not self.faq_entries:
            return []

        # Calculate similarity scores
        scored_entries = []
        for entry in self.faq_entries:
            # Search in both question and answer with higher weight on question
            question_score = self._simple_similarity(query, entry['question']) * 1.5
            answer_score = self._simple_similarity(query, entry['answer']) * 0.8

            total_score = question_score + answer_score

            # Much lower threshold - if any match at all, include it
            if total_score > 0.05:
                scored_entries.append({
                    **entry,
                    'relevance_score': total_score
                })

        # Sort by relevance and return top_k
        scored_entries.sort(key=lambda x: x['relevance_score'], reverse=True)

        # If we have results, return them; otherwise return top 2 FAQs as fallback
        if scored_entries:
            return scored_entries[:top_k]
        else:
            # Return most general FAQs as fallback
            return self.faq_entries[:2]

    def get_company_info(self) -> str:
        """Get formatted company information"""
        info = self.faq_data.get('company_info', {})
        company_name = self.faq_data.get('company_name', '')
        tagline = self.faq_data.get('tagline', '')
        description = self.faq_data.get('description', '')

        return f"{company_name} - {tagline}. {description}"

    def get_all_products(self) -> List[Dict[str, Any]]:
        """Get all products"""
        return self.faq_data.get('products', [])

    def get_pricing_info(self, product_name: str = None) -> str:
        """Get pricing information for a specific product or all"""
        pricing_list = self.faq_data.get('pricing', [])

        if product_name:
            for pricing in pricing_list:
                if product_name.lower() in pricing['product'].lower():
                    return f"{pricing['product']}: {pricing['details']}"
            return "Pricing information not found for that specific product."

        # Return all pricing as summary
        pricing_summary = []
        for pricing in pricing_list[:3]:  # Limit to top 3
            pricing_summary.append(f"{pricing['product']}: {pricing['model']}")

        return "Our pricing: " + "; ".join(pricing_summary) + ". Custom pricing available for high-volume partners."
