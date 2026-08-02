/**
 * Mock analysis engine — simulates backend /api/analyze response
 */
const TOXIC_PATTERNS = [
  { pattern: /\b(stupid|idiot|moron|dumb|hate you|kill yourself|shut up)\b/gi, type: 'toxicity' },
  { pattern: /\b(you're (wrong|an idiot|pathetic)|nobody cares)\b/gi, type: 'toxicity' },
  { pattern: /\b(always|never)\b/gi, type: 'fallacy' },
  { pattern: /\b(everyone knows|obviously)\b/gi, type: 'fallacy' },
];

const FALLACY_LABELS = {
  'Ad Hominem': /\b(you're (stupid|an idiot|pathetic|wrong)|moron|idiot)\b/i,
  'Straw Man': /\b(you think|you believe|you want)\b/i,
  'False Dichotomy': /\b(either|or else|only two)\b/i,
  'Appeal to Emotion': /\b(feel|scared|afraid|worried)\b/i,
  'Hasty Generalization': /\b(always|never|everyone|nobody)\b/i,
};

function detectHighlights(text) {
  const highlights = [];

  TOXIC_PATTERNS.forEach(({ pattern, type }) => {
    let match;
    const regex = new RegExp(pattern.source, pattern.flags);
    while ((match = regex.exec(text)) !== null) {
      highlights.push({
        start: match.index,
        end: match.index + match[0].length,
        type,
      });
    }
  });

  return highlights;
}

function detectFallacies(text) {
  const fallacies = [];
  Object.entries(FALLACY_LABELS).forEach(([label, pattern]) => {
    if (pattern.test(text)) fallacies.push(label);
  });
  return [...new Set(fallacies)];
}

function calculateToxicity(text, highlights) {
  if (!text.trim()) return 0;
  const toxicChars = highlights.filter((h) => h.type === 'toxicity').reduce((sum, h) => sum + (h.end - h.start), 0);
  return Math.min(1, toxicChars / text.length + highlights.length * 0.05);
}

function calculateScore(toxicity, fallacies) {
  let score = Math.round((1 - toxicity) * 100);
  score -= fallacies.length * 5;
  return Math.max(0, Math.min(100, score));
}

function generateRewrite(text) {
  if (!text.trim()) return '';
  return text
    .replace(/\b(stupid|idiot|moron|dumb)\b/gi, 'misguided')
    .replace(/\b(hate you|kill yourself|shut up)\b/gi, "I disagree with your perspective")
    .replace(/\b(you're wrong)\b/gi, "I see things differently")
    .replace(/\b(nobody cares)\b/gi, 'this perspective may not resonate with everyone')
    .replace(/\b(always|never)\b/gi, 'often')
    .replace(/^./, (c) => c.toUpperCase());
}

function detectSentiment(text, toxicity) {
  if (!text.trim()) return 'Neutral';
  if (toxicity > 0.6) return 'Negative';
  if (toxicity > 0.3) return 'Neutral';
  return 'Positive';
}

export function mockAnalyze(text) {
  return new Promise((resolve) => {
    setTimeout(() => {
      const highlightedText = detectHighlights(text);
      const fallacies = detectFallacies(text);
      const toxicity = calculateToxicity(text, highlightedText);
      const score = calculateScore(toxicity, fallacies);
      const sentiment = detectSentiment(text, toxicity);
      const rewrite = generateRewrite(text);

      resolve({
        toxicity: Math.round(toxicity * 100) / 100,
        sentiment,
        fallacies,
        highlightedText,
        rewrite: rewrite !== text ? rewrite : 'Your text looks civil. No rewrite needed.',
        score,
      });
    }, 400);
  });
}

export const mockUsers = [
  { id: 1, name: 'Admin User', email: 'admin@civildialog.com', role: 'admin', avatar: null },
  { id: 2, name: 'Jane Doe', email: 'jane@example.com', role: 'user', avatar: null },
  { id: 3, name: 'John Smith', email: 'john@example.com', role: 'user', avatar: null },
];

export const mockDashboardStats = {
  averageCivilityScore: 78,
  messagesAnalysed: 1247,
  toxicMessagesPrevented: 342,
  overallImprovement: 23,
};

export const mockHistory = [
  {
    id: '1',
    text: "You're so stupid, nobody cares what you think!",
    score: 32,
    sentiment: 'Negative',
    toxicity: 0.91,
    fallacies: ['Ad Hominem', 'Hasty Generalization'],
    createdAt: '2026-08-01T10:30:00Z',
  },
  {
    id: '2',
    text: 'I respectfully disagree with your perspective on this matter.',
    score: 92,
    sentiment: 'Positive',
    toxicity: 0.05,
    fallacies: [],
    createdAt: '2026-08-01T09:15:00Z',
  },
  {
    id: '3',
    text: 'Everyone knows you always make the wrong decisions.',
    score: 45,
    sentiment: 'Negative',
    toxicity: 0.72,
    fallacies: ['Hasty Generalization', 'Ad Hominem'],
    createdAt: '2026-07-31T16:45:00Z',
  },
  {
    id: '4',
    text: 'Could we explore alternative solutions together?',
    score: 88,
    sentiment: 'Positive',
    toxicity: 0.08,
    fallacies: [],
    createdAt: '2026-07-31T14:20:00Z',
  },
  {
    id: '5',
    text: 'Either you agree with me or you are part of the problem.',
    score: 38,
    sentiment: 'Negative',
    toxicity: 0.65,
    fallacies: ['False Dichotomy'],
    createdAt: '2026-07-30T11:00:00Z',
  },
];

export const mockAdminStats = {
  totalUsers: 2847,
  totalMessages: 45230,
  averageScore: 74,
  toxicMessages: 8934,
};

export const mockDailyActivity = [
  { date: 'Mon', messages: 420, score: 72 },
  { date: 'Tue', messages: 580, score: 75 },
  { date: 'Wed', messages: 510, score: 78 },
  { date: 'Thu', messages: 690, score: 74 },
  { date: 'Fri', messages: 750, score: 76 },
  { date: 'Sat', messages: 320, score: 80 },
  { date: 'Sun', messages: 280, score: 82 },
];

export const mockSentimentDistribution = [
  { name: 'Positive', value: 45, color: '#22c55e' },
  { name: 'Neutral', value: 35, color: '#94a3b8' },
  { name: 'Negative', value: 20, color: '#ef4444' },
];

export const mockTopToxicWords = [
  { word: 'stupid', count: 342 },
  { word: 'idiot', count: 287 },
  { word: 'hate', count: 256 },
  { word: 'moron', count: 198 },
  { word: 'pathetic', count: 167 },
  { word: 'worthless', count: 134 },
];

export const mockRecentReports = [
  { id: 1, user: 'user_2847', text: 'Offensive language detected', severity: 'High', date: '2026-08-02' },
  { id: 2, user: 'user_1923', text: 'Hate speech pattern', severity: 'Critical', date: '2026-08-02' },
  { id: 3, user: 'user_4521', text: 'Ad hominem attack', severity: 'Medium', date: '2026-08-01' },
  { id: 4, user: 'user_8834', text: 'Toxic language flagged', severity: 'High', date: '2026-08-01' },
  { id: 5, user: 'user_1102', text: 'Logical fallacy detected', severity: 'Low', date: '2026-07-31' },
];

export function mockLogin(email, password) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const user = mockUsers.find((u) => u.email === email);
      if (user && password.length >= 6) {
        resolve({
          access_token: `mock_jwt_${user.id}_${Date.now()}`,
          refresh_token: `mock_refresh_${user.id}_${Date.now()}`,
          user: { ...user, username: user.email.split('@')[0] },
        });
      } else {
        reject(new Error('Invalid email or password'));
      }
    }, 600);
  });
}

export function mockRegister(data) {
  return new Promise((resolve) => {
    setTimeout(() => {
      const user = {
        id: Date.now(),
        name: data.name,
        email: data.email,
        username: data.username,
        role: 'user',
        avatar: null,
      };
      resolve({
        access_token: `mock_jwt_${user.id}_${Date.now()}`,
        refresh_token: `mock_refresh_${user.id}_${Date.now()}`,
        user,
      });
    }, 600);
  });
}
