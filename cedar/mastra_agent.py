"""
Mastra Agent Implementation for InvestiCAT
Intelligent productivity wrapper for journalism document processing.
"""

from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from dataclasses import dataclass

# OpenAI integration
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

@dataclass
class TimelineQuery:
    """Structured query for timeline data."""
    query: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    entities: Optional[List[str]] = None
    locations: Optional[List[str]] = None

@dataclass 
class InvestigationSummary:
    """Investigation summary data structure."""
    executive_summary: str
    key_findings: List[str]
    timeline_highlights: List[Dict[str, Any]]
    entity_relationships: List[Dict[str, Any]]
    confidence_score: float
    title: str  # Changed from investigation_title to match existing code

class MastraAgent:
    """
    Main Mastra agent for InvestiCAT productivity enhancement.
    Provides intelligent querying and summarization capabilities.
    """
    
    def __init__(self, openai_api_key: str = None):
        """Initialize Mastra agent with optional OpenAI integration."""
        self.ai_enabled = False
        self.client = None
        
        if OPENAI_AVAILABLE and openai_api_key:
            try:
                self.client = OpenAI(api_key=openai_api_key)
                self.ai_enabled = True
                print("Mastra Agent: OpenAI integration enabled")
            except Exception as e:
                print(f"Mastra Agent: OpenAI initialization failed: {e}")
        
        self.system_prompt = """
        You are an expert investigative journalism AI assistant specialized in timeline analysis.
        
        Your role is to:
        1. Analyze document timelines and extract meaningful patterns
        2. Answer natural language queries about investigations  
        3. Provide actionable insights for journalists
        4. Cross-reference events and detect inconsistencies
        5. Generate publication-ready summaries and briefings
        
        Always provide accurate, well-sourced, and journalism-standard responses.
        """
    
    def process_timeline_query(self, timeline_data: List[Dict], query: TimelineQuery) -> Dict[str, Any]:
        """
        Process natural language queries against timeline data with conversational responses.
        
        Examples:
        - "What happened between January and March?"
        - "Who was involved in the merger announcement?"
        - "Show me all events in New York"
        """
        # Filter timeline data based on query parameters
        filtered_events = self._filter_timeline_events(timeline_data, query)
        
        # Generate conversational response based on actual events
        conversational_response = self._generate_conversational_response(query.query, filtered_events)
        
        # Prepare context for AI enhancement if available
        if self.ai_enabled and len(filtered_events) > 0:
            context = self._prepare_detailed_event_context(filtered_events)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an investigative journalism assistant. Provide conversational, human-readable responses about timeline events. Focus on telling the story using actual event details, dates, and participants. Avoid technical jargon and statistics unless specifically asked."},
                    {"role": "user", "content": f"""
                    User Question: {query.query}
                    
                    Timeline Events Found: {context}
                    
                    Please provide a natural, conversational response that directly answers the user's question using the actual event information. Structure your response as if you're explaining the story to someone, mentioning specific dates, people, and what actually happened.
                    """}
                ],
                temperature=0.3
            )
            ai_response = response.choices[0].message.content
        else:
            # Use the conversational response we generated
            ai_response = conversational_response
        
        return {
            "query": query.query,
            "answer": ai_response,
            "supporting_events": filtered_events,
            "event_count": len(filtered_events),
            "entities_involved": list(set(event.get('entity', '') for event in filtered_events if event.get('entity'))),
            "date_range": self._get_date_range(filtered_events),
            "response_type": "conversational"
        }

    def generate_investigation_summary(self, timeline_data: List[Dict], title: str) -> InvestigationSummary:
        """
        Generate comprehensive investigation summary from timeline data.
        Creates publication-ready briefings and key findings.
        """
        context = self._prepare_timeline_context(timeline_data)
        
        if self.ai_enabled:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"""
                    Generate a comprehensive investigation summary for: {title}
                    
                    Timeline data: {context}
                    
                    Create an executive summary, key findings, and timeline highlights.
                    Focus on investigative journalism standards and actionable insights.
                    """}
                ],
                temperature=0.2
            )
            
            summary_text = response.choices[0].message.content
            
            # Parse the AI response into structured data
            return InvestigationSummary(
                executive_summary=self._extract_executive_summary(summary_text),
                key_findings=self._extract_key_findings(summary_text),
                timeline_highlights=self._extract_timeline_highlights(timeline_data),
                entity_relationships=self._analyze_entity_relationships(timeline_data),
                confidence_score=self._calculate_confidence_score(timeline_data),
                title=title
            )
        else:
            # Generate mock summary for demo
            return InvestigationSummary(
                executive_summary=self._generate_mock_summary(title, timeline_data),
                key_findings=[f"Finding {i+1} from timeline analysis" for i in range(3)],
                timeline_highlights=self._extract_timeline_highlights(timeline_data),
                entity_relationships=self._analyze_entity_relationships(timeline_data),
                confidence_score=self._calculate_confidence_score(timeline_data),
                title=title
            )

    # Helper methods for conversational responses
    def _generate_conversational_response(self, query: str, filtered_events: List[Dict]) -> str:
        """Generate a human-readable, conversational response from filtered events."""
        if not filtered_events:
            return f"I couldn't find any events related to '{query}' in the timeline data."
        
        # Sort events by date
        sorted_events = sorted(filtered_events, key=lambda x: x.get('date', '1900-01-01'))
        
        # Analyze query to determine response style
        query_lower = query.lower()
        
        if 'what happened' in query_lower or 'tell me about' in query_lower:
            return self._generate_story_response(query, sorted_events)
        elif 'when' in query_lower:
            return self._generate_date_response(query, sorted_events)
        elif 'who' in query_lower:
            return self._generate_entity_response(query, sorted_events)
        elif 'where' in query_lower:
            return self._generate_location_response(query, sorted_events)
        else:
            return self._generate_general_response(query, sorted_events)
    
    def _generate_story_response(self, query: str, events: List[Dict]) -> str:
        """Generate a narrative story response."""
        if len(events) == 1:
            event = events[0]
            date = event.get('date', 'Unknown date')
            title = event.get('event', event.get('title', 'Unknown event'))
            description = event.get('description', event.get('summary', ''))
            entity = event.get('entity', 'Unknown entity')
            location = event.get('location', '')
            
            location_text = f" in {location}" if location and location != 'Unknown Location' else ""
            return f"Based on the timeline, here's what happened: On {date}, {title}{location_text}. {description} This involved {entity}."
        
        # Multiple events - create a narrative
        response = f"Based on the timeline, here's what happened:\n\n"
        
        for i, event in enumerate(events[:5]):  # Limit to 5 events for readability
            date = event.get('date', 'Unknown date')
            title = event.get('event', event.get('title', 'Unknown event'))
            description = event.get('description', event.get('summary', ''))
            entity = event.get('entity', '')
            location = event.get('location', '')
            
            location_text = f" in {location}" if location and location != 'Unknown Location' else ""
            entity_text = f" involving {entity}" if entity and entity != 'Unknown' else ""
            
            if i == 0:
                response += f"• {date}: {title}{location_text}{entity_text}. {description}\n"
            else:
                response += f"• Then on {date}: {title}{entity_text}. {description}\n"
        
        if len(events) > 5:
            response += f"\n...and {len(events) - 5} more events in the timeline."
        
        return response
    
    def _generate_date_response(self, query: str, events: List[Dict]) -> str:
        """Generate a date-focused response."""
        if not events:
            return "I couldn't find specific dates for that query."
        
        if len(events) == 1:
            event = events[0]
            date = event.get('date', 'Unknown date')
            title = event.get('event', event.get('title', 'the event'))
            return f"{title} happened on {date}."
        
        response = "Here are the relevant dates:\n\n"
        for event in events[:3]:  # Show top 3 dates
            date = event.get('date', 'Unknown date')
            title = event.get('event', event.get('title', 'Event'))
            response += f"• {date}: {title}\n"
        
        return response
    
    def _generate_entity_response(self, query: str, events: List[Dict]) -> str:
        """Generate an entity-focused response."""
        entities = set()
        entity_events = {}
        
        for event in events:
            entity = event.get('entity', '')
            if entity and entity != 'Unknown':
                entities.add(entity)
                if entity not in entity_events:
                    entity_events[entity] = []
                entity_events[entity].append(event)
        
        if not entities:
            return "I couldn't identify specific people or organizations involved."
        
        response = "Here's who was involved:\n\n"
        for entity in list(entities)[:3]:  # Show top 3 entities
            events_for_entity = entity_events[entity]
            response += f"• **{entity}**: Involved in {len(events_for_entity)} event(s)\n"
            for event in events_for_entity[:2]:  # Show up to 2 events per entity
                date = event.get('date', 'Unknown date')
                title = event.get('event', event.get('title', 'Event'))
                response += f"  - {date}: {title}\n"
        
        return response
    
    def _generate_location_response(self, query: str, events: List[Dict]) -> str:
        """Generate a location-focused response."""
        locations = set()
        location_events = {}
        
        for event in events:
            location = event.get('location', '')
            if location and location != 'Unknown Location':
                locations.add(location)
                if location not in location_events:
                    location_events[location] = []
                location_events[location].append(event)
        
        if not locations:
            return "I couldn't identify specific locations from the events."
        
        response = "Here are the relevant locations:\n\n"
        for location in list(locations)[:3]:  # Show top 3 locations
            events_for_location = location_events[location]
            response += f"• **{location}**: {len(events_for_location)} event(s)\n"
            for event in events_for_location[:2]:  # Show up to 2 events per location
                date = event.get('date', 'Unknown date')
                title = event.get('event', event.get('title', 'Event'))
                response += f"  - {date}: {title}\n"
        
        return response
    
    def _generate_general_response(self, query: str, events: List[Dict]) -> str:
        """Generate a general response for other query types."""
        if len(events) == 1:
            event = events[0]
            date = event.get('date', 'Unknown date')
            title = event.get('event', event.get('title', 'Unknown event'))
            description = event.get('description', event.get('summary', ''))
            return f"I found one relevant event: {title} on {date}. {description}"
        
        response = f"I found {len(events)} relevant events:\n\n"
        for event in events[:3]:  # Show top 3 events
            date = event.get('date', 'Unknown date')
            title = event.get('event', event.get('title', 'Event'))
            response += f"• {date}: {title}\n"
        
        if len(events) > 3:
            response += f"\n...and {len(events) - 3} more events."
        
        return response
    
    def _prepare_detailed_event_context(self, events: List[Dict]) -> str:
        """Prepare detailed context from events for AI processing."""
        context_parts = []
        for i, event in enumerate(events, 1):
            context_parts.append(
                f"Event {i}: {event.get('event', event.get('title', 'Unknown'))}"
                f" | Date: {event.get('date', 'Unknown')}"
                f" | Entity: {event.get('entity', 'Unknown')}"
                f" | Location: {event.get('location', 'Unknown')}"
                f" | Description: {event.get('description', event.get('summary', 'No description'))}"
            )
        return "\n".join(context_parts)

    # Existing helper methods
    def _filter_timeline_events(self, timeline_data: List[Dict], query: TimelineQuery) -> List[Dict]:
        """Filter timeline events based on query parameters."""
        filtered = timeline_data
        
        # Filter by date range
        if query.start_date or query.end_date:
            filtered = [event for event in filtered 
                       if self._event_in_date_range(event, query.start_date, query.end_date)]
        
        # Filter by entities
        if query.entities:
            filtered = [event for event in filtered 
                       if any(entity.lower() in event.get('entity', '').lower() 
                             for entity in query.entities)]
        
        # Filter by locations
        if query.locations:
            filtered = [event for event in filtered 
                       if any(loc.lower() in event.get('location', '').lower() 
                             for loc in query.locations)]
        
        return filtered

    def _event_in_date_range(self, event: Dict, start_date: str, end_date: str) -> bool:
        """Check if event falls within date range."""
        event_date = event.get('date', '')
        if not event_date:
            return False
        
        if start_date and event_date < start_date:
            return False
        if end_date and event_date > end_date:
            return False
        
        return True

    def _prepare_timeline_context(self, events: List[Dict]) -> str:
        """Prepare context from filtered events for AI processing."""
        context_items = []
        for event in events:
            item = f"Date: {event.get('date', 'Unknown')}, "
            item += f"Event: {event.get('event', 'Unknown')}, "
            item += f"Entity: {event.get('entity', 'Unknown')}, "
            item += f"Location: {event.get('location', 'Unknown')}"
            context_items.append(item)
        
        return "\n".join(context_items)
    
    def _get_date_range(self, events: List[Dict]) -> Dict[str, str]:
        """Get date range from filtered events."""
        dates = [event.get('date') for event in events if event.get('date')]
        if not dates:
            return {"start": None, "end": None}
        
        return {
            "start": min(dates),
            "end": max(dates)
        }
    
    def _extract_executive_summary(self, summary_text: str) -> str:
        """Extract executive summary from AI response."""
        lines = summary_text.split('\n')
        summary_lines = []
        in_summary = False
        
        for line in lines:
            if 'executive summary' in line.lower():
                in_summary = True
                continue
            elif line.strip().startswith('#') and in_summary:
                break
            elif in_summary and line.strip():
                summary_lines.append(line.strip())
        
        return '\n'.join(summary_lines) if summary_lines else summary_text[:500]
    
    def _extract_key_findings(self, summary_text: str) -> List[str]:
        """Extract key findings from AI response."""
        findings = []
        lines = summary_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                findings.append(line[1:].strip())
            elif line.lower().startswith('finding'):
                findings.append(line)
        
        return findings[:5] if findings else ["Timeline analysis completed", "Events extracted successfully", "Entity relationships mapped"]
    
    def _extract_timeline_highlights(self, timeline_data: List[Dict]) -> List[Dict[str, Any]]:
        """Extract timeline highlights from data."""
        sorted_events = sorted(timeline_data, 
                             key=lambda x: len(x.get('entity', '')), 
                             reverse=True)
        return sorted_events[:5]
    
    def _analyze_entity_relationships(self, timeline_data: List[Dict]) -> List[Dict[str, Any]]:
        """Analyze relationships between entities."""
        relationships = {}
        
        date_groups = {}
        for event in timeline_data:
            date = event.get('date')
            if date not in date_groups:
                date_groups[date] = []
            date_groups[date].append(event.get('entity'))
        
        for date, entities in date_groups.items():
            if len(entities) > 1:
                for i, entity1 in enumerate(entities):
                    for entity2 in entities[i+1:]:
                        if entity1 and entity2:
                            key = tuple(sorted([entity1, entity2]))
                            relationships[key] = relationships.get(key, 0) + 1
        
        return [{"entities": list(k), "interaction_count": v} 
                for k, v in relationships.items()]
    
    def _calculate_confidence_score(self, timeline_data: List[Dict]) -> float:
        """Calculate confidence score based on data quality."""
        if not timeline_data:
            return 0.0
        
        complete_events = sum(1 for event in timeline_data 
                            if all(event.get(field) for field in ['date', 'event', 'entity', 'location']))
        
        return complete_events / len(timeline_data)

    def _generate_mock_summary(self, title: str, timeline_data: List[Dict]) -> str:
        """Generate mock summary for demo purposes."""
        entities = list(set(event.get('entity', '') for event in timeline_data if event.get('entity')))
        locations = list(set(event.get('location', '') for event in timeline_data if event.get('location')))
        
        return f"""## Executive Summary

The {title} investigation reveals a complex timeline of {len(timeline_data)} key events involving {len(entities)} primary entities. 
The investigation spans multiple locations including {', '.join(locations[:3])}, with significant activity patterns emerging.

Key players in this investigation include {', '.join(entities[:3])}, who appear consistently throughout the timeline. 
The events show clear connections between corporate activities and regulatory processes."""