import { motion } from 'framer-motion';
import { cn } from '../../utils/helpers';

export default function Card({ children, className, hover = false, ...props }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={cn(
        'glass-card p-6',
        hover && 'hover:shadow-xl hover:shadow-primary-600/10 transition-shadow duration-300 cursor-pointer',
        className
      )}
      {...props}
    >
      {children}
    </motion.div>
  );
}

export function StatCard({ title, value, change, icon: Icon, color = 'primary' }) {
  const colors = {
    primary: 'bg-primary-100 dark:bg-primary-900/30 text-primary-600',
    green: 'bg-green-100 dark:bg-green-900/30 text-green-600',
    red: 'bg-red-100 dark:bg-red-900/30 text-red-600',
    amber: 'bg-amber-100 dark:bg-amber-900/30 text-amber-600',
  };

  return (
    <Card hover>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-500 dark:text-gray-400">{title}</p>
          <p className="text-3xl font-bold mt-1">{value}</p>
          {change && (
            <p className={`text-sm mt-1 ${change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
              {change >= 0 ? '+' : ''}{change}% from last week
            </p>
          )}
        </div>
        {Icon && (
          <div className={cn('p-3 rounded-xl', colors[color])}>
            <Icon size={22} />
          </div>
        )}
      </div>
    </Card>
  );
}
