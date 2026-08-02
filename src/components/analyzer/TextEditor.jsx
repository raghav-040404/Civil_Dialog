import { useRef, useEffect } from 'react';
import { buildHighlightedHtml } from '../../utils/helpers';

export default function TextEditor({ value, onChange, highlights = [], placeholder, disabled }) {
  const textareaRef = useRef(null);
  const overlayRef = useRef(null);

  const syncScroll = () => {
    if (textareaRef.current && overlayRef.current) {
      overlayRef.current.scrollTop = textareaRef.current.scrollTop;
      overlayRef.current.scrollLeft = textareaRef.current.scrollLeft;
    }
  };

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.addEventListener('scroll', syncScroll);
      return () => textarea.removeEventListener('scroll', syncScroll);
    }
  }, []);

  const highlightedHtml = buildHighlightedHtml(value, highlights);

  return (
    <div className="relative w-full h-full min-h-[300px] rounded-2xl overflow-hidden border border-gray-200 dark:border-gray-700 focus-within:ring-2 focus-within:ring-primary-500/50 focus-within:border-primary-500 transition-all">
      <div
        ref={overlayRef}
        aria-hidden="true"
        className="absolute inset-0 p-6 pointer-events-none overflow-auto whitespace-pre-wrap break-words text-base leading-relaxed font-sans text-transparent"
        dangerouslySetInnerHTML={{ __html: highlightedHtml || placeholder }}
      />
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onScroll={syncScroll}
        placeholder={placeholder}
        disabled={disabled}
        className="absolute inset-0 w-full h-full p-6 bg-transparent text-gray-900 dark:text-white text-base leading-relaxed resize-none focus:outline-none caret-primary-600"
        spellCheck
      />
    </div>
  );
}
