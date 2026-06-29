import { motion } from 'framer-motion'
import { cn } from '../../lib/utils'

interface GlowingCardProps {
  children: React.ReactNode
  className?: string
  glowColor?: 'blue' | 'purple' | 'green' | 'orange'
  delay?: number
}

export default function GlowingCard({ 
  children, 
  className, 
  glowColor = 'blue',
  delay = 0 
}: GlowingCardProps) {
  const glowColors = {
    blue: 'hover:shadow-[0_0_30px_rgba(14,165,233,0.4)]',
    purple: 'hover:shadow-[0_0_30px_rgba(217,70,239,0.4)]',
    green: 'hover:shadow-[0_0_30px_rgba(16,185,129,0.4)]',
    orange: 'hover:shadow-[0_0_30px_rgba(245,158,11,0.4)]',
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      whileHover={{ scale: 1.02, y: -5 }}
      className={cn(
        'glass rounded-xl p-6 transition-all duration-300',
        glowColors[glowColor],
        className
      )}
    >
      {children}
    </motion.div>
  )
}