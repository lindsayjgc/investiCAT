export interface Entity {
  id: string;
  name: string;
  type: 'person' | 'organization' | 'location' | 'object' | 'concept';
  description?: string;
  color: string;
}

export interface Event {
  id: string;
  title: string;
  description: string;
  date: Date;
  location?: string;
  entities: Entity[];
  category: 'communication' | 'meeting' | 'transaction' | 'document' | 'action';
  priority: 'low' | 'medium' | 'high' | 'critical';
  dependencies: string[]; // IDs of related events
  sourceDocument?: string;
  confidence: number; // 0-1 scale
}

export interface Investigation {
  id: string;
  title: string;
  description: string;
  createdAt: Date;
  updatedAt: Date;
  events: Event[];
  entities: Entity[];
  documents: Document[];
}

export interface Document {
  id: string;
  name: string;
  type: string;
  size: number;
  uploadedAt: Date;
  processed: boolean;
  extractedEvents: string[]; // Event IDs
}

export interface TimelineFilter {
  entities: string[];
  dateRange: {
    start: Date | null;
    end: Date | null;
  };
}