import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { createSession, getQuestions } from "../api/client";
import type { ApiErrorResponse } from "../api/types";
import AppShell from "../components/AppShell";
import Icon from "../components/Icon";

const ROLES = ["AI Engineer", "Data Scientist"] as const;
type Role = (typeof ROLES)[number];

export default function StartPage() {
  const [role, setRole] = useState<Role>(ROLES[0]);
  const [name, setName] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  async function handleStart(): Promise<void> {
    setLoading(true);
    setError(null);
    try {
      const sessionRes = await createSession(role, name.trim() || null);
      const questionsRes = await getQuestions(role);

      if (questionsRes.data.length === 0) {
        setError(`No questions are available for ${role} yet. Try another role.`);
        return;
      }

      navigate(`/interview/${sessionRes.data.id}/${questionsRes.data[0].id}`);
    } catch (err) {
      if (axios.isAxiosError<ApiErrorResponse>(err)) {
        setError(err.response?.data?.detail || "We couldn't start your session. Please try again.");
      } else {
        setError("Something unexpected happened. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell currentStep={1}>
      <section className="start-layout" aria-labelledby="start-title">
        <div className="start-copy">
          <p className="eyebrow">Practice with purpose</p>
          <h1 id="start-title">Turn every answer into an <span>advantage.</span></h1>
          <p className="lede">
            Rehearse the questions that matter, get precise AI feedback, and walk into your next technical interview with clarity.
          </p>

          <div className="benefit-row" aria-label="Practice benefits">
            <span className="benefit"><Icon name="target" size={17} /> Role-specific prompts</span>
            <span className="benefit"><Icon name="brain" size={17} /> Actionable evaluation</span>
            <span className="benefit"><Icon name="mic" size={17} /> Text or voice answers</span>
          </div>
        </div>

        <div className="setup-card">
          <div className="setup-card__top">
            <div className="setup-card__icon"><Icon name="sparkles" size={22} /></div>
            <span className="setup-card__step">01 / 03</span>
          </div>
          <h2>Shape your session</h2>
          <p className="setup-card__intro">Choose your target role. We’ll match you with a focused technical prompt.</p>

          <form className="setup-card__form" onSubmit={(event) => { event.preventDefault(); void handleStart(); }}>
            <div className="field">
              <label htmlFor="role">Target role</label>
              <div className="control-wrap">
                <Icon className="control-icon" name="target" size={17} />
                <select id="role" value={role} onChange={(event) => setRole(event.target.value as Role)}>
                  {ROLES.map((item) => <option key={item} value={item}>{item}</option>)}
                </select>
                <Icon className="control-chevron" name="chevron-down" size={17} />
              </div>
            </div>

            <div className="field">
              <label htmlFor="candidate-name">Your name <span className="optional">(optional)</span></label>
              <div className="control-wrap">
                <Icon className="control-icon" name="user" size={17} />
                <input
                  id="candidate-name"
                  autoComplete="name"
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                  placeholder="How should we address you?"
                />
              </div>
            </div>

            {error && <div className="error-banner" role="alert">{error}</div>}

            <button className="primary-button" type="submit" disabled={loading}>
              {loading ? <><span className="button-spinner" /> Preparing your session</> : <>Begin practice <Icon name="arrow-right" size={18} /></>}
            </button>
          </form>
          <p className="privacy-note"><Icon name="check" size={13} /> No account required. Start in seconds.</p>
        </div>
      </section>
    </AppShell>
  );
}
