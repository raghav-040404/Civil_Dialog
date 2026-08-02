import { cn } from '../../utils/helpers';

export default function Input({
  label,
  error,
  icon: Icon,
  className,
  containerClassName,
  ...props
}) {
  return (
    <div className={cn('flex flex-col gap-1.5', containerClassName)}>
      {label && (
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
          {label}
        </label>
      )}
      <div className="relative">
        {Icon && (
          <Icon className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
        )}
        <input
          className={cn(
            'w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700',
            'bg-white dark:bg-gray-800 text-gray-900 dark:text-white',
            'placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500',
            'transition-all duration-200',
            Icon && 'pl-10',
            error && 'border-red-500 focus:ring-red-500/50',
            className
          )}
          {...props}
        />
      </div>
      {error && <p className="text-sm text-red-500">{error}</p>}
    </div>
  );
}
