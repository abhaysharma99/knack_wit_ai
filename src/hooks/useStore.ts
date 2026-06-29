import { create } from 'zustand';
import type { Candidate, JobDescription, DashboardStats } from '../types';
import { mockCandidates, mockJobDescription, mockDashboardStats } from '../data/mockData';

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
  
  setCandidates: (candidates: Candidate[]) => void;
  setJobDescription: (jd: JobDescription) => void;
  setSelectedCandidate: (candidate: Candidate | null) => void;
  setActiveTab: (tab: 'all' | 'hidden-genius' | 'analysis' | 'dashboard') => void;
  setIsLoading: (loading: boolean) => void;
  setSearchQuery: (query: string) => void;
  setSortBy: (sort: 'rank' | 'true_talent_score' | 'current_fit_score' | 'future_potential_score') => void;
  setShowAnalysisModal: (show: boolean) => void;
  setShowUploadModal: (show: boolean) => void;
  
  filteredCandidates: () => Candidate[];
  hiddenGeniusCandidates: () => Candidate[];
}

export const useAppStore = create<AppState>((set, get) => ({
  candidates: mockCandidates,
  jobDescription: mockJobDescription,
  selectedCandidate: null,
  dashboardStats: mockDashboardStats,
  activeTab: 'dashboard',
  isLoading: false,
  searchQuery: '',
  sortBy: 'rank',
  showAnalysisModal: false,
  showUploadModal: false,
  
  setCandidates: (candidates) => set({ candidates }),
  setJobDescription: (jobDescription) => set({ jobDescription }),
  setSelectedCandidate: (selectedCandidate) => set({ selectedCandidate }),
  setActiveTab: (activeTab) => set({ activeTab }),
  setIsLoading: (isLoading) => set({ isLoading }),
  setSearchQuery: (searchQuery) => set({ searchQuery }),
  setSortBy: (sortBy) => set({ sortBy }),
  setShowAnalysisModal: (showAnalysisModal) => set({ showAnalysisModal }),
  setShowUploadModal: (showUploadModal) => set({ showUploadModal }),
  
  filteredCandidates: () => {
    const { candidates, searchQuery, sortBy, activeTab } = get();
    let filtered = [...candidates];
    
    if (activeTab === 'hidden-genius') {
      filtered = filtered.filter(c => c.hidden_genius);
    }
    
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(c => 
        c.name.toLowerCase().includes(query) ||
        c.skills.some(s => s.toLowerCase().includes(query)) ||
        c.college.toLowerCase().includes(query)
      );
    }
    
    filtered.sort((a, b) => {
      if (sortBy === 'rank') return a.rank - b.rank;
      return b[sortBy] - a[sortBy];
    });
    
    return filtered;
  },
  
  hiddenGeniusCandidates: () => {
    return get().candidates.filter(c => c.hidden_genius);
  }
}));