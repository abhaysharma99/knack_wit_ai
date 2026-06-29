import { create } from 'zustand';
import type { Candidate, JobDescription, DashboardStats } from '../types';
import { apiService, type MatchResult } from '../lib/api';

const initialDashboardStats: DashboardStats = {
  total_candidates: 0,
  hidden_geniuses: 0,
  avg_true_talent_score: 0,
  processing_time_ms: 0,
  top_skills: [],
  score_distribution: [],
};

function computeDashboardStats(candidates: Candidate[], processingTimeMs: number): DashboardStats {
  const total = candidates.length;
  const hiddenGeniuses = candidates.filter((c) => c.hidden_genius).length;
  const avgScore =
    total > 0
      ? candidates.reduce((sum, c) => sum + c.true_talent_score, 0) / total
      : 0;

  const skillCounts: Record<string, number> = {};
  candidates.forEach((c) => {
    c.skills.forEach((skill) => {
      skillCounts[skill] = (skillCounts[skill] || 0) + 1;
    });
  });
  const topSkills = Object.entries(skillCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)
    .map(([skill, count]) => ({ skill, count }));

  const buckets = [
    { range: '0-20', min: 0, max: 0.2 },
    { range: '21-40', min: 0.21, max: 0.4 },
    { range: '41-60', min: 0.41, max: 0.6 },
    { range: '61-80', min: 0.61, max: 0.8 },
    { range: '81-100', min: 0.81, max: 1 },
  ];
  const scoreDistribution = buckets.map(({ range, min, max }) => ({
    range,
    count: candidates.filter((c) => c.true_talent_score >= min && c.true_talent_score <= max).length,
  }));

  return {
    total_candidates: total,
    hidden_geniuses: hiddenGeniuses,
    avg_true_talent_score: avgScore * 100,
    processing_time_ms: processingTimeMs,
    top_skills: topSkills,
    score_distribution: scoreDistribution,
  };
}

function mapMatchResultToCandidate(r: MatchResult): Candidate | null {
  const id = r.candidate_id || r.file_id;
  if (!id) return null;

  const fitScore = r.final_score ?? r.fit_score ?? 0;

  return {
    id,
    name: r.candidate_name || 'Unknown Candidate',
    email: '',
    avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${id}`,
    domain: '',
    seniority: '',
    current_role: '',
    experience_years: 0,
    skills: [],
    projects: [],
    current_fit_score: fitScore,
    future_potential_score: 0,
    true_talent_score: fitScore,
    hidden_genius: false,
    growth_velocity: 0,
    learning_consistency: 0,
    skill_expansion_rate: 0,
    project_complexity_growth: 0,
    rank: r.rank,
    reasons: [],
    strengths: [],
    gaps: [],
  };
}

function mapAnalysisToCandidate(base: Candidate, analysis: Awaited<ReturnType<typeof apiService.getCandidateAnalysis>>, details?: Awaited<ReturnType<typeof apiService.getCandidateDetails>>): Candidate {
  return {
    ...base,
    name: analysis.candidate_name || details?.name || base.name,
    email: details?.email || base.email,
    phone: details?.phone || base.phone,
    domain: analysis.domain || details?.domain || base.domain,
    seniority: analysis.seniority || details?.seniority || base.seniority,
    current_role: details?.current_role || base.current_role,
    experience_years: details?.total_experience_years ?? base.experience_years,
    skills: details?.skills?.map((s) => s.name) ?? base.skills,
    projects:
      details?.projects?.map((p, i) => ({
        id: `p-${i}`,
        title: p.title || 'Project',
        description: p.description || '',
        complexity: 3,
        year: new Date().getFullYear(),
        technologies: p.technologies ? p.technologies.split(',').map((t) => t.trim()) : [],
      })) ?? base.projects,
    current_fit_score: analysis.current_fit_score ?? base.current_fit_score,
    future_potential_score: analysis.future_potential,
    true_talent_score: analysis.true_talent_score,
    hidden_genius: analysis.hidden_genius_flag,
    growth_velocity: analysis.growth_features.growth_velocity,
    learning_consistency: analysis.growth_features.consistency,
    skill_expansion_rate: analysis.growth_features.expansion_rate,
    project_complexity_growth: analysis.growth_features.complexity_growth,
    reasons: analysis.reasons,
    strengths: analysis.strengths,
    gaps: analysis.gaps,
  };
}

interface AppState {
  candidates: Candidate[];
  jobDescription: JobDescription | null;
  selectedCandidate: Candidate | null;
  dashboardStats: DashboardStats;
  activeTab: 'all' | 'hidden-genius' | 'analysis' | 'dashboard';
  isLoading: boolean;
  searchQuery: string;
  sortBy: 'rank' | 'true_talent_score' | 'current_fit_score' | 'future_potential_score';
  showAnalysisModal: boolean;
  showUploadModal: boolean;
  error: string | null;
  uploadProgress: { done: number; total: number } | null;

  setCandidates: (candidates: Candidate[]) => void;
  setJobDescription: (jd: JobDescription) => void;
  setSelectedCandidate: (candidate: Candidate | null) => void;
  setActiveTab: (tab: 'all' | 'hidden-genius' | 'analysis' | 'dashboard') => void;
  setIsLoading: (loading: boolean) => void;
  setSearchQuery: (query: string) => void;
  setSortBy: (sort: 'rank' | 'true_talent_score' | 'current_fit_score' | 'future_potential_score') => void;
  setShowAnalysisModal: (show: boolean) => void;
  setShowUploadModal: (show: boolean) => void;
  setError: (error: string | null) => void;

  fetchCandidates: (jd: JobDescription) => Promise<void>;
  analyzeCandidate: (candidateId: string) => Promise<void>;
  uploadFiles: (files: File[]) => Promise<void>;
  parseAndSearch: (jdText?: string, jdFile?: File) => Promise<void>;
  enrichCandidatesWithAnalysis: (candidates: Candidate[]) => Promise<Candidate[]>;

  filteredCandidates: () => Candidate[];
  hiddenGeniusCandidates: () => Candidate[];
}

export const useAppStore = create<AppState>((set, get) => ({
  candidates: [],
  jobDescription: null,
  selectedCandidate: null,
  dashboardStats: initialDashboardStats,
  activeTab: 'dashboard',
  isLoading: false,
  searchQuery: '',
  sortBy: 'rank',
  showAnalysisModal: false,
  showUploadModal: false,
  error: null,
  uploadProgress: null,

  setCandidates: (candidates) => set({ candidates }),
  setJobDescription: (jobDescription) => set({ jobDescription }),
  setSelectedCandidate: (selectedCandidate) => set({ selectedCandidate }),
  setActiveTab: (activeTab) => set({ activeTab }),
  setIsLoading: (isLoading) => set({ isLoading }),
  setSearchQuery: (searchQuery) => set({ searchQuery }),
  setSortBy: (sortBy) => set({ sortBy }),
  setShowAnalysisModal: (showAnalysisModal) => set({ showAnalysisModal }),
  setShowUploadModal: (showUploadModal) => set({ showUploadModal }),
  setError: (error) => set({ error }),

  enrichCandidatesWithAnalysis: async (candidates) => {
    const enriched = await Promise.all(
      candidates.map(async (c) => {
        try {
          const analysis = await apiService.getCandidateAnalysis(c.id, c.current_fit_score);
          return mapAnalysisToCandidate(c, analysis);
        } catch {
          return c;
        }
      }),
    );
    return enriched;
  },

  fetchCandidates: async (jd) => {
    set({ isLoading: true, error: null });
    const start = performance.now();
    try {
      const response = await apiService.searchCandidates(jd, 20);
      const mapped = response.results
        .map(mapMatchResultToCandidate)
        .filter((c): c is Candidate => c !== null);

      if (mapped.length === 0) {
        set({
          candidates: [],
          jobDescription: jd,
          isLoading: false,
          dashboardStats: computeDashboardStats([], Math.round(performance.now() - start)),
          error: response.total_indexed === 0
            ? 'No resumes indexed yet. Upload resumes first, then search.'
            : 'No matching candidates found for this job description.',
        });
        return;
      }

      const enriched = await get().enrichCandidatesWithAnalysis(mapped);
      const processingTime = Math.round(performance.now() - start);

      set({
        candidates: enriched,
        jobDescription: jd,
        isLoading: false,
        dashboardStats: computeDashboardStats(enriched, processingTime),
        activeTab: 'dashboard',
      });
    } catch (error) {
      const message = axiosErrorMessage(error, 'Failed to fetch candidates');
      console.error('Failed to fetch candidates:', error);
      set({ isLoading: false, error: message });
    }
  },

  analyzeCandidate: async (candidateId) => {
    const existing = get().candidates.find((c) => c.id === candidateId);
    if (!existing) return;

    set({ isLoading: true, error: null, selectedCandidate: existing });
    try {
      const [analysis, details] = await Promise.all([
        apiService.getCandidateAnalysis(candidateId, existing.current_fit_score),
        apiService.getCandidateDetails(candidateId),
      ]);

      const updated = mapAnalysisToCandidate(existing, analysis, details);
      const candidates = get().candidates.map((c) => (c.id === candidateId ? updated : c));

      set({
        candidates,
        selectedCandidate: updated,
        isLoading: false,
        showAnalysisModal: true,
        dashboardStats: computeDashboardStats(candidates, get().dashboardStats.processing_time_ms),
      });
    } catch (error) {
      const message = axiosErrorMessage(error, 'Failed to analyze candidate');
      console.error('Failed to analyze candidate:', error);
      set({ isLoading: false, error: message });
    }
  },

  uploadFiles: async (files) => {
    set({ isLoading: true, error: null, uploadProgress: { done: 0, total: files.length } });
    try {
      const uploadResult = await apiService.uploadResumes(files);

      if (uploadResult.total_submitted === 0) {
        throw new Error(
          uploadResult.failed[0]?.error || 'No files were submitted. Check file format (PDF or TXT).',
        );
      }

      const taskIds = uploadResult.submitted.map((s) => s.task_id);
      const status = await apiService.pollTaskStatus(taskIds, (done, total) => {
        set({ uploadProgress: { done, total } });
      });

      if (status.failed > 0) {
        set({
          error: `${status.failed} resume(s) failed to process. ${status.done} succeeded.`,
        });
      }

      set({ isLoading: false, uploadProgress: null });
    } catch (error) {
      const message = axiosErrorMessage(error, 'Failed to upload files');
      console.error('Failed to upload files:', error);
      set({ isLoading: false, uploadProgress: null, error: message });
      throw error;
    }
  },

  parseAndSearch: async (jdText, jdFile) => {
    set({ isLoading: true, error: null });
    try {
      let jd: JobDescription;
      if (jdFile) {
        jd = await apiService.parseJDFromFile(jdFile);
      } else if (jdText?.trim()) {
        jd = await apiService.parseJDFromText(jdText);
      } else {
        throw new Error('Provide a job description file or paste JD text.');
      }

      await get().fetchCandidates(jd);
    } catch (error) {
      const message = axiosErrorMessage(error, 'Failed to parse job description');
      console.error('Failed to parse and search:', error);
      set({ isLoading: false, error: message });
      throw error;
    }
  },

  filteredCandidates: () => {
    const { candidates, searchQuery, sortBy, activeTab } = get();
    let filtered = [...candidates];

    if (activeTab === 'hidden-genius') {
      filtered = filtered.filter((c) => c.hidden_genius);
    }

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (c) =>
          c.name.toLowerCase().includes(query) ||
          c.skills.some((s) => s.toLowerCase().includes(query)) ||
          (c.current_role && c.current_role.toLowerCase().includes(query)) ||
          (c.domain && c.domain.toLowerCase().includes(query)),
      );
    }

    filtered.sort((a, b) => {
      if (sortBy === 'rank') return a.rank - b.rank;
      return b[sortBy] - a[sortBy];
    });

    return filtered;
  },

  hiddenGeniusCandidates: () => get().candidates.filter((c) => c.hidden_genius),
}));

function axiosErrorMessage(error: unknown, fallback: string): string {
  if (typeof error === 'object' && error !== null && 'response' in error) {
    const resp = (error as { response?: { data?: { detail?: string } } }).response;
    if (typeof resp?.data?.detail === 'string') return resp.data.detail;
  }
  if (error instanceof Error) return error.message;
  return fallback;
}
