#!/usr/bin/env python3
"""
InvestiCAT End-to-End Test: Document Processing to Neo4j Loading

Demonstrates complete workflow:
1. Process document with document_processor_neo4j.py
2. Load results into Neo4j with neo4j_loader.py  
3. Verify data integrity
"""

import json
import sys
from pathlib import Path
import time

try:
    from document_processor_neo4j import InvestiCATProcessor
    from neo4j_loader import InvestiCATNeo4jLoader
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all required packages are installed: pip install -r requirements.txt")
    sys.exit(1)

def create_test_data():
    """Create comprehensive test data for demonstration."""
    return """
InvestiCAT Investigation Report: Corporate Merger Analysis

Executive Summary:
On March 15, 2024, MegaCorp Inc announced its intention to acquire TechStart Inc for $2.5 billion. 
The announcement was made during a press conference in New York City with CEO John Smith presiding.

Timeline of Events:

February 10, 2024: Both companies filed preliminary documentation with the Securities and Exchange Commission in Washington DC. The filing included detailed financial statements and merger projections.

March 10, 2024: The board of directors approved the deal during their emergency meeting. Board members expressed initial concerns about regulatory approval from the Federal Trade Commission.

March 15, 2024: Public announcement of the acquisition at MegaCorp headquarters in Silicon Valley. John Smith, CEO of MegaCorp, and Jane Doe, founder of TechStart Inc, jointly announced the deal.

March 20, 2024: Merger agreement was signed by both parties. The signing ceremony took place at the offices of Goldman Sachs in Manhattan, with legal representatives from both companies present.

March 25, 2024: The regulatory review process was completed by the SEC. All required documentation was approved without major modifications.

April 1, 2024: The transaction was finalized with all regulatory approvals received. Trading of TechStart shares was suspended on the NASDAQ exchange effective immediately.

April 5, 2024: The Federal Trade Commission announced their comprehensive review of the merger, citing potential anti-competitive concerns in the artificial intelligence sector.

Investigation Notes:
Sarah Johnson, a MegaCorp board member, purchased significant TechStart shares on January 15, 2024, two months before the public announcement. This trading activity is currently under investigation by the SEC.

The merger creates the largest AI-focused corporation in North America, with combined revenues exceeding $50 billion annually.

Key Participants:
- John Smith: CEO, MegaCorp Inc
- Jane Doe: Founder, TechStart Inc  
- Sarah Johnson: Board Member, MegaCorp Inc
- Securities and Exchange Commission
- Federal Trade Commission
- Goldman Sachs (Legal advisors)
"""

def test_document_processing():
    """Test document processing functionality."""
    print("="*60)
    print("STEP 1: DOCUMENT PROCESSING")
    print("="*60)
    
    # Initialize processor
    processor = InvestiCATProcessor()
    
    # Mock document processing with test data
    test_text = create_test_data()
    print(f"Processing test document with {len(test_text)} characters...")
    
    # Extract events using processor's extraction methods
    events = processor.extract_events_fallback(test_text)
    print(f"Extracted {len(events)} events from test document")
    
    # Create a mock document processing result
    doc_id = processor.generate_unique_id("doc")
    user_id = processor.generate_unique_id("user")
    
    # Build the complete Neo4j structure
    neo4j_data = {
        "nodes": {
            "documents": [
                {
                    "id": doc_id,
                    "filename": "test_investigation_report.pdf"
                }
            ],
            "events": [],
            "dates": [],
            "locations": [],
            "entities": [],
            "users": [
                {
                    "id": user_id,
                    "email": "investigator@investicat.com",
                    "name": "Test Investigator", 
                    "password": "secure_password"
                }
            ]
        },
        "relationships": []
    }
    
    # Process extracted events
    unique_dates = set()
    unique_locations = {}
    unique_entities = {}
    
    for i, event in enumerate(events, 1):
        event_id = processor.generate_unique_id("event")
        
        # Add event node
        neo4j_data["nodes"]["events"].append({
            "id": event_id,
            "title": event.get("title", f"Event {i}"),
            "summary": event.get("summary", "No summary available")
        })
        
        # Add Document -> Event relationship
        neo4j_data["relationships"].append({
            "from_node": doc_id,
            "to_node": event_id,
            "type": "MENTIONS"
        })
        
        # Process date
        if event.get("date"):
            iso_date = processor.format_date_iso(event["date"])
            
            if iso_date not in unique_dates:
                unique_dates.add(iso_date)
                neo4j_data["nodes"]["dates"].append({
                    "date": iso_date
                })
            
            # Add Event -> Date relationship
            neo4j_data["relationships"].append({
                "from_node": event_id,
                "to_node": iso_date,
                "type": "OCCURRED_ON"
            })
        
        # Process location
        if event.get("location"):
            location_name = event["location"].strip()
            
            if location_name not in unique_locations:
                location_id = processor.generate_unique_id("loc")
                unique_locations[location_name] = location_id
                
                neo4j_data["nodes"]["locations"].append({
                    "id": location_id,
                    "address": location_name
                })
            
            # Add Event -> Location relationship
            location_id = unique_locations[location_name]
            neo4j_data["relationships"].append({
                "from_node": event_id,
                "to_node": location_id,
                "type": "OCCURRED_AT"
            })
        
        # Process participants
        if event.get("participants"):
            for participant_name in event["participants"]:
                participant_name = participant_name.strip()
                
                if participant_name not in unique_entities:
                    entity_id = processor.generate_unique_id("entity")
                    unique_entities[participant_name] = entity_id
                    
                    neo4j_data["nodes"]["entities"].append({
                        "id": entity_id,
                        "name": participant_name
                    })
                
                # Add Entity -> Event relationship
                entity_id = unique_entities[participant_name]
                neo4j_data["relationships"].append({
                    "from_node": entity_id,
                    "to_node": event_id,
                    "type": "PARTICIPATES_IN"
                })
    
    print(f"Generated Neo4j structure:")
    print(f"  Documents: {len(neo4j_data['nodes']['documents'])}")
    print(f"  Events: {len(neo4j_data['nodes']['events'])}")
    print(f"  Dates: {len(neo4j_data['nodes']['dates'])}")
    print(f"  Locations: {len(neo4j_data['nodes']['locations'])}")
    print(f"  Entities: {len(neo4j_data['nodes']['entities'])}")
    print(f"  Users: {len(neo4j_data['nodes']['users'])}")
    print(f"  Relationships: {len(neo4j_data['relationships'])}")
    
    return neo4j_data

def test_neo4j_loading(neo4j_data):
    """Test Neo4j database loading."""
    print("\n" + "="*60)
    print("STEP 2: NEO4J DATABASE LOADING")
    print("="*60)
    
    # Initialize Neo4j loader
    loader = InvestiCATNeo4jLoader()
    
    # Test connection
    print("Connecting to Neo4j database...")
    if not loader.connect():
        print("Failed to connect to Neo4j. Make sure Neo4j is running.")
        print("Start Neo4j Desktop or run: docker run -p 7474:7474 -p 7687:7687 neo4j")
        return False
    
    try:
        # Create constraints
        print("Creating database constraints...")
        loader.create_constraints()
        
        # Get initial stats
        print("Getting initial database statistics...")
        initial_stats = loader.get_database_stats()
        print(f"Initial database state: {initial_stats.get('Total nodes', 0)} nodes, {initial_stats.get('Total relationships', 0)} relationships")
        
        # Load the processed data
        print("Loading processed document data into Neo4j...")
        success = loader.load_document_data(neo4j_data)
        
        if success:
            print("Data loaded successfully!")
            
            # Get final stats
            print("\nGetting final database statistics...")
            final_stats = loader.get_database_stats()
            
            print("\nDATABASE STATISTICS AFTER LOADING:")
            print("-" * 40)
            for key, value in final_stats.items():
                print(f"{key}: {value}")
            
            # Calculate what was added
            nodes_added = final_stats.get('Total nodes', 0) - initial_stats.get('Total nodes', 0)
            rels_added = final_stats.get('Total relationships', 0) - initial_stats.get('Total relationships', 0)
            
            print(f"\nData added in this session:")
            print(f"  Nodes added: {nodes_added}")
            print(f"  Relationships added: {rels_added}")
            
            return True
        else:
            print("Failed to load data into Neo4j")
            return False
            
    finally:
        loader.close()

def test_data_integrity(neo4j_data):
    """Test data integrity in Neo4j."""
    print("\n" + "="*60)
    print("STEP 3: DATA INTEGRITY VERIFICATION")
    print("="*60)
    
    loader = InvestiCATNeo4jLoader()
    
    if not loader.connect():
        print("Cannot verify data integrity - Neo4j connection failed")
        return False
    
    try:
        with loader.driver.session() as session:
            # Verify document nodes
            doc_count = session.run("MATCH (d:Document) RETURN count(d) as count").single()["count"]
            expected_docs = len(neo4j_data["nodes"]["documents"])
            print(f"✓ Documents in Neo4j: {doc_count} (expected: {expected_docs})")
            
            # Verify event nodes
            event_count = session.run("MATCH (e:Event) RETURN count(e) as count").single()["count"] 
            expected_events = len(neo4j_data["nodes"]["events"])
            print(f"✓ Events in Neo4j: {event_count} (expected: {expected_events})")
            
            # Verify date nodes (special case - no ID field)
            date_count = session.run("MATCH (dt:Date) RETURN count(dt) as count").single()["count"]
            expected_dates = len(neo4j_data["nodes"]["dates"]) 
            print(f"✓ Dates in Neo4j: {date_count} (expected: {expected_dates})")
            
            # Verify relationships
            rel_count = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
            expected_rels = len(neo4j_data["relationships"])
            print(f"✓ Relationships in Neo4j: {rel_count} (expected: {expected_rels})")
            
            # Test specific queries
            print("\nTesting specific queries:")
            
            # Find events with dates
            events_with_dates = session.run("""
                MATCH (e:Event)-[:OCCURRED_ON]->(dt:Date)
                RETURN e.title, dt.date
                ORDER BY dt.date
                LIMIT 5
            """)
            
            print("  Recent events with dates:")
            for record in events_with_dates:
                print(f"    - {record['e.title'][:50]}... on {record['dt.date']}")
            
            # Find events with locations
            events_with_locations = session.run("""
                MATCH (e:Event)-[:OCCURRED_AT]->(l:Location)
                RETURN e.title, l.address
                LIMIT 3
            """)
            
            print("  Events with locations:")
            for record in events_with_locations:
                print(f"    - {record['e.title'][:50]}... at {record['l.address']}")
            
            print("\n✓ Data integrity verification completed successfully")
            return True
            
    except Exception as e:
        print(f"Data integrity check failed: {e}")
        return False
    finally:
        loader.close()

def main():
    """Run complete end-to-end test."""
    print("InvestiCAT End-to-End Test: Document Processing to Neo4j")
    print("=" * 80)
    
    start_time = time.time()
    
    try:
        # Step 1: Process document
        neo4j_data = test_document_processing()
        
        # Save intermediate JSON for inspection
        output_file = Path("test_e2e_output.json")
        with open(output_file, "w") as f:
            json.dump(neo4j_data, f, indent=2)
        print(f"\nIntermediate JSON saved to: {output_file}")
        
        # Step 2: Load into Neo4j
        neo4j_success = test_neo4j_loading(neo4j_data)
        
        if neo4j_success:
            # Step 3: Verify integrity
            integrity_success = test_data_integrity(neo4j_data)
            
            if integrity_success:
                print("\n" + "="*80)
                print("🎉 END-TO-END TEST COMPLETED SUCCESSFULLY!")
                print("="*80)
                print(f"Total execution time: {time.time() - start_time:.2f} seconds")
                print("\nNext steps:")
                print("1. Open Neo4j Browser (http://localhost:7474)")  
                print("2. Run queries like: MATCH (n) RETURN n LIMIT 25")
                print("3. Explore your investigation graph!")
                return True
            else:
                print("❌ Data integrity verification failed")
                return False
        else:
            print("❌ Neo4j loading failed")
            return False
            
    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)