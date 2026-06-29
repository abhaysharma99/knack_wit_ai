import { motion } from 'framer-motion';
import { Users, Sparkles, TrendingUp, Clock } from 'lucide-react';
import { useAppStore } from '../../hooks/useStore';
import AnimatedCounter from '../animations/AnimatedCounter';
import GlowingCard from '../animations/GlowingCard';
// ... rest same

export default function StatsCards() {
  const { dashboardStats } = useAppStore()

  const stats = [
    {
      label: 'Total Candidates',
      value: dashboardStats.total_candidates,
      suffix: '',
      icon: Users,
      color: 'blue' as const,
      iconColor: 'text-talent-400',
      bgColor: 'bg-talent-500/10',
    },
    {
      label: 'Hidden Geniuses',
      value: dashboardStats.hidden_geniuses,
      suffix: '',
      icon: Sparkles,
      color: 'purple' as const,
      iconColor: 'text-genius-400',
      bgColor: 'bg-genius-500/10',
    },
    {
      label: 'Avg True Talent Score',
      value: Math.round(dashboardStats.avg_true_talent_score),
      suffix: '/100',
      icon: TrendingUp,
      color: 'green' as const,
      iconColor: 'text-success',
      bgColor: 'bg-success/10',
    },
    {
      label: 'Processing Time',
      value: dashboardStats.processing_time_ms,
      suffix: 'ms',
      icon: Clock,
      color: 'orange' as const,
      iconColor: 'text-warning',
      bgColor: 'bg-warning/10',
    },
  ]

  return (
    <div className="grid grid-cols-4 gap-4 mb-6">
      {stats.map((stat, index) => (
        <GlowingCard key={stat.label} glowColor={stat.color} delay={index * 0.1}>
          <div className="flex items-center justify-between mb-4">
            <div className={`p-3 rounded-xl ${stat.bgColor}`}>
              <stat.icon className={`w-5 h-5 ${stat.iconColor}`} />
            </div>
            <motion.div
              className="text-xs text-white/40"
              animate={{ opacity: [0.5, 1, 0.5] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              Live
            </motion.div>
          </div>
          <div className="text-3xl font-bold text-white mb-1">
            <AnimatedCounter 
              end={stat.value} 
              suffix={stat.suffix}
              className="text-white"
            />
          </div>
          <div className="text-sm text-white/50">{stat.label}</div>
        </GlowingCard>
      ))}
    </div>
  )
}