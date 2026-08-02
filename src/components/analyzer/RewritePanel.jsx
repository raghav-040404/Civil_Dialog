import { motion } from 'framer-motion';
import { FiArrowDown, FiCheck, FiCopy, FiRefreshCw } from 'react-icons/fi';
import Button from '../ui/Button';
import { useToast } from '../../context/ToastContext';

export default function RewritePanel({ originalText, rewrite, onAccept, onReplace, loading }) {
  const { addToast } = useToast();

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(rewrite);
      addToast('Rewrite copied to clipboard', 'success');
    } catch {
      addToast('Failed to copy', 'error');
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="glass-card p-6 h-full flex flex-col"
    >
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <FiRefreshCw className="text-primary-500" />
        AI Rewrite Suggestion
      </h3>

      <div className="flex-1 flex flex-col gap-4">
        <div>
          <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
            Original
          </p>
          <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-800/50 text-sm leading-relaxed max-h-32 overflow-y-auto">
            {originalText || 'Start typing to see analysis...'}
          </div>
        </div>

        <div className="flex justify-center">
          <FiArrowDown className="text-primary-500 animate-bounce" size={20} />
        </div>

        <div>
          <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
            AI Rewrite
          </p>
          <div className="p-4 rounded-xl bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800 text-sm leading-relaxed max-h-40 overflow-y-auto">
            {loading ? (
              <div className="flex items-center gap-2 text-gray-500">
                <span className="w-4 h-4 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
                Generating rewrite...
              </div>
            ) : (
              rewrite || 'Rewrite will appear here'
            )}
          </div>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
        <Button size="sm" onClick={onAccept} disabled={!rewrite || loading} icon={FiCheck}>
          Accept
        </Button>
        <Button size="sm" variant="secondary" onClick={handleCopy} disabled={!rewrite} icon={FiCopy}>
          Copy
        </Button>
        <Button size="sm" variant="outline" onClick={onReplace} disabled={!rewrite || loading}>
          Replace
        </Button>
      </div>
    </motion.div>
  );
}
