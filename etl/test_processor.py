#!/usr/bin/env python3
"""
Test script to validate InvestiCAT processor output structure.
"""

import json
import sys
from document_processor_neo4j import InvestiCATProcessor

def validate_neo4j_structure(data):
    """Validate that the output contains all required Neo4j schema elements."""
    
    print("🔍 Validating Neo4j Structure...")
    
    # Check top-level structure
    required_keys = ['nodes', 'relationships']
    for key in required_keys:
        if key not in data:
            print(f"❌ Missing top-level key: {key}")
            return False
        else:
            print(f"✅ Found: {key}")
    
    # Check node types
    required_node_types = ['cats', 'documents', 'events', 'dates', 'locations', 'entities', 'users']
    for node_type in required_node_types:
        if node_type not in data['nodes']:
            print(f"❌ Missing node type: {node_type}")
            return False
        elif len(data['nodes'][node_type]) == 0:
            print(f"⚠️  Empty node type: {node_type}")
        else:
            print(f"✅ {node_type}: {len(data['nodes'][node_type])} nodes")
    
    # Check node structure
    node_checks = {
        'cats': ['id', 'title'],
        'documents': ['id', 'filename'],
        'events': ['id', 'title', 'summary'],
        'locations': ['id', 'address'],
        'entities': ['id', 'name'],
        'users': ['id', 'email', 'name', 'password']
    }
    
    for node_type, required_fields in node_checks.items():
        if data['nodes'][node_type]:  # Only check if nodes exist
            sample_node = data['nodes'][node_type][0]
            for field in required_fields:
                if field not in sample_node:
                    print(f"❌ {node_type} missing field: {field}")
                    return False
    
    # Check relationships structure
    if data['relationships']:
        sample_rel = data['relationships'][0]
        required_rel_fields = ['from_node', 'to_node', 'type']
        for field in required_rel_fields:
            if field not in sample_rel:
                print(f"❌ Relationship missing field: {field}")
                return False
        print(f"✅ relationships: {len(data['relationships'])} relationships")
    
    # Check relationship types
    expected_rel_types = ['HAS_DOCUMENT', 'HAS_EVENT', 'MENTIONS', 'OCCURRED_ON', 'OCCURRED_AT', 'PARTICIPATES_IN', 'OWNS']
    found_rel_types = set(rel['type'] for rel in data['relationships'])
    
    print(f"📊 Found relationship types: {', '.join(sorted(found_rel_types))}")
    
    missing_types = set(expected_rel_types) - found_rel_types
    if missing_types:
        print(f"⚠️  Missing relationship types: {', '.join(missing_types)}")
    
    print("✅ Neo4j structure validation complete!")
    return True

def test_processor():
    """Test the processor with the test document."""
    
    print("🧪 Testing InvestiCAT Document Processor")
    print("=" * 50)
    
    # Initialize processor
    processor = InvestiCATProcessor(openai_api_key=None)  # Use fallback only
    
    try:
        # Process test document
        result = processor.process_document(
            "test_investigation.pdf",
            "Validation Test Investigation"
        )
        
        # Validate structure
        if validate_neo4j_structure(result):
            print("\n🎉 All validation tests passed!")
            
            # Print summary
            nodes = result['nodes']
            print(f"\n📋 Final Summary:")
            print(f"   Investigation: Validation Test Investigation")
            print(f"   Document: test_investigation.pdf")
            print(f"   Total nodes: {sum(len(nodes[nt]) for nt in nodes)}")
            print(f"   Total relationships: {len(result['relationships'])}")
            
            return True
        else:
            print("\n❌ Validation failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_processor()
    sys.exit(0 if success else 1)