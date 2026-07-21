export interface Session {
  id: number;
  public_id: string;
  role: string;
  candidate_name: string | null;
  seniority: string;
  job_description: string | null;
  status: string;
  primary_question_count: number;
  current_primary_index: number;
  plan_summary: Record<string, unknown>;
  created_at: string;
}

export interface Question {
  id: number;
  role: string;
  topic: string;
  difficulty: string;
  text: string;
  kind: "primary" | "follow_up";
  competency: string;
  sequence_index: number | null;
  parent_question_id: number | null;
}

export interface Response {
  id: number;
  session_id: number;
  question_id: number;
  answer_text: string;
  created_at: string;
}

export interface CriteriaScores {
  technical_accuracy: number;
  clarity: number;
  depth: number;
}

export interface Evaluation {
  id: number;
  response_id: number;
  overall_score: number;
  criteria_scores: CriteriaScores;
  feedback: string;
}

export interface FollowUp {
  should_follow_up: boolean;
  follow_up_question: string;
  reasoning: string;
}

export interface ApiErrorResponse {
  detail: string;
}

export interface TranscriptTurn {
  question: Question;
  answer_text: string | null;
  response_id: number | null;
  decision_summary: string | null;
}

export interface InterviewProgress {
  completed_primary: number;
  total_primary: number;
  answered_turns: number;
  elapsed_seconds: number;
}

export interface InterviewState {
  public_id: string;
  status: "created" | "planning" | "in_progress" | "completed" | "failed";
  role: string;
  seniority: string;
  candidate_name: string | null;
  plan_categories: string[];
  current_question: Question | null;
  transcript: TranscriptTurn[];
  progress: InterviewProgress;
  report_token: string | null;
}

export interface InterviewAdvance {
  status: InterviewState["status"];
  action: "probe" | "advance" | "complete" | "duplicate";
  decision_summary: string;
  current_question: Question | null;
  progress: InterviewProgress;
  report_token: string | null;
}

export interface ReportEvidence {
  question_id: number;
  question: string;
  answer_excerpt: string;
  competency: string;
  score: number;
}

export interface SessionReport {
  share_token: string;
  session_public_id: string;
  role: string;
  seniority: string;
  candidate_name: string | null;
  overall_score: number;
  competency_scores: Record<string, number>;
  strengths: string[];
  improvements: string[];
  summary: string;
  evidence: ReportEvidence[];
  coverage_summary: {
    planned?: string[];
    covered?: string[];
    primary_answered?: number;
    follow_ups_answered?: number;
  };
  transcript: TranscriptTurn[];
  created_at: string;
}
