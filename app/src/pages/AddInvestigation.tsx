import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { DocumentUpload } from '@/components/DocumentUpload';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { ArrowLeft, FileText, Plus, Folder } from 'lucide-react';
import { postUserByUserIdCat, postUserByUserIdCatByCatIdDocument } from '@/client';
import { DEFAULT_USER_ID } from '@/App';

const AddInvestigation = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);

  const handleFilesChanged = (files: File[]) => {
    setUploadedFiles(files);
  };

  const handleCreateInvestigation = async () => {
    if (!title.trim()) {
      toast({
        title: "Title required",
        description: "Please enter a title for your investigation.",
        variant: "destructive"
      });
      return;
    }

    setIsCreating(true);
    
    try {
      // First create the cat without documents
      const newCat = await postUserByUserIdCat({ 
        body: { 
          title: title.trim(), 
          ownerId: DEFAULT_USER_ID, 
          description: description.trim()
        }, 
        path: { userId: DEFAULT_USER_ID } 
      });
      
      const catId = newCat.data.id;
      
      if (!catId) {
        throw new Error('Failed to create investigation - no ID returned');
      }

      // Upload each file to the created cat
      const uploadPromises = uploadedFiles.map(async (file) => {
        try {
          const result = await postUserByUserIdCatByCatIdDocument({
            body: { file },
            path: { userId: DEFAULT_USER_ID, catId }
          });
          console.log(`Successfully uploaded document ${file.name} to cat ${catId}`);
          return result;
        } catch (error) {
          console.error(`Failed to upload ${file.name}:`, error);
          throw error;
        }
      });
      
      // Wait for all uploads to complete
      await Promise.all(uploadPromises);

      toast({
        title: "Investigation created",
        description: `"${title}" has been created successfully${uploadedFiles.length > 0 ? ` with ${uploadedFiles.length} document(s)` : ''}.`,
      });

      // Navigate to the specific investigation
      navigate(`/investigation/${catId}`);
    } catch (error) {
      toast({
        title: "Error creating investigation",
        description: "There was a problem creating your investigation. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-timeline">
      {/* Header */}
      <div className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/')}
                className="hover:bg-primary/10"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-foreground">
                  Create New Investigation
                </h1>
                <p className="text-muted-foreground mt-1">
                  Set up your investigation and upload relevant documents
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="space-y-8">
          {/* Investigation Details */}
          <Card className="p-6 bg-gradient-card border-border shadow-card">
            <div className="flex items-center space-x-3 mb-6">
              <Folder className="h-6 w-6 text-primary" />
              <h2 className="text-xl font-semibold">Investigation Details</h2>
            </div>
            
            <div className="space-y-6">
              <div>
                <label htmlFor="title" className="block text-sm font-medium mb-2">
                  Title <span className="text-red-500">*</span>
                </label>
                <Input
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Enter investigation title"
                  className="text-base"
                />
              </div>

              <div>
                <label htmlFor="description" className="block text-sm font-medium mb-2">
                  Description
                </label>
                <Textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Provide a detailed description of the investigation objectives and scope"
                  className="min-h-[120px] text-base"
                />
              </div>
            </div>
          </Card>

          {/* Document Upload */}
          <Card className="p-6 bg-gradient-card border-border shadow-card">
            <div className="flex items-center space-x-3 mb-6">
              <FileText className="h-6 w-6 text-primary" />
              <h2 className="text-xl font-semibold">Documents</h2>
            </div>

            <DocumentUpload 
              onFilesChanged={handleFilesChanged}
            />
          </Card>

          {/* Action Buttons */}
          <div className="flex items-center justify-between pt-6 border-t border-border">
            <Button
              variant="outline"
              onClick={() => navigate('/')}
              className="border-primary/30 hover:bg-primary/10"
            >
              Cancel
            </Button>
            <Button
              onClick={handleCreateInvestigation}
              disabled={!title.trim() || isCreating}
              className="bg-primary transition-all hover:scale-105"
            >
              {isCreating ? (
                <>
                  <div className="h-4 w-4 mr-2 animate-spin rounded-full border-2 border-current border-t-transparent" />
                  Creating...
                </>
              ) : (
                <>
                  <Plus className="h-4 w-4 mr-2" />
                  Create Investigation
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AddInvestigation;