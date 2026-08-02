import { cn } from '../../utils/helpers';

export default function Avatar({ src, name, size = 'md', className }) {
  const sizes = { sm: 'w-8 h-8 text-xs', md: 'w-10 h-10 text-sm', lg: 'w-14 h-14 text-lg', xl: 'w-20 h-20 text-2xl' };
  const initials = name
    ?.split(' ')
    .map((n) => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

  if (src) {
    return (
      <img
        src={src}
        alt={name}
        className={cn('rounded-full object-cover ring-2 ring-primary-500/20', sizes[size], className)}
      />
    );
  }

  return (
    <div
      className={cn(
        'rounded-full bg-gradient-to-br from-primary-500 to-primary-700 text-white font-semibold flex items-center justify-center ring-2 ring-primary-500/20',
        sizes[size],
        className
      )}
    >
      {initials || '?'}
    </div>
  );
}
