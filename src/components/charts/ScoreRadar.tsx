// @ts-nocheck
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts'
import { motion } from 'framer-motion'

interface ScoreRadarProps {
  currentFit: number
  futurePotential: number
  growthVelocity: number
  learningConsistency: number
  skillExpansion: number
  projectComplexity: number
}

export default function ScoreRadar({
  currentFit,
  futurePotential,
  growthVelocity,
  learningConsistency,
  skillExpansion,
  projectComplexity,
}: ScoreRadarProps) {
  const data = [
    { subject: 'Current Fit', A: currentFit, fullMark: 100 },
    { subject: 'Future Potential', A: futurePotential, fullMark: 100 },
    { subject: 'Growth Velocity', A: growthVelocity * 10, fullMark: 100 },
    { subject: 'Consistency', A: learningConsistency * 10, fullMark: 100 },
    { subject: 'Skill Expansion', A: skillExpansion * 10, fullMark: 100 },
    { subject: 'Complexity', A: projectComplexity * 10, fullMark: 100 },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6 }}
      className="w-full h-80"
    >
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="70%" data={data}>
          <PolarGrid stroke="rgba(255,255,255,0.1)" />
          <PolarAngleAxis 
            dataKey="subject" 
            tick={{ fill: 'rgba(255,255,255,0.6)', fontSize: 12 }}
          />
          <PolarRadiusAxis 
            angle={30} 
            domain={[0, 100]} 
            tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 10 }}
            axisLine={false}
          />
          <Radar
            name="Candidate"
            dataKey="A"
            stroke="#0ea5e9"
            strokeWidth={2}
            fill="#0ea5e9"
            fillOpacity={0.3}
          />
        </RadarChart>
      </ResponsiveContainer>
    </motion.div>
  )
}