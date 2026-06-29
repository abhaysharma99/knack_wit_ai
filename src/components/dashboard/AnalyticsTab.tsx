import { motion } from 'framer-motion';
import { BarChart3, PieChart } from 'lucide-react';
import { useAppStore } from '../../hooks/useStore';
import ScoreDistribution from '../charts/ScoreDistribution';
import GlowingCard from '../animations/GlowingCard';
// ... rest same

export default function AnalyticsTab() {
  const { dashboardStats, candidates } = useAppStore()

  const topSkills = dashboardStats.top_skills
  const maxSkillCount = topSkills.length > 0 ? Math.max(...topSkills.map((s) => s.count)) : 1
  const hiddenGeniusCandidates = candidates.filter((c) => c.hidden_genius)
  const avgFuturePotential =
    hiddenGeniusCandidates.length > 0
      ? Math.round(
          (hiddenGeniusCandidates.reduce((acc, c) => acc + c.future_potential_score, 0) /
            hiddenGeniusCandidates.length) *
            100,
        )
      : 0

  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
        <BarChart3 className="w-6 h-6 text-talent-400" />
        Analytics Dashboard
      </h2>

      <div className="grid grid-cols-2 gap-6">
        {/* Score Distribution */}
        <GlowingCard glowColor="blue">
          <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
            <PieChart className="w-4 h-4 text-talent-400" />
            True Talent Score Distribution
          </h3>
          <ScoreDistribution data={dashboardStats.score_distribution} />
        </GlowingCard>

        {/* Top Skills */}
        <GlowingCard glowColor="purple">
          <h3 className="text-white font-semibold mb-4">Top Skills in Candidate Pool</h3>
          <div className="space-y-3">
            {topSkills.map((skill, index) => (
              <motion.div
                key={skill.skill}
                initial={{ width: 0 }}
                animate={{ width: '100%' }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center gap-3"
              >
                <span className="text-white/60 text-sm w-24">{skill.skill}</span>
                <div className="flex-1 h-3 rounded-full bg-white/10 overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(skill.count / maxSkillCount) * 100}%` }}
                    transition={{ duration: 1, delay: index * 0.1 }}
                    className="h-full rounded-full bg-gradient-to-r from-talent-500 to-genius-500"
                  />
                </div>
                <span className="text-white/40 text-sm w-12 text-right">{skill.count}</span>
              </motion.div>
            ))}
          </div>
        </GlowingCard>

        {/* Hidden Genius Stats */}
        <GlowingCard glowColor="purple">
          <h3 className="text-white font-semibold mb-4">Hidden Genius Insights</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-genius-500/10 border border-genius-500/20">
              <div className="text-3xl font-bold text-genius-400 mb-1">
                {dashboardStats.total_candidates > 0
                  ? ((dashboardStats.hidden_geniuses / dashboardStats.total_candidates) * 100).toFixed(1)
                  : '0'}%
              </div>
              <div className="text-white/50 text-sm">Of candidates are Hidden Geniuses</div>
            </div>
            <div className="p-4 rounded-xl bg-talent-500/10 border border-talent-500/20">
              <div className="text-3xl font-bold text-talent-400 mb-1">
                {avgFuturePotential}
              </div>
              <div className="text-white/50 text-sm">Avg Future Potential Score</div>
            </div>
          </div>
        </GlowingCard>

        {/* Processing Stats */}
        <GlowingCard glowColor="green">
          <h3 className="text-white font-semibold mb-4">AI Processing Stats</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-white/60">Resumes Processed</span>
              <span className="text-white font-bold">{dashboardStats.total_candidates}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-white/60">Processing Time</span>
              <span className="text-success font-bold">{dashboardStats.processing_time_ms}ms</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-white/60">Resumes/Second</span>
              <span className="text-talent-400 font-bold">
                {dashboardStats.processing_time_ms > 0
                  ? Math.round(
                      dashboardStats.total_candidates / (dashboardStats.processing_time_ms / 1000),
                    )
                  : '—'}
              </span>
            </div>
          </div>
        </GlowingCard>
      </div>
    </div>
  )
}