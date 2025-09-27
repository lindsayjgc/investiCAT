# InvestiCAT Document Processor

A Python document processing tool for investigative journalism that extracts timeline events from PDF and DOCX documents and outputs structured data for Neo4j graph database.

## Overview

The InvestiCAT Document Processor transforms investigative documents into a structured timeline format suitable for Neo4j graph database analysis. It uses AI-powered event extraction and provides fallback pattern matching for robust processing.

## Neo4j Schema

### Node Types
- **Cat**: Investigation cases (`id`, `title`)
- **Document**: Source documents (`id`, `filename`)
- **Event**: Timeline events (`id`, `title`, `summary`)
- **Date**: Event dates (`date` in ISO format)
- **Location**: Geographic locations (`id`, `address`)
- **Entity**: People and organizations (`id`, `name`)
- **User**: System users (`id`, `email`, `name`, `password`)

### Relationships
- `User -[OWNS]-> Cat`
- `Cat -[HAS_DOCUMENT]-> Document`
- `Cat -[HAS_EVENT]-> Event`
- `Document -[MENTIONS]-> Event`
- `Event -[OCCURRED_ON]-> Date`
- `Event -[OCCURRED_AT]-> Location`
- `Entity -[PARTICIPATES_IN]-> Event`

## Installation

### Prerequisites
- Python 3.8 or higher
- OpenAI API key (optional, for AI extraction)

### Dependencies
```bash
pip install pdfplumber python-docx openai reportlab
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

```bash
# Basic usage - process PDF with investigation title
python cli.py document.pdf -t "Investigation Title"

# Save to JSON file
python cli.py report.docx -t "Corporate Investigation" -o results.json

# Use fallback extraction only (no OpenAI)
python cli.py file.pdf -t "Investigation" --no-ai

# Quiet mode (minimal output)
python cli.py document.pdf -t "Investigation" -o results.json --quiet
```

### Python API

```python
from document_processor_neo4j import InvestiCATProcessor

# Initialize processor
processor = InvestiCATProcessor(openai_api_key="your-api-key")

# Process document
result = processor.process_document("document.pdf", "Investigation Title")

# Access Neo4j data
print(f"Events found: {len(result['nodes']['events'])}")
print(f"Entities: {len(result['nodes']['entities'])}")
print(f"Relationships: {len(result['relationships'])}")
```

### Main Function
```python
def process_document(file_path: str, investigation_title: str) -> dict:
    """
    Process document and return Neo4j-compatible data structure.
    
    Args:
        file_path: Path to PDF or DOCX file
        investigation_title: Title of the investigation
        
    Returns:
        Dict with nodes and relationships in Neo4j format
    """
```

## Output Format

The processor generates JSON in this exact Neo4j-compatible structure:

```json
{
  "nodes": {
    "cats": [{"id": "cat_1", "title": "Investigation Name"}],
    "documents": [{"id": "doc_1", "filename": "file.pdf"}],
    "events": [{"id": "event_1", "title": "Meeting", "summary": "Description"}],
    "dates": [{"date": "2024-01-15T00:00:00Z"}],
    "locations": [{"id": "loc_1", "address": "123 Main St"}],
    "entities": [{"id": "entity_1", "name": "John Doe"}],
    "users": [{"id": "user_1", "email": "journalist@example.com", "name": "System User", "password": "placeholder"}]
  },
  "relationships": [
    {"from_node": "user_1", "to_node": "cat_1", "type": "OWNS"},
    {"from_node": "cat_1", "to_node": "doc_1", "type": "HAS_DOCUMENT"},
    {"from_node": "event_1", "to_node": "date_1", "type": "OCCURRED_ON"}
  ]
}
```

## Features

### Document Processing
- **PDF Support**: Uses pdfplumber for reliable text extraction
- **DOCX Support**: Uses python-docx for Word document processing
- **Error Handling**: Robust error handling with informative messages

### Event Extraction
- **AI-Powered**: Uses OpenAI GPT-4o-mini for intelligent event detection
- **Fallback Processing**: Pattern-based extraction when AI is unavailable
- **Timeline Focus**: Extracts events with dates, locations, and participants

### Neo4j Integration
- **Unique IDs**: Generates unique identifiers for all nodes
- **Complete Schema**: Creates all required node types and relationships
- **Direct Import**: Output ready for Neo4j database import

## Configuration

### OpenAI API Key
Set your OpenAI API key in the processor initialization:

```python
# In code
processor = InvestiCATProcessor(openai_api_key="your-key-here")

# Or modify the default in document_processor_neo4j.py
OPENAI_API_KEY = "your-api-key"
```

### Processing Options
- **AI Extraction**: Uses OpenAI for intelligent event detection
- **Fallback Mode**: Pattern-based extraction for offline processing
- **Quiet Mode**: Suppress progress messages for batch processing

## Examples

### Corporate Investigation
```bash
python cli.py merger_documents.pdf -t "MegaCorp Acquisition Analysis" -o merger_data.json
```

### Government Document Analysis
```bash
python cli.py government_report.docx -t "Policy Investigation" -o policy_data.json
```

### Batch Processing
```python
import os
from document_processor_neo4j import InvestiCATProcessor

processor = InvestiCATProcessor()

for filename in os.listdir("documents/"):
    if filename.endswith(('.pdf', '.docx')):
        result = processor.process_document(f"documents/{filename}", "Batch Investigation")
        with open(f"output/{filename}.json", "w") as f:
            json.dump(result, f, indent=2)
```

## Neo4j Import

To import the processed data into Neo4j:

```cypher
// Load JSON data
WITH $data AS data

// Create Cat nodes
UNWIND data.nodes.cats AS cat
CREATE (:Cat {id: cat.id, title: cat.title})

// Create Document nodes
UNWIND data.nodes.documents AS doc
CREATE (:Document {id: doc.id, filename: doc.filename})

// Create Event nodes
UNWIND data.nodes.events AS event
CREATE (:Event {id: event.id, title: event.title, summary: event.summary})

// Create Date nodes
UNWIND data.nodes.dates AS date
CREATE (:Date {date: datetime(date.date)})

// Create Location nodes
UNWIND data.nodes.locations AS loc
CREATE (:Location {id: loc.id, address: loc.address})

// Create Entity nodes
UNWIND data.nodes.entities AS entity
CREATE (:Entity {id: entity.id, name: entity.name})

// Create relationships
UNWIND data.relationships AS rel
MATCH (from {id: rel.from_node}), (to {id: rel.to_node})
CALL apoc.create.relationship(from, rel.type, {}, to) YIELD rel as relationship
RETURN relationship
```

## Error Handling

The processor includes comprehensive error handling:

- **File Not Found**: Clear error message with file path
- **Unsupported Format**: Validation of PDF/DOCX file types
- **Text Extraction Errors**: Fallback methods for document parsing
- **API Failures**: Graceful fallback to pattern-based extraction
- **Missing Dependencies**: Clear installation instructions

## Troubleshooting

### Common Issues

1. **OpenAI API Errors**
   - Check API key validity
   - Use `--no-ai` flag for offline processing

2. **PDF Parsing Errors**
   - Ensure PDF is not password-protected
   - Check file corruption

3. **Missing Dependencies**
   ```bash
   pip install pdfplumber python-docx openai
   ```

4. **Memory Issues with Large Files**
   - Process files in smaller chunks
   - Use text extraction limits

## Development

### Project Structure
```
etl/
├── document_processor_neo4j.py  # Main processor class
├── cli.py                       # Command-line interface
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

### Contributing
1. Follow Python PEP 8 style guidelines
2. Add comprehensive docstrings
3. Include error handling for new features
4. Test with various document types

## License

This project is part of the InvestiCAT investigative journalism toolkit.
