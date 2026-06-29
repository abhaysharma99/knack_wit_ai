
export interface Candidate {
  id: string; // backend: candidate_id
  name: string;
  email: string;
  phone?: string;
  avatar: string; // keep for UI
  domain: string;
  seniority: string;
  current_role: string;
  experience_years: number;
  skills: string[];
  projects: Project[];
  
  // Scores
  current_fit_score: number;
  future_potential_score: number;
  true_talent_score: number;
  hidden_genius: boolean;
  
  // Growth Features (Phase 3)
  growth_velocity: number;
  learning_consistency: number;
  skill_expansion_rate: number;
  project_complexity_growth: number;
  
  // Ranking
  rank: number;
  
  // Explanability (Phase 3)
  reasons: string[];
  strengths: string[];
  gaps: string[];
}

export interface Project {
  id: string; // we can use title as id if needed
  title: string;
  description: string;
  complexity: number;
  year: number;
  technologies: string[];
}

// Retain JobDescription structure

export interface JobDescription {
  id: string;
  role: string;
  required_skills: string[];
  preferred_skills: string[];
  experience_years: number;
  domain: string;
  seniority: string;
  description: string;
}

export interface DashboardStats {
  total_candidates: number;
  hidden_geniuses: number;
  avg_true_talent_score: number;
  processing_time_ms: number;
  top_skills: { skill: string; count: number }[];
  score_distribution: { range: string; count: number }[];
}