import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import api, { getFollowUp } from "../api/client";
import type { Evaluation, FollowUp } from "../api/types";
import AppShell from "../components/AppShell";
import Icon from "../components/Icon";
import ScoreDisplay from "../components/ScoreDisplay";

export default function ResultsPage() {
  const { responseId } = useParams<{ responseId: string }>();
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
  const [followUp, setFollowUp] = useState<FollowUp | null>(null);
  const [loadingFollowUp, setLoadingFollowUp] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadEvaluation() {
      try {
        const response = await api.get<Evaluation>(`/evaluations/response/${responseId}`);
        setEvaluation(response.data);
      } catch {
        setError("We couldn't load this evaluation.");
      }
    }
    void loadEvaluation();
  }, [responseId]);

  async function handleGetFollowUp(): Promise<void> {
    if (!responseId) return;
    setLoadingFollowUp(true);
    setError(null);
    try {
      const response = await getFollowUp(Number(responseId));
      setFollowUp(response.data);
    } catch {
      setError("We couldn't generate a follow-up question. Please try again.");
    } finally {
      setLoadingFollowUp(false);
    }
  }

  if (error && !evaluation) {
    return (
      <AppShell currentStep={3} compact>
        <div className="error-screen"><div className="error-card"><h2>Results unavailable</h2><p>{error}</p><Link className="secondary-button" to="/">Start a new session</Link></div></div>
      </AppShell>
    );
  }

  if (!evaluation) {
    return (
      <AppShell currentStep={3} compact>
        <div className="loading-screen" role="status"><div className="loading-card"><div className="loading-orbit" /><h2>Building your review</h2><p>Turning your answer into clear, practical insights.</p></div></div>
      </AppShell>
    );
  }

  return (
    <AppShell currentStep={3} compact>
      <div className="results-layout">
        <header className="results-hero">
          <div>
            <p className="eyebrow">Your practice review</p>
            <h1>Insight, not just a score.</h1>
            <p className="results-hero__copy">Use this feedback to make your next answer sharper and more convincing.</p>
          </div>
        </header>

        <div className="results-grid">
          <ScoreDisplay overallScore={evaluation.overall_score} criteriaScores={evaluation.criteria_scores} />

          <div className="insights-column">
            <section className="feedback-card" aria-labelledby="feedback-heading">
              <div className="feedback-card__icon"><Icon name="brain" size={20} /></div>
              <div className="card-kicker"><span>Coach's analysis</span><Icon name="sparkles" size={17} /></div>
              <h2 id="feedback-heading">What to carry forward</h2>
              <p>{evaluation.feedback}</p>
            </section>

            <section className="followup-card" aria-labelledby="followup-heading">
              <div>
                <div className="followup-card__icon"><Icon name="message" size={20} /></div>
                <h2 id="followup-heading">Go one level deeper</h2>
                {!followUp && <p>Ask the AI interviewer for the most useful next question based on your answer.</p>}
                {followUp?.should_follow_up && <p className="followup-question">{followUp.follow_up_question}</p>}
                {followUp && !followUp.should_follow_up && <p>{followUp.reasoning}</p>}
              </div>

              {!followUp && (
                <button className="secondary-button" type="button" onClick={() => void handleGetFollowUp()} disabled={loadingFollowUp}>
                  {loadingFollowUp ? <><span className="button-spinner" /> Thinking</> : <>Generate follow-up <Icon name="arrow-right" size={17} /></>}
                </button>
              )}
            </section>
          </div>
        </div>

        {error && <div className="error-banner error-banner--spaced" role="alert">{error}</div>}

        <div className="result-actions">
          <Link className="text-link" to="/"><Icon name="refresh" size={16} /> Start a new interview</Link>
          <Link className="primary-button" to="/">Practice another answer <Icon name="arrow-right" size={18} /></Link>
        </div>
      </div>
    </AppShell>
  );
}
