"""
Create a simple test PDF for demonstrating Cedar InvestiCAT integration
"""

import json
from pathlib import Path

def create_test_document_data():
    """Create test document data that simulates what the ETL processor would return."""
    
    test_timeline = [
        {
            "date": "2024-01-15",
            "event": "John Smith appointed as CEO of TechCorp",
            "entity": "John Smith",
            "location": "New York"
        },
        {
            "date": "2024-02-20",
            "event": "Board meeting to discuss merger proposal",
            "entity": "Board of Directors", 
            "location": "San Francisco"
        },
        {
            "date": "2024-02-25",
            "event": "Jane Doe hired as Chief Financial Officer",
            "entity": "Jane Doe",
            "location": "New York"
        },
        {
            "date": "2024-03-10",
            "event": "Merger announcement with rival company",
            "entity": "John Smith",
            "location": "New York"
        },
        {
            "date": "2024-03-15",
            "event": "Regulatory filing submitted for merger approval",
            "entity": "Legal Department",
            "location": "Washington DC"
        },
        {
            "date": "2024-03-20",
            "event": "Employee town hall meeting about merger",
            "entity": "John Smith",
            "location": "San Francisco"
        },
        {
            "date": "2024-04-01",
            "event": "Due diligence process begins",
            "entity": "Jane Doe",
            "location": "New York"
        },
        {
            "date": "2024-04-15",
            "event": "Shareholder meeting to vote on merger",
            "entity": "Board of Directors",
            "location": "New York"
        }
    ]
    
    return {
        "document_id": "test_corporate_investigation",
        "investigation_title": "Corporate Merger Investigation",
        "timeline": test_timeline,
        "processed_at": "2025-09-27T19:30:00",
        "neo4j_output": {
            "nodes": [
                {"id": "doc_001", "label": "Document", "properties": {"title": "Corporate Merger Investigation"}},
                {"id": "john_smith", "label": "Entity", "properties": {"name": "John Smith", "role": "CEO"}},
                {"id": "jane_doe", "label": "Entity", "properties": {"name": "Jane Doe", "role": "CFO"}},
                {"id": "board", "label": "Entity", "properties": {"name": "Board of Directors", "role": "Governance"}}
            ],
            "relationships": [
                {"from": "doc_001", "to": "john_smith", "type": "MENTIONS"},
                {"from": "doc_001", "to": "jane_doe", "type": "MENTIONS"},
                {"from": "doc_001", "to": "board", "type": "MENTIONS"}
            ]
        }
    }

if __name__ == "__main__":
    # Create test data
    test_data = create_test_document_data()
    
    # Save to file for testing
    with open("test_timeline_data.json", "w") as f:
        json.dump(test_data, f, indent=2)
    
    print("✅ Test document data created: test_timeline_data.json")
    print(f"📊 Timeline contains {len(test_data['timeline'])} events")
    print("🔍 Ready for Cedar InvestiCAT demo!")