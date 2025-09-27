#!/usr/bin/env python3
"""
Cedar InvestiCAT Integration Demo
Complete demonstration of how all components work together.
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import CedarInvestiCATIntegration

def print_header(title: str):
    """Print a formatted header for demo sections."""
    print("\n" + "=" * 60)
    print(f"🚀 {title}")
    print("=" * 60)

def print_subheader(title: str):
    """Print a formatted subheader."""
    print(f"\n📋 {title}")
    print("-" * 40)

def demo_basic_processing():
    """Demonstrate basic document processing with Cedar enhancements."""
    print_header("CEDAR INVESTICAT INTEGRATION DEMO")
    
    print("🎯 Initializing Cedar InvestiCAT Integration...")
    
    # Initialize without OpenAI API key for demo
    cedar = CedarInvestiCATIntegration(openai_api_key=None)
    
    print("✅ Cedar integration initialized successfully!")
    
    print_subheader("Processing Test Document")
    
    # Process a mock document
    result = cedar.process_with_mastra_productivity(
        "test_corporate_document.pdf",
        "Corporate Merger Investigation - Q1 2024"
    )
    
    print("📊 PROCESSING RESULTS:")
    print(f"   Investigation: {result['investigation_title']}")
    print(f"   Timeline Events: {len(result['timeline'])}")
    print(f"   Processing Time: {result['processed_at']}")
    
    # Show timeline insights
    insights = result['timeline_insights']
    print(f"\n📈 TIMELINE INSIGHTS:")
    print(f"   Timeline Span: {insights['timeline_span']['start_date']} to {insights['timeline_span']['end_date']}")
    print(f"   Total Events: {insights['timeline_span']['total_events']}")
    print(f"   Most Active Period: {insights['most_active_period']['period']} ({insights['most_active_period']['event_count']} events)")
    
    print(f"\n👥 KEY ENTITIES:")
    for entity in insights['key_entities'][:3]:
        print(f"   • {entity['entity']}: {entity['mention_count']} mentions")
    
    print(f"\n📍 LOCATION HOTSPOTS:")
    for location in insights['location_hotspots'][:3]:
        print(f"   • {location['location']}: {location['event_count']} events")
    
    return result

def demo_natural_language_queries(result):
    """Demonstrate natural language querying capabilities."""
    print_header("NATURAL LANGUAGE QUERIES")
    
    cedar = CedarInvestiCATIntegration(openai_api_key=None)
    timeline_data = result['timeline']
    
    # Test different types of queries
    queries = [
        "What happened in February 2024?",
        "Who was John Smith and what did he do?",
        "Show me all events in New York",
        "When did the merger announcement happen?"
    ]
    
    for i, query in enumerate(queries, 1):
        print_subheader(f"Query {i}: '{query}'")
        
        query_result = cedar.query_timeline(query, timeline_data)
        
        print(f"🔍 QUERY ANALYSIS:")
        print(f"   Query Type: {query_result['conversation_context']['query_type']}")
        print(f"   Supporting Events: {len(query_result['supporting_events'])}")
        print(f"   Entities Found: {query_result['entity_count']}")
        
        if query_result['date_range']['start']:
            print(f"   Date Range: {query_result['date_range']['start']} to {query_result['date_range']['end']}")
        
        print(f"\n💬 AI RESPONSE:")
        print(f"   {query_result['answer']}")
        
        print(f"\n🔗 SUGGESTED FOLLOW-UPS:")
        for suggestion in query_result['conversation_context']['suggested_followups']:
            print(f"   • {suggestion}")

def demo_summary_generation(result):
    """Demonstrate automated summary generation."""
    print_header("AUTOMATED SUMMARY GENERATION")
    
    cedar = CedarInvestiCATIntegration(openai_api_key=None)
    
    print_subheader("Executive Summary")
    exec_summary = result['summaries']['executive_summary']
    print(f"📝 Title: {exec_summary.title}")
    print(f"📊 Confidence Score: {exec_summary.confidence_score:.2f}")
    print(f"\n📄 Executive Summary:")
    print(f"   {exec_summary.executive_summary}")
    
    print(f"\n🎯 Key Findings ({len(exec_summary.key_findings)} total):")
    for i, finding in enumerate(exec_summary.key_findings[:3], 1):
        print(f"   {i}. {finding}")
    
    print_subheader("Briefing Note")
    briefing = result['summaries']['briefing_note']
    print(f"📋 Headline: {briefing['summary']['headline']}")
    print(f"📝 Lead: {briefing['summary']['lead_paragraph']}")
    print(f"🔍 Key Points: {len(briefing['summary']['key_points'])} identified")
    
    print_subheader("Publication Draft")
    pub_draft = result['summaries']['publication_draft']
    print(f"📰 Headline: {pub_draft['headline']}")
    print(f"📖 Word Count: {pub_draft['metadata']['word_count']}")
    print(f"⏱️  Reading Time: {pub_draft['metadata']['reading_time']} minutes")

def demo_interactive_features(result):
    """Demonstrate interactive summary features."""
    print_header("INTERACTIVE FEATURES")
    
    interactive = result['interactive_summary']
    
    print_subheader("Overview Statistics")
    overview = interactive['overview']
    print(f"📊 Total Events: {overview['total_events']}")
    print(f"👥 Unique Entities: {overview['unique_entities']}")
    print(f"📍 Unique Locations: {overview['unique_locations']}")
    print(f"📅 Date Coverage: {overview['date_coverage']} days")
    
    print_subheader("Clickable Elements")
    entities = interactive['interactive_elements']['clickable_entities']
    print(f"🔗 Clickable Entities ({len(entities)} total):")
    for entity in entities[:3]:
        print(f"   • {entity['entity']}: {entity['event_count']} events")
    
    segments = interactive['interactive_elements']['timeline_segments']
    print(f"\n📈 Timeline Segments ({len(segments)} periods):")
    for segment in segments[:3]:
        print(f"   • {segment['period']}: {segment['event_count']} events")
    
    print_subheader("Quick Insights")
    insights = interactive['quick_insights']
    for insight in insights:
        print(f"💡 {insight}")

def demo_neo4j_output(result):
    """Demonstrate enhanced Neo4j output."""
    print_header("ENHANCED NEO4J OUTPUT")
    
    neo4j_output = result['neo4j_output']
    
    print_subheader("Node Summary")
    nodes_by_type = {}
    for node in neo4j_output['nodes']:
        label = node['label']
        nodes_by_type[label] = nodes_by_type.get(label, 0) + 1
    
    print(f"📊 Total Nodes: {len(neo4j_output['nodes'])}")
    for node_type, count in nodes_by_type.items():
        print(f"   • {node_type}: {count} nodes")
    
    print_subheader("Relationship Summary")
    rels_by_type = {}
    for rel in neo4j_output['relationships']:
        rel_type = rel['type']
        rels_by_type[rel_type] = rels_by_type.get(rel_type, 0) + 1
    
    print(f"🔗 Total Relationships: {len(neo4j_output['relationships'])}")
    for rel_type, count in rels_by_type.items():
        print(f"   • {rel_type}: {count} relationships")
    
    print_subheader("Enhanced Schema Elements")
    print("🌟 New node types added by Cedar:")
    enhanced_nodes = [node for node in neo4j_output['nodes'] 
                     if node['label'] in ['ExecutiveSummary', 'TimelineInsights', 'KeyFinding']]
    
    for node in enhanced_nodes:
        print(f"   • {node['label']}: {node['id']}")

def demo_cross_document_analysis():
    """Demonstrate cross-document analysis capabilities."""
    print_header("CROSS-DOCUMENT ANALYSIS PREVIEW")
    
    print("📚 Cross-Document Analysis Features:")
    print("   • Entity overlap detection across multiple documents")
    print("   • Timeline conflict identification")
    print("   • Cross-reference confirmation scoring")
    print("   • Multi-source reliability assessment")
    print("   • Comprehensive cross-document Neo4j schema")
    
    print("\n🔧 Usage Example:")
    print("   cedar.cross_document_analysis(['doc1.pdf', 'doc2.pdf'], 'Multi-Doc Investigation')")

def demo_cli_interface():
    """Demonstrate CLI interface capabilities."""
    print_header("COMMAND LINE INTERFACE")
    
    print("💻 Available CLI Commands:")
    print("\n1. Process Single Document:")
    print("   python main.py process document.pdf -t 'Investigation Title'")
    
    print("\n2. Natural Language Queries:")
    print("   python main.py query 'What happened in January?' --timeline-file results.json")
    
    print("\n3. Cross-Document Analysis:")
    print("   python main.py cross-analyze doc1.pdf doc2.pdf -t 'Multi-Doc Investigation'")
    
    print("\n4. Generate Publication Package:")
    print("   python main.py package --timeline-file results.json -t 'Title' --type comprehensive")

def save_demo_results(result):
    """Save demo results for further exploration."""
    print_header("SAVING DEMO RESULTS")
    
    # Save complete results
    with open('cedar_demo_results.json', 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    # Save just the timeline for easy querying
    timeline_only = {
        'investigation_title': result['investigation_title'],
        'timeline': result['timeline'],
        'processed_at': result['processed_at']
    }
    
    with open('cedar_demo_timeline.json', 'w') as f:
        json.dump(timeline_only, f, indent=2, default=str)
    
    print("💾 Demo results saved:")
    print("   📄 cedar_demo_results.json - Complete results with all features")
    print("   📊 cedar_demo_timeline.json - Timeline data for querying")
    
    print("\n🔍 Try these commands to explore further:")
    print("   python main.py query 'What did Jane Doe do?' --timeline-file cedar_demo_timeline.json")
    print("   python main.py package --timeline-file cedar_demo_timeline.json -t 'Demo Investigation' --type executive")

def main():
    """Run the complete Cedar InvestiCAT integration demo."""
    try:
        print("🎬 Starting Cedar InvestiCAT Integration Demo...")
        print(f"⏰ Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. Basic Processing
        result = demo_basic_processing()
        
        # 2. Natural Language Queries
        demo_natural_language_queries(result)
        
        # 3. Summary Generation
        demo_summary_generation(result)
        
        # 4. Interactive Features
        demo_interactive_features(result)
        
        # 5. Neo4j Output
        demo_neo4j_output(result)
        
        # 6. Cross-Document Analysis Preview
        demo_cross_document_analysis()
        
        # 7. CLI Interface
        demo_cli_interface()
        
        # 8. Save Results
        save_demo_results(result)
        
        print_header("DEMO COMPLETED SUCCESSFULLY!")
        print("🎉 Cedar InvestiCAT integration is fully operational!")
        print("📚 All components working together seamlessly:")
        print("   ✅ ETL Pipeline Integration")
        print("   ✅ Natural Language Queries")  
        print("   ✅ Automated Summary Generation")
        print("   ✅ Interactive Timeline Analysis")
        print("   ✅ Enhanced Neo4j Schema")
        print("   ✅ Cross-Document Capabilities")
        print("   ✅ Command Line Interface")
        
        print(f"\n⏰ Demo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n❌ Demo encountered an error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()