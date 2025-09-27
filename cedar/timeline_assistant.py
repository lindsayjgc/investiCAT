"""
Timeline Assistant for InvestiCAT
Natural language interface for timeline queries and analysis.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import re
from mastra_agent import MastraAgent, TimelineQuery

class TimelineAssistant:
    """
    Natural language interface for timeline queries.
    Handles conversational queries about investigation timelines.
    """
    
    def __init__(self, mastra_agent: MastraAgent):
        """Initialize with Mastra agent for AI processing."""
        self.agent = mastra_agent
        self.query_patterns = {
            'date_range': [
                r'between\s+(\w+\s+\d{4})\s+and\s+(\w+\s+\d{4})',
                r'from\s+(\w+\s+\d{4})\s+to\s+(\w+\s+\d{4})',
                r'during\s+(\w+\s+\d{4})'
            ],
            'entity_focused': [
                r'who\s+was\s+involved\s+in\s+(.+?)\?',
                r'what\s+did\s+(\w+\s+\w+)\s+do',
                r'show\s+me\s+(.+?)\s+activities'
            ],
            'location_focused': [
                r'what\s+happened\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'events\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'show\s+me\s+all\s+events\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
            ],
            'event_focused': [
                r'when\s+did\s+(.+?)\s+happen',
                r'tell\s+me\s+about\s+the\s+(.+?)\s+(?:event|incident|meeting)',
                r'what\s+happened\s+(?:on|during)\s+(.+?)\?'
            ]
        }
    
    def process_natural_language_query(self, query: str, timeline_data: List[Dict]) -> Dict[str, Any]:
        """
        Process natural language queries against timeline data.
        
        Examples:
        - "What happened between January and March 2024?"
        - "Who was involved in the merger announcement?"
        - "Show me all events in New York"
        - "When did the CEO resignation happen?"
        """
        # Parse query into structured format
        parsed_query = self._parse_query(query)
        
        # Process with Mastra agent
        result = self.agent.process_timeline_query(timeline_data, parsed_query)
        
        # Enhance result with conversation context
        result['conversation_context'] = {
            'original_query': query,
            'query_type': self._identify_query_type(query),
            'suggested_followups': self._generate_followup_suggestions(result, timeline_data)
        }
        
        return result
    
    def get_timeline_insights(self, timeline_data: List[Dict]) -> Dict[str, Any]:
        """
        Generate automatic insights about the timeline.
        Proactive analysis without specific queries.
        """
        insights = {
            'timeline_span': self._calculate_timeline_span(timeline_data),
            'most_active_period': self._find_most_active_period(timeline_data),
            'key_entities': self._identify_key_entities(timeline_data),
            'location_hotspots': self._identify_location_hotspots(timeline_data),
            'event_patterns': self._analyze_event_patterns(timeline_data),
            'data_quality': self._assess_data_quality(timeline_data)
        }
        
        return insights
    
    def generate_interactive_summary(self, timeline_data: List[Dict]) -> Dict[str, Any]:
        """
        Generate interactive summary with clickable elements and drill-down capability.
        """
        return {
            'overview': self._generate_overview_stats(timeline_data),
            'interactive_elements': {
                'clickable_entities': self._generate_clickable_entities(timeline_data),
                'timeline_segments': self._generate_timeline_segments(timeline_data),
                'location_map': self._generate_location_references(timeline_data)
            },
            'suggested_queries': self._generate_suggested_queries(timeline_data),
            'quick_insights': self._generate_quick_insights(timeline_data)
        }
    
    def _parse_query(self, query: str) -> TimelineQuery:
        """Parse natural language query into structured TimelineQuery."""
        query_lower = query.lower()
        
        # Extract date ranges
        start_date, end_date = self._extract_date_range(query_lower)
        
        # Extract entities
        entities = self._extract_entities(query_lower)
        
        # Extract locations
        locations = self._extract_locations(query)
        
        return TimelineQuery(
            query=query,
            start_date=start_date,
            end_date=end_date,
            entities=entities,
            locations=locations
        )
    
    def _extract_date_range(self, query: str) -> tuple[Optional[str], Optional[str]]:
        """Extract date range from natural language query."""
        for pattern in self.query_patterns['date_range']:
            match = re.search(pattern, query)
            if match:
                if len(match.groups()) == 2:
                    return match.group(1), match.group(2)
                elif len(match.groups()) == 1:
                    # Single date/month - create range around it
                    date_str = match.group(1)
                    return date_str, date_str
        
        return None, None
    
    def _extract_entities(self, query: str) -> Optional[List[str]]:
        """Extract entity names from query."""
        entities = []
        
        for pattern in self.query_patterns['entity_focused']:
            match = re.search(pattern, query)
            if match:
                entity = match.group(1).strip()
                if entity not in ['the', 'a', 'an']:
                    entities.append(entity)
        
        # Look for capitalized names (simple heuristic)
        capitalized_words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', query)
        entities.extend(capitalized_words)
        
        return entities if entities else None
    
    def _extract_locations(self, query: str) -> Optional[List[str]]:
        """Extract location names from query."""
        locations = []
        
        for pattern in self.query_patterns['location_focused']:
            match = re.search(pattern, query)
            if match:
                location = match.group(1).strip()
                locations.append(location)
        
        return locations if locations else None
    
    def _identify_query_type(self, query: str) -> str:
        """Identify the type of query for better response formatting."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['when', 'date', 'time']):
            return 'temporal'
        elif any(word in query_lower for word in ['who', 'person', 'people']):
            return 'entity'
        elif any(word in query_lower for word in ['where', 'location', 'place']):
            return 'spatial'
        elif any(word in query_lower for word in ['what', 'how', 'why']):
            return 'descriptive'
        else:
            return 'general'
    
    def _generate_followup_suggestions(self, result: Dict, timeline_data: List[Dict]) -> List[str]:
        """Generate relevant follow-up question suggestions."""
        suggestions = []
        
        # Based on entities found
        entities = [event.get('entity') for event in result.get('supporting_events', [])]
        unique_entities = list(set(filter(None, entities)))
        
        if unique_entities:
            suggestions.append(f"Tell me more about {unique_entities[0]}'s activities")
            if len(unique_entities) > 1:
                suggestions.append(f"How are {unique_entities[0]} and {unique_entities[1]} connected?")
        
        # Based on locations
        locations = [event.get('location') for event in result.get('supporting_events', [])]
        unique_locations = list(set(filter(None, locations)))
        
        if unique_locations:
            suggestions.append(f"What else happened in {unique_locations[0]}?")
        
        # Based on date range
        date_range = result.get('date_range')
        if date_range and date_range['start'] and date_range['end']:
            suggestions.append(f"What happened before {date_range['start']}?")
            suggestions.append(f"What happened after {date_range['end']}?")
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def _calculate_timeline_span(self, timeline_data: List[Dict]) -> Dict[str, Any]:
        """Calculate the span of the timeline."""
        dates = [event.get('date') for event in timeline_data if event.get('date')]
        if not dates:
            return {"span_days": 0, "start_date": None, "end_date": None}
        
        start_date = min(dates)
        end_date = max(dates)
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "span_days": len(set(dates)),
            "total_events": len(timeline_data)
        }
    
    def _find_most_active_period(self, timeline_data: List[Dict]) -> Dict[str, Any]:
        """Find the period with the most activity."""
        date_counts = {}
        for event in timeline_data:
            date = event.get('date')
            if date:
                # Group by month for analysis
                month_key = date[:7] if len(date) >= 7 else date  # YYYY-MM
                date_counts[month_key] = date_counts.get(month_key, 0) + 1
        
        if not date_counts:
            return {"period": None, "event_count": 0}
        
        most_active = max(date_counts.items(), key=lambda x: x[1])
        
        return {
            "period": most_active[0],
            "event_count": most_active[1],
            "percentage_of_total": (most_active[1] / len(timeline_data)) * 100
        }
    
    def _identify_key_entities(self, timeline_data: List[Dict]) -> List[Dict[str, Any]]:
        """Identify the most frequently mentioned entities."""
        entity_counts = {}
        for event in timeline_data:
            entity = event.get('entity')
            if entity:
                entity_counts[entity] = entity_counts.get(entity, 0) + 1
        
        # Sort by frequency
        sorted_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [{"entity": entity, "mention_count": count} 
                for entity, count in sorted_entities[:5]]
    
    def _identify_location_hotspots(self, timeline_data: List[Dict]) -> List[Dict[str, Any]]:
        """Identify locations with most activity."""
        location_counts = {}
        for event in timeline_data:
            location = event.get('location')
            if location:
                location_counts[location] = location_counts.get(location, 0) + 1
        
        sorted_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [{"location": location, "event_count": count} 
                for location, count in sorted_locations[:3]]
    
    def _analyze_event_patterns(self, timeline_data: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in event types and timing."""
        # Simple pattern analysis
        event_types = {}
        for event in timeline_data:
            event_text = event.get('event', '').lower()
            # Categorize events (basic implementation)
            if any(word in event_text for word in ['meeting', 'conference', 'call']):
                event_types['meetings'] = event_types.get('meetings', 0) + 1
            elif any(word in event_text for word in ['announcement', 'statement', 'press']):
                event_types['announcements'] = event_types.get('announcements', 0) + 1
            elif any(word in event_text for word in ['transaction', 'payment', 'transfer']):
                event_types['transactions'] = event_types.get('transactions', 0) + 1
            else:
                event_types['other'] = event_types.get('other', 0) + 1
        
        return event_types
    
    def _assess_data_quality(self, timeline_data: List[Dict]) -> Dict[str, Any]:
        """Assess the quality and completeness of timeline data."""
        total_events = len(timeline_data)
        if total_events == 0:
            return {"quality_score": 0.0, "completeness": 0.0}
        
        complete_events = 0
        missing_fields = {'date': 0, 'event': 0, 'entity': 0, 'location': 0}
        
        for event in timeline_data:
            event_complete = True
            for field in missing_fields.keys():
                if not event.get(field):
                    missing_fields[field] += 1
                    event_complete = False
            if event_complete:
                complete_events += 1
        
        quality_score = complete_events / total_events
        completeness = 1.0 - (sum(missing_fields.values()) / (total_events * 4))
        
        return {
            "quality_score": quality_score,
            "completeness": completeness,
            "missing_fields": missing_fields,
            "complete_events": complete_events
        }
    
    def _generate_overview_stats(self, timeline_data: List[Dict]) -> Dict[str, Any]:
        """Generate high-level overview statistics."""
        return {
            "total_events": len(timeline_data),
            "unique_entities": len(set(event.get('entity') for event in timeline_data if event.get('entity'))),
            "unique_locations": len(set(event.get('location') for event in timeline_data if event.get('location'))),
            "date_coverage": len(set(event.get('date') for event in timeline_data if event.get('date')))
        }
    
    def _generate_clickable_entities(self, timeline_data: List[Dict]) -> List[Dict[str, Any]]:
        """Generate clickable entity elements for interactive display."""
        entities = {}
        for event in timeline_data:
            entity = event.get('entity')
            if entity:
                if entity not in entities:
                    entities[entity] = []
                entities[entity].append(event)
        
        return [{"entity": entity, "event_count": len(events), "sample_event": events[0]} 
                for entity, events in entities.items()]
    
    def _generate_timeline_segments(self, timeline_data: List[Dict]) -> List[Dict[str, Any]]:
        """Generate timeline segments for visual navigation."""
        # Group events by month
        segments = {}
        for event in timeline_data:
            date = event.get('date')
            if date:
                month_key = date[:7] if len(date) >= 7 else date
                if month_key not in segments:
                    segments[month_key] = []
                segments[month_key].append(event)
        
        return [{"period": period, "event_count": len(events)} 
                for period, events in sorted(segments.items())]
    
    def _generate_location_references(self, timeline_data: List[Dict]) -> List[Dict[str, Any]]:
        """Generate location references for mapping."""
        locations = {}
        for event in timeline_data:
            location = event.get('location')
            if location:
                if location not in locations:
                    locations[location] = []
                locations[location].append(event)
        
        return [{"location": location, "events": events} 
                for location, events in locations.items()]
    
    def _generate_suggested_queries(self, timeline_data: List[Dict]) -> List[str]:
        """Generate suggested queries based on data content."""
        suggestions = []
        
        # Entity-based suggestions
        entities = list(set(event.get('entity') for event in timeline_data if event.get('entity')))
        if entities:
            suggestions.append(f"What did {entities[0]} do?")
            if len(entities) > 1:
                suggestions.append(f"How are {entities[0]} and {entities[1]} connected?")
        
        # Location-based suggestions
        locations = list(set(event.get('location') for event in timeline_data if event.get('location')))
        if locations:
            suggestions.append(f"What happened in {locations[0]}?")
        
        # Time-based suggestions
        dates = [event.get('date') for event in timeline_data if event.get('date')]
        if dates:
            suggestions.append("What happened first?")
            suggestions.append("What was the most recent event?")
        
        return suggestions[:5]
    
    def _generate_quick_insights(self, timeline_data: List[Dict]) -> List[str]:
        """Generate quick insights for immediate display."""
        insights = []
        
        span = self._calculate_timeline_span(timeline_data)
        if span['span_days'] > 0:
            insights.append(f"Timeline spans {span['span_days']} days with {span['total_events']} events")
        
        key_entities = self._identify_key_entities(timeline_data)
        if key_entities:
            top_entity = key_entities[0]
            insights.append(f"{top_entity['entity']} appears {top_entity['mention_count']} times")
        
        active_period = self._find_most_active_period(timeline_data)
        if active_period['period']:
            insights.append(f"Most active period: {active_period['period']} with {active_period['event_count']} events")
        
        return insights