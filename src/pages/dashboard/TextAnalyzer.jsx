import { useEffect } from 'react';
import { motion } from 'framer-motion';
import TextEditor from '../../components/analyzer/TextEditor';
import RewritePanel from '../../components/analyzer/RewritePanel';
import CivilityScore from '../../components/analyzer/CivilityScore';
import ToxicityBar from '../../components/analyzer/ToxicityBar';
import FallacyList from '../../components/analyzer/FallacyList';
import { SentimentBadge } from '../../components/ui/Badge';
import { useAnalysis } from '../../context/AnalysisContext';
import { useDebounce } from '../../hooks/useDebounce';
import { useToast } from '../../context/ToastContext';
import { DEBOUNCE_MS } from '../../utils/constants';
import Button from '../../components/ui/Button';
import { FiSave, FiTrash2 } from 'react-icons/fi';

export default function TextAnalyzer() {
  const { text, setText, result, loading, analyze, saveToHistory, reset } = useAnalysis();
  const debouncedText = useDebounce(text, DEBOUNCE_MS);
  const { addToast } = useToast();

  useEffect(() => {
    if (debouncedText) {
      analyze(debouncedText);
    }
  }, [debouncedText, analyze]);

  const handleAccept = () => {
    addToast('Rewrite accepted', 'success');
  };

  const handleReplace = () => {
    if (result.rewrite) {
      setText(result.rewrite);
      addToast('Text replaced with AI rewrite', 'success');
    }
  };

  const handleSave = async () => {
    if (!text.trim()) {
      addToast('Nothing to save', 'warning');
      return;
    }
    try {
      await saveToHistory();
      addToast('Analysis saved to history', 'success');
    } catch {
      addToast('Failed to save', 'error');
    }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold">Text Analyzer</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Real-time AI moderation as you type
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" size="sm" icon={FiSave} onClick={handleSave}>
            Save
          </Button>
          <Button variant="ghost" size="sm" icon={FiTrash2} onClick={reset}>
            Clear
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2 space-y-6">
          <div className="glass-card p-4 sm:p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-semibold">Your Message</h2>
              {loading && (
                <span className="flex items-center gap-2 text-sm text-primary-600">
                  <span className="w-3 h-3 border-2 border-primary-600 border-t-transparent rounded-full animate-spin" />
                  Analyzing...
                </span>
              )}
            </div>
            <div className="min-h-[300px] lg:min-h-[400px]">
              <TextEditor
                value={text}
                onChange={setText}
                highlights={result.highlightedText}
                placeholder="Start typing your message here... Try: 'You're so stupid, nobody cares what you think!'"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <ToxicityBar toxicity={result.toxicity} />
            <FallacyList fallacies={result.fallacies} />
          </div>
        </div>

        <div className="space-y-6">
          <div className="glass-card p-6 flex flex-col items-center">
            <CivilityScore score={result.score} />
            <div className="mt-4">
              <SentimentBadge sentiment={result.sentiment} />
            </div>
          </div>

          <RewritePanel
            originalText={text}
            rewrite={result.rewrite}
            onAccept={handleAccept}
            onReplace={handleReplace}
            loading={loading}
          />
        </div>
      </div>
    </motion.div>
  );
}
