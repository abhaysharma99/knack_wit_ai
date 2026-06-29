export interface Candidate {
  id: string;
  name: string;
  email: string;
  avatar: string;
  college: string;
  cgpa: number;
  experience_years: number;
  skills: string[];
  projects: Project[];
  certifications: Certification[];
  current_fit_score: number;
  future_potential_score: number;
  true_talent_score: number;
  hidden_genius: boolean;
  growth_velocity: number;
  learning_consistency: number;
  skill_expansion_rate: number;
  project_complexity_growth: number;
  rank: number;
  explanation: string;
  skill_timeline: SkillTimeline[];
  skill_gap: SkillGap[];
}

export interface Project {
  id: string;
  title: string;
  description: string;
  complexity: number;
  year: number;
  technologies: string[];
}

export interface Certification {
  id: string;
  name: string;
  level: number;
  year: number;
}

export interface SkillTimeline {
  year: number;
  skill_level: number;
  skills: string[];
}

export interface SkillGap {
  skill: string;
  required: boolean;
  candidate_has: boolean;
  similarity: number;
}

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