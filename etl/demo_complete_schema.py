#!/usr/bin/env python3
"""
Demonstration script showing all 7 Neo4j node types in InvestiCAT output.
"""

from document_processor_neo4j import InvestiCATProcessor
import json

def demonstrate_all_node_types():
    """Show all 7 node types in the output."""
    
    print("🎯 InvestiCAT Neo4j Schema - All 7 Node Types")
    print("=" * 50)
    
    processor = InvestiCATProcessor(openai_api_key=None)  # Use fallback
    
    try:
        result = processor.process_document(
            "test_investigation.pdf",
            "Complete Schema Demonstration"
        )
        
        # Display all node types
        for node_type, nodes in result['nodes'].items():
            print(f"\n{node_type.upper()}: {len(nodes)} nodes")
            if nodes:
                sample = nodes[0]
                if node_type == 'users':
                    print(f"  Sample: {sample['name']} ({sample['email']})")
                elif node_type == 'cats':
                    print(f"  Sample: {sample['title']}")
                elif node_type == 'documents':
                    print(f"  Sample: {sample['filename']}")
                elif node_type == 'events':
                    print(f"  Sample: {sample['title'][:50]}...")
                elif node_type == 'entities':
                    print(f"  Sample: {sample['name']}")
                elif node_type == 'locations':
                    print(f"  Sample: {sample['address']}")
                elif node_type == 'dates':
                    print(f"  Sample: {sample['date']}")
        
        # Display relationship types
        print(f"\nRELATIONSHIPS: {len(result['relationships'])} total")
        rel_types = set(rel['type'] for rel in result['relationships'])
        print(f"Types: {', '.join(sorted(rel_types))}")
        
        # Verify all 7 node types are present
        expected_types = ['cats', 'documents', 'events', 'dates', 'locations', 'entities', 'users']
        missing_types = set(expected_types) - set(result['nodes'].keys())
        
        if not missing_types:
            print("\n✅ SUCCESS: All 7 required node types are present!")
        else:
            print(f"\n❌ MISSING: {', '.join(missing_types)}")
        
        # Check for OWNS relationship
        owns_relations = [rel for rel in result['relationships'] if rel['type'] == 'OWNS']
        if owns_relations:
            print("✅ SUCCESS: User OWNS Cat relationship found!")
        else:
            print("❌ MISSING: User OWNS Cat relationship not found!")
        
        return result
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return None

if __name__ == "__main__":
    demonstrate_all_node_types()