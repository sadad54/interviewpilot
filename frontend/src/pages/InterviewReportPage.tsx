import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { getInterviewReport, getSharedReport } from "../api/client";
import type { SessionReport } from "../api/types";
import AppShell from "../components/AppShell";
import Icon from "../components/Icon";

const label = (value: string) => value.replaceAll("_", " ");

export default function InterviewReportPage({ shared = false }: { shared?: boolean }) {
  const { publicId, shareToken } = useParams<{ publicId: string; shareToken: string }>();
  const [report, setReport] = useState<SessionReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const request = shared && shareToken ? getSharedReport(shareToken) : publicId ? getInterviewReport(publicId) : null;
    if (!request) return;
    request.then(({ data }) => setReport(data)).catch(() => setError("The interview report is not available."));
  }, [publicId, shareToken, shared]);

  if (error) return <AppShell currentStep={3}><div className="error-screen"><div className="error-card"><h2>Report unavailable</h2><p>{error}</p><Link className="secondary-button" to="/">Start an interview</Link></div></div></AppShell>;
  if (!report) return <AppShell currentStep={3}><div className="loading-screen" role="status"><div className="loading-card"><div className="loading-orbit" /><h2>Building the evidence trail</h2><p>Aggregating scores across the full interview.</p></div></div></AppShell>;

  return (
    <AppShell currentStep={3} compact>
      <div className="session-report">
        <header className="report-header">
          <div><p className="eyebrow">Completed interview</p><h1>{report.candidate_name ? `${report.candidate_name}'s` : "Your"} interview evidence.</h1><p>{report.role} · {report.seniority} · {report.summary}</p></div>
          <div className="report-score"><span>{report.overall_score.toFixed(1)}</span><small>overall / 10</small></div>
        </header>

        <section className="report-section" aria-labelledby="competency-heading">
          <div className="section-heading"><div><span className="panel-label">Competency map</span><h2 id="competency-heading">Where the evidence landed</h2></div><span>{Object.keys(report.competency_scores).length} areas covered</span></div>
          <div className="competency-grid">
            {Object.entries(report.competency_scores).map(([competency, score]) => <div className="competency-card" key={competency}><div><span>{label(competency)}</span><strong>{score.toFixed(1)}</strong></div><div className="criterion__track"><span className="criterion__bar" style={{ width: `${score * 10}%` }} /></div></div>)}
          </div>
        </section>

        <div className="report-columns">
          <section className="report-section"><span className="panel-label">Signals to keep</span><h2>Strengths</h2><ul className="report-list report-list--positive">{report.strengths.map((item) => <li key={item}><Icon name="check" size={16} />{item}</li>)}</ul></section>
          <section className="report-section"><span className="panel-label">Next practice focus</span><h2>Improvements</h2><ul className="report-list">{report.improvements.map((item) => <li key={item}><Icon name="target" size={16} />{item}</li>)}</ul></section>
        </div>

        <section className="report-section">
          <div className="section-heading"><div><span className="panel-label">Auditable assessment</span><h2>Transcript evidence</h2></div><span>{report.coverage_summary.follow_ups_answered ?? 0} adaptive probes</span></div>
          <div className="evidence-list">
            {report.evidence.map((item, index) => <article className="evidence-row" key={`${item.question_id}-${index}`}><span className="evidence-index">{String(index + 1).padStart(2, "0")}</span><div><div className="question-meta"><span className="meta-pill">{label(item.competency)}</span><span className="meta-pill meta-pill--accent">{item.score.toFixed(1)} / 10</span></div><h3>{item.question}</h3><blockquote>{item.answer_excerpt}</blockquote></div></article>)}
          </div>
        </section>

        <div className="result-actions"><Link className="text-link" to="/"><Icon name="refresh" size={16} /> New interview</Link>{!shared && <Link className="secondary-button" to={`/shared-report/${report.share_token}`}>Open shareable report <Icon name="arrow-right" size={17} /></Link>}</div>
      </div>
    </AppShell>
  );
}
