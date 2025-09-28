#!/usr/bin/env python3
"""
InvestiCAT Document Processor CLI
Command-line interface for the ETL document processor
"""

import sys
import json
import argparse
from pathlib import Path
from document_processor_neo4j import InvestiCATProcessor

def main():
    parser = argparse.ArgumentParser(
        description="InvestiCAT Document Processor - ETL for Timeline Extraction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.pdf                          # Process PDF document
  %(prog)s document.docx -o output.json         # Process DOCX with custom output
  %(prog)s file.pdf --openai-key YOUR_KEY      # Use OpenAI for extraction
  %(prog)s file.pdf --pretty                   # Pretty print output to console
  %(prog)s file.pdf --load-neo4j               # Process and load into Neo4j
  %(prog)s file.pdf --load-neo4j --neo4j-clear # Clear database, then load

Output:
  Generates Neo4j-compatible JSON with document-level nodes and relationships.
  Includes: Document, Events, Dates, Locations, Entities, Users
  
Note: 
  This ETL processor handles document-level extraction only.
  Cat nodes and investigation management are handled by the frontend/API.
        """
    )
    
    parser.add_argument(
        'document',
        help='Path to PDF or DOCX document to process'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output JSON file path (default: auto-generated)',
        type=Path
    )
    
    parser.add_argument(
        '--openai-key',
        help='OpenAI API key for enhanced event extraction'
    )
    
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty print output to console instead of saving'
    )
    
    parser.add_argument(
        '--summary',
        action='store_true', 
        help='Show processing summary'
    )
    
    parser.add_argument(
        '--load-neo4j',
        action='store_true',
        help='Load processed data directly into Neo4j database'
    )
    
    parser.add_argument(
        '--neo4j-uri', 
        default='neo4j://localhost:7687',
        help='Neo4j database URI (default: neo4j://localhost:7687)'
    )
    
    parser.add_argument(
        '--neo4j-clear',
        action='store_true',
        help='Clear Neo4j database before loading (use with --load-neo4j)'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    input_file = Path(args.document)
    if not input_file.exists():
        print(f"Error: Document not found: {input_file}")
        sys.exit(1)
    
    if input_file.suffix.lower() not in ['.pdf', '.docx']:
        print(f"Error: Unsupported file type. Only PDF and DOCX supported.")
        sys.exit(1)
    
    # Initialize processor
    print(f"Processing document: {input_file.name}")
    processor = InvestiCATProcessor(openai_api_key=args.openai_key)
    
    try:
        # Process document
        result = processor.process_document(str(input_file))
        
        # Handle output
        if args.pretty:
            print("\n" + "="*60)
            print("NEO4J DOCUMENT STRUCTURE")
            print("="*60)
            print(json.dumps(result, indent=2))
        else:
            # Determine output file
            if args.output:
                output_file = args.output
            else:
                output_file = input_file.with_suffix('.neo4j.json')
            
            # Save results
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            print(f"Neo4j structure saved to: {output_file}")
        
        # Show summary if requested
        if args.summary or args.pretty:
            nodes = result["nodes"]
            relationships = result["relationships"]
            
            print(f"\n" + "="*40)
            print("PROCESSING SUMMARY")
            print("="*40)
            print(f"Document: {input_file.name}")
            print(f"Events extracted: {len(nodes['events'])}")
            print(f"Dates found: {len(nodes['dates'])}")
            print(f"Locations found: {len(nodes['locations'])}")
            print(f"Entities found: {len(nodes['entities'])}")
            print(f"Total relationships: {len(relationships)}")
            
            # Show relationship breakdown
            rel_types = {}
            for rel in relationships:
                rel_type = rel['type']
                rel_types[rel_type] = rel_types.get(rel_type, 0) + 1
            
            if rel_types:
                print(f"\nRelationships by type:")
                for rel_type, count in sorted(rel_types.items()):
                    print(f"  {rel_type}: {count}")
            
            print(f"\nScope: Document-level ETL (Cat nodes handled by frontend)")
    
        # Load into Neo4j if requested
        if args.load_neo4j:
            print(f"\n" + "="*40)
            print("NEO4J DATABASE LOADING")
            print("="*40)
            
            try:
                from neo4j_loader import InvestiCATNeo4jLoader
                
                # Initialize Neo4j loader
                loader = InvestiCATNeo4jLoader(uri=args.neo4j_uri)
                
                # Connect to Neo4j
                if loader.connect():
                    # Clear database if requested
                    if args.neo4j_clear:
                        print("Clearing Neo4j database...")
                        loader.clear_database(confirm=True)
                    
                    # Create constraints
                    loader.create_constraints()
                    
                    # Load data
                    print("Loading data into Neo4j...")
                    success = loader.load_document_data(result)
                    
                    if success:
                        print("Data loaded successfully into Neo4j!")
                        
                        # Show Neo4j stats
                        stats = loader.get_database_stats()
                        print("\nNeo4j Database Statistics:")
                        for key, value in stats.items():
                            print(f"  {key}: {value}")
                        
                        print(f"\nAccess Neo4j Browser: http://localhost:7474")
                    else:
                        print("Failed to load data into Neo4j")
                    
                    loader.close()
                else:
                    print("Failed to connect to Neo4j database")
                    print("Make sure Neo4j is running and credentials are correct")
                    
            except ImportError:
                print("Neo4j loader not available. Install with: pip install neo4j")
            except Exception as e:
                print(f"Neo4j loading error: {e}")
    
    except Exception as e:
        print(f"Error processing document: {e}")
        if args.pretty:  # Show more detail in pretty mode
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()