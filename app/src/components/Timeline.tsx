import { useState } from 'react';
import { format } from 'date-fns';
import { MapPin, Users, Calendar, AlertTriangle, ChevronDown, ChevronUp, Link } from 'lucide-react';
import { Event, TimelineFilter } from '@/types/investigation';
import { EventDetail } from './EventDetail';
import { Button } from '@/components/ui/button';
import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { EventDto } from '@/client';

interface TimelineProps {
  events: EventDto[];
  filter: TimelineFilter;
  onFilterChange: (filter: TimelineFilter) => void;
}

export const Timeline = ({ events, filter }: TimelineProps) => {
  const [selectedEvent, setSelectedEvent] = useState<EventDto | null>(null);
  const [expandedEvents, setExpandedEvents] = useState<Set<string>>(new Set());

  const getEventColor = (category: Event['category']) => {
    const colors = {
      communication: 'event-primary',
      meeting: 'event-secondary',
      transaction: 'event-warning',
      document: 'muted',
      action: 'event-danger'
    };
    return colors[category];
  };

  const getPriorityIcon = (priority: Event['priority']) => {
    if (priority === 'critical' || priority === 'high') {
      return <AlertTriangle className="h-4 w-4 text-event-danger" />;
    }
    return null;
  };

  const filteredEvents = events
    .filter(event => {
      // Filter by entities
      if (filter.entities.length > 0) {
        const hasFilteredEntity = event.entities.some(entity => 
          filter.entities.includes(entity.id)
        );
        if (!hasFilteredEntity) return false;
      }

      // // Filter by categories
      // if (filter.categories.length > 0 && !filter.categories.includes(event.category)) {
      //   return false;
      // }

      // // Filter by priority
      // if (filter.priority.length > 0 && !filter.priority.includes(event.priority)) {
      //   return false;
      // }

      // Filter by date range
      if (filter.dateRange.start && new Date(event.date) < filter.dateRange.start) {
        return false;
      }
      if (filter.dateRange.end && new Date(event.date) > filter.dateRange.end) {
        return false;
      }

      return true;
    })
    .sort((a, b) => (new Date(a.date)).getTime() - (new Date(b.date)).getTime());

  const getRelatedEvents = (eventId: string) => {
    return []
  };

  const toggleEventExpansion = (eventId: string) => {
    const newExpanded = new Set(expandedEvents);
    if (newExpanded.has(eventId)) {
      newExpanded.delete(eventId);
    } else {
      newExpanded.add(eventId);
    }
    setExpandedEvents(newExpanded);
  };

  return (
    <div className="relative">
      <ScrollArea className="w-full">
        <div className="relative pb-8">
          {/* Horizontal Timeline Line */}
          <div className="absolute top-16 left-0 right-0 h-0.5 bg-timeline-line" />
          
          {/* Timeline Container */}
          <div className="flex gap-8 px-4 py-4 min-w-max">
            {filteredEvents.map((event, index) => {
              const relatedEvents = getRelatedEvents(event.id);
              const hasRelationships = relatedEvents.length > 0;
              const isExpanded = expandedEvents.has(event.id);
              
              return (
                <div
                  key={event.id}
                  className="relative flex flex-col items-center animate-fade-in"
                  style={{ 
                    animationDelay: `${index * 0.1}s`,
                    minWidth: '400px'
                  }}
                >
                  {/* Event Label (above timeline) */}
                  <div className="mb-4 text-center max-w-sm">
                    <div className="text-xs text-muted-foreground mb-1">
                      {format(event.date, 'MMM dd')}
                    </div>
                    <div className="text-sm font-medium text-foreground truncate">
                      {event.title}
                    </div>
                  </div>
                  
                  {/* Timeline Dot */}
                  <div 
                    className={`relative z-10 w-6 h-6 rounded-sm border-4 border-gray cursor-pointer transition-all duration-300 hover:scale-110 
                      'bg-primary shadow-glow' 
                    }`}
                    onClick={() => toggleEventExpansion(event.id)}
                  >
                    {/* {getPriorityIcon(event.priority) && (
                      <div className="absolute -bottom-2 -right-2 w-4 h-4 p-0.5 bg-gray-100 rounded-full">
                        <AlertTriangle className="h-3 w-3 text-event-danger" />
                      </div>
                    )} */}
                    {hasRelationships && (
                      <div className="absolute -top-2 -right-2 w-4 h-4 p-0.5 bg-gray-300 rounded-full">
                        <Link className="relative h-3 w-3" />
                      </div>
                    )}
                  </div>

                  {/* Expandable Event Card (below timeline) */}
                    <Collapsible open={isExpanded} onOpenChange={() => toggleEventExpansion(event.id)}>
                    <div className="flex justify-center mt-4">
                      <CollapsibleTrigger asChild>
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        className="text-xs text-muted-foreground hover:dark-gray"
                      >
                        {isExpanded ? (
                        <>Less <ChevronUp className="h-3 w-3 ml-1" /></>
                        ) : (
                        <>More <ChevronDown className="h-3 w-3 ml-1" /></>
                        )}
                      </Button>
                      </CollapsibleTrigger>
                    </div>
                    
                    <CollapsibleContent className="mt-4">
                      <div className="bg-gradient-card border border-border rounded-lg p-4 shadow-card max-w-sm">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1">
                            <h3 className="text-sm font-semibold mb-1">{event.title}</h3>
                            <p className="text-xs text-muted-foreground line-clamp-3">
                              {event.summary}
                            </p>
                          </div>
                          {/* <div className={`px-2 py-1 rounded-full text-xs font-medium bg-event-${getEventColor(event.category).replace('event-', '')}/20 text-event-${getEventColor(event.category).replace('event-', '')} border border-event-${getEventColor(event.category).replace('event-', '')}/30`}>
                            {event.category}
                          </div> */}
                        </div>

                        <div className="space-y-2 text-xs">
                          <div className="flex items-center text-muted-foreground">
                            <Calendar className="h-3 w-3 mr-2" />
                            {format(event.date, 'MMM dd, yyyy HH:mm')}
                          </div>
                          
                          {event.location && (
                            <div className="flex items-center text-muted-foreground">
                              <MapPin className="h-3 w-3 mr-2" />
                              {event.location.address}
                            </div>
                          )}
                          
                          <div className="flex items-center text-muted-foreground">
                            <Users className="h-3 w-3 mr-2" />
                            {event.entities.length} entities
                          </div>
                        </div>

                        {event.entities.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-3">
                            {event.entities.slice(0, 3).map(entity => (
                              <div
                                key={entity.id}
                                className="px-2 py-1 rounded text-xs border bg-green-700"
                              >
                                {entity.name}
                              </div>
                            ))}
                            {event.entities.length > 3 && (
                              <div className="px-2 py-1 bg-muted text-muted-foreground rounded text-xs">
                                +{event.entities.length - 3} more
                              </div>
                            )}
                          </div>
                        )}

                        <div className="flex justify-between items-center mt-3 pt-3 border-t border-border">
                          {/* <div className="text-xs text-muted-foreground">
                            Confidence: {Math.round(event.confidence * 100)}%
                          </div> */}
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            className="text-xs text-primary hover:text-primary-foreground hover:bg-primary"
                            onClick={() => setSelectedEvent(event)}
                          >
                            Details
                          </Button>
                        </div>
                      </div>
                    </CollapsibleContent>
                  </Collapsible>
                </div>
              );
            })}
          </div>
        </div>
        <ScrollBar orientation="horizontal" />
      </ScrollArea>

      {selectedEvent && (
        <EventDetail
          event={selectedEvent}
          relatedEvents={getRelatedEvents(selectedEvent.id)}
          onClose={() => setSelectedEvent(null)}
        />
      )}
    </div>
  );
};