import { motion } from 'framer-motion';
import { cn } from '../../utils/helpers';

export default function ProgressBar({ value, max = 100, label, showValue = true, color }) {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));

  const getColor = () => {
    if (color) return color;
    if (percentage > 70) return 'bg-red-500';
    if (percentage > 40) return 'bg-amber-500';
    return 'bg-green-500';
  };

  return (
    <div className="w-full">
      {(label || showValue) && (
        <div className="flex justify-between mb-2">
          {label && <span className="text-sm font-medium text-gray-600 dark:text-gray-400">{label}</span>}
          {showValue && <span className="text-sm font-semibold">{Math.round(percentage)}%</span>}
        </div>
      )}
      <div className="h-2.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
          className={cn('h-full rounded-full', getColor())}
        />
      </div>
    </div>
  );
}
