import { motion } from 'framer-motion';
import { Sparkles, Star, TrendingUp, Award, ChevronRight } from 'lucide-react';
import type { Candidate } from '../../types';
import { useAppStore } from '../../hooks/useStore';
// ... rest same

interface CandidateCardProps {
  candidate: Candidate
  index: number
}

export default function CandidateCard({ candidate, index }: CandidateCardProps) {
  const { analyzeCandidate } = useAppStore()

  const handleClick = () => {
    analyzeCandidate(candidate.id)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.05 }}
      whileHover={{ scale: 1.02, y: -3 }}
      onClick={handleClick}
      className={`glass rounded-xl p-5 cursor-pointer transition-all duration-300 hover:shadow-2xl group relative overflow-hidden ${
        candidate.hidden_genius ? 'border-genius-500/40' : 'border-white/10'
      }`}
    >
      {/* Hidden Genius Glow Effect */}
      {candidate.hidden_genius && (
        <div className="absolute inset-0 bg-gradient-to-r from-genius-500/5 to-talent-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
      )}

      {/* Rank Badge */}
      <div className="absolute top-4 right-4">
        <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm ${
          candidate.rank <= 3 
            ? 'bg-gradient-to-br from-yellow-400 to-orange-500 text-white' 
            : 'bg-white/10 text-white/60'
        }`}>
          #{candidate.rank}
        </div>
      </div>

      <div className="flex items-start gap-4">
        {/* Avatar */}
        <div className="relative">
          <img
            src={candidate.avatar}
            alt={candidate.name}
            className="w-14 h-14 rounded-xl bg-white/10"
          />
          {candidate.hidden_genius && (
            <motion.div
              animate={{ rotate: [0, 10, -10, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="absolute -top-2 -right-2"
            >
              <Sparkles className="w-5 h-5 text-genius-400" />
            </motion.div>
          )}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-white font-semibold text-lg">{candidate.name}</h3>
            {candidate.hidden_genius && (
              <motion.span
                animate={{ scale: [1, 1.1, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="px-2 py-0.5 rounded-full bg-genius-500/20 text-genius-400 text-xs font-bold border border-genius-500/30"
              >
                HIDDEN GENIUS
              </motion.span>
            )}
          </div>
          <p className="text-white/40 text-sm mb-2">{candidate.current_role || 'No Role'} • {candidate.domain || 'No Domain'} • {candidate.experience_years} years</p>
          
          {/* Skills */}
          <div className="flex flex-wrap gap-1.5 mb-3">
            {candidate.skills.slice(0, 5).map((skill) => (
              <span key={skill} className="px-2 py-0.5 rounded-md bg-white/5 text-white/60 text-xs border border-white/10">
                {skill}
              </span>
            ))}
            {candidate.skills.length > 5 && (
              <span className="px-2 py-0.5 rounded-md bg-white/5 text-white/40 text-xs">
                +{candidate.skills.length - 5}
              </span>
            )}
          </div>

          {/* Scores */}
          <div className="grid grid-cols-3 gap-2">
            <ScoreBadge 
              icon={Star} 
              label="Current Fit" 
              score={Math.round(candidate.current_fit_score * 100)} 
              color="text-talent-400" 
            />
            <ScoreBadge 
              icon={TrendingUp} 
              label="Future Potential" 
              score={Math.round(candidate.future_potential_score * 100)} 
              color="text-genius-400" 
            />
            <ScoreBadge 
              icon={Award} 
              label="True Talent" 
              score={Math.round(candidate.true_talent_score * 100)} 
              color="text-success" 
              highlight
            />
          </div>
        </div>

        {/* Arrow */}
        <ChevronRight className="w-5 h-5 text-white/20 group-hover:text-white/60 transition-colors self-center" />
      </div>
    </motion.div>
  )
}

function ScoreBadge({ 
  icon: Icon, 
  label, 
  score, 
  color, 
  highlight = false 
}: { 
  icon: any
  label: string
  score: number
  color: string
  highlight?: boolean 
}) {
  return (
    <div className={`p-2 rounded-lg ${highlight ? 'bg-white/10' : 'bg-white/5'}`}>
      <div className="flex items-center gap-1 mb-1">
        <Icon className={`w-3 h-3 ${color}`} />
        <span className="text-white/40 text-xs">{label}</span>
      </div>
      <div className={`text-lg font-bold ${color}`}>{score}</div>
    </div>
  )
}