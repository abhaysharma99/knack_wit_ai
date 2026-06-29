import axios from 'axios';
import type { JobDescription } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
});

export interface MatchResult {
  rank: number;
  file_id: string;
  candidate_id?: string | null;
  faiss_score: number;
  rerank_score: number;
  fit_score?: number | null;
  final_score?: number | null;
  candidate_name?: string | null;
  file_path?: string | null;
}

export interface MatchResponse {
  total_indexed: number;
  results: MatchResult[];
}

export interface GrowthFeatures {
  growth_velocity: number;
  consistency: number;
  expansion_rate: number;
  complexity_growth: number;
}

export interface AnalysisResult {
  candidate_id: string;
  candidate_name?: string | null;
  domain?: string | null;
  seniority?: string | null;
  current_fit_score?: number | null;
  growth_features: GrowthFeatures;
  future_potential: number;
  true_talent_score: number;
  hidden_genius_flag: boolean;
  reasons: string[];
  strengths: string[];
  gaps: string[];
}

export interface CandidateDetails {
  id: string;
  file_id: string;
  name?: string | null;
  email?: string | null;
  phone?: string | null;
  current_role?: string | null;
  domain?: string | null;
  seniority?: string | null;
  total_experience_years?: number | null;
  skills: { name: string; category?: string | null }[];
  projects: {
    title?: string | null;
    description?: string | null;
    technologies?: string | null;
  }[];
}

export interface FileUploadResult {
  file_id: string;
  task_id: string;
  filename?: string | null;
  status: string;
}

export interface ProcessFilesResponse {
  total_submitted: number;
  total_failed: number;
  submitted: FileUploadResult[];
  failed: { filename?: string | null; error: string }[];
}

export interface TaskStatusEntry {
  task_id: string;
  status: string;
  result?: unknown;
  error?: string;
}

export interface BulkTaskStatusResponse {
  total: number;
  done: number;
  failed: number;
  pending: number;
  tasks: TaskStatusEntry[];
}

export interface ParsedJD {
  role: string;
  required_skills: string[];
  preferred_skills: string[];
  experience_years?: number | null;
  domain?: string | null;
  seniority?: string | null;
}

function toJobDescription(parsed: ParsedJD): JobDescription {
  return {
    id: `jd-${Date.now()}`,
    role: parsed.role,
    required_skills: parsed.required_skills ?? [],
    preferred_skills: parsed.preferred_skills ?? [],
    experience_years: parsed.experience_years ?? 0,
    domain: parsed.domain ?? '',
    seniority: parsed.seniority ?? '',
    description: '',
  };
}

export const apiService = {
  uploadResumes: async (files: File[]): Promise<ProcessFilesResponse> => {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    const response = await api.post<ProcessFilesResponse>('/ingest/process-files', formData);
    return response.data;
  },

  pollTaskStatus: async (
    taskIds: string[],
    onProgress?: (done: number, total: number) => void,
    intervalMs = 1500,
    maxAttempts = 120,
  ): Promise<BulkTaskStatusResponse> => {
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      const response = await api.post<BulkTaskStatusResponse>('/ingest/tasks-status', taskIds);
      const { done, total, pending } = response.data;
      onProgress?.(done, total);
      if (pending === 0) return response.data;
      await new Promise((r) => setTimeout(r, intervalMs));
    }
    throw new Error('Resume processing timed out. Try again or check the backend worker.');
  },

  parseJDFromFile: async (file: File): Promise<JobDescription> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post<ParsedJD>('/ingest/parse-jd', formData);
    return toJobDescription(response.data);
  },

  parseJDFromText: async (text: string): Promise<JobDescription> => {
    const response = await api.post<ParsedJD>('/ingest/parse-jd-text', { text });
    return toJobDescription(response.data);
  },

  searchCandidates: async (jd: JobDescription, topN = 20): Promise<MatchResponse> => {
    const payload = {
      jd: {
        role: jd.role,
        required_skills: jd.required_skills,
        preferred_skills: jd.preferred_skills,
        experience_years: jd.experience_years,
        domain: jd.domain || null,
        seniority: jd.seniority || null,
      },
      top_n: topN,
    };
    const response = await api.post<MatchResponse>('/match/search-candidates', payload);
    return response.data;
  },

  getCandidateDetails: async (candidateId: string): Promise<CandidateDetails> => {
    const response = await api.get<CandidateDetails>(`/match/candidates/${candidateId}`);
    return response.data;
  },

  getCandidateAnalysis: async (
    candidateId: string,
    currentFit?: number,
  ): Promise<AnalysisResult> => {
    const params = currentFit != null ? { current_fit: currentFit } : {};
    const response = await api.get<AnalysisResult>(`/candidate/${candidateId}/analysis`, {
      params,
    });
    return response.data;
  },

  listCandidates: async () => {
    const response = await api.get('/match/candidates');
    return response.data;
  },
};
