
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Zap, Brain, TrendingUp, Shield, ArrowRight, Sparkles } from 'lucide-react';
import ParticleBackground from '../components/animations/ParticleBackground';
import ShimmerText from '../components/animations/ShimmerText';

export default function LandingPage() {
  const navigate = useNavigate()

  const features = [
    {
      icon: Brain,
      title: 'Semantic Matching',
      description: 'AI understands context, not just keywords. TensorFlow ≈ PyTorch.',
      color: 'text-talent-400',
      bgColor: 'bg-talent-500/10',
    },
    {
      icon: TrendingUp,
      title: 'Growth Prediction',
      description: 'Predict who will be exceptional tomorrow, not just who is good today.',
      color: 'text-genius-400',
      bgColor: 'bg-genius-500/10',
    },
    {
      icon: Shield,
      title: 'Bias-Free Ranking',
      description: 'College name and CGPA are ignored. Only skills and growth matter.',
      color: 'text-success',
      bgColor: 'bg-success/10',
    },
  ]

  return (
    <div className="min-h-screen relative overflow-hidden">
      <ParticleBackground />
      
      {/* Hero Section */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-4">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center max-w-4xl"
        >
          {/* Badge */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.3, type: 'spring' }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-8"
          >
            <Sparkles className="w-4 h-4 text-genius-400" />
            <span className="text-white/60 text-sm">AI-Powered Recruitment Intelligence</span>
          </motion.div>

          {/* Title */}
          <h1 className="text-6xl md:text-7xl font-bold mb-6">
            <span className="text-white">Discover</span>{' '}
            <ShimmerText text="Hidden Talent" className="text-6xl md:text-7xl font-bold" />
          </h1>

          <p className="text-xl text-white/60 mb-8 max-w-2xl mx-auto leading-relaxed">
            Traditional ATS answers "Who is best today?" 
            TalentMind answers "Who is best today AND who could become exceptional tomorrow?"
          </p>

          {/* CTA */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate('/dashboard')}
            className="px-8 py-4 rounded-2xl bg-gradient-to-r from-talent-500 to-genius-500 text-white font-bold text-lg flex items-center gap-3 mx-auto shadow-2xl shadow-talent-500/25"
          >
            <Zap className="w-5 h-5" />
            Launch Dashboard
            <ArrowRight className="w-5 h-5" />
          </motion.button>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="flex items-center justify-center gap-8 mt-12"
          >
            <div className="text-center">
              <div className="text-3xl font-bold text-white">487</div>
              <div className="text-white/40 text-sm">Resumes</div>
            </div>
            <div className="w-px h-10 bg-white/10" />
            <div className="text-center">
              <div className="text-3xl font-bold text-white">847ms</div>
              <div className="text-white/40 text-sm">Processing</div>
            </div>
            <div className="w-px h-10 bg-white/10" />
            <div className="text-center">
              <div className="text-3xl font-bold text-genius-400">23</div>
              <div className="text-white/40 text-sm">Hidden Geniuses</div>
            </div>
          </motion.div>
        </motion.div>

        {/* Features */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="grid grid-cols-3 gap-6 max-w-4xl mt-20"
        >
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              whileHover={{ y: -10, scale: 1.02 }}
              className="glass rounded-xl p-6 text-center"
            >
              <div className={`w-12 h-12 rounded-xl ${feature.bgColor} flex items-center justify-center mx-auto mb-4`}>
                <feature.icon className={`w-6 h-6 ${feature.color}`} />
              </div>
              <h3 className="text-white font-semibold mb-2">{feature.title}</h3>
              <p className="text-white/50 text-sm">{feature.description}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </div>
  )
}