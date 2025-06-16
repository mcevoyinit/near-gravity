#!/usr/bin/env python3
"""
Test script for NearGravity RAG flow
Demonstrates end-to-end processing
"""
import sys
import os
from pathlib import Path

# Add src to path
src_path = str(Path(__file__).parent.parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)


def main():
    """Run end-to-end RAG test"""
    print("Initializing NearGravity RAG Service...")
    
    # Initialize service
    rag_service = RAGService(
        model="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=1000
    )
    
    print("Adding injection messages...")
    
    # Add some injection messages (ads/promotional content)
    injection_messages = [
        {
            "content": "Experience the rich flavors of our premium Colombian coffee beans, ethically sourced and roasted to perfection.",
            "provider_id": "coffee_company",
            "metadata": {"category": "beverages", "product": "coffee"}
        },
        {
            "content": "Transform your productivity with our AI-powered task management system, designed for modern teams.",
            "provider_id": "tech_startup",
            "metadata": {"category": "technology", "product": "software"}
        },
        {
            "content": "Discover sustainable fashion that makes a difference. Our eco-friendly materials reduce environmental impact by 70%.",
            "provider_id": "fashion_brand",
            "metadata": {"category": "fashion", "product": "clothing"}
        }
    ]
    
    # Add injection messages
    for msg in injection_messages:
        msg_id = rag_service.add_injection_content(
            content=msg["content"],
            provider_id=msg["provider_id"],
            metadata=msg["metadata"]
        )
        print(f"Added injection: {msg_id}")
    
    print("\nTesting RAG flow...")
    
    # Test cases
    test_cases = [
        {
            "content": "I need help organizing my morning routine to be more productive",
            "modality": "text",
            "expected_injection": "tech_startup"
        },
        {
            "content": "Looking for recommendations on what to drink while working",
            "modality": "text",
            "expected_injection": "coffee_company"
        },
        {
            "content": "I want to update my wardrobe with environmentally conscious choices",
            "modality": "text",
            "expected_injection": "fashion_brand"
        }
    ]
