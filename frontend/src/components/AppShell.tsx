import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import Icon from "./Icon";

interface AppShellProps {
  children: ReactNode;
  currentStep: 1 | 2 | 3;
  compact?: boolean;
}

const steps = ["Set your focus", "Answer the prompt", "Review insights"];

export default function AppShell({ children, currentStep, compact = false }: AppShellProps) {
  return (
    <div className={`app-shell${compact ? " app-shell--compact" : ""}`}>
      <a className="skip-link" href="#main-content">Skip to main content</a>
      <div className="ambient ambient--one" />
      <div className="ambient ambient--two" />

      <header className="site-header">
        <Link className="brand" to="/" aria-label="InterviewPilot home">
          <span className="brand__mark"><Icon name="sparkles" size={18} /></span>
          <span>Interview<span>Pilot</span></span>
        </Link>
        <div className="header-note">
          <span className="status-dot" />
          AI practice studio
        </div>
      </header>

      <main id="main-content" className="main-content" tabIndex={-1}>
        {children}
      </main>

      <nav className="journey" aria-label="Interview progress">
        {steps.map((step, index) => {
          const number = index + 1;
          const state = number < currentStep ? "complete" : number === currentStep ? "active" : "upcoming";
          return (
            <div className={`journey__step journey__step--${state}`} key={step} aria-current={state === "active" ? "step" : undefined}>
              <span className="journey__number">
                {state === "complete" ? <Icon name="check" size={14} /> : String(number).padStart(2, "0")}
              </span>
              <span>{step}</span>
            </div>
          );
        })}
      </nav>
    </div>
  );
}
