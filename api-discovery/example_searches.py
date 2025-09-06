#!/usr/bin/env python3
"""
🔍 Example Search Queries for CatalystAI API Discovery

This script demonstrates various types of search queries you can use
with the intelligent search tool to find relevant APIs.
"""

import subprocess
import sys
import time

def run_search(query: str, description: str):
    """Run a search query and display results"""
    print(f"\n{'='*80}")
    print(f"🔍 **{description}**")
    print(f"Query: {query}")
    print(f"{'='*80}")
    
    try:
        result = subprocess.run([
            'python', 'intelligent_search.py', query
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"❌ Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("⏰ Search timed out")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Run example searches"""
    
    print("🚀 **CatalystAI API Discovery - Example Searches**")
    print("This script demonstrates various search queries for finding relevant APIs.")
    
    # Example queries
    examples = [
        {
            "query": "I need to build an e-commerce platform with payment processing, user authentication, and notifications",
            "description": "E-commerce Platform Integration"
        },
        {
            "query": "Compare payment processing APIs and recommend the best one for a startup",
            "description": "Payment API Comparison for Startups"
        },
        {
            "query": "How do I integrate authentication and user management for a mobile app?",
            "description": "Mobile App Authentication"
        },
        {
            "query": "What APIs do I need for a social media platform with messaging and notifications?",
            "description": "Social Media Platform APIs"
        },
        {
            "query": "I need to send SMS notifications and handle user authentication for a healthcare app",
            "description": "Healthcare App Integration"
        },
        {
            "query": "Compare communication APIs for sending notifications and managing team collaboration",
            "description": "Communication APIs Comparison"
        },
        {
            "query": "What's the best way to integrate maps and location services with payment processing?",
            "description": "Maps + Payment Integration"
        },
        {
            "query": "I need APIs for a marketplace platform with payments, authentication, and team collaboration",
            "description": "Marketplace Platform APIs"
        }
    ]
    
    print(f"\n📋 **Running {len(examples)} example searches...**")
    print("This will take a few minutes as each search uses OpenAI for analysis.")
    
    for i, example in enumerate(examples, 1):
        print(f"\n🔄 Running search {i}/{len(examples)}...")
        run_search(example["query"], example["description"])
        
        # Add delay between searches to be respectful
        if i < len(examples):
            print("\n⏳ Waiting 5 seconds before next search...")
            time.sleep(5)
    
    print(f"\n{'='*80}")
    print("✅ **All example searches completed!**")
    print("="*80)
    print("\n🎯 **Key Takeaways:**")
    print("• The intelligent search tool can handle complex, multi-faceted queries")
    print("• It provides comprehensive recommendations with integration strategies")
    print("• It considers security, cost, and best practices")
    print("• It offers actionable next steps for implementation")
    print("\n🚀 **Try your own queries:**")
    print("python intelligent_search.py \"Your custom query here\"")

if __name__ == "__main__":
    main()
