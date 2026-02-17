import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { Upload, Loader2, Download, AlertCircle } from "lucide-react";
import FileList from "@/components/FileList";

interface TranscriptionResponse {
  text: string | null;
  formattedText: string | null;
}

interface FileWithUrl {
  file: File;
  url: string;
  id: string;
}

type Language = "en" | "fr";

const translations = {
  en: {
    language: "Language",
    english: "English",
    french: "French",
    appTitle: "Notary Transcriber",
    appSubtitle: "Upload audio, transcribe, and export as notary-style DOCX.",
    uploadSectionTitle: "Upload Audio Files",
    uploadPrompt: "Click to upload or drag and drop",
    supportedFormats: "Supported formats: MP3, MP4, WAV, WEBM, M4A, WMA",
    optionsTitle: "Options",
    applyFormatting: "Apply notary-style formatting",
    transcribe: "Transcribe",
    transcribing: "Transcribing...",
    rawTranscriptTitle: "Raw Transcript",
    rawTranscriptPlaceholder: "Raw transcript will appear here...",
    formattedTranscriptTitle: "Formatted Transcript",
    formattedTranscriptPlaceholder: "Formatted transcript will appear here...",
    exporting: "Exporting to DOCX...",
    export: "Export to DOCX",
    dragToReorder: "Drag to reorder",
    noFilesError: "Please upload at least one file first.",
    transcriptionCompleteTitle: "Transcription complete",
    transcriptionCompleteDescription: (count: number) =>
      `Successfully transcribed ${count} file${count !== 1 ? "s" : ""}.`,
    transcriptionFailedTitle: "Transcription failed",
    failedToTranscribe: "Failed to transcribe",
    exportSuccessTitle: "Export successful",
    exportSuccessDescription: "Your download should start automatically.",
    exportFailedTitle: "Export failed",
    failedToExport: "Failed to export",
    selectedFilesLabel: (count: number) =>
      `${count} file${count !== 1 ? "s" : ""} selected`,
  },
  fr: {
    language: "Langue",
    english: "Anglais",
    french: "Français",
    appTitle: "Transcripteur notarial",
    appSubtitle: "Téléversez l'audio, transcrivez et exportez en DOCX de style notarial.",
    uploadSectionTitle: "Téléverser des fichiers audio",
    uploadPrompt: "Cliquez pour téléverser ou glissez-déposez",
    supportedFormats: "Formats pris en charge : MP3, MP4, WAV, WEBM, M4A, WMA",
    optionsTitle: "Options",
    applyFormatting: "Appliquer le formatage de style notarial",
    transcribe: "Transcrire",
    transcribing: "Transcription en cours...",
    rawTranscriptTitle: "Transcription brute",
    rawTranscriptPlaceholder: "La transcription brute apparaîtra ici...",
    formattedTranscriptTitle: "Transcription formatée",
    formattedTranscriptPlaceholder: "La transcription formatée apparaîtra ici...",
    exporting: "Exportation en DOCX...",
    export: "Exporter en DOCX",
    dragToReorder: "Glisser pour réorganiser",
    noFilesError: "Veuillez d'abord téléverser au moins un fichier.",
    transcriptionCompleteTitle: "Transcription terminée",
    transcriptionCompleteDescription: (count: number) =>
      `${count} fichier${count > 1 ? "s" : ""} transcrit${count > 1 ? "s" : ""} avec succès.`,
    transcriptionFailedTitle: "Échec de la transcription",
    failedToTranscribe: "Échec de la transcription",
    exportSuccessTitle: "Exportation réussie",
    exportSuccessDescription: "Le téléchargement devrait démarrer automatiquement.",
    exportFailedTitle: "Échec de l'exportation",
    failedToExport: "Échec de l'exportation",
    selectedFilesLabel: (count: number) =>
      `${count} fichier${count > 1 ? "s" : ""} sélectionné${count > 1 ? "s" : ""}`,
  },
} as const;

const Index = () => {
  const [files, setFiles] = useState<FileWithUrl[]>([]);
  const [language, setLanguage] = useState<Language>("fr");
  const [applyFormatting, setApplyFormatting] = useState(true);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [rawTranscript, setRawTranscript] = useState<string>("");
  const [formattedTranscript, setFormattedTranscript] = useState<string>("");
  const [error, setError] = useState<string>("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();
  const t = translations[language];

  const acceptedFileTypes = [
    ".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm", ".wma",
  ].join(",");

  const addFiles = (newFiles: FileList | File[]) => {
    const fileArray = Array.from(newFiles);
    const newFileItems: FileWithUrl[] = fileArray.map((file) => ({
      file,
      url: URL.createObjectURL(file),
      id: `${file.name}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    }));

    setFiles((prev) => [...prev, ...newFileItems]);
    setError("");
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      addFiles(e.target.files);
      e.target.value = "";
    }
  };

  const handleReorder = (reorderedFiles: FileWithUrl[]) => {
    setFiles(reorderedFiles);
  };

  const handleRemove = (id: string) => {
    setFiles((prev) => {
      const fileToRemove = prev.find((f) => f.id === id);
      if (fileToRemove) {
        URL.revokeObjectURL(fileToRemove.url);
      }
      return prev.filter((f) => f.id !== id);
    });
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (e.dataTransfer.files.length > 0) {
      addFiles(e.dataTransfer.files);
    }
  };

  const handleTranscribe = async () => {
    if (files.length === 0) {
      setError(t.noFilesError);
      return;
    }

    setIsTranscribing(true);
    setError("");
    setRawTranscript("");
    setFormattedTranscript("");

    try {
      const formData = new FormData();
      files.forEach((fileItem) => {
        formData.append("files", fileItem.file);
      });

      const response = await fetch(
        `http://localhost:8000/transcribe?format_output=${applyFormatting}`,
        {
          method: "POST",
          body: formData,
        },
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Error ${response.status}: ${errorText}`);
      }

      const data: TranscriptionResponse = await response.json();

      setRawTranscript(data.text || "");
      setFormattedTranscript(data.formattedText || "");

      toast({
        title: t.transcriptionCompleteTitle,
        description: t.transcriptionCompleteDescription(files.length),
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : t.failedToTranscribe;
      setError(errorMessage);
      toast({
        title: t.transcriptionFailedTitle,
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
        title: t.exportSuccessTitle,
        description: t.exportSuccessDescription,
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : t.failedToExport;
      setError(errorMessage);
      toast({
        title: t.exportFailedTitle,
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
        <div className="flex justify-end">
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">{t.language}</span>
            <Select value={language} onValueChange={(value) => setLanguage(value as Language)}>
              <SelectTrigger className="w-48">
                <SelectValue>
                  {language === "fr" ? `🇫🇷 ${t.french}` : `🇬🇧 ${t.english}`}
                </SelectValue>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="fr">🇫🇷 {t.french}</SelectItem>
                <SelectItem value="en">🇬🇧 {t.english}</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <header className="space-y-2 text-center">
          <h1 className="text-4xl font-bold text-foreground">{t.appTitle}</h1>
          <p className="text-lg text-muted-foreground">{t.appSubtitle}</p>
        </header>

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <Card className="space-y-6 p-8 shadow-lg">
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-foreground">{t.uploadSectionTitle}</h2>
            <div
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className="cursor-pointer rounded-lg border-2 border-dashed border-border p-8 text-center transition-all hover:border-primary hover:bg-accent/5"
            >
              <input
                ref={fileInputRef}
                type="file"
                accept={acceptedFileTypes}
                multiple
                onChange={handleFileChange}
                className="hidden"
              />
              <Upload className="mx-auto mb-4 h-12 w-12 text-muted-foreground" />
              <p className="mb-2 font-medium text-foreground">{t.uploadPrompt}</p>
              <p className="text-sm text-muted-foreground">{t.supportedFormats}</p>
            </div>

            <FileList
              files={files}
              onReorder={handleReorder}
              onRemove={handleRemove}
              selectedFilesLabel={t.selectedFilesLabel(files.length)}
              dragToReorderLabel={t.dragToReorder}
            />
          </div>

          <div className="space-y-3">
            <h2 className="text-xl font-semibold text-foreground">{t.optionsTitle}</h2>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="formatting"
                checked={applyFormatting}
                onCheckedChange={(checked) => setApplyFormatting(checked === true)}
              />
              <label
                htmlFor="formatting"
                className="text-sm font-medium leading-none text-foreground peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                {t.applyFormatting}
              </label>
            </div>
          </div>

          <Button
            onClick={handleTranscribe}
            disabled={files.length === 0 || isTranscribing}
            className="w-full"
            size="lg"
          >
            {isTranscribing ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                {t.transcribing}
              </>
            ) : (
              t.transcribe
            )}
          </Button>
        </Card>

        {(rawTranscript || formattedTranscript) && (
          <div className="space-y-6">
            <Card className="space-y-4 p-6 shadow-lg">
              <h2 className="text-xl font-semibold text-foreground">{t.rawTranscriptTitle}</h2>
              <Textarea
                value={rawTranscript}
                onChange={(e) => setRawTranscript(e.target.value)}
                placeholder={t.rawTranscriptPlaceholder}
                className="min-h-[200px] font-mono text-sm"
              />
            </Card>

            {formattedTranscript && (
              <Card className="space-y-4 p-6 shadow-lg">
                <h2 className="text-xl font-semibold text-foreground">{t.formattedTranscriptTitle}</h2>
                <Textarea
                  value={formattedTranscript}
                  onChange={(e) => setFormattedTranscript(e.target.value)}
                  placeholder={t.formattedTranscriptPlaceholder}
                  className="min-h-[300px] font-mono text-sm"
                />
              </Card>
            )}

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
                      {t.exporting}
                    </>
                  ) : (
                    <>
                      <Download className="mr-2 h-4 w-4" />
                      {t.export}
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
