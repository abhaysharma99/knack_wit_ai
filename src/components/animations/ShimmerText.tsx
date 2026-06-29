import { motion } from 'framer-motion'

interface ShimmerTextProps {
  text: string
  className?: string
}

export default function ShimmerText({ text, className }: ShimmerTextProps) {
  return (
    <motion.span
      className={`relative inline-block ${className}`}
      initial={{ backgroundPosition: '-200% center' }}
      animate={{ backgroundPosition: '200% center' }}
      transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
      style={{
        background: 'linear-gradient(90deg, #0ea5e9, #d946ef, #0ea5e9)',
        backgroundSize: '200% auto',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        backgroundClip: 'text',
      }}
    >
      {text}
    </motion.span>
  )
}