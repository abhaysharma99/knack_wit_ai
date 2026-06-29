import { motion, AnimatePresence } from 'framer-motion';
import { useAppStore } from '../../hooks/useStore';
import CandidateCard from './CandidateCard';
// ... rest same

export default function CandidateList() {
  const { filteredCandidates, activeTab } = useAppStore()
  const candidates = filteredCandidates()

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-white">
          {activeTab === 'hidden-genius' ? 'Hidden Geniuses' : 'All Candidates'}
          <span className="ml-2 text-white/40 text-sm font-normal">
            ({candidates.length} results)
          </span>
        </h2>
      </div>

      <div className="space-y-3">
        <AnimatePresence mode="popLayout">
          {candidates.map((candidate, index) => (
            <CandidateCard 
              key={candidate.id} 
              candidate={candidate} 
              index={index}
            />
          ))}
        </AnimatePresence>
      </div>

      {candidates.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-20 text-white/40"
        >
          No candidates found matching your criteria
        </motion.div>
      )}
    </div>
  )
}