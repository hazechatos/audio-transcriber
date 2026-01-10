import { useState } from "react";
import { FileAudio, GripVertical, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import AudioPlayer from "@/components/AudioPlayer";

interface FileWithUrl {
  file: File;
  url: string;
  id: string;
}

interface FileListProps {
  files: FileWithUrl[];
  onReorder: (files: FileWithUrl[]) => void;
  onRemove: (id: string) => void;
}

const FileList = ({ files, onReorder, onRemove }: FileListProps) => {
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null);

  const handleDragStart = (index: number) => {
    setDraggedIndex(index);
  };

  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    if (draggedIndex !== null && draggedIndex !== index) {
      setDragOverIndex(index);
    }
  };

  const handleDragLeave = () => {
    setDragOverIndex(null);
  };

  const handleDrop = (index: number) => {
    if (draggedIndex === null || draggedIndex === index) {
      setDraggedIndex(null);
      setDragOverIndex(null);
      return;
    }

    const newFiles = [...files];
    const [draggedItem] = newFiles.splice(draggedIndex, 1);
    newFiles.splice(index, 0, draggedItem);
    onReorder(newFiles);

    setDraggedIndex(null);
    setDragOverIndex(null);
  };

  const handleDragEnd = () => {
    setDraggedIndex(null);
    setDragOverIndex(null);
  };

  if (files.length === 0) return null;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-muted-foreground">
          {files.length} file{files.length !== 1 ? "s" : ""} selected
        </h3>
        <p className="text-xs text-muted-foreground">Drag to reorder</p>
      </div>
      <div className="space-y-2">
        {files.map((fileItem, index) => (
          <div
            key={fileItem.id}
            draggable
            onDragStart={() => handleDragStart(index)}
            onDragOver={(e) => handleDragOver(e, index)}
            onDragLeave={handleDragLeave}
            onDrop={() => handleDrop(index)}
            onDragEnd={handleDragEnd}
            className={`
              bg-secondary/50 rounded-lg p-3 space-y-2 cursor-grab active:cursor-grabbing transition-all
              ${draggedIndex === index ? "opacity-50 scale-95" : ""}
              ${dragOverIndex === index ? "ring-2 ring-primary ring-offset-2 ring-offset-background" : ""}
            `}
          >
            <div className="flex items-center gap-3">
              <GripVertical className="h-4 w-4 text-muted-foreground flex-shrink-0" />
              <span className="text-xs font-medium text-muted-foreground w-6">
                {index + 1}.
              </span>
              <FileAudio className="h-4 w-4 text-primary flex-shrink-0" />
              <span className="text-foreground text-sm font-medium truncate flex-1">
                {fileItem.file.name}
              </span>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0 hover:bg-destructive/10 hover:text-destructive"
                onClick={(e) => {
                  e.stopPropagation();
                  onRemove(fileItem.id);
                }}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            <AudioPlayer src={fileItem.url} />
          </div>
        ))}
      </div>
    </div>
  );
};

export default FileList;