import { useState } from 'react';
import { Filter, X, Calendar, Users, Tag, AlertCircle } from 'lucide-react';
import { TimelineFilter } from '@/types/investigation';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

interface FilterPanelProps {
  filter: TimelineFilter;
  entities: string[];
  onFilterChange: (filter: TimelineFilter) => void;
  className?: string;
}

const categories = [
  { id: 'communication', label: 'Communication', color: 'event-primary' },
  { id: 'meeting', label: 'Meeting', color: 'event-secondary' },
  { id: 'transaction', label: 'Transaction', color: 'event-warning' },
  { id: 'document', label: 'Document', color: 'muted' },
  { id: 'action', label: 'Action', color: 'event-danger' }
];

const priorities = [
  { id: 'low', label: 'Low', color: 'muted' },
  { id: 'medium', label: 'Medium', color: 'event-secondary' },
  { id: 'high', label: 'High', color: 'event-warning' },
  { id: 'critical', label: 'Critical', color: 'event-danger' }
];

export const FilterPanel = ({ filter, entities, onFilterChange, className = '' }: FilterPanelProps) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const updateFilter = (updates: Partial<TimelineFilter>) => {
    onFilterChange({ ...filter, ...updates });
  };

  const clearFilters = () => {
    onFilterChange({
      entities: [],
      dateRange: { start: null, end: null }
    });
  };

  const activeFiltersCount =
    filter.entities.length +
    (filter.dateRange.start || filter.dateRange.end ? 1 : 0);

  return (
    <div className={`bg-card border border-border rounded-lg shadow-card ${className}`}>
      {/* Filter Header */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        <div className="flex items-center space-x-2">
          <Filter className="h-5 w-5 text-primary" />
          <h3 className="font-semibold">Filters</h3>
          {activeFiltersCount > 0 && (
            <div className="px-2 py-1 bg-primary/20 text-primary text-xs rounded-full">
              {activeFiltersCount}
            </div>
          )}
        </div>
        <div className="flex items-center space-x-2">
          {activeFiltersCount > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={clearFilters}
              className="text-muted-foreground hover:text-foreground"
            >
              Clear All
            </Button>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? <X className="h-4 w-4" /> : <Filter className="h-4 w-4" />}
          </Button>
        </div>
      </div>

      {/* Filter Content */}
      {isExpanded && (
        <div className="p-4 space-y-6">
          {/* Date Range */}
          <div>
            <Label className="text-sm font-medium flex items-center mb-3">
              <Calendar className="h-4 w-4 mr-2" />
              Date Range
            </Label>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <Label htmlFor="start-date" className="text-xs text-muted-foreground">
                  Start Date
                </Label>
                <Input
                  id="start-date"
                  type="date"
                  value={filter.dateRange.start?.toISOString().split('T')[0] || ''}
                  onChange={(e) => updateFilter({
                    dateRange: {
                      ...filter.dateRange,
                      start: e.target.value ? new Date(e.target.value) : null
                    }
                  })}
                />
              </div>
              <div>
                <Label htmlFor="end-date" className="text-xs text-muted-foreground">
                  End Date
                </Label>
                <Input
                  id="end-date"
                  type="date"
                  value={filter.dateRange.end?.toISOString().split('T')[0] || ''}
                  onChange={(e) => updateFilter({
                    dateRange: {
                      ...filter.dateRange,
                      end: e.target.value ? new Date(e.target.value) : null
                    }
                  })}
                />
              </div>
            </div>
          </div>

          {/* Entities */}
          {entities.length > 0 && (
            <div>
              <Label className="text-sm font-medium flex items-center mb-3">
                <Users className="h-4 w-4 mr-2" />
                Entities ({entities.length})
              </Label>
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {entities.map(entity => (
                  <div key={entity} className="flex items-center space-x-2">
                    <Checkbox
                      id={`entity-${entity}`}
                      checked={filter.entities.includes(entity)}
                      onCheckedChange={(checked) => {
                        if (checked) {
                          updateFilter({
                            entities: [...filter.entities, entity]
                          });
                        } else {
                          updateFilter({
                            entities: filter.entities.filter(e => e !== entity)
                          });
                        }
                      }}
                    />
                    <div
                      className="w-3 h-3 rounded-full bg-green-700"
                    />
                    <Label 
                      htmlFor={`entity-${entity}`}
                      className="text-sm cursor-pointer flex-1"
                    >
                      {entity}
                    </Label>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};