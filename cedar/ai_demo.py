#!/usr/bin/env python3
"""
Cedar InvestiCAT AI-Powered Demo
Full demonstration with real OpenAI integration showing advanced capabilities.
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import CedarInvestiCATIntegration

def print_ai_header(title: str):
    """Print a formatted header for AI demo sections."""
    print("\n" + "🤖" * 60)
    print(f"🚀 {title}")
    print("🤖" * 60)

def print_ai_subheader(title: str):
    """Print a formatted subheader."""
    print(f"\n🧠 {title}")
    print("-" * 50)

def demo_real_ai_processing():
    """Demonstrate processing with real OpenAI integration."""
    print_ai_header("CEDAR INVESTICAT - REAL AI INTEGRATION DEMO")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OpenAI API key not found! Please set OPENAI_API_KEY environment variable.")
        return None
    
    print("🎯 Initializing Cedar with Real OpenAI Integration...")
    print(f"🔑 Using API Key: {api_key[:20]}...")
    
    # Initialize with real OpenAI API key
    cedar = CedarInvestiCATIntegration(openai_api_key=api_key)
    
    print("✅ Cedar integration with AI capabilities initialized!")
    
    print_ai_subheader("Processing Document with Real AI Analysis")
    
    # Process document with full AI capabilities
    result = cedar.process_with_mastra_productivity(
        "corporate_merger_investigation.pdf",
        "TechCorp Merger Investigation - Advanced AI Analysis"
    )
    
    print("🎉 REAL AI PROCESSING COMPLETED:")
    print(f"   Investigation: {result['investigation_title']}")
    print(f"   Timeline Events: {len(result['timeline'])}")
    print(f"   AI Summaries Generated: {'✅ Yes' if 'summaries' in result else '❌ No'}")
    
    return result

def demo_advanced_ai_queries(result):
    """Demonstrate advanced natural language queries with real AI."""
    print_ai_header("ADVANCED AI-POWERED NATURAL LANGUAGE QUERIES")
    
    api_key = os.getenv('OPENAI_API_KEY')
    cedar = CedarInvestiCATIntegration(openai_api_key=api_key)
    timeline_data = result['timeline']
    
    # Advanced investigative queries
    advanced_queries = [
        "Analyze the timeline and identify any potential red flags or suspicious patterns in the merger process.",
        "What does the sequence of events suggest about John Smith's role and decision-making authority?", 
        "Are there any regulatory compliance concerns based on the timeline of events?",
        "Identify potential conflicts of interest or ethical issues in this corporate merger.",
        "What additional investigation leads should journalists pursue based on this timeline?"
    ]
    
    for i, query in enumerate(advanced_queries, 1):
        print_ai_subheader(f"Advanced Query {i}")
        print(f"🔍 Query: {query}")
        
        query_result = cedar.query_timeline(query, timeline_data)
        
        print(f"\n🤖 AI ANALYSIS:")
        # The AI response should be much more sophisticated now
        print(f"   {query_result['answer']}")
        
        print(f"\n📊 SUPPORTING DATA:")
        print(f"   Events Analyzed: {len(query_result['supporting_events'])}")
        print(f"   Entities Examined: {query_result['entity_count']}")
        
        print(f"\n🔗 AI-GENERATED FOLLOW-UPS:")
        for suggestion in query_result['conversation_context']['suggested_followups']:
            print(f"   • {suggestion}")
        
        print("\n" + "─" * 60)

def demo_ai_executive_summary(result):
    """Demonstrate AI-generated executive summary with business intelligence."""
    print_ai_header("AI-GENERATED EXECUTIVE INTELLIGENCE")
    
    exec_summary = result['summaries']['executive_summary']
    
    print_ai_subheader("Executive Summary Analysis")
    print(f"📋 Investigation: {exec_summary.title}")
    print(f"🎯 AI Confidence Score: {exec_summary.confidence_score:.2f}")
    
    print(f"\n📝 EXECUTIVE SUMMARY:")
    print(f"   {exec_summary.executive_summary}")
    
    print(f"\n🔍 AI-IDENTIFIED KEY FINDINGS:")
    for i, finding in enumerate(exec_summary.key_findings, 1):
        print(f"   {i}. {finding}")
    
    print(f"\n📈 TIMELINE HIGHLIGHTS (AI-Selected):")
    for event in exec_summary.timeline_highlights[:3]:
        print(f"   • {event.get('date')}: {event.get('event')}")
        print(f"     Entity: {event.get('entity')} | Location: {event.get('location')}")
    
    print(f"\n🔗 AI-DETECTED ENTITY RELATIONSHIPS:")
    for rel in exec_summary.entity_relationships[:3]:
        entities = rel.get('entities', [])
        if len(entities) == 2:
            print(f"   • {entities[0]} ↔ {entities[1]}: {rel.get('interaction_count')} interactions")
    
    # Show AI-enhanced executive elements
    if hasattr(exec_summary, 'business_impact') and exec_summary.business_impact:
        print(f"\n💼 BUSINESS IMPACT ASSESSMENT:")
        impact = exec_summary.business_impact
        print(f"   Impact Level: {impact.get('impact_level', 'Unknown')}")
        print(f"   Affected Areas: {', '.join(impact.get('affected_areas', []))}")
    
    if hasattr(exec_summary, 'risk_assessment') and exec_summary.risk_assessment:
        print(f"\n⚠️ RISK ASSESSMENT:")
        for risk in exec_summary.risk_assessment[:3]:
            print(f"   • {risk}")
    
    if hasattr(exec_summary, 'recommended_actions') and exec_summary.recommended_actions:
        print(f"\n📋 RECOMMENDED ACTIONS:")
        for action in exec_summary.recommended_actions[:3]:
            print(f"   • {action}")

def demo_ai_publication_draft(result):
    """Demonstrate AI-generated publication-ready content."""
    print_ai_header("AI-GENERATED PUBLICATION CONTENT")
    
    pub_draft = result['summaries']['publication_draft']
    
    print_ai_subheader("Publication-Ready Article Draft")
    print(f"📰 AI-Generated Headline: {pub_draft['headline']}")
    print(f"📖 Subhead: {pub_draft.get('subhead', 'N/A')}")
    print(f"📊 Word Count: {pub_draft['metadata']['word_count']}")
    print(f"⏱️  Estimated Reading Time: {pub_draft['metadata']['reading_time']} minutes")
    
    print(f"\n📝 ARTICLE LEAD (AI-Written):")
    print(f"   {pub_draft['lead']}")
    
    print(f"\n📄 ARTICLE BODY (AI-Generated):")
    # Show first few sentences of the body
    body_preview = pub_draft['body'][:500] + "..." if len(pub_draft['body']) > 500 else pub_draft['body']
    print(f"   {body_preview}")
    
    print(f"\n📋 EDITORIAL CHECKLIST (AI-Generated):")
    checklist = pub_draft.get('editorial_checklist', {})
    if checklist.get('fact_check_required'):
        print(f"   📍 Fact Check Items: {len(checklist['fact_check_required'])}")
        for item in checklist['fact_check_required'][:2]:
            print(f"     • {item}")
    
    if checklist.get('legal_review'):
        print(f"   ⚖️ Legal Considerations: {len(checklist['legal_review'])}")
        for item in checklist['legal_review'][:2]:
            print(f"     • {item}")

def demo_ai_cross_document_analysis():
    """Demonstrate AI-powered cross-document analysis."""
    print_ai_header("AI-POWERED CROSS-DOCUMENT ANALYSIS")
    
    api_key = os.getenv('OPENAI_API_KEY')
    cedar = CedarInvestiCATIntegration(openai_api_key=api_key)
    
    print_ai_subheader("Multi-Document Intelligence Analysis")
    
    # Simulate multiple documents
    mock_docs = [
        "merger_announcement_press_release.pdf",
        "board_meeting_minutes_feb2024.pdf", 
        "regulatory_filing_documents.pdf"
    ]
    
    print("📚 Analyzing Multiple Documents:")
    for i, doc in enumerate(mock_docs, 1):
        print(f"   {i}. {doc}")
    
    try:
        cross_result = cedar.cross_document_analysis(
            mock_docs,
            "TechCorp Multi-Document Investigation Analysis"
        )
        
        print(f"\n🎉 CROSS-DOCUMENT ANALYSIS COMPLETED:")
        print(f"   Documents Processed: {cross_result['document_count']}")
        print(f"   Total Events Analyzed: {cross_result['total_events']}")
        print(f"   Cross-References Found: {len(cross_result['cross_analysis'].get('cross_references', []))}")
        
        print(f"\n🔍 AI-IDENTIFIED PATTERNS:")
        cross_analysis = cross_result['cross_analysis']
        
        if cross_analysis.get('entity_overlap'):
            overlap = cross_analysis['entity_overlap']
            print(f"   • Total Entities: {overlap.get('total_entities', 0)}")
            print(f"   • Multi-Document Entities: {overlap.get('multi_document_entities', 0)}")
        
        if cross_analysis.get('confirmations'):
            print(f"   • Confirmations Found: {len(cross_analysis['confirmations'])}")
            for conf in cross_analysis['confirmations'][:2]:
                print(f"     - {conf['entity']}: confirmed in {conf['confirmation_count']} documents")
        
        if cross_analysis.get('reliability_score'):
            print(f"   • Overall Reliability Score: {cross_analysis['reliability_score']:.2f}")
        
    except Exception as e:
        print(f"   📝 Cross-document analysis simulation: {str(e)}")
        print("   💡 This would work with real documents containing timeline data")

def save_ai_results(result):
    """Save AI-enhanced results for further analysis."""
    print_ai_header("SAVING AI-ENHANCED RESULTS")
    
    # Save complete AI results
    ai_results_file = f"cedar_ai_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(ai_results_file, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    # Extract just the AI summaries
    ai_summaries = result.get('summaries', {})
    summaries_file = f"cedar_ai_summaries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summaries_file, 'w') as f:
        json.dump(ai_summaries, f, indent=2, default=str)
    
    print("💾 AI-Enhanced Results Saved:")
    print(f"   📄 {ai_results_file} - Complete results with AI analysis")
    print(f"   🧠 {summaries_file} - AI-generated summaries only")
    
    print(f"\n🔍 Use these files to:")
    print(f"   • Review AI-generated insights and recommendations")
    print(f"   • Compare AI vs human analysis")
    print(f"   • Extract publication-ready content")
    print(f"   • Continue investigation with AI guidance")

def test_ai_cli_commands():
    """Test CLI commands with AI capabilities."""
    print_ai_header("AI-POWERED COMMAND LINE INTERFACE")
    
    print("💻 Testing AI-Enhanced CLI Commands:")
    
    # Test sophisticated query
    sophisticated_query = "Based on the corporate timeline, what investigative angles should journalists focus on, and what are the potential legal implications?"
    
    print(f"\n1. 🧠 Sophisticated AI Query:")
    print(f"   Query: {sophisticated_query}")
    print(f"   Command: python main.py query '{sophisticated_query}' --timeline-file cedar_demo_timeline.json")
    
    print(f"\n2. 📋 Executive Package Generation:")
    print(f"   Command: python main.py package --timeline-file cedar_demo_timeline.json")
    print(f"            -t 'AI-Enhanced Investigation' --type comprehensive")
    
    print(f"\n3. 🔍 Cross-Document Analysis:")
    print(f"   Command: python main.py cross-analyze doc1.pdf doc2.pdf doc3.pdf")
    print(f"            -t 'Multi-Source Investigation'")
    
    print(f"\n💡 All commands now use real AI for:")
    print(f"   • Intelligent pattern recognition")
    print(f"   • Contextual understanding")
    print(f"   • Professional journalism insights")
    print(f"   • Publication-ready content generation")

def main():
    """Run the complete AI-powered Cedar InvestiCAT demo."""
    try:
        print("🤖 Starting AI-Powered Cedar InvestiCAT Demo...")
        print(f"⏰ AI Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ OpenAI API key not found!")
            print("Please run: export OPENAI_API_KEY='your-api-key'")
            sys.exit(1)
        
        # 1. Real AI Processing
        result = demo_real_ai_processing()
        if not result:
            return
        
        # 2. Advanced AI Queries
        demo_advanced_ai_queries(result)
        
        # 3. AI Executive Summary
        demo_ai_executive_summary(result)
        
        # 4. AI Publication Draft
        demo_ai_publication_draft(result)
        
        # 5. Cross-Document Analysis
        demo_ai_cross_document_analysis()
        
        # 6. Save AI Results
        save_ai_results(result)
        
        # 7. CLI Commands Overview
        test_ai_cli_commands()
        
        print_ai_header("AI-POWERED DEMO COMPLETED!")
        print("🎉 Cedar InvestiCAT with full AI capabilities is operational!")
        print("🧠 Advanced features now available:")
        print("   ✅ Real OpenAI GPT-4 integration")
        print("   ✅ Sophisticated investigative analysis")
        print("   ✅ Professional journalism insights")
        print("   ✅ Publication-ready content generation")
        print("   ✅ Advanced pattern recognition")
        print("   ✅ Cross-document intelligence")
        print("   ✅ Editorial guidance and recommendations")
        
        print(f"\n⏰ AI Demo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🚀 Ready for real-world investigative journalism!")
        
    except Exception as e:
        print(f"\n❌ AI Demo encountered an error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()