import axios, { type AxiosResponse } from "axios";
import type { Session, Question, Response, Evaluation, FollowUp } from "./types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: { "Content-Type": "application/json" },
});


export const createSession = (
  role: string,
  candidateName: string | null
): Promise<AxiosResponse<Session>> =>
  api.post("/sessions/", { role, candidate_name: candidateName });

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