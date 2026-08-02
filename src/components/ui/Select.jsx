import { cn } from '../../utils/helpers';

export default function Select({ label, options, error, className, ...props }) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">{label}</label>
      )}
      <select
        className={cn(
          'w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700',
          'bg-white dark:bg-gray-800 text-gray-900 dark:text-white',
          'focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500',
          error && 'border-red-500',
          className
        )}
        {...props}
      >
        {options.map(({ value, label: optLabel }) => (
          <option key={value} value={value}>{optLabel}</option>
        ))}
      </select>
      {error && <p className="text-sm text-red-500">{error}</p>}
    </div>
  );
}
