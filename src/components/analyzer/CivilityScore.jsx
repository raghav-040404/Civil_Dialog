import { motion } from 'framer-motion';
import { getCivilityColor, getCivilityLabel } from '../../utils/helpers';

export default function CivilityScore({ score, size = 160 }) {
  const strokeWidth = 10;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = (score / 100) * circumference;
  const color = getCivilityColor(score);
  const label = getCivilityLabel(score);

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth={strokeWidth}
            className="text-gray-200 dark:text-gray-700"
          />
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: circumference - progress }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            key={score}
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="text-4xl font-bold"
            style={{ color }}
          >
            {score}
          </motion.span>
          <span className="text-xs text-gray-500 dark:text-gray-400 mt-1">/ 100</span>
        </div>
      </div>
      <div className="text-center">
        <p className="font-semibold" style={{ color }}>{label}</p>
        <p className="text-sm text-gray-500 dark:text-gray-400">Civility Score</p>
      </div>
    </div>
  );
}
