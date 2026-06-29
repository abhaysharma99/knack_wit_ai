import { motion } from 'framer-motion';
import { LayoutDashboard, Users, Sparkles, BarChart3, Settings, Upload,  } from 'lucide-react';
import { useAppStore } from '../../hooks/useStore';

// ... rest same

export default function Sidebar() {
  const { activeTab, setActiveTab, setShowUploadModal, hiddenGeniusCandidates } = useAppStore()
  const geniusCount = hiddenGeniusCandidates().length

  const menuItems = [
    { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { id: 'all', icon: Users, label: 'All Candidates' },
    { id: 'hidden-genius', icon: Sparkles, label: 'Hidden Geniuses' },
    { id: 'analysis', icon: BarChart3, label: 'Analytics' },
  ]

  return (
    <motion.aside
      initial={{ x: -100, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.6 }}
      className="fixed left-0 top-0 h-full w-72 glass-strong z-50 flex flex-col"
    >

{/* Logo */}
<div className="p-6 border-b border-white/10">
  <motion.div 
    className="flex items-center gap-3"
    whileHover={{ scale: 1.02 }}
  >
    {/* Logo Image - Use EXACT filename */}
    <div className="relative w-11 h-11 flex items-center justify-center">
      <img 
        src="/logo-icon.png" 
        alt="KnackWit" 
        className="w-full h-full object-contain"
        onError={(e) => {
          // Fallback if image fails to load
          (e.target as HTMLImageElement).style.display = 'none';
        }}
      />
      {/* Fallback icon if image doesn't load */}
      <div className="absolute inset-0 flex items-center justify-center text-2xl">
        
      </div>
    </div>
    
    {/* Brand Text */}
    <div>
      <h1 className="text-lg font-bold tracking-wider">
        <span className="text-white">Knack</span>
        <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-500">Wit</span>
      </h1>
      <p className="text-xs text-white/40 tracking-widest">AI INTELLIGENCE</p>
    </div>
  </motion.div>
</div>
      {/* Upload Button */}
      <div className="p-4">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setShowUploadModal(true)}
          className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-talent-500 to-genius-500 text-white font-medium flex items-center justify-center gap-2 shadow-lg shadow-talent-500/25"
        >
          <Upload className="w-4 h-4" />
          Upload JD / Resumes
        </motion.button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-2">
        {menuItems.map((item, index) => (
          <motion.button
            key={item.id}
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: index * 0.1 }}
            onClick={() => setActiveTab(item.id as any)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl mb-1 transition-all duration-200 ${
              activeTab === item.id
                ? 'bg-gradient-to-r from-talent-500/20 to-genius-500/20 text-white border border-talent-500/30'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            <item.icon className={`w-5 h-5 ${activeTab === item.id ? 'text-talent-400' : ''}`} />
            <span className="font-medium">{item.label}</span>
            {item.id === 'hidden-genius' && geniusCount > 0 && (
              <span className="ml-auto px-2 py-0.5 rounded-full bg-genius-500/20 text-genius-400 text-xs font-bold">
                {geniusCount}
              </span>
            )}
          </motion.button>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-white/10">
        <div className="flex items-center gap-3 text-white/40 text-sm">
          <Settings className="w-4 h-4" />
          <span>Settings</span>
        </div>
      </div>
    </motion.aside>
  )
}