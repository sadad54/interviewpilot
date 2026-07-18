import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import axios from "axios";
import { evaluateResponse, getQuestion, submitAudioResponse, submitTextResponse } from "../api/client";
import type { ApiErrorResponse, Question } from "../api/types";
import AppShell from "../components/AppShell";
import AudioRecorder from "../components/AudioRecorder";
import Icon from "../components/Icon";
import QuestionCard from "../components/QuestionCard";

type AnswerMode = "text" | "audio";

export default function InterviewPage() {
  const { sessionId, questionId } = useParams<{ sessionId: string; questionId: string }>();
  const navigate = useNavigate();
  const [question, setQuestion] = useState<Question | null>(null);
  const [mode, setMode] = useState<AnswerMode>("text");
  const [textAnswer, setTextAnswer] = useState("");
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadQuestion() {
      try {
        const response = await getQuestion(Number(questionId));
        setQuestion(response.data);
      } catch {
        setError("We couldn't load this interview question.");
      }
    }
    void loadQuestion();
  }, [questionId]);

  async function handleSubmit(): Promise<void> {
    if (!sessionId || !questionId) return;
    if (mode === "text" && !textAnswer.trim()) {
      setError("Add your answer before asking for an evaluation.");
      return;
    }
    if (mode === "audio" && !audioBlob) {
      setError("Record an answer before asking for an evaluation.");
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const response = mode === "text"
        ? await submitTextResponse(Number(sessionId), Number(questionId), textAnswer)
        : await submitAudioResponse(Number(sessionId), Number(questionId), audioBlob as Blob);

      await evaluateResponse(response.data.id);
      navigate(`/results/${response.data.id}`);
    } catch (err) {
      if (axios.isAxiosError<ApiErrorResponse>(err)) {
        setError(err.response?.data?.detail || "Your answer couldn't be submitted. Please try again.");
      } else {
        setError("Something unexpected happened while evaluating your answer.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  if (error && !question) {
    return (
      <AppShell currentStep={2} compact>
        <div className="error-screen">
          <div className="error-card">
            <h2>Question unavailable</h2>
            <p>{error}</p>
            <Link className="secondary-button" to="/">Return to session setup</Link>
          </div>
        </div>
      </AppShell>
    );
  }

  if (!question) {
    return (
      <AppShell currentStep={2} compact>
        <div className="loading-screen" role="status">
          <div className="loading-card"><div className="loading-orbit" /><h2>Preparing your prompt</h2><p>Matching the question to your practice session.</p></div>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell currentStep={2} compact>
      <div className="workspace">
        <article className="workspace__main">
          <div className="panel-head">
            <span className="panel-label">Practice room</span>
            <span className="panel-status"><span className="status-dot" /> Session active</span>
          </div>

          <QuestionCard question={question} />

          <section className="answer-area" aria-labelledby="answer-heading">
            <div className="answer-toolbar">
              <div>
                <span className="field-label" id="answer-heading">Choose how to respond</span>
              </div>
              <div className="mode-switcher" role="radiogroup" aria-label="Answer format">
                <button
                  className={`mode-button${mode === "text" ? " mode-button--active" : ""}`}
                  type="button"
                  role="radio"
                  aria-checked={mode === "text"}
                  onClick={() => { setMode("text"); setError(null); }}
                >
                  <Icon name="message" size={16} /> Write
                </button>
                <button
                  className={`mode-button${mode === "audio" ? " mode-button--active" : ""}`}
                  type="button"
                  role="radio"
                  aria-checked={mode === "audio"}
                  onClick={() => { setMode("audio"); setError(null); }}
                >
                  <Icon name="mic" size={16} /> Record
                </button>
              </div>
            </div>

            {mode === "text" ? (
              <div className="textarea-wrap">
                <label className="sr-only" htmlFor="answer-text">Your answer</label>
                <textarea
                  id="answer-text"
                  value={textAnswer}
                  onChange={(event) => setTextAnswer(event.target.value)}
                  placeholder="Build your answer here. Explain your reasoning, trade-offs, and the approach you would take…"
                  aria-describedby="character-count"
                />
                <span className="character-count" id="character-count">{textAnswer.length} characters</span>
              </div>
            ) : (
              <AudioRecorder onRecordingComplete={setAudioBlob} />
            )}

            {error && <div className="error-banner error-banner--spaced" role="alert">{error}</div>}

            <div className="submit-row">
              <p className="submit-row__hint">Your answer is evaluated for technical accuracy, clarity, and depth.</p>
              <button className="primary-button" type="button" onClick={() => void handleSubmit()} disabled={submitting}>
                {submitting ? <><span className="button-spinner" /> Evaluating answer</> : <>Get my feedback <Icon name="arrow-right" size={18} /></>}
              </button>
            </div>
          </section>
        </article>

        <aside className="workspace__aside" aria-label="Answer guidance">
          <h3>A stronger answer</h3>
          <ul className="tip-list">
            <li className="tip"><span className="tip__icon"><Icon name="target" size={15} /></span><div><strong>Lead with your approach</strong><p>State the direction first, then explain why it fits.</p></div></li>
            <li className="tip"><span className="tip__icon"><Icon name="brain" size={15} /></span><div><strong>Make trade-offs visible</strong><p>Show that you understand what your choices cost.</p></div></li>
            <li className="tip"><span className="tip__icon"><Icon name="sparkles" size={15} /></span><div><strong>Finish with impact</strong><p>Connect the implementation back to the outcome.</p></div></li>
          </ul>
          <div className="aside-divider" />
          <div className="privacy-block"><Icon name="volume" size={17} /><span>Voice recordings are transcribed only when you submit them for evaluation.</span></div>
        </aside>
      </div>
    </AppShell>
  );
}
