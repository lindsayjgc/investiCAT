"""
InvestiCAT Cedar Integration
Main integration point for Mastra agent productivity wrapper with existing ETL pipeline.
"""

import sys
import os
import importlib.util

from typing import Dict, List, Any, Optional
import json
from pathlib import Path
from datetime import datetime

# Import ETL processor (real version)
try:
    import sys
    from pathlib import Path
    etl_path = str(Path(__file__).parent.parent / 'etl')
    if etl_path not in sys.path:
        sys.path.insert(0, etl_path)
    
    # Import with explicit module path to avoid conflicts
    import importlib.util
    spec = importlib.util.spec_from_file_location("real_etl", Path(__file__).parent.parent / 'etl' / 'document_processor_neo4j.py')
    real_etl_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(real_etl_module)
    
    RealETLProcessor = real_etl_module.InvestiCATProcessor
    ETL_AVAILABLE = True
    print("✅ Real ETL processor imported directly in Cedar")
except Exception as e:
    # Fallback to mock processor
    try:
        from document_processor_neo4j import InvestiCATProcessor as RealETLProcessor
        ETL_AVAILABLE = False
        print(f"⚠️ Using mock ETL processor in Cedar: {e}")
    except ImportError:
        RealETLProcessor = None
        ETL_AVAILABLE = False
        print("❌ No ETL processor available in Cedar")

# Import Cedar components
from mastra_agent import MastraAgent, TimelineQuery
from timeline_assistant import TimelineAssistant
from summary_generator import SummaryGenerator

class CedarInvestiCATIntegration:
    """
    Main integration class that combines existing ETL processing 
    with Mastra agent productivity enhancements.
    """
    
    def __init__(self, openai_api_key: str = None, neo4j_config: Dict = None):
        """
        Initialize Cedar integration with existing InvestiCAT processor.
        
        Args:
            openai_api_key: OpenAI API key for Mastra agent
            neo4j_config: Neo4j database configuration
        """
        # Initialize existing ETL processor with OpenAI key
        if RealETLProcessor:
            self.etl_processor = RealETLProcessor(openai_api_key=openai_api_key)
        else:
            raise ImportError("No ETL processor available")
        
        # Initialize Mastra components
        self.mastra_agent = MastraAgent(openai_api_key)
        self.timeline_assistant = TimelineAssistant(self.mastra_agent)
        self.summary_generator = SummaryGenerator(self.mastra_agent)
        
        # Configuration
        self.neo4j_config = neo4j_config or {}
        
        print(f"✅ Cedar InvestiCAT Integration initialized successfully")
        if ETL_AVAILABLE:
            print("  🔧 Using real ETL processor with PDF parsing")
        else:
            print("  ⚠️  Using mock ETL processor")
        if openai_api_key:
            print("  🤖 OpenAI integration enabled")
    
    def process_with_mastra_productivity(self, file_path: str, 
                                       investigation_title: str,
                                       generate_summaries: bool = True,
                                       enable_queries: bool = True) -> Dict[str, Any]:
        """
        Main function: Process document with existing ETL + Mastra productivity enhancements.
        
        Args:
            file_path: Path to PDF or DOCX document
            investigation_title: Title for the investigation
            generate_summaries: Whether to generate auto-summaries
            enable_queries: Whether to enable natural language queries
        
        Returns:
            Enhanced Neo4j compatible output with productivity features
        """
        print(f"🚀 Processing {file_path} with Cedar productivity enhancements...")
        
        # Step 1: Use existing ETL processor for document extraction
        print("📄 Running ETL document extraction...")
        etl_result = self.etl_processor.process_document(file_path, investigation_title)
        
        if not etl_result:
            raise ValueError("ETL processing failed - no result returned")
        
        # Convert Neo4j format to timeline format
        timeline_data = self._convert_neo4j_to_timeline(etl_result)
        
        if not timeline_data:
            raise ValueError("ETL processing failed or returned no timeline data")
        
        print(f"✅ Extracted {len(timeline_data)} timeline events")
        
        # Step 2: Apply Mastra productivity enhancements
        enhanced_result = {
            # Original ETL results
            'original_etl_output': etl_result,
            'investigation_title': investigation_title,
            'processed_at': datetime.now().isoformat(),
            'file_path': str(file_path),
            
            # Enhanced timeline data
            'timeline': timeline_data,
            'timeline_insights': self.timeline_assistant.get_timeline_insights(timeline_data),
            'interactive_summary': self.timeline_assistant.generate_interactive_summary(timeline_data),
            
            # Neo4j integration
            'neo4j_original': etl_result,
            'neo4j_enhanced': None  # Will be populated later
        }
        
        # Step 3: Generate summaries if requested
        if generate_summaries:
            print("📝 Generating intelligent summaries...")
            enhanced_result['summaries'] = {
                'executive_summary': self.summary_generator.generate_executive_summary(
                    timeline_data, investigation_title
                ),
                'briefing_note': self.summary_generator.generate_briefing_note(
                    timeline_data, investigation_title
                ),
                'publication_draft': self.summary_generator.generate_publication_draft(
                    timeline_data, investigation_title
                ),
                'multi_format_package': self.summary_generator.generate_multi_format_package(
                    timeline_data, investigation_title
                )
            }
        
        # Step 4: Enable query interface if requested
        if enable_queries:
            print("🤖 Setting up natural language query interface...")
            enhanced_result['query_interface'] = {
                'enabled': True,
                'sample_queries': self._generate_sample_queries(timeline_data),
                'query_capabilities': [
                    'Natural language timeline queries',
                    'Entity relationship analysis',
                    'Date range filtering',
                    'Location-based searches',
                    'Cross-reference detection'
                ]
            }
        
        # Step 5: Generate enhanced Neo4j output
        enhanced_result['neo4j_output'] = self._generate_enhanced_neo4j_output(
            etl_result, enhanced_result
        )
        
        print("✅ Cedar processing completed successfully")
        return enhanced_result
    
    def query_timeline(self, query: str, timeline_data: List[Dict] = None,
                      investigation_id: str = None) -> Dict[str, Any]:
        """
        Process natural language queries against timeline data.
        
        Args:
            query: Natural language query (e.g., "What happened in January?")
            timeline_data: Timeline data to query (if not provided, loads from investigation_id)
            investigation_id: ID of previous investigation to query
        """
        if timeline_data is None and investigation_id is None:
            raise ValueError("Either timeline_data or investigation_id must be provided")
        
        if timeline_data is None:
            # Load timeline data from stored investigation
            timeline_data = self._load_timeline_data(investigation_id)
        
        print(f"🔍 Processing query: '{query}'")
        result = self.timeline_assistant.process_natural_language_query(query, timeline_data)
        
        return result
    
    def cross_document_analysis(self, file_paths: List[str], 
                              investigation_title: str) -> Dict[str, Any]:
        """
        Analyze multiple documents for overlapping entities and timeline conflicts.
        
        Args:
            file_paths: List of document paths to analyze
            investigation_title: Title for the cross-document investigation
        """
        print(f"📊 Starting cross-document analysis of {len(file_paths)} documents...")
        
        document_results = []
        
        # Process each document
        for i, file_path in enumerate(file_paths):
            print(f"Processing document {i+1}/{len(file_paths)}: {file_path}")
            
            doc_result = self.etl_processor.process_document(file_path, f"{investigation_title} - Doc {i+1}")
            if doc_result and 'timeline' in doc_result:
                doc_result['document_id'] = f"doc_{i+1}"
                doc_result['file_path'] = str(file_path)
                document_results.append(doc_result)
        
        if not document_results:
            raise ValueError("No documents were successfully processed")
        
        # Perform cross-document analysis
        cross_analysis = self.mastra_agent.cross_document_analysis(document_results)
        
        # Generate comprehensive analysis
        all_timeline_data = []
        for doc in document_results:
            all_timeline_data.extend(doc.get('timeline', []))
        
        result = {
            'investigation_title': investigation_title,
            'document_count': len(document_results),
            'total_events': len(all_timeline_data),
            'processed_at': datetime.now().isoformat(),
            
            'cross_analysis': cross_analysis,
            'combined_timeline': all_timeline_data,
            'combined_insights': self.timeline_assistant.get_timeline_insights(all_timeline_data),
            
            'document_summaries': [
                {
                    'document_id': doc['document_id'],
                    'file_path': doc['file_path'],
                    'event_count': len(doc.get('timeline', [])),
                    'key_entities': list(set(event.get('entity') for event in doc.get('timeline', []) if event.get('entity')))[:5],
                    'date_range': self._calculate_doc_date_range(doc.get('timeline', []))
                }
                for doc in document_results
            ],
            
            'comprehensive_summary': self.summary_generator.generate_executive_summary(
                all_timeline_data, f"Cross-Document Analysis: {investigation_title}"
            ),
            
            'neo4j_output': self._generate_cross_document_neo4j_output(document_results, cross_analysis)
        }
        
        print("✅ Cross-document analysis completed")
        return result
    
    def generate_publication_package(self, timeline_data: List[Dict], 
                                   investigation_title: str,
                                   package_type: str = 'comprehensive') -> Dict[str, Any]:
        """
        Generate complete publication package with multiple formats.
        
        Args:
            timeline_data: Timeline data from investigation
            investigation_title: Title of investigation
            package_type: 'executive', 'journalistic', 'comprehensive'
        """
        print(f"📦 Generating {package_type} publication package...")
        
        if package_type == 'comprehensive':
            package = self.summary_generator.generate_multi_format_package(
                timeline_data, investigation_title
            )
        elif package_type == 'executive':
            package = {
                'executive_summary': self.summary_generator.generate_executive_summary(
                    timeline_data, investigation_title
                ),
                'briefing_note': self.summary_generator.generate_briefing_note(
                    timeline_data, investigation_title, urgency='high'
                )
            }
        elif package_type == 'journalistic':
            package = {
                'publication_draft': self.summary_generator.generate_publication_draft(
                    timeline_data, investigation_title, style='investigative'
                ),
                'briefing_note': self.summary_generator.generate_briefing_note(
                    timeline_data, investigation_title
                )
            }
        else:
            raise ValueError(f"Unknown package_type: {package_type}")
        
        # Add metadata
        package['package_metadata'] = {
            'package_type': package_type,
            'generated_at': datetime.now().isoformat(),
            'investigation_title': investigation_title,
            'data_source': 'cedar_mastra_integration'
        }
        
        print("✅ Publication package generated")
        return package
    
    def _generate_enhanced_neo4j_output(self, etl_result: Dict, 
                                      enhanced_result: Dict) -> Dict[str, Any]:
        """
        Generate enhanced Neo4j output with additional summary nodes.
        """
        # Start with original Neo4j output from ETL
        neo4j_output = etl_result.get('neo4j_output', {
            'nodes': [],
            'relationships': []
        })
        
        # Add summary nodes if summaries were generated
        if 'summaries' in enhanced_result:
            summaries = enhanced_result['summaries']
            
            # Executive summary node
            if 'executive_summary' in summaries:
                exec_summary = summaries['executive_summary']
                neo4j_output['nodes'].append({
                    'id': f"summary_executive_{hash(exec_summary.title)}",
                    'label': 'ExecutiveSummary',
                    'properties': {
                        'title': exec_summary.title,
                        'executive_summary': exec_summary.executive_summary,
                        'confidence_score': exec_summary.confidence_score,
                        'key_findings': exec_summary.key_findings,
                        'created_at': datetime.now().isoformat()
                    }
                })
            
            # Key findings nodes
            if 'executive_summary' in summaries:
                for i, finding in enumerate(summaries['executive_summary'].key_findings):
                    finding_id = f"finding_{hash(finding)}_{i}"
                    neo4j_output['nodes'].append({
                        'id': finding_id,
                        'label': 'KeyFinding',
                        'properties': {
                            'finding': finding,
                            'order': i,
                            'investigation': enhanced_result['investigation_title']
                        }
                    })
                    
                    # Relationship from summary to finding
                    neo4j_output['relationships'].append({
                        'from': f"summary_executive_{hash(exec_summary.title)}",
                        'to': finding_id,
                        'type': 'HAS_FINDING',
                        'properties': {'order': i}
                    })
        
        # Add insight nodes from timeline analysis
        if 'timeline_insights' in enhanced_result:
            insights = enhanced_result['timeline_insights']
            insights_id = f"insights_{hash(enhanced_result['investigation_title'])}"
            
            neo4j_output['nodes'].append({
                'id': insights_id,
                'label': 'TimelineInsights',
                'properties': {
                    'investigation': enhanced_result['investigation_title'],
                    'timeline_span': insights.get('timeline_span', {}),
                    'most_active_period': insights.get('most_active_period', {}),
                    'key_entities': insights.get('key_entities', []),
                    'location_hotspots': insights.get('location_hotspots', []),
                    'data_quality': insights.get('data_quality', {}),
                    'created_at': datetime.now().isoformat()
                }
            })
        
        # Connect original document to enhanced summaries
        document_id = f"document_{hash(enhanced_result['file_path'])}"
        if 'summaries' in enhanced_result:
            neo4j_output['relationships'].append({
                'from': document_id,
                'to': f"summary_executive_{hash(enhanced_result['investigation_title'])}",
                'type': 'GENERATED_SUMMARY',
                'properties': {'generated_at': datetime.now().isoformat()}
            })
        
        if 'timeline_insights' in enhanced_result:
            neo4j_output['relationships'].append({
                'from': document_id,
                'to': insights_id,
                'type': 'GENERATED_INSIGHTS',
                'properties': {'generated_at': datetime.now().isoformat()}
            })
        
        return neo4j_output
    
    def _generate_cross_document_neo4j_output(self, document_results: List[Dict],
                                            cross_analysis: Dict) -> Dict[str, Any]:
        """
        Generate Neo4j output for cross-document analysis.
        """
        neo4j_output = {
            'nodes': [],
            'relationships': []
        }
        
        # Add cross-reference nodes
        cross_refs = cross_analysis.get('cross_references', [])
        for i, cross_ref in enumerate(cross_refs):
            cross_ref_id = f"cross_ref_{i}"
            neo4j_output['nodes'].append({
                'id': cross_ref_id,
                'label': 'CrossReference',
                'properties': {
                    'entity': cross_ref['entity'],
                    'documents': cross_ref['documents'],
                    'confirmation_count': len(cross_ref['documents']),
                    'reliability_score': cross_analysis.get('reliability_score', 0.5)
                }
            })
        
        # Add confirmation nodes
        confirmations = cross_analysis.get('confirmations', [])
        for i, confirmation in enumerate(confirmations):
            conf_id = f"confirmation_{i}"
            neo4j_output['nodes'].append({
                'id': conf_id,
                'label': 'Confirmation',
                'properties': {
                    'entity': confirmation['entity'],
                    'confirmation_count': confirmation['confirmation_count'],
                    'sources': confirmation['sources']
                }
            })
        
        return neo4j_output
    
    def _generate_sample_queries(self, timeline_data: List[Dict]) -> List[str]:
        """Generate sample queries based on timeline content."""
        queries = [
            "What happened first?",
            "What was the most recent event?",
            "Show me all events this month"
        ]
        
        # Entity-based queries
        entities = list(set(event.get('entity') for event in timeline_data if event.get('entity')))
        if entities:
            queries.append(f"What did {entities[0]} do?")
            if len(entities) > 1:
                queries.append(f"How are {entities[0]} and {entities[1]} connected?")
        
        # Location-based queries  
        locations = list(set(event.get('location') for event in timeline_data if event.get('location')))
        if locations:
            queries.append(f"What happened in {locations[0]}?")
        
        return queries[:8]  # Return top 8 sample queries
    
    def _load_timeline_data(self, investigation_id: str) -> List[Dict]:
        """Load timeline data from stored investigation (placeholder)."""
        # In a real implementation, this would load from database
        # For now, return empty list
        print(f"⚠️  Loading timeline data for investigation {investigation_id} - not yet implemented")
        return []
    
    def _convert_neo4j_to_timeline(self, neo4j_result: Dict[str, Any]) -> List[Dict]:
        """
        Convert Neo4j format result from ETL processor to timeline format for Cedar.
        
        Args:
            neo4j_result: Neo4j structure with nodes and relationships
            
        Returns:
            List of timeline events in the format Cedar expects
        """
        try:
            nodes = neo4j_result.get('nodes', {})
            events = nodes.get('events', [])
            dates = nodes.get('dates', [])
            locations = nodes.get('locations', [])
            entities = nodes.get('entities', [])
            
            # Create lookup maps - handle both id-based and direct formats
            date_map = {}
            for i, date in enumerate(dates):
                if 'id' in date:
                    date_map[date['id']] = date.get('value', date.get('date', ''))
                else:
                    date_map[f"date_{i+1}"] = date.get('date', date.get('value', ''))
            
            location_map = {}
            for i, loc in enumerate(locations):
                if 'id' in loc:
                    location_map[loc['id']] = loc.get('name', loc.get('address', ''))
                else:
                    location_map[f"loc_{i+1}"] = loc.get('address', loc.get('name', ''))
            
            entity_map = {}
            for i, entity in enumerate(entities):
                if 'id' in entity:
                    entity_map[entity['id']] = entity.get('name', '')
                else:
                    entity_map[f"entity_{i+1}"] = entity.get('name', '')
            
            # Get relationships
            relationships = neo4j_result.get('relationships', [])
            
            timeline_events = []
            for i, event in enumerate(events):
                event_id = event.get('id', f'event_{i+1}')
                
                # Find related date, location, entities through relationships
                event_date = None
                event_location = None
                event_entities = []
                
                for rel in relationships:
                    if rel.get('from_node') == event_id:
                        to_node = rel.get('to_node')
                        if to_node in date_map:
                            event_date = date_map[to_node]
                        elif to_node in location_map:
                            event_location = location_map[to_node]
                        elif to_node in entity_map:
                            event_entities.append(entity_map[to_node])
                    elif rel.get('to_node') == event_id:
                        from_node = rel.get('from_node')
                        if from_node in entity_map:
                            event_entities.append(entity_map[from_node])
                
                # If no date found through relationships, use the first available date
                if not event_date and dates:
                    event_date = dates[0].get('date', dates[0].get('value', '2024-01-01'))
                
                # If no location found through relationships, use the first available location
                if not event_location and locations:
                    event_location = locations[0].get('address', locations[0].get('name', 'Unknown Location'))
                
                # Create timeline event
                timeline_event = {
                    'date': event_date or '2024-01-01',  # Default date if none found
                    'event': event.get('title', 'Untitled Event'),
                    'description': event.get('summary', event.get('description', '')),
                    'entity': ', '.join(event_entities) if event_entities else 'Unknown',
                    'entities': event_entities,
                    'location': event_location or 'Unknown Location',
                    'source_event_id': event_id
                }
                
                timeline_events.append(timeline_event)
            
            print(f"🔄 Converted {len(timeline_events)} Neo4j events to timeline format")
            return timeline_events
            
        except Exception as e:
            print(f"❌ Error converting Neo4j to timeline: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _calculate_doc_date_range(self, timeline: List[Dict]) -> Dict[str, str]:
        """Calculate date range for a document's timeline."""
        dates = [event.get('date') for event in timeline if event.get('date')]
        if not dates:
            return {'start': None, 'end': None}
        
        return {
            'start': min(dates),
            'end': max(dates)
        }

def main():
    """
    Command-line interface for Cedar InvestiCAT integration.
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Cedar InvestiCAT - Mastra Agent Productivity Wrapper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py process document.pdf -t "Corporate Investigation" 
  python main.py process report.docx -t "Merger Analysis" --no-summaries
  python main.py query "What happened in January?" --investigation-id inv_123
  python main.py cross-analyze doc1.pdf doc2.pdf -t "Multi-Doc Investigation"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process single document')
    process_parser.add_argument('file', help='Path to PDF or DOCX file')
    process_parser.add_argument('-t', '--title', required=True, 
                               help='Investigation title')
    process_parser.add_argument('--no-summaries', action='store_true',
                               help='Skip summary generation')
    process_parser.add_argument('--no-queries', action='store_true',
                               help='Skip query interface setup')
    process_parser.add_argument('-o', '--output', 
                               help='Output file for results (JSON)')
    
    # Query command  
    query_parser = subparsers.add_parser('query', help='Query timeline data')
    query_parser.add_argument('query', help='Natural language query')
    query_parser.add_argument('--investigation-id', 
                             help='Investigation ID to query')
    query_parser.add_argument('--timeline-file',
                             help='JSON file with timeline data')
    
    # Cross-analyze command
    cross_parser = subparsers.add_parser('cross-analyze', 
                                        help='Cross-document analysis')
    cross_parser.add_argument('files', nargs='+', 
                             help='Multiple PDF/DOCX files to analyze')
    cross_parser.add_argument('-t', '--title', required=True,
                             help='Investigation title')
    cross_parser.add_argument('-o', '--output',
                             help='Output file for results (JSON)')
    
    # Package command
    package_parser = subparsers.add_parser('package', 
                                          help='Generate publication package')
    package_parser.add_argument('--timeline-file', required=True,
                               help='JSON file with timeline data')
    package_parser.add_argument('-t', '--title', required=True,
                               help='Investigation title')
    package_parser.add_argument('--type', choices=['executive', 'journalistic', 'comprehensive'],
                               default='comprehensive', help='Package type')
    package_parser.add_argument('-o', '--output', required=True,
                               help='Output file for package (JSON)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize Cedar integration
    cedar = CedarInvestiCATIntegration()
    
    try:
        if args.command == 'process':
            result = cedar.process_with_mastra_productivity(
                args.file, 
                args.title,
                generate_summaries=not args.no_summaries,
                enable_queries=not args.no_queries
            )
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
                print(f"✅ Results saved to {args.output}")
            else:
                print(json.dumps(result, indent=2, default=str))
        
        elif args.command == 'query':
            timeline_data = None
            if args.timeline_file:
                with open(args.timeline_file, 'r') as f:
                    data = json.load(f)
                    timeline_data = data.get('timeline', [])
            
            result = cedar.query_timeline(
                args.query,
                timeline_data=timeline_data,
                investigation_id=args.investigation_id
            )
            
            print("🔍 Query Results:")
            print(json.dumps(result, indent=2, default=str))
        
        elif args.command == 'cross-analyze':
            result = cedar.cross_document_analysis(args.files, args.title)
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
                print(f"✅ Cross-analysis results saved to {args.output}")
            else:
                print(json.dumps(result, indent=2, default=str))
        
        elif args.command == 'package':
            with open(args.timeline_file, 'r') as f:
                data = json.load(f)
                timeline_data = data.get('timeline', [])
            
            result = cedar.generate_publication_package(
                timeline_data, args.title, args.type
            )
            
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"✅ Publication package saved to {args.output}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()