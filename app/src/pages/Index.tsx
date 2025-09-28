import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { FileText, Search, Clock, Users, ArrowRight, Plus, MessageSquare } from 'lucide-react';

const Index = () => {
  const [isHovered, setIsHovered] = useState(false);

  const features = [
    {
      icon: FileText,
      title: 'Document Analysis',
      description: 'Upload and process documents to extract key events and entities automatically.'
    },
    {
      icon: Clock,
      title: 'Timeline Visualization',
      description: 'View events chronologically with interactive timeline showing relationships.'
    },
    {
      icon: Search,
      title: 'Smart Filtering',
      description: 'Filter events by entities, categories, dates, and priority levels.'
    },
    {
      icon: MessageSquare,
      title: 'Chat with your Data',
      description: 'Interact with your investigation data using natural language queries.'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-timeline">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-primary opacity-10"></div>
        <div className="relative max-w-6xl mx-auto px-6 py-20">
          <div className="text-center">
            <h1 className="text-5xl font-bold mb-6 bg-gradient-primary bg-clip-text text-transparent p-2">
              Investigation Timeline Builder
            </h1>
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto leading-relaxed">
              Transform documents into interactive timelines. Uncover connections, track entities, 
              and visualize the complete story of your investigation.
            </p>
            <Button
              size="lg"
              onClick={() => window.location.href = '/add-investigation'}
              onMouseEnter={() => setIsHovered(true)}
              onMouseLeave={() => setIsHovered(false)}
              className="bg-primary text-lg px-8 py-3 hover:scale-105 transition-all duration-300 shadow-glow"
            >
              <Plus className={`h-5 w-5 mr-2 transition-transform ${isHovered ? 'rotate-90' : ''}`} />
              Start New Investigation
              <ArrowRight className={`h-5 w-5 ml-2 transition-transform ${isHovered ? 'translate-x-1' : ''}`} />
            </Button>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-6xl mx-auto px-6 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">Powerful Investigation Tools</h2>
          <p className="text-muted-foreground text-lg">
            Everything you need to analyze documents and build comprehensive timelines
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <Card
              key={index}
              className="p-6 bg-gradient-card border-border shadow-card group"
            >
              <feature.icon className="h-10 w-10 text-primary mb-4 group-hover:text-accent transition-colors" />
              <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                {feature.description}
              </p>
            </Card>
          ))}
        </div>
      </div>

      {/* Demo Section */}
      <div className="border-t border-border bg-card/30 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-6 py-16">
          <div className="text-center">
            <h2 className="text-3xl font-bold mb-4">See It In Action</h2>
            <p className="text-muted-foreground text-lg mb-8">
              Explore a sample investigation with real timeline data
            </p>
            <Button
              variant="outline"
              size="lg"
              onClick={() => window.location.href = '/investigation'}
              className="border-primary/30 hover:bg-primary/10 hover:border-primary transition-all"
            >
              <Clock className="h-5 w-5 mr-2" />
              View Demo Investigation
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
