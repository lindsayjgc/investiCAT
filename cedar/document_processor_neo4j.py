"""
Mock InvestiCAT Processor for Cedar Demo
Simulates the existing ETL pipeline for demonstration purposes.
"""

import json
from typing import Dict, List, Any
from pathlib import Path

class InvestiCATProcessor:
    """
    Mock version of the InvestiCAT document processor for demonstration.
    In production, this would be imported from ../etl/document_processor_neo4j.py
    """
    
    def process_document(self, file_path: str, investigation_title: str) -> Dict[str, Any]:
        """
        Mock document processing that returns simulated timeline data.
        
        Args:
            file_path: Path to document (simulated)
            investigation_title: Title for the investigation
            
        Returns:
            Dict with timeline data and Neo4j output
        """
        print(f"📄 [MOCK ETL] Processing document: {file_path}")
        print(f"📋 [MOCK ETL] Investigation: {investigation_title}")
        
        # Load test data if available, otherwise create sample data
        test_data_path = Path("test_timeline_data.json")
        if test_data_path.exists():
            with open(test_data_path, 'r') as f:
                test_data = json.load(f)
                test_data['investigation_title'] = investigation_title
                test_data['source_file'] = str(file_path)
                print(f"✅ [MOCK ETL] Loaded {len(test_data['timeline'])} events from test data")
                return test_data
        
        # Fallback sample data
        timeline_data = [
            {
                "date": "2024-01-15",
                "event": "Initial investigation event",
                "entity": "Sample Entity",
                "location": "Sample Location"
            }
        ]
        
        return {
            "document_id": f"doc_{hash(file_path)}",
            "investigation_title": investigation_title,
            "source_file": str(file_path),
            "timeline": timeline_data,
            "neo4j_output": {
                "nodes": [
                    {"id": "doc_001", "label": "Document", "properties": {"title": investigation_title}}
                ],
                "relationships": []
            }
        }