import { useState, useCallback } from 'react';
import { Upload, File, X, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  status: 'pending' | 'ready';
}

interface DocumentUploadProps {
  onFilesChanged: (files: File[]) => void;
}

export const DocumentUpload = ({ onFilesChanged }: DocumentUploadProps) => {
  const [displayFiles, setDisplayFiles] = useState<UploadedFile[]>([]);
  const [actualFiles, setActualFiles] = useState<File[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const { toast } = useToast();

  const handleFiles = useCallback((fileList: FileList) => {
    const newFileArray = Array.from(fileList);
    const newDisplayFiles: UploadedFile[] = newFileArray.map(file => ({
      id: crypto.randomUUID(),
      name: file.name,
      size: file.size,
      status: 'ready' as const
    }));
    
    setDisplayFiles(prev => [...prev, ...newDisplayFiles]);
    setActualFiles(prev => {
      const updatedFiles = [...prev, ...newFileArray];
      onFilesChanged(updatedFiles);
      return updatedFiles;
    });
  }, [onFilesChanged]);

  const removeFile = (fileId: string) => {
    const fileIndex = displayFiles.findIndex(f => f.id === fileId);
    if (fileIndex !== -1) {
      setDisplayFiles(prev => prev.filter(file => file.id !== fileId));
      setActualFiles(prev => {
        const updatedFiles = prev.filter((_, index) => index !== fileIndex);
        onFilesChanged(updatedFiles);
        return updatedFiles;
      });
    }
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

      {displayFiles.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-muted-foreground">Selected Files</h4>
          {displayFiles.map((file) => (
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
                  {file.status === 'ready' && (
                    <Check className="h-5 w-5 text-green-500" />
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile(file.id)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              
              <div className="text-xs text-muted-foreground">
                Ready to upload
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};