import { CIVILITY_THRESHOLDS } from './constants';

export function getCivilityColor(score) {
  if (score >= CIVILITY_THRESHOLDS.high) return '#22c55e';
  if (score >= CIVILITY_THRESHOLDS.medium) return '#eab308';
  return '#ef4444';
}

export function getCivilityLabel(score) {
  if (score >= CIVILITY_THRESHOLDS.high) return 'Excellent';
  if (score >= CIVILITY_THRESHOLDS.medium) return 'Moderate';
  return 'Needs Improvement';
}

export function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function truncateText(text, maxLength = 100) {
  if (!text || text.length <= maxLength) return text;
  return `${text.slice(0, maxLength)}...`;
}

export function cn(...classes) {
  return classes.filter(Boolean).join(' ');
}

export function buildHighlightedHtml(text, highlights = []) {
  if (!text || !highlights.length) return text;

  const sorted = [...highlights].sort((a, b) => a.start - b.start);
  let result = '';
  let lastIndex = 0;

  sorted.forEach(({ start, end, type }) => {
    if (start < lastIndex) return;
    result += escapeHtml(text.slice(lastIndex, start));
    const className =
      type === 'toxicity'
        ? 'highlight-toxicity'
        : type === 'fallacy'
          ? 'highlight-fallacy'
          : 'highlight-sentiment';
    result += `<mark class="${className}">${escapeHtml(text.slice(start, end))}</mark>`;
    lastIndex = end;
  });

  result += escapeHtml(text.slice(lastIndex));
  return result;
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

export function generateId() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}
