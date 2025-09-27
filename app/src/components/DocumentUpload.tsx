import { useState, useCallback } from 'react';
import { Upload, File, X, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/hooks/use-toast';

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
}

interface DocumentUploadProps {
  onFileProcessed: (fileId: string) => void;
  onFileAdded?: (file: File) => string;
}

export const DocumentUpload = ({ onFileProcessed, onFileAdded }: DocumentUploadProps) => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const { toast } = useToast();

  const handleFiles = useCallback((fileList: FileList) => {
    const newFiles: UploadedFile[] = Array.from(fileList).map(file => {
      const fileId = onFileAdded ? onFileAdded(file) : crypto.randomUUID();
      return {
        id: fileId,
        name: file.name,
        size: file.size,
        progress: 0,
        status: 'uploading'
      };
    });

    setFiles(prev => [...prev, ...newFiles]);

    // Simulate file upload and processing
    newFiles.forEach(file => {
      simulateUpload(file.id);
    });
  }, [onFileAdded]);

  const simulateUpload = (fileId: string) => {
    const updateProgress = (progress: number, status?: UploadedFile['status']) => {
      setFiles(prev => prev.map(file => 
        file.id === fileId 
          ? { ...file, progress, ...(status && { status }) }
          : file
      ));
    };

    // Simulate upload progress
    let progress = 0;
    const uploadInterval = setInterval(() => {
      progress += Math.random() * 30;
      if (progress >= 100) {
        clearInterval(uploadInterval);
        updateProgress(100, 'processing');
        
        // Simulate processing
        setTimeout(() => {
          updateProgress(100, 'completed');
          onFileProcessed(fileId);
          toast({
            title: "Document processed",
            description: "Events have been extracted and added to the timeline.",
          });
        }, 2000);
      } else {
        updateProgress(progress);
      }
    }, 200);
  };

  const removeFile = (fileId: string) => {
    setFiles(prev => prev.filter(file => file.id !== fileId));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer?.files) {
      handleFiles(e.dataTransfer.files);
    }
  }, [handleFiles]);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  return (
    <div className="space-y-6">
      <div
        className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300 ${
          dragActive 
            ? 'border-primary bg-primary/10 scale-[1.02]' 
            : 'border-border hover:border-primary/50 bg-card'
        }`}
        onDrop={handleDrop}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
      >
        <Upload className={`h-12 w-12 mx-auto mb-4 transition-colors ${
          dragActive ? 'text-primary' : 'text-muted-foreground'
        }`} />
        <h3 className="text-lg font-semibold mb-2">Upload Investigation Documents</h3>
        <p className="text-muted-foreground mb-4">
          Drag and drop files here or click to browse
        </p>
        <p className="text-sm text-muted-foreground mb-4">
          Supports PDF, DOC, DOCX, TXT files up to 20MB
        </p>
        <Button
          onClick={() => document.getElementById('file-input')?.click()}
          variant="outline"
          className="transition-all hover:scale-105"
        >
          Select Files
        </Button>
        <input
          id="file-input"
          type="file"
          multiple
          accept=".pdf,.doc,.docx,.txt"
          className="hidden"
          onChange={(e) => e.target.files && handleFiles(e.target.files)}
        />
      </div>

      {files.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-muted-foreground">Uploaded Files</h4>
          {files.map((file) => (
            <div key={file.id} className="bg-card p-4 rounded-lg border shadow-card">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-3">
                  <File className="h-5 w-5 text-primary" />
                  <div>
                    <p className="font-medium text-sm">{file.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {formatFileSize(file.size)}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {file.status === 'completed' && (
                    <Check className="h-5 w-5 text-green-500" />
                  )}
                  {file.status !== 'completed' && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeFile(file.id)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="capitalize text-muted-foreground">
                    {file.status === 'uploading' && 'Uploading...'}
                    {file.status === 'processing' && 'Processing...'}
                    {file.status === 'completed' && 'Completed'}
                    {file.status === 'error' && 'Error'}
                  </span>
                  <span className="text-muted-foreground">{Math.round(file.progress)}%</span>
                </div>
                <Progress value={file.progress} className="h-2" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};