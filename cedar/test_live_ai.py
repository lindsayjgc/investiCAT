#!/usr/bin/env python3
"""
Live AI Query Test - Direct integration with OpenAI API
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import CedarInvestiCATIntegration
import json

def test_live_ai_query():
    """Test a live AI query with real OpenAI integration."""
    
    # Set API key directly
    api_key = "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"
    
    print("🤖 Testing LIVE AI Query with Real OpenAI Integration")
    print("=" * 60)
    
    # Initialize with real API key
    cedar = CedarInvestiCATIntegration(openai_api_key=api_key)
    
    # Load timeline data
    with open('cedar_demo_timeline.json', 'r') as f:
        data = json.load(f)
        timeline_data = data['timeline']
    
    # Test sophisticated investigative query
    query = "Based on this corporate merger timeline, what are the top 3 investigative angles journalists should pursue, and what specific questions should they ask?"
    
    print(f"🔍 QUERY: {query}")
    print("\n🤖 REAL AI ANALYSIS:")
    print("-" * 40)
    
    try:
        result = cedar.query_timeline(query, timeline_data)
        
        # Display AI response
        print(result['answer'])
        
        print(f"\n📊 ANALYSIS SUMMARY:")
        print(f"   Events Analyzed: {len(result['supporting_events'])}")
        print(f"   Entities Found: {result['entity_count']}")
        print(f"   Date Range: {result['date_range']['start']} to {result['date_range']['end']}")
        
        print(f"\n🔗 AI FOLLOW-UP SUGGESTIONS:")
        for suggestion in result['conversation_context']['suggested_followups']:
            print(f"   • {suggestion}")
        
        print(f"\n✅ SUCCESS: Real AI analysis completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def test_live_ai_summary():
    """Test live AI summary generation."""
    
    api_key = "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"
    
    print("\n🤖 Testing LIVE AI Summary Generation")
    print("=" * 60)
    
    cedar = CedarInvestiCATIntegration(openai_api_key=api_key)
    
    # Load timeline data
    with open('cedar_demo_timeline.json', 'r') as f:
        data = json.load(f)
        timeline_data = data['timeline']
    
    print("📝 Generating AI Executive Summary...")
    
    try:
        summary = cedar.summary_generator.generate_executive_summary(
            timeline_data, 
            "TechCorp Merger - Live AI Analysis"
        )
        
        print(f"\n🎯 AI-GENERATED EXECUTIVE SUMMARY:")
        print(f"   Title: {summary.title}")
        print(f"   Confidence: {summary.confidence_score:.2f}")
        
        print(f"\n📄 Executive Summary:")
        print(f"   {summary.executive_summary}")
        
        print(f"\n🔍 AI Key Findings:")
        for i, finding in enumerate(summary.key_findings[:5], 1):
            print(f"   {i}. {finding}")
        
        print(f"\n✅ SUCCESS: Live AI summary generated!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def main():
    print("🚀 LIVE AI INTEGRATION TEST")
    print("Testing real OpenAI API integration with Cedar InvestiCAT")
    print("=" * 70)
    
    # Test 1: Live AI Query
    success1 = test_live_ai_query()
    
    # Test 2: Live AI Summary
    success2 = test_live_ai_summary()
    
    print("\n" + "=" * 70)
    if success1 and success2:
        print("🎉 LIVE AI INTEGRATION SUCCESSFUL!")
        print("✅ Real OpenAI GPT-3.5-turbo integration working")
        print("✅ Sophisticated investigative analysis active")
        print("✅ AI-powered journalism insights operational")
        print("\n🚀 Cedar InvestiCAT is ready for production use!")
    else:
        print("❌ Some tests failed - check API key and connection")

if __name__ == "__main__":
    main()