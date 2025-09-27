#!/usr/bin/env python3
"""
Example usage of the InvestiCAT Document Processor
Demonstrates processing different document types and use cases.
"""

import json
import os
from document_processor_neo4j import InvestiCATProcessor

def example_pdf_processing():
    """Example: Process a PDF document."""
    print("📄 Example 1: PDF Document Processing")
    print("-" * 40)
    
    processor = InvestiCATProcessor()
    
    try:
        result = processor.process_document(
            "test_investigation.pdf",
            "Corporate Merger Timeline Analysis"
        )
        
        # Save results
        with open("pdf_analysis.json", "w") as f:
            json.dump(result, f, indent=2)
        
        print(f"✅ PDF processed successfully")
        print(f"   Events: {len(result['nodes']['events'])}")
        print(f"   Entities: {len(result['nodes']['entities'])}")
        print(f"   Output: pdf_analysis.json")
        
    except Exception as e:
        print(f"❌ PDF processing failed: {e}")

def example_batch_processing():
    """Example: Batch process multiple documents."""
    print("\n📁 Example 2: Batch Processing")
    print("-" * 40)
    
    processor = InvestiCATProcessor()
    
    # Simulate multiple documents
    documents = [
        ("test_investigation.pdf", "Document 1 Investigation"),
        # Add more documents here as needed
    ]
    
    results = {}
    
    for doc_path, investigation_title in documents:
        if os.path.exists(doc_path):
            try:
                result = processor.process_document(doc_path, investigation_title)
                results[doc_path] = result
                print(f"✅ Processed: {doc_path}")
            except Exception as e:
                print(f"❌ Failed: {doc_path} - {e}")
                results[doc_path] = {"error": str(e)}
    
    # Save batch results
    with open("batch_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Batch processing complete: batch_results.json")

def example_neo4j_import_queries():
    """Example: Generate Neo4j import queries."""
    print("\n🗄️  Example 3: Neo4j Import Queries")
    print("-" * 40)
    
    # Load processed data
    if os.path.exists("pdf_analysis.json"):
        with open("pdf_analysis.json", "r") as f:
            data = json.load(f)
        
        # Generate Cypher queries
        queries = []
        
        # Create nodes
        for node_type, nodes in data['nodes'].items():
            if nodes:
                if node_type == 'cats':
                    query = "// Create Cat nodes\n"
                    for node in nodes:
                        query += f"CREATE (:Cat {{id: '{node['id']}', title: '{node['title']}'}})\n"
                    queries.append(query)
                
                elif node_type == 'events':
                    query = "// Create Event nodes\n"
                    for node in nodes:
                        title = node['title'].replace("'", "\\'")
                        summary = node['summary'].replace("'", "\\'")
                        query += f"CREATE (:Event {{id: '{node['id']}', title: '{title}', summary: '{summary}'}})\n"
                    queries.append(query)
        
        # Save queries
        with open("neo4j_import.cypher", "w") as f:
            f.write("\n".join(queries))
        
        print("✅ Neo4j import queries generated: neo4j_import.cypher")
    else:
        print("❌ No processed data found. Run PDF processing first.")

def example_api_usage():
    """Example: Using the processor as an API."""
    print("\n🔧 Example 4: API Usage")
    print("-" * 40)
    
    # Function that could be called from web API
    def process_document_api(file_path, title):
        """API function to process a document."""
        processor = InvestiCATProcessor()
        
        try:
            result = processor.process_document(file_path, title)
            return {
                "status": "success",
                "data": result,
                "summary": {
                    "events": len(result['nodes']['events']),
                    "entities": len(result['nodes']['entities']),
                    "relationships": len(result['relationships'])
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "data": None
            }
    
    # Test API function
    if os.path.exists("test_investigation.pdf"):
        api_result = process_document_api("test_investigation.pdf", "API Test Investigation")
        
        if api_result["status"] == "success":
            print("✅ API call successful")
            print(f"   Events: {api_result['summary']['events']}")
            print(f"   Entities: {api_result['summary']['entities']}")
            print(f"   Relationships: {api_result['summary']['relationships']}")
        else:
            print(f"❌ API call failed: {api_result['error']}")

def main():
    """Run all examples."""
    print("🚀 InvestiCAT Document Processor Examples")
    print("=" * 50)
    
    # Run examples
    example_pdf_processing()
    example_batch_processing()
    example_neo4j_import_queries()
    example_api_usage()
    
    print("\n🎉 All examples completed!")
    print("\nGenerated files:")
    generated_files = [
        "pdf_analysis.json",
        "batch_results.json", 
        "neo4j_import.cypher"
    ]
    
    for filename in generated_files:
        if os.path.exists(filename):
            print(f"   ✅ {filename}")
        else:
            print(f"   ❌ {filename} (not generated)")

if __name__ == "__main__":
    main()