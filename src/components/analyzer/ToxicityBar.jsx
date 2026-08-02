import { motion } from 'framer-motion';
import { FiAlertTriangle } from 'react-icons/fi';
import ProgressBar from '../ui/ProgressBar';

export default function ToxicityBar({ toxicity }) {
  const percentage = Math.round(toxicity * 100);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-5"
    >
      <div className="flex items-center gap-2 mb-3">
        <FiAlertTriangle className={percentage > 50 ? 'text-red-500' : 'text-amber-500'} />
        <h4 className="font-semibold">Toxicity Level</h4>
      </div>
      <ProgressBar
        value={percentage}
        label="Detected toxicity"
        color={percentage > 70 ? 'bg-red-500' : percentage > 40 ? 'bg-amber-500' : 'bg-green-500'}
      />
    </motion.div>
  );
}
