import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Upload, FileText, Check, Loader2, Briefcase, Users } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { useAppStore } from '../../hooks/useStore';

type UploadTab = 'resumes' | 'jd';

export default function UploadModal() {
  const {
    showUploadModal,
    setShowUploadModal,
    uploadFiles,
    parseAndSearch,
    uploadProgress,
    error,
    setError,
  } = useAppStore();

  const [activeTab, setActiveTab] = useState<UploadTab>('resumes');
  const [resumeFiles, setResumeFiles] = useState<File[]>([]);
  const [jdFile, setJdFile] = useState<File | null>(null);
  const [jdText, setJdText] = useState('');
  const [processing, setProcessing] = useState(false);
  const [success, setSuccess] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const onResumeDrop = useCallback((acceptedFiles: File[]) => {
    setResumeFiles((prev) => [...prev, ...acceptedFiles]);
  }, []);

  const onJdDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles[0]) setJdFile(acceptedFiles[0]);
  }, []);

  const resumeDropzone = useDropzone({
    onDrop: onResumeDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
    },
  });

  const jdDropzone = useDropzone({
    onDrop: onJdDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    maxFiles: 1,
  });

  const resetState = () => {
    setResumeFiles([]);
    setJdFile(null);
    setJdText('');
    setProcessing(false);
    setSuccess(false);
    setSuccessMessage('');
    setError(null);
  };

  const handleClose = () => {
    setShowUploadModal(false);
    resetState();
  };

  const handleResumeUpload = async () => {
    if (resumeFiles.length === 0) return;
    setProcessing(true);
    setError(null);
    try {
      await uploadFiles(resumeFiles);
      setSuccess(true);
      setSuccessMessage(`${resumeFiles.length} resume(s) processed and indexed.`);
      setTimeout(() => {
        setActiveTab('jd');
        setSuccess(false);
        setResumeFiles([]);
      }, 2000);
    } catch {
      // error stored in store
    } finally {
      setProcessing(false);
    }
  };

  const handleJdSearch = async () => {
    if (!jdFile && !jdText.trim()) return;
    setProcessing(true);
    setError(null);
    try {
      await parseAndSearch(jdText, jdFile ?? undefined);
      setSuccess(true);
      setSuccessMessage('Candidates ranked. Opening dashboard...');
      setTimeout(() => {
        handleClose();
      }, 1500);
    } catch {
      // error stored in store
    } finally {
      setProcessing(false);
    }
  };

  if (!showUploadModal) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[100] flex items-center justify-center p-4"
        onClick={handleClose}
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
            onClick={handleClose}
            className="absolute top-4 right-4 p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5 text-white/60" />
          </button>

          <h2 className="text-xl font-bold text-white mb-2">Upload & Search</h2>
          <p className="text-white/50 text-sm mb-4">
            Step 1: Upload resumes. Step 2: Add a job description to rank candidates.
          </p>

          {/* Tabs */}
          <div className="flex gap-2 mb-6">
            <button
              onClick={() => setActiveTab('resumes')}
              className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'resumes'
                  ? 'bg-talent-500/20 text-talent-400 border border-talent-500/30'
                  : 'bg-white/5 text-white/50 hover:text-white'
              }`}
            >
              <Users className="w-4 h-4" />
              Resumes
            </button>
            <button
              onClick={() => setActiveTab('jd')}
              className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'jd'
                  ? 'bg-genius-500/20 text-genius-400 border border-genius-500/30'
                  : 'bg-white/5 text-white/50 hover:text-white'
              }`}
            >
              <Briefcase className="w-4 h-4" />
              Job Description
            </button>
          </div>

          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-sm">
              {error}
            </div>
          )}

          {activeTab === 'resumes' && (
            <>
              <div
                {...resumeDropzone.getRootProps()}
                className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
                  resumeDropzone.isDragActive
                    ? 'border-talent-500 bg-talent-500/10'
                    : 'border-white/20 hover:border-white/40'
                }`}
              >
                <input {...resumeDropzone.getInputProps()} />
                <Upload
                  className={`w-10 h-10 mx-auto mb-3 ${
                    resumeDropzone.isDragActive ? 'text-talent-400' : 'text-white/30'
                  }`}
                />
                <p className="text-white/60 text-sm">
                  Drag & drop resume files, or click to select
                </p>
                <p className="text-white/30 text-xs mt-1">PDF or TXT — up to 50 files</p>
              </div>

              {resumeFiles.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 space-y-2 max-h-32 overflow-y-auto"
                >
                  {resumeFiles.map((file, index) => (
                    <div
                      key={index}
                      className="flex items-center gap-3 p-3 rounded-lg bg-white/5 border border-white/10"
                    >
                      <FileText className="w-5 h-5 text-talent-400" />
                      <span className="text-white/70 text-sm flex-1 truncate">{file.name}</span>
                      <span className="text-white/40 text-xs">
                        {(file.size / 1024).toFixed(1)} KB
                      </span>
                    </div>
                  ))}
                </motion.div>
              )}

              {uploadProgress && (
                <div className="mt-4 text-center text-white/50 text-sm">
                  Processing {uploadProgress.done}/{uploadProgress.total} resumes...
                </div>
              )}

              {resumeFiles.length > 0 && !success && (
                <motion.button
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleResumeUpload}
                  disabled={processing}
                  className="w-full mt-6 py-3 rounded-xl bg-gradient-to-r from-talent-500 to-genius-500 text-white font-medium flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {processing ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Indexing resumes...
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4" />
                      Upload {resumeFiles.length} Resume(s)
                    </>
                  )}
                </motion.button>
              )}
            </>
          )}

          {activeTab === 'jd' && (
            <>
              <div
                {...jdDropzone.getRootProps()}
                className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all mb-4 ${
                  jdDropzone.isDragActive
                    ? 'border-genius-500 bg-genius-500/10'
                    : 'border-white/20 hover:border-white/40'
                }`}
              >
                <input {...jdDropzone.getInputProps()} />
                <Briefcase className="w-8 h-8 mx-auto mb-2 text-white/30" />
                <p className="text-white/60 text-sm">
                  {jdFile ? jdFile.name : 'Drop JD PDF here, or click to select'}
                </p>
              </div>

              <textarea
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
                placeholder="Or paste job description text here..."
                rows={5}
                className="w-full p-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-white/30 text-sm focus:outline-none focus:border-genius-500/50 resize-none"
              />

              {!success && (
                <motion.button
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleJdSearch}
                  disabled={processing || (!jdFile && !jdText.trim())}
                  className="w-full mt-4 py-3 rounded-xl bg-gradient-to-r from-genius-500 to-talent-500 text-white font-medium flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {processing ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Parsing JD & ranking candidates...
                    </>
                  ) : (
                    <>
                      <Briefcase className="w-4 h-4" />
                      Parse JD & Search Candidates
                    </>
                  )}
                </motion.button>
              )}
            </>
          )}

          {success && (
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="mt-6 p-4 rounded-xl bg-success/10 border border-success/30 text-center"
            >
              <Check className="w-8 h-8 text-success mx-auto mb-2" />
              <p className="text-success font-medium">{successMessage}</p>
            </motion.div>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
