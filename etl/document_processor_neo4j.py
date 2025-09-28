#!/usr/bin/env python3
"""
InvestiCAT Document Processor for Neo4j Timeline Tool (ETL)

Document-level ETL processor for investigative journalism that extracts structured
timeline data from PDF/DOCX documents for Neo4j graph database storage.

SCOPE: Processes individual documents only. Does NOT create Cat nodes or 
       Cat relationships (handled by frontend/API layer).

OUTPUT: Document, Events, Dates, Locations, Entities, Users and their relationships
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
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

class InvestiCATProcessor:
    """
    Document processor for investigative journalism timeline extraction.
    
    Processes individual documents and extracts structured timeline data
    for Neo4j database storage. Generates document-level nodes and relationships only.
    """
    
    def __init__(self, openai_api_key: str = None):
        """Initialize the processor with optional OpenAI client."""
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
            'filed', 'completed', 'finalized', 'reported', 'meeting', 'deal',
            'transaction', 'contract', 'agreement', 'decision', 'ruling'
        ]
        
        # Date patterns with named groups
        date_patterns = [
            (r'(?P<month>January|February|March|April|May|June|July|August|September|October|November|December)\s+(?P<day>\d{1,2}),?\s+(?P<year>\d{4})', "%B %d %Y"),
            (r'(?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(?P<day>\d{1,2}),?\s+(?P<year>\d{4})', "%b %d %Y"),
            (r'(?P<month>\d{1,2})[/-](?P<day>\d{1,2})[/-](?P<year>\d{4})', "%m/%d/%Y"),
            (r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})', "%Y-%m-%d")
        ]
        
        for sentence in sentences[:15]:  # Process more sentences
            sentence_lower = sentence.lower()
            
            if any(indicator in sentence_lower for indicator in indicators):
                # Extract date
                date_found = None
                for pattern, date_format in date_patterns:
                    match = re.search(pattern, sentence)
                    if match:
                        try:
                            # Reconstruct date string and parse it
                            if 'month' in match.groupdict():
                                month = match.group('month')
                                day = match.group('day')
                                year = match.group('year')
                                date_str = f"{month} {day} {year}"
                            else:
                                date_str = match.group(0)
                            
                            # Try to parse with the matching format
                            dt = datetime.strptime(date_str, date_format)
                            date_found = dt.strftime("%Y-%m-%d")
                            break
                        except ValueError:
                            continue
                
                # Extract location
                location_match = re.search(r'\b(?:in|at|from)\s+([A-Z][a-zA-Z\s,]+?)(?:[,.]|\s+(?:on|in|at|with|and|or|the)|$)', sentence)
                location = None
                if location_match:
                    location = location_match.group(1).strip()
                    # Clean up location
                    location = re.sub(r'\s+(on|in|at|with|and|or|the).*$', '', location)
                    if len(location) > 50 or len(location) < 3:
                        location = None
                
                # Extract participants (proper nouns and organizations)
                participants = []
                # Look for names (Title Case sequences)
                name_matches = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', sentence)
                # Look for organizations
                org_matches = re.findall(r'\b[A-Z][a-zA-Z]+(?:\s+(?:Inc|Ltd|Corp|LLC|Company|Group|Technologies|Systems))?\b', sentence)
                
                all_participants = name_matches + org_matches
                for p in all_participants:
                    p = p.strip()
                    if (len(p) > 2 and len(p) < 30 and 
                        p not in ['The', 'This', 'That', 'They', 'These', 'Those', 'With', 'From', 'Into'] and
                        p not in participants):
                        participants.append(p)
                
                # Limit participants
                participants = participants[:5]
                
                # Create title
                title = sentence[:75] + "..." if len(sentence) > 75 else sentence
                
                events.append({
                    "title": title,
                    "summary": sentence,
                    "date": date_found,
                    "location": location,
                    "participants": participants
                })
        
        return events[:10]  # Return max 10 events
    
    def generate_unique_id(self, prefix: str) -> str:
        """Generate unique ID with prefix."""
        return f"{prefix}_{str(uuid.uuid4())[:8]}"
    
    def format_date_iso(self, date_str: str) -> str:
        """Convert date string to ISO format."""
        try:
            # Try common date formats
            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y", "%d/%m/%Y"]:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.isoformat() + "Z"
                except ValueError:
                    continue
            
            # If no format matches, return with default time
            return f"{date_str}T00:00:00Z"
        except Exception:
            return f"{date_str}T00:00:00Z"
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        Process document and return Neo4j-compatible data structure.
        
        SCOPE: Document-level processing only. Does NOT create Cat nodes or relationships.
        
        Args:
            file_path: Path to PDF or DOCX file
            
        Returns:
            Dict with nodes and relationships in Neo4j format following required schema
        """
        filename = Path(file_path).name
        print(f"Processing document: {filename}")
        
        # Extract text from document
        try:
            text = self.extract_text(file_path)
            print(f"Extracted {len(text)} characters from document")
        except Exception as e:
            raise Exception(f"Text extraction failed: {e}")
        
        # Extract events from text
        print("Extracting timeline events...")
        events = self.extract_events_with_openai(text)
        print(f"Extracted {len(events)} events from document")
        
        # Generate document ID
        doc_id = self.generate_unique_id("doc")
        user_id = self.generate_unique_id("user")
        
        # Initialize Neo4j data structure following required schema
        neo4j_data = {
            "nodes": {
                "documents": [
                    {
                        "id": doc_id,
                        "filename": filename
                    }
                ],
                "events": [],
                "dates": [],
                "locations": [],
                "entities": [],
                "users": [
                    {
                        "id": user_id,
                        "email": "journalist@example.com", 
                        "name": "System User",
                        "password": "placeholder"
                    }
                ]
            },
            "relationships": []
        }
        
        # Track unique items to avoid duplicates
        unique_dates = set()
        unique_locations = {}  # location_name -> location_id
        unique_entities = {}   # entity_name -> entity_id
        
        # Process each extracted event
        for i, event in enumerate(events, 1):
            event_id = self.generate_unique_id("event")
            
            # Add event node
            neo4j_data["nodes"]["events"].append({
                "id": event_id,
                "title": event.get("title", f"Event {i}"),
                "summary": event.get("summary", "No summary available")
            })
            
            # Add Document -> Event relationship (document mentions event)
            neo4j_data["relationships"].append({
                "from_node": doc_id,
                "to_node": event_id,
                "type": "MENTIONS"
            })
            
            # Process event date
            if event.get("date"):
                date_str = event["date"]
                iso_date = self.format_date_iso(date_str)
                
                if iso_date not in unique_dates:
                    unique_dates.add(iso_date)
                    
                    # Add date node (NO ID FIELD as per schema)
                    neo4j_data["nodes"]["dates"].append({
                        "date": iso_date
                    })
                
                # Add Event -> Date relationship
                neo4j_data["relationships"].append({
                    "from_node": event_id,
                    "to_node": iso_date,
                    "type": "OCCURRED_ON"
                })
            
            # Process event location
            if event.get("location"):
                location_name = event["location"].strip()
                
                if location_name not in unique_locations:
                    location_id = self.generate_unique_id("loc")
                    unique_locations[location_name] = location_id
                    
                    # Add location node
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
            
            # Process event participants (entities)
            if event.get("participants"):
                for participant_name in event["participants"]:
                    participant_name = participant_name.strip()
                    
                    if participant_name not in unique_entities:
                        entity_id = self.generate_unique_id("entity")
                        unique_entities[participant_name] = entity_id
                        
                        # Add entity node
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
        
        # Ensure we have at least one event (document processed event)
        if not neo4j_data["nodes"]["events"]:
            default_event_id = self.generate_unique_id("event")
            current_time = datetime.now().isoformat() + "Z"
            
            neo4j_data["nodes"]["events"].append({
                "id": default_event_id,
                "title": "Document processed",
                "summary": f"Document {filename} was processed for timeline extraction"
            })
            
            neo4j_data["nodes"]["dates"].append({
                "date": current_time
            })
            
            neo4j_data["relationships"].extend([
                {
                    "from_node": doc_id,
                    "to_node": default_event_id,
                    "type": "MENTIONS"
                },
                {
                    "from_node": default_event_id,
                    "to_node": current_time,
                    "type": "OCCURRED_ON"
                }
            ])
        
        print(f"Generated Neo4j data structure with {len(neo4j_data['nodes']['events'])} events")
        return neo4j_data

def main():
    """Example usage of the InvestiCAT document processor."""
    processor = InvestiCATProcessor()
    
    # Check for sample document in uploads folder
    sample_documents = list(Path("/Users/maskeenkaur/investiCAT/uploads").glob("*.pdf"))
    
    if not sample_documents:
        print("No sample documents found in uploads folder.")
        print("Please add a PDF document to /Users/maskeenkaur/investiCAT/uploads/ for testing.")
        return
    
    # Process the first available document
    sample_doc = sample_documents[0]
    print(f"Using sample document: {sample_doc.name}")
    
    try:
        # Process document (no investigation title needed)
        result = processor.process_document(str(sample_doc))
        
        print("\n" + "="*60)
        print("NEO4J OUTPUT (DOCUMENT-LEVEL ETL)")
        print("="*60)
        print(json.dumps(result, indent=2))
        
        # Save output  
        output_file = Path("/Users/maskeenkaur/investiCAT/etl/neo4j_document_output.json")
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)
        
        print(f"\nOutput saved to: {output_file}")
        
        # Print summary
        nodes = result["nodes"]
        print(f"\nDocument Processing Summary:")
        print(f"   Documents: {len(nodes['documents'])}")
        print(f"   Events: {len(nodes['events'])}")
        print(f"   Dates: {len(nodes['dates'])}")
        print(f"   Locations: {len(nodes['locations'])}")
        print(f"   Entities: {len(nodes['entities'])}")
        print(f"   Users: {len(nodes['users'])}")
        print(f"   Relationships: {len(result['relationships'])}")
        
        print(f"\nNOTE: This ETL processor generates document-level data only.")
        print(f"Cat nodes and Cat relationships are handled by the frontend/API layer.")
        
    except Exception as e:
        print(f"Document processing failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()