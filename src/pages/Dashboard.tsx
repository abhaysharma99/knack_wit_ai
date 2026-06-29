import { motion } from 'framer-motion';
import { Loader2, Upload } from 'lucide-react';
import { useAppStore } from '../hooks/useStore';
import Sidebar from '../components/dashboard/Sidebar';
import TopBar from '../components/dashboard/TopBar';
import StatsCards from '../components/dashboard/StatsCards';
import CandidateList from '../components/candidate/CandidateList';
import HiddenGeniusTab from '../components/dashboard/HiddenGeniusTab';
import AnalyticsTab from '../components/dashboard/AnalyticsTab';
import AnalysisModal from '../components/modals/AnalysisModal';
import UploadModal from '../components/modals/UploadModal';

export default function Dashboard() {
  const { activeTab, isLoading, candidates, error, setShowUploadModal } = useAppStore();

  return (
    <div className="min-h-screen relative">
      <Sidebar />

      <div className="ml-72">
        <TopBar />

        {error && (
          <div className="mx-6 mt-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-sm">
            {error}
          </div>
        )}

        <motion.main
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="p-6"
        >
          {candidates.length === 0 && !isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center py-20"
            >
              <p className="text-white/50 mb-4">
                No candidates yet. Upload resumes and a job description to start ranking.
              </p>
              <button
                onClick={() => setShowUploadModal(true)}
                className="px-6 py-3 rounded-xl bg-gradient-to-r from-talent-500 to-genius-500 text-white font-medium flex items-center gap-2 mx-auto"
              >
                <Upload className="w-4 h-4" />
                Upload JD / Resumes
              </button>
            </motion.div>
          )}

          {activeTab === 'dashboard' && candidates.length > 0 && (
            <motion.div key="dashboard" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
              <StatsCards />
              <CandidateList />
            </motion.div>
          )}

          {activeTab === 'all' && candidates.length > 0 && (
            <motion.div key="all" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
              <StatsCards />
              <CandidateList />
            </motion.div>
          )}

          {activeTab === 'hidden-genius' && (
            <motion.div key="hidden-genius" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
              <HiddenGeniusTab />
            </motion.div>
          )}

          {activeTab === 'analysis' && candidates.length > 0 && (
            <motion.div key="analysis" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
              <AnalyticsTab />
            </motion.div>
          )}
        </motion.main>
      </div>

      {isLoading && (
        <div className="fixed inset-0 z-[90] flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="flex items-center gap-3 px-6 py-4 rounded-xl glass-strong border border-white/20">
            <Loader2 className="w-5 h-5 text-talent-400 animate-spin" />
            <span className="text-white/80">Processing with AI...</span>
          </div>
        </div>
      )}

      <AnalysisModal />
      <UploadModal />
    </div>
  );
}
