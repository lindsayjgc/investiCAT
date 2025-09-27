"""
Summary Generator for InvestiCAT
Automated generation of investigation summaries and publication-ready briefings.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
from mastra_agent import MastraAgent, InvestigationSummary

class SummaryGenerator:
    """
    Automated summary generation for investigation timelines.
    Creates executive summaries, key findings, and publication-ready briefings.
    """
    
    def __init__(self, mastra_agent: MastraAgent):
        """Initialize with Mastra agent for AI processing."""
        self.agent = mastra_agent
        self.summary_templates = {
            'executive': {
                'format': 'executive_summary',
                'length': 'medium',
                'audience': 'executives'
            },
            'briefing': {
                'format': 'briefing_note',
                'length': 'short',
                'audience': 'journalists'
            },
            'detailed': {
                'format': 'detailed_report',
                'length': 'long',
                'audience': 'investigators'
            },
            'publication': {
                'format': 'article_draft',
                'length': 'medium',
                'audience': 'public'
            }
        }
    
    def generate_executive_summary(self, timeline_data: List[Dict], title: str, 
                                 template_type: str = 'executive') -> InvestigationSummary:
        """
        Generate executive summary optimized for senior leadership consumption.
        """
        template = self.summary_templates.get(template_type, self.summary_templates['executive'])
        
        # Generate base summary using Mastra agent
        base_summary = self.agent.generate_investigation_summary(timeline_data, title)
        
        # Enhance for executive audience
        enhanced_summary = self._enhance_for_executives(base_summary, timeline_data)
        
        return enhanced_summary
    
    def generate_briefing_note(self, timeline_data: List[Dict], title: str, 
                             urgency: str = 'normal') -> Dict[str, Any]:
        """
        Generate concise briefing note for journalists and editors.
        
        Args:
            urgency: 'high', 'normal', 'low' - affects structure and emphasis
        """
        summary = self.agent.generate_investigation_summary(timeline_data, title)
        
        briefing = {
            'header': {
                'title': title,
                'date_generated': datetime.now().isoformat(),
                'urgency': urgency,
                'classification': 'internal'
            },
            'summary': {
                'headline': self._generate_headline(timeline_data, title),
                'lead_paragraph': self._generate_lead_paragraph(summary),
                'key_points': summary.key_findings[:5],  # Top 5 findings
                'context': self._generate_context_paragraph(timeline_data)
            },
            'details': {
                'timeline_highlights': summary.timeline_highlights,
                'key_figures': self._extract_key_figures(timeline_data),
                'locations': self._extract_key_locations(timeline_data),
                'source_quality': self._assess_source_quality(timeline_data)
            },
            'editorial_notes': {
                'angle_suggestions': self._suggest_story_angles(timeline_data),
                'verification_needed': self._identify_verification_needs(timeline_data),
                'follow_up_leads': self._generate_follow_up_leads(timeline_data)
            }
        }
        
        if urgency == 'high':
            briefing['alert'] = {
                'reason': 'High priority investigation',
                'immediate_actions': self._generate_immediate_actions(timeline_data),
                'deadline_sensitive': True
            }
        
        return briefing
    
    def generate_publication_draft(self, timeline_data: List[Dict], title: str, 
                                 style: str = 'news') -> Dict[str, Any]:
        """
        Generate publication-ready article draft.
        
        Args:
            style: 'news', 'feature', 'investigative', 'brief'
        """
        summary = self.agent.generate_investigation_summary(timeline_data, title)
        
        article_structure = {
            'headline': self._generate_headline(timeline_data, title),
            'subhead': self._generate_subhead(summary),
            'byline': '[BYLINE]',
            'date': datetime.now().strftime('%B %d, %Y'),
            
            'lead': self._generate_article_lead(summary, style),
            'body': self._generate_article_body(timeline_data, summary, style),
            'conclusion': self._generate_conclusion(summary),
            
            'metadata': {
                'word_count': 0,  # To be calculated
                'reading_time': 0,  # To be calculated
                'key_entities': [entity for rel in summary.entity_relationships for entity in rel.get('entities', [])],
                'locations': self._extract_key_locations(timeline_data),
                'time_span': self._calculate_time_span(timeline_data)
            },
            
            'editorial_checklist': {
                'fact_check_required': self._identify_fact_check_items(timeline_data),
                'legal_review': self._identify_legal_considerations(timeline_data),
                'source_verification': self._identify_sources_to_verify(timeline_data),
                'additional_reporting': self._suggest_additional_reporting(timeline_data)
            }
        }
        
        # Calculate metadata
        full_text = f"{article_structure['lead']} {article_structure['body']} {article_structure['conclusion']}"
        article_structure['metadata']['word_count'] = len(full_text.split())
        article_structure['metadata']['reading_time'] = max(1, article_structure['metadata']['word_count'] // 200)
        
        return article_structure
    
    def generate_multi_format_package(self, timeline_data: List[Dict], title: str) -> Dict[str, Any]:
        """
        Generate complete package with multiple format summaries.
        """
        base_summary = self.agent.generate_investigation_summary(timeline_data, title)
        
        package = {
            'investigation_title': title,
            'generated_at': datetime.now().isoformat(),
            'source_data_summary': {
                'total_events': len(timeline_data),
                'date_range': self._calculate_time_span(timeline_data),
                'entity_count': len(set(event.get('entity') for event in timeline_data if event.get('entity'))),
                'location_count': len(set(event.get('location') for event in timeline_data if event.get('location')))
            },
            
            'formats': {
                'executive_summary': self.generate_executive_summary(timeline_data, title),
                'briefing_note': self.generate_briefing_note(timeline_data, title),
                'publication_draft': self.generate_publication_draft(timeline_data, title),
                'detailed_timeline': self._generate_detailed_timeline(timeline_data),
                'entity_profiles': self._generate_entity_profiles(timeline_data),
                'infographic_data': self._generate_infographic_data(timeline_data)
            },
            
            'quality_assessment': {
                'confidence_score': base_summary.confidence_score,
                'data_completeness': self._calculate_completeness(timeline_data),
                'verification_status': self._assess_verification_status(timeline_data),
                'editorial_readiness': self._assess_editorial_readiness(timeline_data)
            },
            
            'next_steps': {
                'immediate_actions': self._generate_immediate_actions(timeline_data),
                'investigation_leads': self._generate_follow_up_leads(timeline_data),
                'publication_timeline': self._suggest_publication_timeline(timeline_data)
            }
        }
        
        return package
    
    def _enhance_for_executives(self, summary: InvestigationSummary, 
                              timeline_data: List[Dict]) -> InvestigationSummary:
        """Enhance summary specifically for executive audience."""
        # Add executive-focused elements
        summary.business_impact = self._assess_business_impact(timeline_data)
        summary.risk_assessment = self._assess_risks(timeline_data)
        summary.recommended_actions = self._generate_executive_actions(timeline_data)
        
        return summary
    
    def _generate_headline(self, timeline_data: List[Dict], title: str) -> str:
        """Generate compelling headline from investigation data."""
        # Find the most significant event or pattern
        key_entities = list(set(event.get('entity') for event in timeline_data if event.get('entity')))
        key_events = [event.get('event', '') for event in timeline_data]
        
        # Simple headline generation logic
        if key_entities:
            primary_entity = key_entities[0]
            if any('investigation' in event.lower() for event in key_events):
                return f"{primary_entity} Under Investigation: {title}"
            elif any('announcement' in event.lower() for event in key_events):
                return f"{primary_entity} Announces Major Changes in {title}"
            else:
                return f"New Details Emerge in {title} Investigation"
        
        return f"Investigation Reveals Timeline of {title}"
    
    def _generate_subhead(self, summary: InvestigationSummary) -> str:
        """Generate subheadline from summary."""
        if summary.key_findings:
            return summary.key_findings[0]  # Use first key finding as subhead
        return "Timeline analysis reveals new insights into ongoing investigation"
    
    def _generate_lead_paragraph(self, summary: InvestigationSummary) -> str:
        """Generate compelling lead paragraph."""
        # Extract first sentence of executive summary as lead
        sentences = summary.executive_summary.split('. ')
        if sentences:
            lead = sentences[0] + '.'
            if len(sentences) > 1:
                lead += ' ' + sentences[1] + '.'
            return lead
        return summary.executive_summary[:200] + '...'
    
    def _generate_context_paragraph(self, timeline_data: List[Dict]) -> str:
        """Generate context paragraph explaining the investigation background."""
        time_span = self._calculate_time_span(timeline_data)
        entity_count = len(set(event.get('entity') for event in timeline_data if event.get('entity')))
        
        return f"This investigation spans {time_span} and involves {entity_count} key entities. " \
               f"Analysis of {len(timeline_data)} events reveals patterns of activity that " \
               f"provide new insights into the timeline of events."
    
    def _generate_article_lead(self, summary: InvestigationSummary, style: str) -> str:
        """Generate article lead based on style."""
        if style == 'news':
            return self._generate_news_lead(summary)
        elif style == 'feature':
            return self._generate_feature_lead(summary)
        elif style == 'investigative':
            return self._generate_investigative_lead(summary)
        else:
            return self._generate_news_lead(summary)
    
    def _generate_news_lead(self, summary: InvestigationSummary) -> str:
        """Generate news-style lead paragraph."""
        return f"{summary.executive_summary.split('.')[0]}. " \
               f"The investigation reveals {len(summary.key_findings)} key findings " \
               f"that shed new light on the events surrounding {summary.title}."
    
    def _generate_feature_lead(self, summary: InvestigationSummary) -> str:
        """Generate feature-style lead paragraph."""
        return f"The timeline of events in the {summary.title} investigation tells " \
               f"a complex story of {', '.join(summary.key_findings[:2])}. " \
               f"Through careful analysis of documentation and records, a clearer " \
               f"picture emerges of what really happened."
    
    def _generate_investigative_lead(self, summary: InvestigationSummary) -> str:
        """Generate investigative-style lead paragraph."""
        return f"An investigation by this newsroom has uncovered new details about " \
               f"{summary.title}. {summary.executive_summary.split('.')[0]}. " \
               f"The findings, based on analysis of internal documents and records, " \
               f"reveal {summary.key_findings[0].lower() if summary.key_findings else 'significant new information'}."
    
    def _generate_article_body(self, timeline_data: List[Dict], 
                             summary: InvestigationSummary, style: str) -> str:
        """Generate article body content."""
        paragraphs = []
        
        # Key findings section
        if summary.key_findings:
            paragraphs.append("Key findings from the investigation include:")
            for finding in summary.key_findings[:5]:  # Top 5 findings
                paragraphs.append(f"• {finding}")
        
        # Timeline highlights
        if summary.timeline_highlights:
            paragraphs.append("\nTimeline of Events:")
            for event in summary.timeline_highlights[:3]:  # Top 3 events
                date = event.get('date', 'Date unknown')
                event_text = event.get('event', 'Event details unavailable')
                entity = event.get('entity', '')
                paragraphs.append(f"{date}: {event_text}" + (f" ({entity})" if entity else ""))
        
        # Entity relationships
        if summary.entity_relationships:
            paragraphs.append("\nKey Relationships:")
            for relationship in summary.entity_relationships[:3]:
                entities = relationship.get('entities', [])
                count = relationship.get('interaction_count', 0)
                if len(entities) == 2:
                    paragraphs.append(f"{entities[0]} and {entities[1]} appear together in {count} events.")
        
        return '\n\n'.join(paragraphs)
    
    def _generate_conclusion(self, summary: InvestigationSummary) -> str:
        """Generate article conclusion."""
        return f"The investigation continues to develop, with a confidence score of " \
               f"{summary.confidence_score:.2f} based on the available evidence. " \
               f"Further reporting may reveal additional details about {summary.title}."
    
    def _extract_key_figures(self, timeline_data: List[Dict]) -> List[Dict[str, Any]]:
        """Extract key figures mentioned in the timeline."""
        figures = {}
        for event in timeline_data:
            entity = event.get('entity')
            if entity and entity not in figures:
                figures[entity] = {
                    'name': entity,
                    'first_mention': event.get('date'),
                    'events': [],
                    'roles': set()
                }
            if entity:
                figures[entity]['events'].append(event)
                # Simple role extraction (could be enhanced)
                event_text = event.get('event', '').lower()
                if 'ceo' in event_text:
                    figures[entity]['roles'].add('CEO')
                elif 'president' in event_text:
                    figures[entity]['roles'].add('President')
                elif 'director' in event_text:
                    figures[entity]['roles'].add('Director')
        
        # Convert to list and sort by relevance
        figure_list = []
        for figure_data in figures.values():
            figure_data['roles'] = list(figure_data['roles'])
            figure_data['event_count'] = len(figure_data['events'])
            figure_list.append(figure_data)
        
        return sorted(figure_list, key=lambda x: x['event_count'], reverse=True)[:5]
    
    def _extract_key_locations(self, timeline_data: List[Dict]) -> List[str]:
        """Extract key locations from timeline."""
        locations = {}
        for event in timeline_data:
            location = event.get('location')
            if location:
                locations[location] = locations.get(location, 0) + 1
        
        return [loc for loc, count in sorted(locations.items(), key=lambda x: x[1], reverse=True)[:3]]
    
    def _assess_source_quality(self, timeline_data: List[Dict]) -> Dict[str, Any]:
        """Assess quality of source data."""
        total_events = len(timeline_data)
        complete_events = sum(1 for event in timeline_data 
                            if all(event.get(field) for field in ['date', 'event', 'entity', 'location']))
        
        return {
            'completeness_score': complete_events / total_events if total_events > 0 else 0,
            'total_events': total_events,
            'complete_events': complete_events,
            'data_quality': 'high' if complete_events / total_events > 0.8 else 
                           'medium' if complete_events / total_events > 0.5 else 'low'
        }
    
    def _suggest_story_angles(self, timeline_data: List[Dict]) -> List[str]:
        """Suggest potential story angles."""
        angles = []
        
        # Entity-focused angles
        entities = list(set(event.get('entity') for event in timeline_data if event.get('entity')))
        if entities:
            angles.append(f"Profile of {entities[0]}'s role in events")
            if len(entities) > 1:
                angles.append(f"Relationship between {entities[0]} and {entities[1]}")
        
        # Timeline-focused angles
        dates = [event.get('date') for event in timeline_data if event.get('date')]
        if dates:
            time_span = self._calculate_time_span(timeline_data)
            angles.append(f"How events unfolded over {time_span}")
        
        # Location-focused angles
        locations = self._extract_key_locations(timeline_data)
        if locations:
            angles.append(f"Why {locations[0]} was central to events")
        
        return angles[:5]
    
    def _identify_verification_needs(self, timeline_data: List[Dict]) -> List[str]:
        """Identify elements that need verification."""
        needs_verification = []
        
        # Events without complete information
        incomplete_events = [event for event in timeline_data 
                           if not all(event.get(field) for field in ['date', 'event', 'entity', 'location'])]
        
        if incomplete_events:
            needs_verification.append(f"{len(incomplete_events)} events need additional detail")
        
        # Unique claims that should be verified
        unique_events = set(event.get('event') for event in timeline_data if event.get('event'))
        if unique_events:
            needs_verification.append("All event descriptions should be source-verified")
        
        return needs_verification
    
    def _generate_follow_up_leads(self, timeline_data: List[Dict]) -> List[str]:
        """Generate follow-up investigation leads."""
        leads = []
        
        # Entities that appear frequently
        entities = {}
        for event in timeline_data:
            entity = event.get('entity')
            if entity:
                entities[entity] = entities.get(entity, 0) + 1
        
        top_entities = sorted(entities.items(), key=lambda x: x[1], reverse=True)[:3]
        for entity, count in top_entities:
            leads.append(f"Interview {entity} (mentioned {count} times)")
        
        # Gaps in timeline
        dates = sorted([event.get('date') for event in timeline_data if event.get('date')])
        if len(dates) > 1:
            leads.append(f"Investigate gap between {dates[0]} and {dates[-1]}")
        
        return leads[:5]
    
    def _calculate_time_span(self, timeline_data: List[Dict]) -> str:
        """Calculate human-readable time span."""
        dates = [event.get('date') for event in timeline_data if event.get('date')]
        if not dates:
            return "unknown time period"
        
        start_date = min(dates)
        end_date = max(dates)
        
        if start_date == end_date:
            return f"events on {start_date}"
        else:
            return f"{start_date} to {end_date}"
    
    def _generate_immediate_actions(self, timeline_data: List[Dict]) -> List[str]:
        """Generate immediate action items."""
        return [
            "Verify all entity names and roles",
            "Confirm timeline accuracy with primary sources",
            "Cross-reference events with public records",
            "Identify additional sources for corroboration"
        ]
    
    def _calculate_completeness(self, timeline_data: List[Dict]) -> float:
        """Calculate data completeness score."""
        if not timeline_data:
            return 0.0
        
        total_fields = len(timeline_data) * 4  # date, event, entity, location
        filled_fields = sum(1 for event in timeline_data 
                          for field in ['date', 'event', 'entity', 'location'] 
                          if event.get(field))
        
        return filled_fields / total_fields
    
    def _assess_verification_status(self, timeline_data: List[Dict]) -> str:
        """Assess overall verification status."""
        completeness = self._calculate_completeness(timeline_data)
        
        if completeness > 0.9:
            return "high_verification"
        elif completeness > 0.7:
            return "medium_verification"
        else:
            return "low_verification"
    
    def _assess_editorial_readiness(self, timeline_data: List[Dict]) -> str:
        """Assess readiness for editorial review."""
        quality = self._assess_source_quality(timeline_data)
        
        if quality['data_quality'] == 'high' and len(timeline_data) > 5:
            return "ready_for_review"
        elif quality['data_quality'] == 'medium':
            return "needs_additional_work"
        else:
            return "requires_more_investigation"
    
    def _suggest_publication_timeline(self, timeline_data: List[Dict]) -> Dict[str, str]:
        """Suggest publication timeline based on data quality."""
        readiness = self._assess_editorial_readiness(timeline_data)
        
        timelines = {
            "ready_for_review": {
                "editorial_review": "1-2 days",
                "fact_checking": "2-3 days", 
                "publication": "1 week"
            },
            "needs_additional_work": {
                "additional_reporting": "1 week",
                "editorial_review": "2-3 days",
                "publication": "2 weeks"
            },
            "requires_more_investigation": {
                "additional_investigation": "2-3 weeks",
                "editorial_review": "3-5 days",
                "publication": "1 month"
            }
        }
        
        return timelines.get(readiness, timelines["needs_additional_work"])
    
    def _assess_business_impact(self, timeline_data: List[Dict]) -> Dict[str, Any]:
        """Assess business impact for executive summary."""
        # Placeholder implementation
        return {
            "impact_level": "medium",
            "affected_areas": ["reputation", "operations"],
            "financial_implications": "under_assessment"
        }
    
    def _assess_risks(self, timeline_data: List[Dict]) -> List[str]:
        """Assess risks for executive summary."""
        return [
            "Reputational risk if story develops further",
            "Regulatory scrutiny potential",
            "Media attention escalation"
        ]
    
    def _generate_executive_actions(self, timeline_data: List[Dict]) -> List[str]:
        """Generate recommended actions for executives."""
        return [
            "Monitor media coverage and public sentiment",
            "Prepare stakeholder communications",
            "Review internal processes and controls",
            "Consider legal consultation"
        ]
    
    # Additional helper methods for complete package generation
    
    def _generate_detailed_timeline(self, timeline_data: List[Dict]) -> List[Dict]:
        """Generate detailed timeline for package."""
        return sorted(timeline_data, key=lambda x: x.get('date', ''))
    
    def _generate_entity_profiles(self, timeline_data: List[Dict]) -> Dict[str, Dict]:
        """Generate entity profiles for package."""
        profiles = {}
        for event in timeline_data:
            entity = event.get('entity')
            if entity and entity not in profiles:
                profiles[entity] = {
                    'name': entity,
                    'first_appearance': event.get('date'),
                    'total_mentions': 0,
                    'key_events': [],
                    'associated_locations': set(),
                    'timeline_role': 'participant'
                }
            
            if entity:
                profiles[entity]['total_mentions'] += 1
                profiles[entity]['key_events'].append(event)
                if event.get('location'):
                    profiles[entity]['associated_locations'].add(event.get('location'))
        
        # Convert sets to lists for JSON serialization
        for profile in profiles.values():
            profile['associated_locations'] = list(profile['associated_locations'])
        
        return profiles
    
    def _generate_infographic_data(self, timeline_data: List[Dict]) -> Dict[str, Any]:
        """Generate data suitable for infographic creation."""
        return {
            'timeline_points': [
                {
                    'date': event.get('date'),
                    'title': event.get('event', '')[:50] + '...',
                    'entity': event.get('entity'),
                    'importance': 'high' if event.get('entity') else 'medium'
                }
                for event in sorted(timeline_data, key=lambda x: x.get('date', ''))[:10]
            ],
            'entity_network': self._generate_network_data(timeline_data),
            'location_map': self._generate_map_data(timeline_data),
            'statistics': {
                'total_events': len(timeline_data),
                'time_span': self._calculate_time_span(timeline_data),
                'key_players': len(set(event.get('entity') for event in timeline_data if event.get('entity'))),
                'locations': len(set(event.get('location') for event in timeline_data if event.get('location')))
            }
        }
    
    def _generate_network_data(self, timeline_data: List[Dict]) -> List[Dict]:
        """Generate network data for visualization."""
        # Simple network based on co-occurrence
        entities = list(set(event.get('entity') for event in timeline_data if event.get('entity')))
        connections = []
        
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                # Check if entities appear in same date events
                shared_events = sum(1 for event in timeline_data
                                  if event.get('entity') in [entity1, entity2])
                if shared_events > 1:
                    connections.append({
                        'source': entity1,
                        'target': entity2,
                        'strength': shared_events
                    })
        
        return connections
    
    def _generate_map_data(self, timeline_data: List[Dict]) -> List[Dict]:
        """Generate map data for location visualization."""
        locations = {}
        for event in timeline_data:
            location = event.get('location')
            if location:
                if location not in locations:
                    locations[location] = {
                        'name': location,
                        'events': [],
                        'event_count': 0
                    }
                locations[location]['events'].append(event)
                locations[location]['event_count'] += 1
        
        return list(locations.values())
    
    def _identify_fact_check_items(self, timeline_data: List[Dict]) -> List[str]:
        """Identify items requiring fact-checking."""
        items = []
        for event in timeline_data:
            if event.get('event'):
                items.append(f"Verify: {event['event'][:100]}...")
        return items[:5]  # Top 5 items
    
    def _identify_legal_considerations(self, timeline_data: List[Dict]) -> List[str]:
        """Identify potential legal considerations."""
        considerations = []
        
        # Check for sensitive terms that might require legal review
        sensitive_terms = ['lawsuit', 'fraud', 'criminal', 'illegal', 'violation']
        for event in timeline_data:
            event_text = event.get('event', '').lower()
            for term in sensitive_terms:
                if term in event_text:
                    considerations.append(f"Legal review needed for allegations involving '{term}'")
                    break
        
        if not considerations:
            considerations.append("Standard legal review recommended")
        
        return list(set(considerations))  # Remove duplicates
    
    def _identify_sources_to_verify(self, timeline_data: List[Dict]) -> List[str]:
        """Identify sources that need verification."""
        sources = []
        entities = list(set(event.get('entity') for event in timeline_data if event.get('entity')))
        
        for entity in entities[:5]:  # Top 5 entities
            sources.append(f"Verify statements and actions attributed to {entity}")
        
        return sources
    
    def _suggest_additional_reporting(self, timeline_data: List[Dict]) -> List[str]:
        """Suggest additional reporting opportunities."""
        suggestions = []
        
        # Look for gaps in timeline
        dates = sorted([event.get('date') for event in timeline_data if event.get('date')])
        if len(dates) > 1:
            suggestions.append(f"Investigate gap in timeline between {dates[0]} and {dates[-1]}")
        
        # Entities that could provide more information
        entities = list(set(event.get('entity') for event in timeline_data if event.get('entity')))
        for entity in entities[:3]:
            suggestions.append(f"Follow up interview with {entity}")
        
        # Locations for additional investigation
        locations = list(set(event.get('location') for event in timeline_data if event.get('location')))
        if locations:
            suggestions.append(f"On-site investigation at {locations[0]}")
        
        return suggestions[:5]  # Limit to 5 suggestions