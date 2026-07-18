import type { Question } from "../api/types";

interface QuestionCardProps {
  question: Question;
}

export default function QuestionCard({ question }: QuestionCardProps) {
  return (
    <section className="question-card" aria-labelledby="question-text">
      <div className="question-meta">
        <span className="meta-pill meta-pill--accent">{question.role}</span>
        <span className="meta-pill">{question.topic}</span>
        <span className="meta-pill">{question.difficulty}</span>
      </div>
      <p className="question-card__text" id="question-text">{question.text}</p>
    </section>
  );
}
