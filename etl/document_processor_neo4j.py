#!/usr/bin/env python3
"""
InvestiCAT Document Processor for Neo4j Timeline Tool
Processes PDF/DOCX documents and outputs structured data for Neo4j graph database.
"""

import os
import json
import uuid
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Document parsing libraries
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    from docx import Document as DocxDocument
except ImportError:
    DocxDocument = None

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Configuration
OPENAI_API_KEY = "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"

class InvestiCATProcessor:
    """Document processor for investigative journalism timeline extraction."""
    
    def __init__(self, openai_api_key: str = None):
        """Initialize the processor with OpenAI client."""
        self.openai_client = None
        
        if OPENAI_AVAILABLE and (openai_api_key or OPENAI_API_KEY):
            try:
                api_key = openai_api_key or OPENAI_API_KEY
                self.openai_client = OpenAI(api_key=api_key)
                print("OpenAI client initialized successfully")
            except Exception as e:
                print(f"OpenAI initialization failed: {e}")
                print("Will use fallback event extraction")
    
    def parse_pdf(self, file_path: str) -> str:
        """Extract text from PDF using pdfplumber."""
        if not pdfplumber:
            raise ImportError("pdfplumber not installed. Run: pip install pdfplumber")
        
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Failed to parse PDF: {e}")
    
    def parse_docx(self, file_path: str) -> str:
        """Extract text from DOCX using python-docx."""
        if not DocxDocument:
            raise ImportError("python-docx not installed. Run: pip install python-docx")
        
        try:
            doc = DocxDocument(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Failed to parse DOCX: {e}")
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from PDF or DOCX file."""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            return self.parse_pdf(file_path)
        elif file_ext == '.docx':
            return self.parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}. Only PDF and DOCX supported.")
    
    def extract_events_with_openai(self, text: str) -> List[Dict[str, Any]]:
        """Extract timeline events using OpenAI API."""
        if not self.openai_client:
            return self.extract_events_fallback(text)
        
        try:
            prompt = f"""
Extract timeline events from this investigative document. For each significant event, provide:
- title: Brief descriptive title (max 80 chars)
- summary: Detailed description
- date: Date in YYYY-MM-DD format (null if not found)
- location: Specific location/address (null if not found)
- participants: List of people/organizations involved

Focus on: meetings, transactions, announcements, approvals, signings, filings, investigations.

Return as JSON array:
[{{"title": "Event Title", "summary": "Detailed description", "date": "2024-01-15", "location": "New York City", "participants": ["John Doe", "Acme Corp"]}}]

Document text:
{text[:4000]}
"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean JSON response
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            events = json.loads(content)
            return events if isinstance(events, list) else []
            
        except Exception as e:
            print(f"OpenAI extraction failed: {e}")
            return self.extract_events_fallback(text)
    
    def extract_events_fallback(self, text: str) -> List[Dict[str, Any]]:
        """Fallback event extraction using pattern matching."""
        events = []
        sentences = [s.strip() for s in text.replace('\n', ' ').split('.') if len(s.strip()) > 15]
        
        # Event indicators
        indicators = [
            'announced', 'signed', 'acquired', 'merged', 'agreed', 'approved',
            'filed', 'completed', 'finalized', 'reported', 'meeting', 'deal'
        ]
        
        # Date patterns
        date_patterns = [
            r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}'
        ]
        
        for sentence in sentences[:10]:  # Limit to first 10 relevant sentences
            sentence_lower = sentence.lower()
            
            if any(indicator in sentence_lower for indicator in indicators):
                # Extract date
                date_found = None
                for pattern in date_patterns:
                    match = re.search(pattern, sentence)
                    if match:
                        # Convert to standard format (simplified)
                        date_found = "2024-01-15"  # Placeholder - would need proper date parsing
                        break
                
                # Extract location
                location_match = re.search(r'\b(?:in|at)\s+([A-Z][a-zA-Z\s,]+?)(?:[,.]|$)', sentence)
                location = location_match.group(1).strip() if location_match else None
                if location and len(location) > 50:
                    location = location[:50]
                
                # Extract participants (proper nouns)
                participants = []
                participant_matches = re.findall(r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*(?:\s+(?:Inc|Ltd|Corp|LLC))?\b', sentence)
                for p in participant_matches[:5]:  # Limit to 5
                    if len(p) > 2 and p not in ['The', 'This', 'That']:
                        participants.append(p)
                
                title = sentence[:80] + "..." if len(sentence) > 80 else sentence
                
                events.append({
                    "title": title,
                    "summary": sentence,
                    "date": date_found,
                    "location": location,
                    "participants": participants
                })
        
        return events[:8]  # Return max 8 events
    
    def generate_unique_id(self, prefix: str) -> str:
        """Generate unique ID with prefix."""
        return f"{prefix}_{str(uuid.uuid4())[:8]}"
    
    def process_document(self, file_path: str, investigation_title: str) -> Dict[str, Any]:
        """
        Main function: Process document and return Neo4j-compatible data structure.
        
        Args:
            file_path: Path to PDF or DOCX file
            investigation_title: Title of the investigation
            
        Returns:
            Dict with nodes and relationships in Neo4j format
        """
        print(f"Processing: {Path(file_path).name}")
        print(f"Investigation: {investigation_title}")
        
        # Extract text
        try:
            text = self.extract_text(file_path)
            print(f"Extracted {len(text)} characters")
        except Exception as e:
            raise Exception(f"Text extraction failed: {e}")
        
        # Extract events
        print("🎯 Extracting timeline events...")
        events = self.extract_events_with_openai(text)
        print(f"Found {len(events)} events")
        
        # Generate IDs
        cat_id = self.generate_unique_id("cat")
        doc_id = self.generate_unique_id("doc")
        filename = Path(file_path).name
        
        # Initialize Neo4j structure
        neo4j_data = {
            "nodes": {
                "cats": [{"id": cat_id, "title": investigation_title}],
                "documents": [{"id": doc_id, "filename": filename}],
                "events": [],
                "dates": [],
                "locations": [],
                "entities": [],
                "users": [{"id": "user_1", "email": "journalist@example.com", "name": "System User", "password": "placeholder"}]
            },
            "relationships": [
                # Cat -> Document relationship
                {"from_node": cat_id, "to_node": doc_id, "type": "HAS_DOCUMENT"},
                # User -> Cat relationship
                {"from_node": "user_1", "to_node": cat_id, "type": "OWNS"}
            ]
        }
        
        # Track unique items
        unique_dates = set()
        unique_locations = {}
        unique_entities = {}
        date_id_counter = 1
        location_id_counter = 1
        entity_id_counter = 1
        
        # Process each event
        for i, event in enumerate(events, 1):
            event_id = f"event_{i}"
            
            # Add event node
            neo4j_data["nodes"]["events"].append({
                "id": event_id,
                "title": event["title"],
                "summary": event["summary"]
            })
            
            # Add Cat -> Event relationship
            neo4j_data["relationships"].append({
                "from_node": cat_id,
                "to_node": event_id,
                "type": "HAS_EVENT"
            })
            
            # Add Document -> Event relationship
            neo4j_data["relationships"].append({
                "from_node": doc_id,
                "to_node": event_id,
                "type": "MENTIONS"
            })
            
            # Process date
            if event.get("date"):
                date_str = event["date"]
                if date_str not in unique_dates:
                    unique_dates.add(date_str)
                    date_id = f"date_{date_id_counter}"
                    date_id_counter += 1
                    
                    # Convert to ISO format
                    try:
                        dt = datetime.strptime(date_str, "%Y-%m-%d")
                        iso_date = dt.isoformat() + "Z"
                    except:
                        iso_date = f"{date_str}T00:00:00Z"
                    
                    neo4j_data["nodes"]["dates"].append({
                        "id": date_id, 
                        "date": iso_date
                    })
                    
                    # Add Event -> Date relationship
                    neo4j_data["relationships"].append({
                        "from_node": event_id,
                        "to_node": date_id,
                        "type": "OCCURRED_ON"
                    })
            
            # Process location
            if event.get("location"):
                location = event["location"]
                if location not in unique_locations:
                    location_id = f"loc_{location_id_counter}"
                    location_id_counter += 1
                    unique_locations[location] = location_id
                    
                    neo4j_data["nodes"]["locations"].append({
                        "id": location_id,
                        "address": location
                    })
                    
                    # Add Event -> Location relationship
                    neo4j_data["relationships"].append({
                        "from_node": event_id,
                        "to_node": location_id,
                        "type": "OCCURRED_AT"
                    })
            
            # Process participants (entities)
            if event.get("participants"):
                for participant in event["participants"]:
                    if participant not in unique_entities:
                        entity_id = f"entity_{entity_id_counter}"
                        entity_id_counter += 1
                        unique_entities[participant] = entity_id
                        
                        neo4j_data["nodes"]["entities"].append({
                            "id": entity_id,
                            "name": participant
                        })
                    
                    # Add Entity -> Event relationship
                    entity_id = unique_entities[participant]
                    neo4j_data["relationships"].append({
                        "from_node": entity_id,
                        "to_node": event_id,
                        "type": "PARTICIPATES_IN"
                    })
        
        # Ensure all node types exist (add defaults if empty)
        if not neo4j_data["nodes"]["events"]:
            event_id = "event_1"
            neo4j_data["nodes"]["events"].append({
                "id": event_id,
                "title": "Document processed",
                "summary": f"Document {filename} was processed"
            })
            neo4j_data["relationships"].extend([
                {"from_node": cat_id, "to_node": event_id, "type": "HAS_EVENT"},
                {"from_node": doc_id, "to_node": event_id, "type": "MENTIONS"}
            ])
        
        if not neo4j_data["nodes"]["dates"]:
            neo4j_data["nodes"]["dates"].append({
                "date": datetime.now().isoformat() + "Z"
            })
        
        if not neo4j_data["nodes"]["locations"]:
            neo4j_data["nodes"]["locations"].append({
                "id": "loc_1",
                "address": "Unknown Location"
            })
        
        if not neo4j_data["nodes"]["entities"]:
            neo4j_data["nodes"]["entities"].append({
                "id": "entity_1",
                "name": "Unknown Entity"
            })
        
        # Users are always created above, but ensure they exist
        if not neo4j_data["nodes"]["users"]:
            neo4j_data["nodes"]["users"].append({
                "id": "user_1",
                "email": "journalist@example.com",
                "name": "System User",
                "password": "placeholder"
            })
            # Add User -> Cat relationship if missing
            user_owns_cat = any(rel["from_node"] == "user_1" and rel["to_node"] == cat_id and rel["type"] == "OWNS" 
                               for rel in neo4j_data["relationships"])
            if not user_owns_cat:
                neo4j_data["relationships"].append({
                    "from_node": "user_1",
                    "to_node": cat_id,
                    "type": "OWNS"
                })
        
        print("Neo4j data structure generated")
        return neo4j_data

def main():
    """Example usage of the InvestiCAT processor."""
    processor = InvestiCATProcessor()
    
    # Example usage
    try:
        result = processor.process_document(
            "/Users/maskeenkaur/investiCAT/test_document.pdf",
            "Corporate Acquisition Investigation"
        )
        
        print("\n" + "="*60)
        print("NEO4J OUTPUT:")
        print("="*60)
        print(json.dumps(result, indent=2))
        
        # Save output
        with open("/Users/maskeenkaur/investiCAT/etl/neo4j_output.json", "w") as f:
            json.dump(result, f, indent=2)
        
        print(f"\nOutput saved to: /Users/maskeenkaur/investiCAT/etl/neo4j_output.json")
        
        # Print summary
        nodes = result["nodes"]
        print(f"\nSummary:")
        print(f"   Cats: {len(nodes['cats'])}")
        print(f"   Documents: {len(nodes['documents'])}")
        print(f"   Events: {len(nodes['events'])}")
        print(f"   Dates: {len(nodes['dates'])}")
        print(f"   Locations: {len(nodes['locations'])}")
        print(f"   Entities: {len(nodes['entities'])}")
        print(f"   Relationships: {len(result['relationships'])}")
        
    except Exception as e:
        print(f"Processing failed: {e}")

if __name__ == "__main__":
    main()