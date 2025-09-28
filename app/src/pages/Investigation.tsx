import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { DocumentUpload } from "@/components/DocumentUpload";
import { Timeline } from "@/components/Timeline";
import { FilterPanel } from "@/components/FilterPanel";
import { TimelineFilter } from "@/types/investigation";
import { CatDto } from "@/client/types.gen";
import { Button } from "@/components/ui/button";
import { FileText, Clock, Users, Filter, FilterIcon } from "lucide-react";
import {
  getUserByUserIdCatByCatId,
  postUserByUserIdCatByCatIdDocument,
} from "@/client";
import { DEFAULT_USER_ID } from "@/App";
import { useCedarState, useRegisterState, useSubscribeStateToAgentContext } from "cedar-os";

const Investigation = () => {
  const INIITIAL_FILTER: TimelineFilter = {
    entities: [],
    dateRange: { start: null, end: null },
  };
  const { id } = useParams<{ id: string }>();
  // const [cat, setCat] = useState<CatDto | undefined>(undefined);
  const [cat, setCat] = useCedarState<CatDto | undefined>({
    key: "cat",
    initialValue: undefined,
    description: "the current investigation cat or timeline being viewed",
  });
  const [showUpload, setShowUpload] = useState(false);
  const [filter, setFilter] = useCedarState<TimelineFilter>({
    key: "filter",
    initialValue: INIITIAL_FILTER,
    description:
      "filter by entitiies, categories, priority, and date range (with start and end dates) for the investigation timeline",
    stateSetters: {
      clearFilter: {
        name: "clearFilter",
        description: "clear all filters",
        execute: (currentFilter, setCurrentFilter, args: {}) => {
          setCurrentFilter(INIITIAL_FILTER);
        },
      },
      addEntityToFilter: {
        name: "addEntityToFilter",
        description: "add an entity to the filter",
        execute: (
          currentFilter,
          setCurrentFilter,
          args: { entity: string }
        ) => {
          const { entity } = args;
          if (
            !currentFilter.entities
              .map((e) => e.toLowerCase())
              .includes(entity.toLowerCase())
          ) {
            setCurrentFilter({
              ...currentFilter,
              entities: [...currentFilter.entities, entity],
            });
          }
        },
      },
      removeEntityToFilter: {
        name: "removeEntityToFilter",
        description: "remove an entity from the filter",
        execute: (
          currentFilter,
          setCurrentFilter,
          args: { entity: string }
        ) => {
          const { entity } = args;
          if (
            currentFilter.entities
              .map((e) => e.toLowerCase())
              .includes(entity.toLowerCase())
          ) {
            setCurrentFilter({
              ...currentFilter,
              entities: currentFilter.entities.filter(
                (e) => e.toLowerCase() !== entity.toLowerCase()
              ),
            });
          }
        },
      },
      setStartDate: {
        name: "setStartDate",
        description: "set the start date for the date range filter",
        execute: (
          currentFilter,
          setCurrentFilter,
          args: { startDate: Date | null }
        ) => {
          const { startDate } = args;
          setCurrentFilter({
            ...currentFilter,
            dateRange: { ...currentFilter.dateRange, start: startDate },
          });
        },
      },
      setEndDate: {
        name: "setEndDate",
        description: "set the end date for the date range filter",
        execute: (
          currentFilter,
          setCurrentFilter,
          args: { endDate: Date | null }
        ) => {
          const { endDate } = args;
          setCurrentFilter({
            ...currentFilter,
            dateRange: { ...currentFilter.dateRange, end: endDate },
          });
        },
      },
    },
  });

  useSubscribeStateToAgentContext('filter', 
    (filter) => ({
      filter: filter
    }),
    {
      icon: <FilterIcon />,
      color: '#10B981',
      labelField: 'entities',
      showInChat: true,
      collapse: {
        threshold: 0,
        label: `Filter: ${filter.entities.length} entities`,
      }
    }
  );

  useSubscribeStateToAgentContext('cat', 
    (cat) => ({
      cat: cat
    }),
    {
      icon: <Clock />,
      color: '#3B82F6',
      labelField: 'events',
      showInChat: true,
      collapse: {
        threshold: 0,
        label: `${cat?.title || 'Investigation'}`,
      }
    }
  );  

  useEffect(() => {
    const fetchData = async () => {
      console.log("Fetching investigation data for id:", id);
      const response = await getUserByUserIdCatByCatId({
        path: { userId: DEFAULT_USER_ID, catId: id },
      });
      if (response && response.data) {
        setCat(response.data);
      }
      console.log(response);
    };
    fetchData();
  }, [id]);

  const handleFilesChanged = async (files: File[]) => {
    await Promise.all(
      files.map((file) =>
        postUserByUserIdCatByCatIdDocument({
          body: { file },
          path: { userId: DEFAULT_USER_ID, catId: id },
        })
      )
    );

    setShowUpload(false);
  };

  const filteredEventsCount = cat?.events.filter((event) => {
    // Apply the same filtering logic as in Timeline component
    if (filter.entities.length > 0) {
      const hasFilteredEntity = event.entities.some((entity) =>
        filter.entities
          .map((e) => e.toLowerCase())
          .includes(entity.name.toLowerCase())
      );
      if (!hasFilteredEntity) return false;
    }

    // if (filter.categories.length > 0 && !filter.categories.includes(event.category)) {
    //   return false;
    // }

    // if (filter.priority.length > 0 && !filter.priority.includes(event.priority)) {
    //   return false;
    // }

    if (
      filter.dateRange.start &&
      new Date(event.date) < filter.dateRange.start
    ) {
      return false;
    }
    if (filter.dateRange.end && new Date(event.date) > filter.dateRange.end) {
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
                {cat?.title}
              </h1>
              <p className="text-muted-foreground mt-1">{cat?.description}</p>
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
            <DocumentUpload onFilesChanged={handleFilesChanged} />
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
                    <div className="text-2xl font-bold">
                      {filteredEventsCount}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {filteredEventsCount === cat?.events.length
                        ? "Events"
                        : `of ${cat?.events.length} Events`}
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-card border border-border rounded-lg p-4 shadow-card">
                <div className="flex items-center space-x-3">
                  <Users className="h-8 w-8 text-accent" />
                  <div>
                    {cat?.events.flatMap((event) => event.entities).length}
                    <div className="text-sm text-muted-foreground">
                      Entities
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Filter Panel */}
            <FilterPanel
              filter={filter}
              entities={
                cat?.events
                  .flatMap((event) => event.entities)
                  .map((entity) => entity.name) || []
              }
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
                  {filteredEventsCount} of {cat?.events.length} events shown
                </div>
              </div>
              <p className="text-muted-foreground mt-1">
                Chronological sequence of events extracted from documents
              </p>
            </div>

            <Timeline
              events={cat?.events || []}
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
