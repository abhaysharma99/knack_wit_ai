import { motion } from 'framer-motion';
import { useAppStore } from '../hooks/useStore';
import Sidebar from '../components/dashboard/Sidebar';
import TopBar from '../components/dashboard/TopBar';
import StatsCards from '../components/dashboard/StatsCards';
import CandidateList from '../components/candidate/CandidateList';
import HiddenGeniusTab from '../components/dashboard/HiddenGeniusTab';
import AnalyticsTab from '../components/dashboard/AnalyticsTab';
import AnalysisModal from '../components/modals/AnalysisModal';
import UploadModal from '../components/modals/UploadModal';
// ... rest same

export default function Dashboard() {
  const { activeTab } = useAppStore()

  return (
    <div className="min-h-screen relative">
      <Sidebar />
      
      <div className="ml-72">
        <TopBar />
        
        <motion.main
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="p-6"
        >
          {activeTab === 'dashboard' && (
            <motion.div
              key="dashboard"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <StatsCards />
              <CandidateList />
            </motion.div>
          )}

          {activeTab === 'all' && (
            <motion.div
              key="all"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <StatsCards />
              <CandidateList />
            </motion.div>
          )}

          {activeTab === 'hidden-genius' && (
            <motion.div
              key="hidden-genius"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <HiddenGeniusTab />
            </motion.div>
          )}

          {activeTab === 'analysis' && (
            <motion.div
              key="analysis"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <AnalyticsTab />
            </motion.div>
          )}
        </motion.main>
      </div>

      <AnalysisModal />
      <UploadModal />
    </div>
  )
}