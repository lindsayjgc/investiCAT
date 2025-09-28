import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import Investigation from "./pages/Investigation";
import AddInvestigation from "./pages/AddInvestigation";
import NotFound from "./pages/NotFound";
import { CedarCopilot } from 'cedar-os';
import { FloatingCedarChat } from "./cedar/components/chatComponents/FloatingCedarChat";

const queryClient = new QueryClient();

export const DEFAULT_USER_ID = "1";

const App = () => (
  <CedarCopilot
    llmProvider={{
				provider: 'openai',
				apiKey: import.meta.env.VITE_OPENAI_API_KEY,
			}}
    >
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <FloatingCedarChat />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/investigation/:id" element={<Investigation />} />
          <Route path="/add-investigation" element={<AddInvestigation />} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
  </CedarCopilot>
);

export default App;
