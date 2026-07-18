import { useEffect, useRef, useState } from "react";
import Icon from "./Icon";

interface AudioRecorderProps {
  onRecordingComplete: (blob: Blob) => void;
}

export default function AudioRecorder({ onRecordingComplete }: AudioRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [hasRecording, setHasRecording] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  useEffect(() => {
    if (!isRecording) return;
    const timer = window.setInterval(() => setElapsed((value) => value + 1), 1000);
    return () => window.clearInterval(timer);
  }, [isRecording]);

  useEffect(() => () => streamRef.current?.getTracks().forEach((track) => track.stop()), []);

  async function startRecording(): Promise<void> {
    setError(null);
    setElapsed(0);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      streamRef.current = stream;
      chunksRef.current = [];

      recorder.ondataavailable = (event: BlobEvent) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };

      recorder.onstop = () => {
        onRecordingComplete(new Blob(chunksRef.current, { type: "audio/webm" }));
        setHasRecording(true);
        stream.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      };

      recorder.start();
      mediaRecorderRef.current = recorder;
      setIsRecording(true);
    } catch {
      setError("Microphone access is unavailable. Check your browser permission and try again.");
    }
  }

  function stopRecording(): void {
    mediaRecorderRef.current?.stop();
    setIsRecording(false);
  }

  const time = `${String(Math.floor(elapsed / 60)).padStart(2, "0")}:${String(elapsed % 60).padStart(2, "0")}`;

  return (
    <div className={`recorder${isRecording ? " recorder--active" : ""}`}>
      <div className="recorder__visual">
        <span className="recorder__ring" />
        <button
          className="record-button"
          type="button"
          onClick={() => isRecording ? stopRecording() : void startRecording()}
          aria-label={isRecording ? "Stop recording" : hasRecording ? "Record a new answer" : "Start recording"}
        >
          <Icon name={isRecording ? "stop" : hasRecording ? "refresh" : "mic"} size={23} />
        </button>
      </div>
      <div className="recorder__title">
        {isRecording ? <span className="recorder__time">Recording · {time}</span> : hasRecording ? "Your answer is ready" : "Record your answer"}
      </div>
      {isRecording ? (
        <div className="waveform" aria-hidden="true">{Array.from({ length: 7 }, (_, index) => <span key={index} />)}</div>
      ) : (
        <p className="recorder__detail">{hasRecording ? "Press again to replace this recording" : "Press the microphone when you’re ready"}</p>
      )}
      {hasRecording && !isRecording && <span className="recorded-state"><Icon name="check" size={14} /> Recording captured</span>}
      {error && <div className="error-banner" role="alert">{error}</div>}
    </div>
  );
}
