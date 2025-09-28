# InvestiCAT Document Processor - ETL Module

Document-level ETL processor for investigative journalism that extracts structured timeline data from PDF/DOCX documents for Neo4j graph database storage.

## System Architecture

The InvestiCAT system has clear separation of concerns:

- **Frontend/API**: Manages investigations (Cat nodes) and orchestrates document processing  
- **ETL Processor** (this module): Processes individual documents and extracts structured timeline data
- **Neo4j Database**: Stores the complete investigation graph

## ETL Processor Scope

This ETL processor handles **document-level processing only**:

### GENERATES:
- Document nodes (from processed files)
- Events extracted from document content
- Dates, Locations, Entities mentioned in events  
- User nodes (system users)
- Document-level relationships only

### DOES NOT GENERATE:
- Cat nodes (investigations created by frontend)
- Any Cat relationships (HAS_DOCUMENT, HAS_EVENT, OWNS)

## Neo4j Schema

### Nodes (with properties):
- **Cat**: Investigation cases (id: string, title: string) - *Created by frontend*
- **Document**: Source documents (id: string, filename: string)
- **Event**: Timeline events (id: string, title: string, summary: string)  
- **Date**: Event dates (date: datetime) - **NO ID FIELD**
- **Location**: Geographic locations (id: string, address: string)
- **Entity**: People/organizations (id: string, name: string)
- **User**: System users (id: string, email: string, name: string, password: string)

### Relationships:
- **Document** -[MENTIONS]-> **Event** (document mentions extracted events)
- **Event** -[OCCURRED_ON]-> **Date** (event happened on specific date)
- **Event** -[OCCURRED_AT]-> **Location** (event happened at location)
- **Entity** -[PARTICIPATES_IN]-> **Event** (entity involved in event)

*Note: Cat relationships (User -[OWNS]-> Cat, Cat -[HAS_DOCUMENT]-> Document, Cat -[HAS_EVENT]-> Event) are handled by frontend*

## Installation

```bash
# Install required dependencies
pip install -r requirements.txt

# Required packages:
# - pdfplumber (PDF parsing)
# - python-docx (DOCX parsing) 
# - openai (optional, for enhanced extraction)
# - neo4j (database connectivity)
```

## Complete Workflow

The InvestiCAT ETL system provides a complete pipeline from document processing to Neo4j storage:

### 1. Document Processing
Extract timeline data from investigative documents:

```bash
# Process a document and save JSON
python cli.py document.pdf -o output.json

# Process with OpenAI enhancement
python cli.py document.pdf --openai-key YOUR_KEY --summary
```

### 2. Neo4j Database Loading  
Load processed data into Neo4j database:

```bash
# Load JSON data into Neo4j
python neo4j_loader.py output.json

# Clear database first, then load
python neo4j_loader.py output.json --clear

# Show database statistics
python neo4j_loader.py --stats
```

### 3. End-to-End Testing
Run complete workflow test:

```bash
# Test document processing + Neo4j loading
python test_e2e.py
```
pip install -r requirements.txt

# Required packages:
# - pdfplumber (PDF parsing)
# - python-docx (DOCX parsing) 
# - openai (optional, for enhanced extraction)
```

## Usage

### Command Line Interface

```bash
# Process a PDF document
python cli.py document.pdf

# Process with custom output file
python cli.py document.docx -o output.json

# Use OpenAI for enhanced extraction
python cli.py file.pdf --openai-key YOUR_KEY

# Pretty print to console with summary
python cli.py file.pdf --pretty --summary
```

### Python API

```python
from document_processor_neo4j import InvestiCATProcessor

# Initialize processor
processor = InvestiCATProcessor()

# Process document (returns Neo4j-compatible structure)
result = processor.process_document("path/to/document.pdf")

# Save results
import json
with open("output.json", "w") as f:
    json.dump(result, f, indent=2)
```

## Output Format

The processor generates Neo4j-compatible JSON following this schema:

```json
{
  "nodes": {
    "documents": [
      {
        "id": "doc_a1b2c3d4", 
        "filename": "merger_agreement.pdf"
      }
    ],
    "events": [
      {
        "id": "event_1",
        "title": "Board approved acquisition", 
        "summary": "Board of Directors approved the acquisition..."
      }
    ],
    "dates": [
      {
        "date": "2024-03-15T00:00:00Z"
      }
    ],
    "locations": [
      {
        "id": "loc_1",
        "address": "New York City"
      }
    ],
    "entities": [
      {
        "id": "entity_1", 
        "name": "MegaCorp Inc"
      }
    ],
    "users": [
      {
        "id": "user_a1b2c3d4",
        "email": "journalist@example.com",
        "name": "System User", 
        "password": "placeholder"
      }
    ]
  },
  "relationships": [
    {
      "from_node": "doc_a1b2c3d4",
      "to_node": "event_1", 
      "type": "MENTIONS"
    },
    {
      "from_node": "event_1",
      "to_node": "2024-03-15T00:00:00Z",
      "type": "OCCURRED_ON"
    },
    {
      "from_node": "event_1", 
      "to_node": "loc_1",
      "type": "OCCURRED_AT"
    },
    {
      "from_node": "entity_1",
      "to_node": "event_1",
      "type": "PARTICIPATES_IN"
    }
  ]
}
```

## Event Extraction

The processor uses two methods for event extraction:

1. **OpenAI API** (if API key provided): Advanced natural language processing for high-quality event extraction
2. **Fallback Pattern Matching**: Regex-based extraction focusing on investigative journalism keywords

### Event Types Detected:
- Meetings, transactions, announcements
- Approvals, signings, filings
- Investigations, rulings, decisions
- Contracts, agreements, mergers

## Files

- **`document_processor_neo4j.py`**: Main processor class
- **`cli.py`**: Command-line interface
- **`test_processor.py`**: Comprehensive test suite
- **`requirements.txt`**: Python dependencies

## Testing

```bash
# Run comprehensive tests
python test_processor.py

# Test with sample data
python document_processor_neo4j.py
```

## Integration

This ETL module integrates with the larger InvestiCAT system:

1. **Frontend** creates Cat nodes and manages investigations
2. **ETL Processor** (this module) processes individual documents
3. **Frontend** combines Cat + Document data for complete Neo4j graph
4. **Neo4j Database** stores the unified investigation graph

The separation ensures scalability and clear responsibility boundaries.

## Configuration

Set OpenAI API key for enhanced extraction:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or pass directly to processor:

```python
processor = InvestiCATProcessor(openai_api_key="your-api-key")
```