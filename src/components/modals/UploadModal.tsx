import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Upload, FileText, Check, Loader2 } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { useAppStore } from '../../hooks/useStore';
// ... rest same

export default function UploadModal() {
  const { showUploadModal, setShowUploadModal } = useAppStore()
  const [files, setFiles] = useState<File[]>([])
  const [uploading, setUploading] = useState(false)
  const [uploaded, setUploaded] = useState(false)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(prev => [...prev, ...acceptedFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
    },
  })

  const handleUpload = async () => {
    setUploading(true)
    // Simulate upload
    await new Promise(resolve => setTimeout(resolve, 3000))
    setUploading(false)
    setUploaded(true)
    setTimeout(() => {
      setShowUploadModal(false)
      setFiles([])
      setUploaded(false)
    }, 2000)
  }

  if (!showUploadModal) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[100] flex items-center justify-center p-4"
        onClick={() => setShowUploadModal(false)}
      >
        <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" />

        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
          className="relative w-full max-w-lg glass-strong rounded-2xl border border-white/20 p-6"
        >
          <button
            onClick={() => setShowUploadModal(false)}
            className="absolute top-4 right-4 p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5 text-white/60" />
          </button>

          <h2 className="text-xl font-bold text-white mb-2">Upload Documents</h2>
          <p className="text-white/50 text-sm mb-6">Upload Job Description and Candidate Resumes</p>

          {/* Drop Zone */}
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
              isDragActive 
                ? 'border-talent-500 bg-talent-500/10' 
                : 'border-white/20 hover:border-white/40'
            }`}
          >
            <input {...getInputProps()} />
            <Upload className={`w-10 h-10 mx-auto mb-3 ${isDragActive ? 'text-talent-400' : 'text-white/30'}`} />
            <p className="text-white/60 text-sm">
              {isDragActive ? 'Drop files here...' : 'Drag & drop files here, or click to select'}
            </p>
            <p className="text-white/30 text-xs mt-1">PDF, TXT files supported</p>
          </div>

          {/* File List */}
          {files.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 space-y-2"
            >
              {files.map((file, index) => (
                <div key={index} className="flex items-center gap-3 p-3 rounded-lg bg-white/5 border border-white/10">
                  <FileText className="w-5 h-5 text-talent-400" />
                  <span className="text-white/70 text-sm flex-1">{file.name}</span>
                  <span className="text-white/40 text-xs">{(file.size / 1024).toFixed(1)} KB</span>
                </div>
              ))}
            </motion.div>
          )}

          {/* Upload Button */}
          {files.length > 0 && !uploaded && (
            <motion.button
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleUpload}
              disabled={uploading}
              className="w-full mt-6 py-3 rounded-xl bg-gradient-to-r from-talent-500 to-genius-500 text-white font-medium flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {uploading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Processing with AI...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  Upload & Analyze
                </>
              )}
            </motion.button>
          )}

          {/* Success */}
          {uploaded && (
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="mt-6 p-4 rounded-xl bg-success/10 border border-success/30 text-center"
            >
              <Check className="w-8 h-8 text-success mx-auto mb-2" />
              <p className="text-success font-medium">Upload Complete!</p>
              <p className="text-white/50 text-sm">AI is analyzing candidates...</p>
            </motion.div>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}