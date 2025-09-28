import { useState } from 'react';
import { DocumentUpload } from '@/components/DocumentUpload';
import { Timeline } from '@/components/Timeline';
import { FilterPanel } from '@/components/FilterPanel';
import { mockInvestigation } from '@/data/mockData';
import { TimelineFilter } from '@/types/investigation';
import { Button } from '@/components/ui/button';
import { FileText, Clock, Users, Filter } from 'lucide-react';

const Investigation = () => {
  const [investigation] = useState(mockInvestigation);
  const [showUpload, setShowUpload] = useState(false);
  const [filter, setFilter] = useState<TimelineFilter>({
    entities: [],
    categories: [],
    priority: [],
    dateRange: { start: null, end: null }
  });

  const handleFileProcessed = (fileId: string) => {
    // In a real app, this would trigger re-fetching of events
    console.log('File processed:', fileId);
  };

  const filteredEventsCount = investigation.events.filter(event => {
    // Apply the same filtering logic as in Timeline component
    if (filter.entities.length > 0) {
      const hasFilteredEntity = event.entities.some(entity => 
        filter.entities.includes(entity.id)
      );
      if (!hasFilteredEntity) return false;
    }

    if (filter.categories.length > 0 && !filter.categories.includes(event.category)) {
      return false;
    }

    if (filter.priority.length > 0 && !filter.priority.includes(event.priority)) {
      return false;
    }

    if (filter.dateRange.start && event.date < filter.dateRange.start) {
      return false;
    }
    if (filter.dateRange.end && event.date > filter.dateRange.end) {
      return false;
    }

    return true;
  }).length;

  return (
    <div className="min-h-screen bg-gradient-timeline">
      {/* Header */}
      <div className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-foreground">
                {investigation.title}
              </h1>
              <p className="text-muted-foreground mt-1">
                {investigation.description}
              </p>
            </div>
            <Button
              onClick={() => setShowUpload(!showUpload)}
              className="bg-primary transition-transform"
            >
              <FileText className="h-4 w-4 mr-2" />
              Add Documents
            </Button>
          </div>
        </div>
      </div>

      {/* Upload Section */}
      {showUpload && (
        <div className="border-b border-border bg-card/30 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto px-6 py-6">
            <DocumentUpload onFileProcessed={handleFileProcessed} />
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-2 lg:grid-cols-1 gap-4">
              <div className="bg-gradient-card border border-border rounded-lg p-4 shadow-card">
                <div className="flex items-center space-x-3">
                  <Clock className="h-8 w-8 text-primary" />
                  <div>
                    <div className="text-2xl font-bold">{filteredEventsCount}</div>
                    <div className="text-sm text-muted-foreground">
                      {filteredEventsCount === investigation.events.length ? 'Events' : `of ${investigation.events.length} Events`}
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-card border border-border rounded-lg p-4 shadow-card">
                <div className="flex items-center space-x-3">
                  <Users className="h-8 w-8 text-accent" />
                  <div>
                    <div className="text-2xl font-bold">{investigation.entities.length}</div>
                    <div className="text-sm text-muted-foreground">Entities</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Filter Panel */}
            <FilterPanel
              filter={filter}
              entities={investigation.entities}
              onFilterChange={setFilter}
            />
          </div>

          {/* Timeline */}
          <div className="lg:col-span-3">
            <div className="mb-6">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold flex items-center">
                  <Clock className="h-5 w-5 mr-2 text-primary" />
                  Investigation Timeline
                </h2>
                <div className="flex items-center text-sm text-muted-foreground">
                  <Filter className="h-4 w-4 mr-1" />
                  {filteredEventsCount} of {investigation.events.length} events shown
                </div>
              </div>
              <p className="text-muted-foreground mt-1">
                Chronological sequence of events extracted from documents
              </p>
            </div>

            <Timeline
              events={investigation.events}
              filter={filter}
              onFilterChange={setFilter}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Investigation;