import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { AnalysisProvider } from '../context/AnalysisContext';
import TextAnalyzer from './dashboard/TextAnalyzer';
import Navbar from '../components/common/Navbar';
import Button from '../components/ui/Button';

function DemoContent() {
  return (
    <div className="min-h-screen bg-surface dark:bg-surface-dark">
      <Navbar />
      <div className="pt-24 pb-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary-100 dark:bg-primary-900/40 text-primary-700 dark:text-primary-300 text-sm font-medium mb-4">
            Live Demo — No account required
          </span>
          <h1 className="text-3xl sm:text-4xl font-bold mb-2">Try CivilDialog</h1>
          <p className="text-gray-500 dark:text-gray-400 max-w-xl mx-auto">
            Type a message below to see real-time toxicity detection, fallacy identification,
            and AI rewrite suggestions in action.
          </p>
          <div className="mt-4">
            <Link to="/register">
              <Button size="sm">Create Free Account</Button>
            </Link>
          </div>
        </motion.div>
        <TextAnalyzer />
      </div>
    </div>
  );
}

export default function DemoPage() {
  return (
    <AnalysisProvider>
      <DemoContent />
    </AnalysisProvider>
  );
}
