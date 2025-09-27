#!/usr/bin/env python3
"""
InvestiCAT Document Processor CLI
Command-line interface for processing documents into Neo4j format.
"""

import argparse
import json
import sys
from pathlib import Path
from document_processor_neo4j import InvestiCATProcessor

def main():
    """Command-line interface for document processing."""
    parser = argparse.ArgumentParser(
        description="InvestiCAT Document Processor - Extract timeline events for Neo4j",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py document.pdf -t "Corporate Investigation"
  python cli.py report.docx -t "Merger Analysis" -o output.json
  python cli.py file.pdf -t "Investigation" --no-ai
        """
    )
    
    parser.add_argument(
        "file",
        help="Path to PDF or DOCX file to process"
    )
    
    parser.add_argument(
        "-t", "--title",
        required=True,
        help="Investigation title (required)"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output JSON file path (default: print to stdout)"
    )
    
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Use fallback extraction only (no OpenAI)"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress messages"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"File not found: {args.file}", file=sys.stderr)
        return 1
    
    if file_path.suffix.lower() not in ['.pdf', '.docx']:
        print(f"Unsupported file type: {file_path.suffix}", file=sys.stderr)
        print("Only PDF and DOCX files are supported", file=sys.stderr)
        return 1
    
    try:
        # Initialize processor
        api_key = None if args.no_ai else None  # Uses default key from module
        processor = InvestiCATProcessor(openai_api_key=api_key)
        
        # Suppress progress if quiet
        if args.quiet:
            import contextlib
            import io
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                result = processor.process_document(str(file_path), args.title)
        else:
            result = processor.process_document(str(file_path), args.title)
        
        # Output results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            if not args.quiet:
                print(f"\n Results saved to: {args.output}")
        else:
            print(json.dumps(result, indent=2))
        
        # Print summary unless quiet
        if not args.quiet and args.output:
            nodes = result["nodes"]
            print(f"\n Processing Summary:")
            print(f"   Investigation: {args.title}")
            print(f"   Document: {file_path.name}")
            print(f"   Events extracted: {len(nodes['events'])}")
            print(f"   Entities found: {len(nodes['entities'])}")
            print(f"   Dates identified: {len(nodes['dates'])}")
            print(f"   Locations found: {len(nodes['locations'])}")
            print(f"   Users created: {len(nodes['users'])}")
            print(f"   Total relationships: {len(result['relationships'])}")

        return 0
        
    except Exception as e:
        print(f"Processing failed: {e}", file=sys.stderr)
        if not args.quiet:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())