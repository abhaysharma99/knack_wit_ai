import { motion, AnimatePresence } from 'framer-motion';
import { X, Sparkles, TrendingUp, Star, Award, AlertTriangle, CheckCircle, Lightbulb } from 'lucide-react';
import { useAppStore } from '../../hooks/useStore';
import ScoreRadar from '../charts/ScoreRadar';
// ... rest same

export default function AnalysisModal() {
  const { selectedCandidate, showAnalysisModal, setShowAnalysisModal } = useAppStore()

  if (!selectedCandidate || !showAnalysisModal) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[100] flex items-center justify-center p-4"
        onClick={() => setShowAnalysisModal(false)}
      >
        {/* Backdrop */}
        <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" />

        {/* Modal */}
        <motion.div
          initial={{ scale: 0.9, opacity: 0, y: 20 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.9, opacity: 0, y: 20 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          onClick={(e) => e.stopPropagation()}
          className="relative w-full max-w-5xl max-h-[90vh] overflow-y-auto glass-strong rounded-2xl border border-white/20 shadow-2xl"
        >
          {/* Close Button */}
          <button
            onClick={() => setShowAnalysisModal(false)}
            className="absolute top-4 right-4 p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors z-10"
          >
            <X className="w-5 h-5 text-white/60" />
          </button>

          {/* Header */}
          <div className="p-6 border-b border-white/10">
            <div className="flex items-center gap-4">
              <img
                src={selectedCandidate.avatar}
                alt={selectedCandidate.name}
                className="w-16 h-16 rounded-xl bg-white/10"
              />
              <div>
                <div className="flex items-center gap-3">
                  <h2 className="text-2xl font-bold text-white">{selectedCandidate.name}</h2>
                  {selectedCandidate.hidden_genius && (
                    <motion.span
                      animate={{ scale: [1, 1.1, 1] }}
                      transition={{ duration: 2, repeat: Infinity }}
                      className="px-3 py-1 rounded-full bg-genius-500/20 text-genius-400 text-sm font-bold border border-genius-500/30 flex items-center gap-1"
                    >
                      <Sparkles className="w-4 h-4" />
                      HIDDEN GENIUS
                    </motion.span>
                  )}
                </div>
                <p className="text-white/50">{selectedCandidate.domain || 'Unknown Domain'} • {selectedCandidate.seniority || 'Unknown Seniority'} • {selectedCandidate.experience_years} years exp</p>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 grid grid-cols-2 gap-6">
            {/* Left Column */}
            <div className="space-y-6">
              {/* Scores */}
              <div className="grid grid-cols-3 gap-3">
                <ScoreCard
                  icon={Star}
                  label="Current Fit"
                  score={Math.round(selectedCandidate.current_fit_score * 100)}
                  color="text-talent-400"
                  bgColor="bg-talent-500/10"
                />
                <ScoreCard
                  icon={TrendingUp}
                  label="Future Potential"
                  score={Math.round(selectedCandidate.future_potential_score * 100)}
                  color="text-genius-400"
                  bgColor="bg-genius-500/10"
                />
                <ScoreCard
                  icon={Award}
                  label="True Talent"
                  score={Math.round(selectedCandidate.true_talent_score * 100)}
                  color="text-success"
                  bgColor="bg-success/10"
                  large
                />
              </div>

              {/* Radar Chart */}
              <div className="glass rounded-xl p-4">
                <h3 className="text-white font-semibold mb-4">Skill Analysis</h3>
                <ScoreRadar
                  currentFit={selectedCandidate.current_fit_score * 100}
                  futurePotential={selectedCandidate.future_potential_score * 100}
                  growthVelocity={selectedCandidate.growth_velocity * 100}
                  learningConsistency={selectedCandidate.learning_consistency * 100}
                  skillExpansion={selectedCandidate.skill_expansion_rate * 100}
                  projectComplexity={selectedCandidate.project_complexity_growth * 100}
                />
              </div>

            </div>

            {/* Right Column */}
            <div className="space-y-6">
              {/* AI Analysis Reasons */}
              <div className="glass rounded-xl p-4">
                <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
                  <Lightbulb className="w-4 h-4 text-genius-400" />
                  AI Analysis Reasons
                </h3>
                <ul className="space-y-2">
                  {selectedCandidate.reasons?.map((reason, i) => (
                    <li key={i} className="text-white/70 text-sm flex items-start gap-2">
                      <span className="text-talent-400 mt-1">•</span>
                      <span>{reason}</span>
                    </li>
                  ))}
                  {(!selectedCandidate.reasons || selectedCandidate.reasons.length === 0) && (
                    <li className="text-white/40 text-sm">No specific reasons generated.</li>
                  )}
                </ul>
              </div>

              {/* Skills */}
              <div className="glass rounded-xl p-4">
                <h3 className="text-white font-semibold mb-3">Skills</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedCandidate.skills.map((skill) => (
                    <span key={skill} className="px-3 py-1 rounded-lg bg-white/5 text-white/70 text-sm border border-white/10">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>

              {/* Projects */}
              <div className="glass rounded-xl p-4">
                <h3 className="text-white font-semibold mb-3">Projects</h3>
                <div className="space-y-3">
                  {selectedCandidate.projects.map((project) => (
                    <div key={project.id} className="p-3 rounded-lg bg-white/5 border border-white/10">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-white font-medium text-sm">{project.title}</span>
                        <span className="text-white/40 text-xs">{project.year}</span>
                      </div>
                      <p className="text-white/50 text-xs mb-2">{project.description}</p>
                      <div className="flex items-center gap-1">
                        {[...Array(5)].map((_, i) => (
                          <div
                            key={i}
                            className={`w-2 h-2 rounded-full ${
                              i < project.complexity ? 'bg-talent-400' : 'bg-white/10'
                            }`}
                          />
                        ))}
                        <span className="ml-2 text-white/40 text-xs">Complexity</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Strengths & Gaps Analysis */}
              <div className="grid grid-cols-2 gap-4">
                {/* Strengths */}
                <div className="glass rounded-xl p-4">
                  <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-success" />
                    Strengths
                  </h3>
                  <ul className="space-y-2">
                    {selectedCandidate.strengths?.map((strength, i) => (
                      <li key={i} className="text-white/70 text-sm flex items-start gap-2">
                        <span className="text-success mt-1">•</span>
                        <span>{strength}</span>
                      </li>
                    ))}
                    {(!selectedCandidate.strengths || selectedCandidate.strengths.length === 0) && (
                      <li className="text-white/40 text-sm">No notable strengths identified.</li>
                    )}
                  </ul>
                </div>

                {/* Gaps */}
                <div className="glass rounded-xl p-4">
                  <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-warning" />
                    Skill Gaps
                  </h3>
                  <ul className="space-y-2">
                    {selectedCandidate.gaps?.map((gap, i) => (
                      <li key={i} className="text-white/70 text-sm flex items-start gap-2">
                        <span className="text-warning mt-1">•</span>
                        <span>{gap}</span>
                      </li>
                    ))}
                    {(!selectedCandidate.gaps || selectedCandidate.gaps.length === 0) && (
                      <li className="text-white/40 text-sm">No notable gaps identified.</li>
                    )}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

function ScoreCard({ 
  icon: Icon, 
  label, 
  score, 
  color, 
  bgColor, 
  large = false 
}: { 
  icon: any
  label: string
  score: number
  color: string
  bgColor: string
  large?: boolean 
}) {
  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      className={`${bgColor} rounded-xl p-4 border border-white/10`}
    >
      <div className="flex items-center gap-2 mb-2">
        <Icon className={`w-4 h-4 ${color}`} />
        <span className="text-white/50 text-xs">{label}</span>
      </div>
      <div className={`font-bold ${color} ${large ? 'text-3xl' : 'text-2xl'}`}>
        {score}
      </div>
    </motion.div>
  )
}