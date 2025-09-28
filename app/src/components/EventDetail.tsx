import { format } from 'date-fns';
import { X, MapPin, Users, Calendar, FileText, Network } from 'lucide-react';
import { Event } from '@/types/investigation';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface EventDetailProps {
  event: Event;
  relatedEvents: Event[];
  onClose: () => void;
}

export const EventDetail = ({ event, relatedEvents, onClose }: EventDetailProps) => {
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

  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-card border border-border rounded-lg shadow-glow max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-start justify-between p-6 border-b border-border">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-2">
              <h2 className="text-xl font-semibold">{event.title}</h2>
              <Badge 
                variant="outline" 
                className={`bg-${getEventColor(event.category)}/20 text-${getEventColor(event.category)} border-${getEventColor(event.category)}/30`}
              >
                {event.category}
              </Badge>
              <Badge variant="outline" className={`
                ${event.priority === 'critical' ? 'bg-event-danger/20 text-event-danger border-event-danger/30' : ''}
                ${event.priority === 'high' ? 'bg-event-warning/20 text-event-warning border-event-warning/30' : ''}
                ${event.priority === 'medium' ? 'bg-event-secondary/20 text-event-secondary border-event-secondary/30' : ''}
                ${event.priority === 'low' ? 'bg-muted/20 text-muted-foreground border-muted/30' : ''}
              `}>
                {event.priority} priority
              </Badge>
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Description */}
          <div>
            <h3 className="text-sm font-medium text-muted-foreground mb-2">Description</h3>
            <p className="text-sm leading-relaxed">{event.description}</p>
          </div>

          {/* Event Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-3">
              <div className="flex items-center text-sm">
                <Calendar className="h-4 w-4 mr-3 text-muted-foreground" />
                <span className="text-muted-foreground mr-2">Date:</span>
                <span>{format(event.date, 'MMMM dd, yyyy HH:mm')}</span>
              </div>
              
              {event.location && (
                <div className="flex items-center text-sm">
                  <MapPin className="h-4 w-4 mr-3 text-muted-foreground" />
                  <span className="text-muted-foreground mr-2">Location:</span>
                  <span>{event.location}</span>
                </div>
              )}

              {event.sourceDocument && (
                <div className="flex items-center text-sm">
                  <FileText className="h-4 w-4 mr-3 text-muted-foreground" />
                  <span className="text-muted-foreground mr-2">Source:</span>
                  <span className="text-primary cursor-pointer hover:underline">
                    {event.sourceDocument}
                  </span>
                </div>
              )}
            </div>

            <div className="space-y-3">
              <div className="flex items-center text-sm">
                <span className="text-muted-foreground mr-2">Confidence:</span>
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <div className="flex-1 bg-muted rounded-full h-2">
                      <div 
                        className="h-2 rounded-full bg-primary"
                        style={{ width: `${event.confidence * 100}%` }}
                      />
                    </div>
                    <span className="text-xs">{Math.round(event.confidence * 100)}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Entities */}
          {event.entities.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-muted-foreground mb-3 flex items-center">
                <Users className="h-4 w-4 mr-2" />
                Participating Entities ({event.entities.length})
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {event.entities.map(entity => (
                  <div
                    key={entity.id}
                    className="flex items-center space-x-3 p-3 border border-border rounded-lg bg-gradient-card"
                  >
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: entity.color }}
                    />
                    <div className="flex-1">
                      <div className="font-medium text-sm">{entity.name}</div>
                      <div className="text-xs text-muted-foreground capitalize">
                        {entity.type}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Related Events */}
          {relatedEvents.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-muted-foreground mb-3 flex items-center">
                <Network className="h-4 w-4 mr-2" />
                Related Events ({relatedEvents.length})
              </h3>
              <div className="space-y-2">
                {relatedEvents.map(relatedEvent => (
                  <div
                    key={relatedEvent.id}
                    className="flex items-center justify-between p-3 border border-relationship-highlight/30 rounded-lg bg-relationship-highlight/5"
                  >
                    <div className="flex-1">
                      <div className="font-medium text-sm">{relatedEvent.title}</div>
                      <div className="text-xs text-muted-foreground">
                        {format(relatedEvent.date, 'MMM dd, yyyy HH:mm')}
                      </div>
                    </div>
                    <Badge 
                      variant="outline" 
                      className={`bg-${getEventColor(relatedEvent.category)}/20 text-${getEventColor(relatedEvent.category)} border-${getEventColor(relatedEvent.category)}/30`}
                    >
                      {relatedEvent.category}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};