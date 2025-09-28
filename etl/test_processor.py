#!/usr/bin/env python3
"""
Test script for InvestiCAT Document Processor
Demonstrates the complete ETL workflow with sample data
"""

import json
from pathlib import Path
from document_processor_neo4j import InvestiCATProcessor

def create_sample_data():
    """Create a sample text document for testing."""
    sample_investigative_text = """
Corporate Acquisition Investigation Report

On March 15, 2024, MegaCorp Inc announced its acquisition of TechStart Inc for $2.5 billion. The announcement was made during a press conference in New York City.

John Smith, CEO of MegaCorp, and Jane Doe, founder of TechStart Inc, signed the merger agreement on March 20, 2024. The signing ceremony took place at the MegaCorp headquarters in Silicon Valley.

The board of directors approved the deal during their emergency meeting on March 10, 2024. Board members expressed concerns about regulatory approval from the Securities and Exchange Commission.

On February 10, 2024, both companies filed preliminary documentation with the SEC in Washington DC. The regulatory review process was completed on March 25, 2024.

The transaction was finalized on April 1, 2024, with all regulatory approvals received. Trading of TechStart shares was suspended on the NASDAQ exchange.

Investigation notes suggest potential insider trading activity. Sarah Johnson, a MegaCorp board member, purchased significant TechStart shares on January 15, 2024, two months before the public announcement.

The Federal Trade Commission announced their review of the merger on April 5, 2024, citing anti-competitive concerns in the artificial intelligence sector.
"""
    return sample_investigative_text

def test_direct_processing():
    """Test processing with sample text directly."""
    processor = InvestiCATProcessor()
    sample_text = create_sample_data()
    
    print("Testing direct event extraction...")
    events = processor.extract_events_fallback(sample_text)
    
    print(f"Extracted {len(events)} events:")
    for i, event in enumerate(events, 1):
        print(f"\n{i}. Title: {event['title']}")
        print(f"   Summary: {event['summary']}")
        print(f"   Date: {event.get('date', 'None')}")
        print(f"   Location: {event.get('location', 'None')}")
        print(f"   Participants: {event.get('participants', [])}")
    
    return events

def test_neo4j_structure():
    """Test the complete Neo4j structure generation."""
    processor = InvestiCATProcessor()
    
    # Mock the text extraction to use our sample data
    original_extract_text = processor.extract_text
    def mock_extract_text(file_path):
        return create_sample_data()
    processor.extract_text = mock_extract_text
    
    print("\n" + "="*80)
    print("TESTING COMPLETE NEO4J STRUCTURE GENERATION")
    print("="*80)
    
    result = processor.process_document("sample_document.pdf")
    
    print("\nGenerated Neo4j Structure:")
    print(json.dumps(result, indent=2))
    
    # Analyze the structure
    nodes = result["nodes"]
    relationships = result["relationships"]
    
    print(f"\n" + "="*50)
    print("STRUCTURE ANALYSIS")
    print("="*50)
    print(f"Documents: {len(nodes['documents'])}")
    print(f"Events: {len(nodes['events'])}")
    print(f"Dates: {len(nodes['dates'])}")
    print(f"Locations: {len(nodes['locations'])}")
    print(f"Entities: {len(nodes['entities'])}")
    print(f"Users: {len(nodes['users'])}")
    print(f"Total Relationships: {len(relationships)}")
    
    # Analyze relationships by type
    rel_types = {}
    for rel in relationships:
        rel_type = rel['type']
        rel_types[rel_type] = rel_types.get(rel_type, 0) + 1
    
    print(f"\nRelationship Types:")
    for rel_type, count in rel_types.items():
        print(f"   {rel_type}: {count}")
    
    # Validate schema compliance
    print(f"\n" + "="*50)
    print("SCHEMA COMPLIANCE CHECK")
    print("="*50)
    
    # Check that Date nodes don't have ID field
    dates_have_id = any('id' in date for date in nodes['dates'])
    print(f"✓ Dates have NO ID field: {not dates_have_id}")
    
    # Check required node types exist
    required_node_types = ['documents', 'events', 'dates', 'locations', 'entities', 'users']
    for node_type in required_node_types:
        exists = node_type in nodes and len(nodes[node_type]) > 0
        print(f"✓ {node_type.title()} nodes exist: {exists}")
    
    # Check no Cat nodes or Cat relationships exist
    has_cats = 'cats' in nodes and len(nodes.get('cats', [])) > 0
    cat_relationships = [rel for rel in relationships if rel['type'] in ['OWNS', 'HAS_DOCUMENT', 'HAS_EVENT']]
    print(f"✓ No Cat nodes (ETL scope): {not has_cats}")
    print(f"✓ No Cat relationships (ETL scope): {len(cat_relationships) == 0}")
    
    return result

if __name__ == "__main__":
    # Run both tests
    print("="*80)
    print("INVESTICAT DOCUMENT PROCESSOR TEST")
    print("="*80)
    
    # Test 1: Direct event extraction
    events = test_direct_processing()
    
    # Test 2: Complete Neo4j structure
    neo4j_result = test_neo4j_structure()
    
    # Save results
    output_file = Path("test_neo4j_output.json")
    with open(output_file, "w") as f:
        json.dump(neo4j_result, f, indent=2)
    
    print(f"\n" + "="*80)
    print(f"TEST COMPLETE - Results saved to {output_file}")
    print("="*80)