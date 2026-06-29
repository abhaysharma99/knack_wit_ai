import { motion } from 'framer-motion';
import { Search, Bell, Filter } from 'lucide-react';
import { useAppStore } from '../../hooks/useStore';

export default function TopBar() {
  const { searchQuery, setSearchQuery, sortBy, setSortBy } = useAppStore()

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="h-16 glass-strong border-b border-white/10 flex items-center justify-between px-6 sticky top-0 z-40"
    >
      {/* Search */}
      <div className="flex items-center gap-4 flex-1">
        <div className="relative w-96">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
          <input
            type="text"
            placeholder="Search candidates, skills, colleges..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-white/30 focus:outline-none focus:border-talent-500/50 focus:ring-2 focus:ring-talent-500/20 transition-all"
          />
        </div>
      </div>

      {/* Sort & Actions */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/5 border border-white/10">
          <Filter className="w-4 h-4 text-white/40" />
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="bg-transparent text-white text-sm focus:outline-none"
          >
            <option value="rank" className="bg-gray-900">Rank</option>
            <option value="true_talent_score" className="bg-gray-900">True Talent Score</option>
            <option value="current_fit_score" className="bg-gray-900">Current Fit</option>
            <option value="future_potential_score" className="bg-gray-900">Future Potential</option>
          </select>
        </div>

        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          className="relative p-2 rounded-lg bg-white/5 border border-white/10"
        >
          <Bell className="w-5 h-5 text-white/60" />
          <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-genius-500 animate-pulse" />
        </motion.button>
      </div>
    </motion.header>
  )
}