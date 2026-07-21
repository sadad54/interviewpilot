import axios, { type AxiosResponse } from "axios";
import type { Session, Question, Response, Evaluation, FollowUp, InterviewState, InterviewAdvance, SessionReport } from "./types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: { "Content-Type": "application/json" },
});


export const createSession = (
  role: string,
  candidateName: string | null,
  seniority = "mid",
  jobDescription: string | null = null,
): Promise<AxiosResponse<Session>> =>
  api.post("/sessions/", { role, candidate_name: candidateName, seniority, job_description: jobDescription });

export const startInterview = (publicId: string): Promise<AxiosResponse<InterviewState>> =>
  api.post(`/sessions/${publicId}/start`);

export const getInterviewState = (publicId: string): Promise<AxiosResponse<InterviewState>> =>
  api.get(`/sessions/${publicId}/state`);

export const submitInterviewAnswer = (
  publicId: string,
  questionId: number,
  answerText: string,
  clientRequestId: string,
): Promise<AxiosResponse<InterviewAdvance>> => api.post(`/sessions/${publicId}/answers`, {
  question_id: questionId,
  answer_text: answerText,
  client_request_id: clientRequestId,
});

export const submitInterviewAudioAnswer = (
  publicId: string,
  questionId: number,
  audioBlob: Blob,
  clientRequestId: string,
): Promise<AxiosResponse<InterviewAdvance>> => {
  const formData = new FormData();
  formData.append("question_id", String(questionId));
  formData.append("client_request_id", clientRequestId);
  formData.append("audio", audioBlob, "answer.webm");
  return api.post(`/sessions/${publicId}/answers/audio`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const completeInterview = (publicId: string): Promise<AxiosResponse<SessionReport>> =>
  api.post(`/sessions/${publicId}/complete`);

export const getInterviewReport = (publicId: string): Promise<AxiosResponse<SessionReport>> =>
  api.get(`/sessions/${publicId}/report`);

export const getSharedReport = (token: string): Promise<AxiosResponse<SessionReport>> =>
  api.get(`/sessions/reports/shared/${token}`);

export const getQuestions = (role: string): Promise<AxiosResponse<Question[]>> =>
  api.get("/questions/", { params: { role } });

export const submitTextResponse = (
  sessionId: number,
  questionId: number,
  answerText: string
): Promise<AxiosResponse<Response>> =>
  api.post("/responses/", {
    session_id: sessionId,
    question_id: questionId,
    answer_text: answerText,
  });

export const submitAudioResponse = (
  sessionId: number,
  questionId: number,
  audioBlob: Blob
): Promise<AxiosResponse<Response>> => {
  const formData = new FormData();
  formData.append("session_id", String(sessionId));
  formData.append("question_id", String(questionId));
  formData.append("audio", audioBlob, "answer.webm");
  return api.post("/responses/audio", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const evaluateResponse = (
  responseId: number
): Promise<AxiosResponse<Evaluation>> => api.post(`/evaluations/${responseId}`);

export const getFollowUp = (
  responseId: number
): Promise<AxiosResponse<FollowUp>> => api.post(`/responses/${responseId}/follow-up`);

export default api;

export const getQuestion = (questionId: number): Promise<AxiosResponse<Question>> =>
  api.get(`/questions/${questionId}`);
