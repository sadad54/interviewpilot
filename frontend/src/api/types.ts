export interface Session {
  id: number;
  role: string;
  candidate_name: string | null;
  status: string;
  created_at: string;
}

export interface Question {
  id: number;
  role: string;
  topic: string;
  difficulty: string;
  text: string;
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