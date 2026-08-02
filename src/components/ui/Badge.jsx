import { cn } from '../../utils/helpers';
import { SENTIMENT_COLORS } from '../../utils/constants';

export default function Badge({ children, variant = 'default', className }) {
  const variants = {
    default: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300',
    primary: 'bg-primary-100 text-primary-800 dark:bg-primary-900/40 dark:text-primary-300',
    success: 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300',
    warning: 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300',
    danger: 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300',
  };

  return (
    <span className={cn('inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium', variants[variant], className)}>
      {children}
    </span>
  );
}

export function SentimentBadge({ sentiment }) {
  return (
    <span className={cn('inline-flex items-center px-3 py-1 rounded-full text-sm font-medium', SENTIMENT_COLORS[sentiment] || SENTIMENT_COLORS.Neutral)}>
      {sentiment}
    </span>
  );
}
