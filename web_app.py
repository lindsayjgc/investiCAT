#!/usr/bin/env python3
"""
InvestiCAT Web Application
Simple Flask web interface for PDF document processing and timeline analysis
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import os
import sys
from pathlib import Path
import json
import uuid
from datetime import datetime

# Add the etl and cedar directories to the Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / 'etl'))
sys.path.insert(0, str(current_dir / 'cedar'))

try:
    from document_processor_neo4j import InvestiCATProcessor as RealETLProcessor
    REAL_ETL_AVAILABLE = True
    print("✅ Real ETL processor imported successfully")
except ImportError as e:
    RealETLProcessor = None
    REAL_ETL_AVAILABLE = False
    print(f"❌ Could not import real ETL processor: {e}")

try:
    from main import CedarInvestiCATIntegration
except ImportError:
    CedarInvestiCATIntegration = None
    print("Warning: Could not import CedarInvestiCATIntegration from cedar")

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Configuration
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)
os.makedirs('templates', exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['file']
        investigation_title = request.form.get('investigation_title', 'Untitled Investigation')
        
        # If user does not select file, browser also submits an empty part without filename
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to avoid name conflicts
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process the document
            try:
                result_id = process_document(filepath, investigation_title, filename)
                flash(f'File successfully uploaded and processed! Investigation ID: {result_id}')
                return redirect(url_for('view_results', result_id=result_id))
            except Exception as e:
                flash(f'Error processing file: {str(e)}')
                return redirect(request.url)
        else:
            flash('Invalid file type. Please upload PDF, TXT, DOC, or DOCX files.')
            return redirect(request.url)
    
    return render_template('upload.html')

def convert_neo4j_to_timeline(neo4j_result):
    """Convert Neo4j format result to timeline format for Cedar"""
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
        
        return {
            'timeline': timeline_events,
            'neo4j_output': neo4j_result,
            'summary': f'Extracted {len(timeline_events)} events from document',
            'investigation_title': neo4j_result.get('investigation_title', 'Investigation')
        }
        
    except Exception as e:
        print(f"Error converting Neo4j to timeline: {e}")
        return {
            'timeline': [],
            'neo4j_output': neo4j_result,
            'summary': f'Error processing: {str(e)}',
            'investigation_title': 'Investigation'
        }

def extract_entities_from_timeline(timeline_data):
    """Extract unique entities from timeline events"""
    entities = set()
    for event in timeline_data:
        if isinstance(event, dict):
            if 'entity' in event and event['entity']:
                entities.add(event['entity'])
            if 'entities' in event and event['entities']:
                if isinstance(event['entities'], list):
                    entities.update(event['entities'])
                else:
                    entities.add(event['entities'])
    return list(entities)

def process_document(filepath, investigation_title, original_filename):
    """Process uploaded document through ETL and Cedar AI pipeline"""
    result_id = str(uuid.uuid4())
    
    try:
        # Try Cedar AI integration first
        if CedarInvestiCATIntegration:
            print("🤖 Processing with Cedar AI Integration...")
            # Set OpenAI API key for real AI processing
            api_key = "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"
            cedar = CedarInvestiCATIntegration(openai_api_key=api_key)
            result = cedar.process_with_mastra_productivity(filepath, investigation_title)
            
            timeline_data = result.get('timeline', [])
            entities = extract_entities_from_timeline(timeline_data)
            
            # Extract summary and key findings
            summaries = result.get('summaries', {})
            executive_summary = summaries.get('executive_summary', {})
            
            # Handle both dict and object formats
            if hasattr(executive_summary, 'executive_summary'):
                summary_text = executive_summary.executive_summary
                key_findings = getattr(executive_summary, 'key_findings', [])
            elif isinstance(executive_summary, dict):
                summary_text = executive_summary.get('executive_summary', 'Processing completed successfully')
                key_findings = executive_summary.get('key_findings', [])
            else:
                summary_text = str(executive_summary) if executive_summary else 'Processing completed successfully'
                key_findings = []
            
            # Save results
            result_data = {
                'id': result_id,
                'title': investigation_title,
                'filename': original_filename,
                'uploaded_at': datetime.now().isoformat(),
                'processing_method': 'Cedar AI Integration',
                'status': 'completed',
                'cedar_result': {
                    'timeline': timeline_data,
                    'summary': summary_text,
                    'entities': entities,
                    'key_findings': key_findings,
                    'interactive_summary': result.get('interactive_summary', ''),
                    'timeline_insights': result.get('timeline_insights', {}),
                    'query_interface': result.get('query_interface', {})
                }
            }
            
        # Fallback to real ETL processor
        elif RealETLProcessor:
            print("📄 Processing with Real ETL Pipeline...")
            api_key = "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"
            processor = RealETLProcessor(openai_api_key=api_key)
            neo4j_result = processor.process_document(filepath, investigation_title)
            
            # Convert Neo4j format to timeline format
            result = convert_neo4j_to_timeline(neo4j_result)
            
            result_data = {
                'id': result_id,
                'title': investigation_title,
                'filename': original_filename,
                'uploaded_at': datetime.now().isoformat(),
                'processing_method': 'Real ETL Pipeline',
                'status': 'completed',
                'etl_result': {
                    'timeline': result.get('timeline', []),
                    'summary': result.get('summary', 'Processing completed successfully'),
                    'entities': extract_entities_from_timeline(result.get('timeline', [])),
                    'neo4j_output': result.get('neo4j_output', {}),
                    'investigation_title': result.get('investigation_title', investigation_title)
                }
            }
            
        else:
            # Mock processing for demo
            print("🔄 Using mock processing...")
            result_data = {
                'id': result_id,
                'title': investigation_title,
                'filename': original_filename,
                'uploaded_at': datetime.now().isoformat(),
                'processing_method': 'Mock Demo',
                'status': 'completed',
                'mock_result': {
                    'timeline': [
                        {
                            'date': '2024-01-15',
                            'event': 'Document uploaded for analysis',
                            'entity': 'System',
                            'location': 'InvestiCAT Platform'
                        }
                    ],
                    'summary': f'Successfully processed {original_filename}',
                    'entities': ['System', 'User'],
                    'key_findings': ['Document processing completed', 'Ready for investigation']
                }
            }
        
        # Save results to file
        result_file = os.path.join(RESULTS_FOLDER, f'{result_id}.json')
        with open(result_file, 'w') as f:
            json.dump(result_data, f, indent=2, default=str)
            
        return result_id
        
    except Exception as e:
        print(f"Error processing document: {e}")
        # Save error result
        error_data = {
            'id': result_id,
            'title': investigation_title,
            'filename': original_filename,
            'uploaded_at': datetime.now().isoformat(),
            'processing_method': 'Error',
            'status': 'error',
            'error': str(e)
        }
        
        result_file = os.path.join(RESULTS_FOLDER, f'{result_id}.json')
        with open(result_file, 'w') as f:
            json.dump(error_data, f, indent=2, default=str)
            
        return result_id

@app.route('/results/<result_id>')
def view_results(result_id):
    try:
        result_file = os.path.join(RESULTS_FOLDER, f'{result_id}.json')
        with open(result_file, 'r') as f:
            result_data = json.load(f)
        return render_template('results.html', result=result_data)
    except FileNotFoundError:
        flash('Results not found')
        return redirect(url_for('index'))

@app.route('/api/query', methods=['POST'])
def api_query():
    """API endpoint for AI queries against processed documents"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        result_id = data.get('result_id', '')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
            
        if not result_id:
            return jsonify({'error': 'Result ID is required'}), 400
            
        # Load result data
        result_file = os.path.join(RESULTS_FOLDER, f'{result_id}.json')
        with open(result_file, 'r') as f:
            result_data = json.load(f)
            
        # Try to process query with Cedar AI
        if CedarInvestiCATIntegration and 'cedar_result' in result_data:
            cedar = CedarInvestiCATIntegration()
            timeline_data = result_data['cedar_result'].get('timeline', [])
            
            query_result = cedar.query_timeline(query, timeline_data)
            return jsonify(query_result)
        else:
            # Mock response
            return jsonify({
                'answer': f'Mock response to: {query}',
                'supporting_events': [],
                'confidence': 0.5
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/investigations')
def list_investigations():
    """List all processed investigations"""
    investigations = []
    
    try:
        for filename in os.listdir(RESULTS_FOLDER):
            if filename.endswith('.json'):
                with open(os.path.join(RESULTS_FOLDER, filename), 'r') as f:
                    data = json.load(f)
                    investigations.append({
                        'id': data['id'],
                        'title': data['title'],
                        'filename': data['filename'],
                        'uploaded_at': data['uploaded_at'],
                        'status': data['status'],
                        'processing_method': data['processing_method']
                    })
    except Exception as e:
        print(f"Error loading investigations: {e}")
        
    # Sort by upload date, newest first
    investigations.sort(key=lambda x: x['uploaded_at'], reverse=True)
    
    return render_template('investigations.html', investigations=investigations)

if __name__ == '__main__':
    print("🚀 Starting InvestiCAT Web Application")
    print("=" * 50)
    print("📱 Access the application at: http://127.0.0.1:5001")
    print("📄 Upload PDFs at: http://127.0.0.1:5001/upload")
    print("📋 View investigations at: http://127.0.0.1:5001/investigations")
    print("🔧 Available integrations:")
    if CedarInvestiCATIntegration:
        print("  ✅ Cedar AI Integration")
    else:
        print("  ❌ Cedar AI Integration (not available)")
    if REAL_ETL_AVAILABLE:
        print("  ✅ Real ETL Pipeline with PDF parsing")
    else:
        print("  ❌ Real ETL Pipeline (not available)")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5001)