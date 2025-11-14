import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useToast } from "@/hooks/use-toast";
import { Upload, FileAudio, Loader2, Download, AlertCircle } from "lucide-react";

interface TranscriptionResponse {
  text: string | null;
  formattedText: string | null;
}

const Index = () => {
  const [file, setFile] = useState<File | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [applyFormatting, setApplyFormatting] = useState(true);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [rawTranscript, setRawTranscript] = useState<string>("");
  const [formattedTranscript, setFormattedTranscript] = useState<string>("");
  const [error, setError] = useState<string>("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const acceptedFileTypes = [
    ".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm", ".wma"
  ].join(",");

  const handleFileChange = (selectedFile: File | null) => {
    if (!selectedFile) return;
    
    setFile(selectedFile);
    setError("");
    
    // Create audio URL for preview
    const url = URL.createObjectURL(selectedFile);
    setAudioUrl(url);
    
    // Clear previous transcripts
    setRawTranscript("");
    setFormattedTranscript("");
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      handleFileChange(droppedFile);
    }
  };

  const handleTranscribe = async () => {
    if (!file) {
      setError("Please upload a file first.");
      return;
    }

    setIsTranscribing(true);
    setError("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(
        `http://localhost:8000/transcribe?format_output=${applyFormatting}`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Error ${response.status}: ${errorText}`);
      }

      const data: TranscriptionResponse = await response.json();
      setRawTranscript(data.text || "");
      setFormattedTranscript(data.formattedText || "");

      toast({
        title: "Transcription complete",
        description: "Your audio has been successfully transcribed.",
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to transcribe";
      setError(errorMessage);
      toast({
        title: "Transcription failed",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsTranscribing(false);
    }
  };

  const handleExport = async () => {
    if (!formattedTranscript) return;

    setIsExporting(true);
    setError("");

    try {
      const response = await fetch("http://localhost:8000/export", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ content: formattedTranscript }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Error ${response.status}: ${errorText}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "transcript.docx";
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast({
        title: "Export successful",
        description: "Your download should start automatically.",
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to export";
      setError(errorMessage);
      toast({
        title: "Export failed",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="min-h-screen bg-background py-8 px-4">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <header className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-foreground flex items-center justify-center gap-2">
            📝 Notary Transcriber
          </h1>
          <p className="text-muted-foreground text-lg">
            Upload audio, transcribe, and export as notary-style DOCX.
          </p>
        </header>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Main Card */}
        <Card className="p-8 shadow-lg space-y-6">
          {/* File Upload */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-foreground">Upload Audio File</h2>
            <div
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-border rounded-lg p-8 text-center cursor-pointer hover:border-primary hover:bg-accent/5 transition-all"
            >
              <input
                ref={fileInputRef}
                type="file"
                accept={acceptedFileTypes}
                onChange={(e) => handleFileChange(e.target.files?.[0] || null)}
                className="hidden"
              />
              <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-foreground font-medium mb-2">
                Click to upload or drag and drop
              </p>
              <p className="text-sm text-muted-foreground">
                Supported formats: MP3, MP4, WAV, WEBM, M4A, WMA
              </p>
            </div>

            {/* File Preview */}
            {file && audioUrl && (
              <div className="bg-secondary/50 rounded-lg p-4 space-y-3">
                <div className="flex items-center gap-3">
                  <FileAudio className="h-5 w-5 text-primary" />
                  <span className="text-foreground font-medium">{file.name}</span>
                </div>
                <audio controls className="w-full" src={audioUrl}>
                  Your browser does not support the audio element.
                </audio>
              </div>
            )}
          </div>

          {/* Options */}
          <div className="space-y-3">
            <h2 className="text-xl font-semibold text-foreground">Options</h2>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="formatting"
                checked={applyFormatting}
                onCheckedChange={(checked) => setApplyFormatting(checked === true)}
              />
              <label
                htmlFor="formatting"
                className="text-sm font-medium text-foreground leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                Apply notary-style formatting
              </label>
            </div>
          </div>

          {/* Transcribe Button */}
          <Button
            onClick={handleTranscribe}
            disabled={!file || isTranscribing}
            className="w-full"
            size="lg"
          >
            {isTranscribing ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Transcribing...
              </>
            ) : (
              "Transcribe"
            )}
          </Button>
        </Card>

        {/* Transcript Display */}
        {(rawTranscript || formattedTranscript) && (
          <div className="space-y-6">
            {/* Raw Transcript */}
            <Card className="p-6 shadow-lg space-y-4">
              <h2 className="text-xl font-semibold text-foreground">Raw Transcript</h2>
              <Textarea
                value={rawTranscript}
                onChange={(e) => setRawTranscript(e.target.value)}
                placeholder="Raw transcript will appear here..."
                className="min-h-[200px] font-mono text-sm"
              />
            </Card>

            {/* Formatted Transcript */}
            {formattedTranscript && (
              <Card className="p-6 shadow-lg space-y-4">
                <h2 className="text-xl font-semibold text-foreground">Formatted Transcript</h2>
                <Textarea
                  value={formattedTranscript}
                  onChange={(e) => setFormattedTranscript(e.target.value)}
                  placeholder="Formatted transcript will appear here..."
                  className="min-h-[300px] font-mono text-sm"
                />
              </Card>
            )}

            {/* Export Button */}
            {formattedTranscript && (
              <Card className="p-6 shadow-lg">
                <Button
                  onClick={handleExport}
                  disabled={isExporting}
                  className="w-full"
                  size="lg"
                >
                  {isExporting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Exporting to DOCX...
                    </>
                  ) : (
                    <>
                      <Download className="mr-2 h-4 w-4" />
                      Export to DOCX
                    </>
                  )}
                </Button>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Index;
