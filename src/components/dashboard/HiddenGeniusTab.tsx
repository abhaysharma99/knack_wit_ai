import { motion } from 'framer-motion';
import { Sparkles, TrendingUp, Zap } from 'lucide-react';
import { useAppStore } from '../../hooks/useStore';
import CandidateCard from '../candidate/CandidateCard';
// ... rest same

export default function HiddenGeniusTab() {
  const { hiddenGeniusCandidates } = useAppStore()
  const geniuses = hiddenGeniusCandidates()

  return (
    <div>
      {/* Hero Banner */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6 p-6 rounded-2xl bg-gradient-to-r from-genius-900/50 via-genius-800/30 to-talent-900/50 border border-genius-500/30 relative overflow-hidden"
      >
        <div className="absolute inset-0 bg-gradient-to-r from-genius-500/10 to-transparent" />
        <div className="relative flex items-center gap-4">
          <motion.div
            animate={{ rotate: [0, 10, -10, 0] }}
            transition={{ duration: 4, repeat: Infinity }}
            className="w-16 h-16 rounded-2xl bg-genius-500/20 flex items-center justify-center border border-genius-500/30"
          >
            <Sparkles className="w-8 h-8 text-genius-400" />
          </motion.div>
          <div>
            <h2 className="text-2xl font-bold text-white mb-1">Hidden Geniuses Discovered</h2>
            <p className="text-white/60">
              These candidates might not have the best resumes today, but their growth trajectory predicts exceptional future performance.
            </p>
          </div>
          <div className="ml-auto flex items-center gap-2 px-4 py-2 rounded-xl bg-genius-500/20 border border-genius-500/30">
            <Zap className="w-5 h-5 text-genius-400" />
            <span className="text-genius-400 font-bold text-xl">{geniuses.length}</span>
            <span className="text-white/50 text-sm">Found</span>
          </div>
        </div>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="glass rounded-xl p-4 border border-genius-500/20"
        >
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-4 h-4 text-genius-400" />
            <span className="text-white/50 text-sm">Avg Growth Velocity</span>
          </div>
          <div className="text-2xl font-bold text-genius-400">
            {(geniuses.reduce((acc, g) => acc + g.growth_velocity, 0) / geniuses.length).toFixed(1)}
          </div>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="glass rounded-xl p-4 border border-genius-500/20"
        >
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-4 h-4 text-genius-400" />
            <span className="text-white/50 text-sm">Avg Future Potential</span>
          </div>
          <div className="text-2xl font-bold text-genius-400">
            {Math.round(geniuses.reduce((acc, g) => acc + g.future_potential_score, 0) / geniuses.length)}
          </div>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="glass rounded-xl p-4 border border-genius-500/20"
        >
          <div className="flex items-center gap-2 mb-2">
            <Zap className="w-4 h-4 text-genius-400" />
            <span className="text-white/50 text-sm">Top True Talent</span>
          </div>
          <div className="text-2xl font-bold text-genius-400">
            {Math.max(...geniuses.map(g => g.true_talent_score))}
          </div>
        </motion.div>
      </div>

      {/* Candidate List */}
      <div className="space-y-3">
        {geniuses.map((candidate, index) => (
          <CandidateCard key={candidate.id} candidate={candidate} index={index} />
        ))}
      </div>
    </div>
  )
}