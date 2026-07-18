import type { CSSProperties } from "react";
import type { CriteriaScores } from "../api/types";
import Icon from "./Icon";

interface ScoreDisplayProps {
  overallScore: number;
  criteriaScores: CriteriaScores;
}

function scoreColor(score: number): string {
  if (score >= 7) return "#52cfad";
  if (score >= 4) return "#f4a261";
  return "#ff7e78";
}

export default function ScoreDisplay({ overallScore, criteriaScores }: ScoreDisplayProps) {
  const overallColor = scoreColor(overallScore);
  const ringStyle = {
    "--score-color": overallColor,
    "--score-progress": `${Math.max(0, Math.min(100, overallScore * 10))}%`,
  } as CSSProperties;

  return (
    <section className="score-card" style={ringStyle} aria-label={`Overall score ${overallScore.toFixed(1)} out of 10`}>
      <div className="card-kicker"><span>Performance score</span><Icon name="target" size={17} /></div>
      <div className="score-ring">
        <div className="score-ring__value">{overallScore.toFixed(1)} <small>/ 10</small></div>
      </div>
      <div className="criteria-list">
        {Object.entries(criteriaScores).map(([key, value]) => (
          <div className="criterion" key={key}>
            <div className="criterion__top"><span>{key.replace("_", " ")}</span><span className="criterion__value">{value}/10</span></div>
            <div className="criterion__track" role="progressbar" aria-label={key.replace("_", " ")} aria-valuemin={0} aria-valuemax={10} aria-valuenow={value}>
              <span className="criterion__bar" style={{ width: `${Math.max(0, Math.min(100, value * 10))}%`, "--bar-color": scoreColor(value) } as CSSProperties} />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
