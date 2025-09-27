# Cedar InvestiCAT Integration

A Mastra agent-based productivity wrapper for the InvestiCAT journalism tool that adds intelligent querying and summarization capabilities on top of the existing document processing pipeline.

## Overview

Cedar enhances InvestiCAT with AI-powered productivity features:

- **Natural Language Timeline Queries**: Ask questions like "What happened between January and March?" or "Who was involved in the merger announcement?"
- **Auto-Summary Generation**: Generate executive summaries, briefing notes, and publication-ready drafts
- **Cross-Document Analysis**: Find overlapping entities and detect timeline conflicts across multiple documents
- **Enhanced Neo4j Output**: Augments existing schema with summary and insight nodes

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Input Docs    │    │   ETL Pipeline   │    │  Cedar Mastra   │
│  (PDF/DOCX)     │───▶│  (Existing)      │───▶│   Enhancement   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
┌─────────────────────────────────────────────────────────────────┐
│                  Cedar Output                                    │
├─────────────────┬─────────────────┬──────────────────────────────┤
│ Original ETL    │ AI Summaries    │ Query Interface              │
│ Results         │ - Executive     │ - Natural Language           │
│ - Timeline      │ - Briefing      │ - Entity Analysis            │
│ - Neo4j Data    │ - Publication   │ - Cross-References           │
└─────────────────┴─────────────────┴──────────────────────────────┘
```

## Installation

1. Install Cedar dependencies:
```bash
cd cedar
pip install -r requirements_cedar.txt
```

2. Set up environment variables:
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

## Usage

### Process Single Document

```bash
# Basic processing with all features
python main.py process document.pdf -t "Corporate Investigation"

# Skip summaries (faster processing)
python main.py process report.docx -t "Merger Analysis" --no-summaries

# Save results to file
python main.py process file.pdf -t "Investigation" -o results.json
```

### Natural Language Queries

```bash
# Query with timeline file
python main.py query "What happened in January?" --timeline-file results.json

# Query stored investigation
python main.py query "Who was involved in the announcement?" --investigation-id inv_123
```

### Cross-Document Analysis

```bash
# Analyze multiple documents
python main.py cross-analyze doc1.pdf doc2.pdf doc3.pdf -t "Multi-Doc Investigation" -o cross_analysis.json
```

### Generate Publication Package

```bash
# Comprehensive package with all formats
python main.py package --timeline-file results.json -t "Investigation Title" --type comprehensive -o package.json

# Executive summary package
python main.py package --timeline-file results.json -t "Investigation Title" --type executive -o exec_package.json
```

## Python API

```python
from cedar.main import CedarInvestiCATIntegration

# Initialize
cedar = CedarInvestiCATIntegration(openai_api_key="your-key")

# Process document
result = cedar.process_with_mastra_productivity(
    "document.pdf", 
    "Investigation Title"
)

# Natural language query
query_result = cedar.query_timeline(
    "What happened between January and March?",
    timeline_data=result['timeline']
)

# Cross-document analysis
cross_result = cedar.cross_document_analysis(
    ["doc1.pdf", "doc2.pdf"],
    "Multi-Document Investigation"
)

# Generate publication package
package = cedar.generate_publication_package(
    result['timeline'],
    "Investigation Title",
    package_type='comprehensive'
)
```

## Features

### 1. Natural Language Timeline Queries

Ask conversational questions about your investigation timeline:

- **Temporal**: "What happened in March 2024?"
- **Entity-focused**: "What did John Smith do?"
- **Location-based**: "Show me all events in New York"
- **Event-focused**: "When did the merger announcement happen?"

### 2. Auto-Summary Generation

Generate multiple summary formats:

- **Executive Summary**: High-level overview for leadership
- **Briefing Note**: Concise summary for journalists and editors
- **Publication Draft**: Article-ready content with headlines
- **Multi-Format Package**: Comprehensive package with all formats

### 3. Cross-Document Analysis

Analyze multiple documents together:

- **Entity Overlap**: Find entities mentioned across documents
- **Timeline Conflicts**: Detect contradicting information
- **Confirmations**: Identify corroborating evidence
- **Cross-References**: Generate connections between sources

### 4. Enhanced Neo4j Output

Extends existing Neo4j schema with:

```cypher
# New node types
(:ExecutiveSummary)-[:HAS_FINDING]->(:KeyFinding)
(:TimelineInsights)-[:GENERATED_FROM]->(:Document)
(:CrossReference)-[:CONFIRMS]->(:Entity)
```

## Output Formats

### Enhanced Processing Result

```json
{
  "original_etl_output": { /* existing ETL results */ },
  "timeline": [ /* extracted events */ ],
  "timeline_insights": {
    "timeline_span": { "start_date": "2024-01-01", "end_date": "2024-03-31" },
    "most_active_period": { "period": "2024-02", "event_count": 15 },
    "key_entities": [{"entity": "John Smith", "mention_count": 8}],
    "location_hotspots": [{"location": "New York", "event_count": 12}]
  },
  "summaries": {
    "executive_summary": { /* structured summary object */ },
    "briefing_note": { /* journalist-focused brief */ },
    "publication_draft": { /* article-ready content */ }
  },
  "query_interface": {
    "enabled": true,
    "sample_queries": ["What did John Smith do?", "What happened in February?"]
  },
  "neo4j_output": { /* enhanced Neo4j nodes and relationships */ }
}
```

### Natural Language Query Result

```json
{
  "query": "What happened in January?",
  "answer": "In January 2024, three significant events occurred...",
  "supporting_events": [ /* filtered timeline events */ ],
  "entity_count": 5,
  "date_range": {"start": "2024-01-01", "end": "2024-01-31"},
  "conversation_context": {
    "query_type": "temporal",
    "suggested_followups": ["What happened before January?", "Who was involved?"]
  }
}
```

## Integration with Existing ETL

Cedar seamlessly integrates with the existing ETL pipeline:

1. **Imports existing processor**: Uses `document_processor_neo4j.py` from `../etl/`
2. **Preserves original output**: All existing ETL results are maintained
3. **Adds enhancements**: Layers AI productivity features on top
4. **Compatible schema**: Extends rather than replaces Neo4j output

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Required for Mastra agent functionality
- `NEO4J_URI`: Optional, for direct Neo4j integration
- `NEO4J_USER`: Optional Neo4j username
- `NEO4J_PASSWORD`: Optional Neo4j password

### Custom Configuration

```python
# Custom Neo4j configuration
neo4j_config = {
    "uri": "bolt://localhost:7687",
    "user": "neo4j",
    "password": "password"
}

cedar = CedarInvestiCATIntegration(
    openai_api_key="your-key",
    neo4j_config=neo4j_config
)
```

## Development

### Project Structure

```
cedar/
├── main.py                   # Main integration and CLI
├── mastra_agent.py          # Core Mastra agent implementation  
├── timeline_assistant.py    # Natural language query interface
├── summary_generator.py     # Auto-summary generation
├── requirements_cedar.txt   # Python dependencies
└── README.md               # This file
```

### Adding New Features

1. **New Query Types**: Extend `TimelineAssistant.query_patterns`
2. **Summary Formats**: Add templates to `SummaryGenerator.summary_templates`
3. **Neo4j Enhancements**: Modify `_generate_enhanced_neo4j_output()`

## Error Handling

Cedar includes comprehensive error handling:

- **ETL Failures**: Graceful handling when document processing fails
- **AI API Errors**: Fallback when OpenAI API is unavailable
- **Data Validation**: Ensures timeline data integrity
- **File Processing**: Handles missing or corrupted files

## Performance Considerations

- **Lazy Loading**: Summaries generated only when requested
- **Caching**: Query results cached for repeated queries
- **Batch Processing**: Efficient cross-document analysis
- **Memory Management**: Large documents processed in chunks

## Future Enhancements

- **Real-time Query Interface**: Web-based query dashboard
- **Advanced Visualizations**: Interactive timeline and network graphs
- **Multi-language Support**: Process documents in multiple languages
- **Collaborative Features**: Multi-user investigation support
- **Export Formats**: Word, PDF, and presentation outputs