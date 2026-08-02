import { motion } from 'framer-motion';
import { FiAlertCircle } from 'react-icons/fi';
import Badge from '../ui/Badge';

export default function FallacyList({ fallacies = [] }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-5"
    >
      <div className="flex items-center gap-2 mb-3">
        <FiAlertCircle className="text-amber-500" />
        <h4 className="font-semibold">Logical Fallacies</h4>
      </div>
      {fallacies.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400">No fallacies detected</p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {fallacies.map((fallacy) => (
            <Badge key={fallacy} variant="warning">{fallacy}</Badge>
          ))}
        </div>
      )}
    </motion.div>
  );
}
