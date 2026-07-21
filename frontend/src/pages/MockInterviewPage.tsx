import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import axios from "axios";

import { completeInterview, getInterviewState, submitInterviewAnswer, submitInterviewAudioAnswer } from "../api/client";
import type { ApiErrorResponse, InterviewState } from "../api/types";
import AppShell from "../components/AppShell";
import AudioRecorder from "../components/AudioRecorder";
import Icon from "../components/Icon";

type AnswerMode = "text" | "audio";

const competencyLabel = (value: string) => value.replaceAll("_", " ");

export default function MockInterviewPage() {
  const { publicId } = useParams<{ publicId: string }>();
  const navigate = useNavigate();
  const [state, setState] = useState<InterviewState | null>(null);
  const [answer, setAnswer] = useState("");
  const [mode, setMode] = useState<AnswerMode>("text");
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    if (!publicId) return;
    getInterviewState(publicId)
      .then(({ data }) => {
        setState(data);
        setSeconds(data.progress.elapsed_seconds);
        if (data.status === "completed") navigate(`/report/${publicId}`, { replace: true });
      })
      .catch(() => setError("The interview room could not be restored. Return to setup and start a new session."));
  }, [navigate, publicId]);

  useEffect(() => {
    const timer = window.setInterval(() => setSeconds((value) => value + 1), 1000);
    return () => window.clearInterval(timer);
  }, []);

  const timeLabel = useMemo(() => `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`, [seconds]);

  function speakQuestion() {
    if (!state?.current_question || !("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(new SpeechSynthesisUtterance(state.current_question.text));
  }

  async function refreshState() {
    if (!publicId) return;
    const response = await getInterviewState(publicId);
    setState(response.data);
  }

  async function submitAnswer() {
    if (!publicId || !state?.current_question) return;
    if (mode === "text" && !answer.trim()) {
      setError("Give your answer before moving to the next interview turn.");
      return;
    }
    if (mode === "audio" && !audioBlob) {
      setError("Record your answer before moving to the next interview turn.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const requestId = crypto.randomUUID();
      const response = mode === "text"
        ? await submitInterviewAnswer(publicId, state.current_question.id, answer, requestId)
        : await submitInterviewAudioAnswer(publicId, state.current_question.id, audioBlob as Blob, requestId);
      if (response.data.status === "completed") {
        navigate(`/report/${publicId}`);
        return;
      }
      setAnswer("");
      setAudioBlob(null);
      await refreshState();
    } catch (err) {
      const message = axios.isAxiosError<ApiErrorResponse>(err)
        ? err.response?.data?.detail
        : null;
      setError(message || "The answer was not processed. Your place is saved; try again.");
    } finally {
      setSubmitting(false);
    }
  }

  async function finishEarly() {
    if (!publicId || !window.confirm("Finish the interview now? Your report will use the answers completed so far.")) return;
    setSubmitting(true);
    try {
      await completeInterview(publicId);
      navigate(`/report/${publicId}`);
    } catch (err) {
      const message = axios.isAxiosError<ApiErrorResponse>(err) ? err.response?.data?.detail : null;
      setError(message || "The interview could not be completed yet.");
    } finally {
      setSubmitting(false);
    }
  }

  if (error && !state) {
    return <AppShell currentStep={2}><div className="error-screen"><div className="error-card"><h2>Interview unavailable</h2><p>{error}</p><Link className="secondary-button" to="/">Return to setup</Link></div></div></AppShell>;
  }
  if (!state?.current_question) {
    return <AppShell currentStep={2}><div className="loading-screen" role="status"><div className="loading-card"><div className="loading-orbit" /><h2>Restoring the room</h2><p>Loading your interview plan and transcript.</p></div></div></AppShell>;
  }

  const question = state.current_question;
  return (
    <AppShell currentStep={2} compact>
      <div className="mock-room">
        <header className="room-bar">
          <div><span className="status-dot" /> Live mock interview</div>
          <div className="room-bar__meta"><span>{state.role} · {state.seniority}</span><span className="room-timer">{timeLabel}</span></div>
        </header>

        <aside className="interview-spine" aria-label="Interview plan and transcript">
          <div className="spine-heading"><span>Interview plan</span><strong>{state.progress.completed_primary}/{state.progress.total_primary}</strong></div>
          <div className="spine-list">
            {state.plan_categories.map((category, index) => {
              const completed = index < state.progress.completed_primary;
              const active = category === question.competency;
              return <div className={`spine-item${completed ? " spine-item--complete" : ""}${active ? " spine-item--active" : ""}`} key={`${category}-${index}`}>
                <span className="spine-node">{completed ? <Icon name="check" size={13} /> : index + 1}</span>
                <span>{competencyLabel(category)}</span>
              </div>;
            })}
          </div>
          <div className="spine-transcript">
            <span className="panel-label">Completed turns</span>
            {state.transcript.filter((turn) => turn.answer_text).map((turn) => (
              <details key={turn.question.id}>
                <summary>{turn.question.kind === "follow_up" ? "Probe" : `Question ${(turn.question.sequence_index ?? 0) + 1}`}</summary>
                <p>{turn.question.text}</p>
                <blockquote>{turn.answer_text}</blockquote>
                {turn.decision_summary && <small>{turn.decision_summary}</small>}
              </details>
            ))}
          </div>
        </aside>

        <main className="interviewer-stage">
          <div className="interviewer-presence">
            <div className="interviewer-avatar"><Icon name="brain" size={22} /></div>
            <div><strong>AI interviewer</strong><span>Listening for evidence and trade-offs</span></div>
            <button className="speak-button" type="button" onClick={speakQuestion} aria-label="Read question aloud"><Icon name="volume" size={18} /></button>
          </div>

          <section className="live-question" aria-labelledby="live-question-text">
            <div className="question-meta">
              <span className="meta-pill meta-pill--accent">{question.kind === "follow_up" ? "Adaptive follow-up" : `Question ${(question.sequence_index ?? 0) + 1} of 5`}</span>
              <span className="meta-pill">{competencyLabel(question.competency)}</span>
            </div>
            <h1 id="live-question-text">{question.text}</h1>
          </section>

          <section className="live-answer" aria-label="Your answer">
            <div className="answer-toolbar">
              <span className="field-label">Respond naturally. Feedback stays hidden until the end.</span>
              <div className="mode-switcher" role="radiogroup" aria-label="Answer format">
                <button className={`mode-button${mode === "text" ? " mode-button--active" : ""}`} type="button" role="radio" aria-checked={mode === "text"} onClick={() => setMode("text")}><Icon name="message" size={16} /> Write</button>
                <button className={`mode-button${mode === "audio" ? " mode-button--active" : ""}`} type="button" role="radio" aria-checked={mode === "audio"} onClick={() => setMode("audio")}><Icon name="mic" size={16} /> Record</button>
              </div>
            </div>
            {mode === "text" ? <textarea value={answer} onChange={(event) => setAnswer(event.target.value)} placeholder="Answer as you would in the room. Think aloud, explain decisions, and make trade-offs explicit." /> : <AudioRecorder onRecordingComplete={setAudioBlob} />}
            {error && <div className="error-banner error-banner--spaced" role="alert">{error}</div>}
            <div className="room-actions">
              <button className="text-link" type="button" onClick={() => void finishEarly()} disabled={submitting}>Finish early</button>
              <button className="primary-button" type="button" onClick={() => void submitAnswer()} disabled={submitting}>
                {submitting ? <><span className="button-spinner" /> Processing turn</> : <>Submit answer <Icon name="arrow-right" size={18} /></>}
              </button>
            </div>
          </section>
        </main>
      </div>
    </AppShell>
  );
}
