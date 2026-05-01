import axios, { AxiosError } from 'axios';
import { Run, AnalysisResult } from './types';

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 15000,
});

export const getRuns = async (): Promise<Run[]> => {
  const response = await api.get('/runs');
  return response.data.runs;
};

export const getRunById = async (id: string): Promise<Run> => {
  const response = await api.get(`/runs/${id}`);
  return response.data;
};

export const analyzeRun = async (id: string): Promise<AnalysisResult> => {
  try {
    const response = await api.post(`/runs/${id}/analyze`);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 429) {
      throw new Error('Gemini rate limit reached \u2014 please wait 60 seconds and try again');
    }
    throw error;
  }
};
