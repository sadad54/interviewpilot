import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { createSession, startInterview } from "../api/client";
import type { ApiErrorResponse } from "../api/types";
import AppShell from "../components/AppShell";
import Icon from "../components/Icon";

const ROLES = ["AI Engineer", "Data Scientist"] as const;
const SENIORITY_LEVELS = ["Junior", "Mid", "Senior", "Lead"] as const;
type Role = (typeof ROLES)[number];

export default function StartPage() {
  const [role, setRole] = useState<Role>(ROLES[0]);
  const [name, setName] = useState<string>("");
  const [seniority, setSeniority] = useState<(typeof SENIORITY_LEVELS)[number]>("Mid");
  const [jobDescription, setJobDescription] = useState("");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  async function handleStart(): Promise<void> {
    setLoading(true);
    setError(null);
    try {
      const sessionRes = await createSession(
        role,
        name.trim() || null,
        seniority.toLowerCase(),
        jobDescription.trim() || null,
      );
      await startInterview(sessionRes.data.public_id);
      navigate(`/mock-interview/${sessionRes.data.public_id}`);
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
            Sit through a complete, adaptive mock interview shaped around the role and level you are targeting.
          </p>

          <div className="benefit-row" aria-label="Practice benefits">
            <span className="benefit"><Icon name="target" size={17} /> Five planned competencies</span>
            <span className="benefit"><Icon name="brain" size={17} /> Adaptive interviewer probes</span>
            <span className="benefit"><Icon name="mic" size={17} /> Text or voice answers</span>
          </div>
        </div>

        <div className="setup-card">
          <div className="setup-card__top">
            <div className="setup-card__icon"><Icon name="sparkles" size={22} /></div>
            <span className="setup-card__step">01 / 03</span>
          </div>
          <h2>Shape your session</h2>
          <p className="setup-card__intro">Tell the interviewer what you are preparing for. Your plan is generated before the room opens.</p>

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
              <label htmlFor="seniority">Seniority</label>
              <div className="control-wrap">
                <Icon className="control-icon" name="brain" size={17} />
                <select id="seniority" value={seniority} onChange={(event) => setSeniority(event.target.value as (typeof SENIORITY_LEVELS)[number])}>
                  {SENIORITY_LEVELS.map((item) => <option key={item} value={item}>{item}</option>)}
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

            <div className="field">
              <label htmlFor="job-description">Job description <span className="optional">(optional)</span></label>
              <textarea
                className="setup-textarea"
                id="job-description"
                value={jobDescription}
                onChange={(event) => setJobDescription(event.target.value)}
                placeholder="Paste the responsibilities or skills you want the interview to reflect."
                rows={3}
              />
            </div>

            {error && <div className="error-banner" role="alert">{error}</div>}

            <button className="primary-button" type="submit" disabled={loading}>
              {loading ? <><span className="button-spinner" /> Planning your interview</> : <>Enter interview room <Icon name="arrow-right" size={18} /></>}
            </button>
          </form>
          <p className="privacy-note"><Icon name="check" size={13} /> Anonymous session · shareable report at the end</p>
        </div>
      </section>
    </AppShell>
  );
}
