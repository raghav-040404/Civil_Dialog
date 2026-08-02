import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  FiShield,
  FiEdit3,
  FiBarChart2,
  FiZap,
  FiRefreshCw,
  FiTarget,
  FiCpu,
  FiGlobe,
  FiArrowRight,
} from 'react-icons/fi';
import Navbar from '../components/common/Navbar';
import Footer from '../components/common/Footer';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';

const fadeUp = {
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6 },
};

const features = [
  {
    icon: FiShield,
    title: 'Toxicity Detection',
    description: 'Real-time identification of toxic language, hate speech, and harmful content as you type.',
  },
  {
    icon: FiTarget,
    title: 'Logical Fallacy Detection',
    description: 'Spot ad hominem attacks, straw man arguments, false dichotomies, and more.',
  },
  {
    icon: FiRefreshCw,
    title: 'AI Rewrite Suggestions',
    description: 'Get constructive alternatives that preserve your message while improving civility.',
  },
  {
    icon: FiBarChart2,
    title: 'Civility Score',
    description: 'Track your communication quality with an animated 0–100 civility score.',
  },
  {
    icon: FiZap,
    title: 'Real-Time Analysis',
    description: 'Debounced API analysis with live text highlighting and instant feedback.',
  },
  {
    icon: FiEdit3,
    title: 'Sentiment Analysis',
    description: 'Understand the emotional tone of your messages with sentiment badges.',
  },
];

const steps = [
  { step: '01', title: 'Type Your Message', description: 'Enter text in the real-time analyzer editor.' },
  { step: '02', title: 'AI Analyzes Instantly', description: 'Our AI detects toxicity, fallacies, and sentiment.' },
  { step: '03', title: 'Review Highlights', description: 'Problematic text is highlighted with color-coded markers.' },
  { step: '04', title: 'Apply Rewrites', description: 'Accept AI suggestions to improve your civility score.' },
];

const techStack = [
  { icon: FiCpu, name: 'FastAPI Backend', desc: 'High-performance Python API' },
  { icon: FiGlobe, name: 'React 19 Frontend', desc: 'Modern reactive UI' },
  { icon: FiZap, name: 'Real-Time Processing', desc: 'Socket.IO streaming support' },
  { icon: FiShield, name: 'JWT Authentication', desc: 'Secure token-based auth' },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      <Navbar transparent />

      {/* Hero */}
      <section className="relative pt-32 pb-20 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-white to-primary-100 dark:from-gray-900 dark:via-surface-dark dark:to-primary-950" />
        <div className="absolute top-20 right-0 w-[500px] h-[500px] bg-primary-400/20 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-primary-600/10 rounded-full blur-3xl" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div {...fadeUp}>
            <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary-100 dark:bg-primary-900/40 text-primary-700 dark:text-primary-300 text-sm font-medium mb-6">
              <FiZap size={14} /> AI-Powered Moderation Platform
            </span>
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight mb-6">
              Communicate with{' '}
              <span className="gradient-text">Civility</span>
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
              CivilDialog detects toxic language, hate speech, and logical fallacies in real-time.
              Get AI rewrite suggestions and track your civility score.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/register">
                <Button size="lg" icon={FiArrowRight}>
                  Get Started Free
                </Button>
              </Link>
              <Link to="/demo">
                <Button size="lg" variant="secondary">
                  Try Demo
                </Button>
              </Link>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.8 }}
            className="mt-16 mx-auto max-w-4xl"
          >
            <div className="glass-card p-2 shadow-2xl shadow-primary-600/10">
              <div className="rounded-xl bg-gray-900 p-6 text-left">
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-3 h-3 rounded-full bg-red-500" />
                  <div className="w-3 h-3 rounded-full bg-amber-500" />
                  <div className="w-3 h-3 rounded-full bg-green-500" />
                  <span className="ml-2 text-xs text-gray-500">Text Analyzer</span>
                </div>
                <p className="text-gray-300 text-sm leading-relaxed">
                  I think you're{' '}
                  <span className="bg-red-500/30 text-red-300 px-1 rounded underline decoration-red-400">
                    completely wrong
                  </span>{' '}
                  and{' '}
                  <span className="bg-red-500/30 text-red-300 px-1 rounded underline decoration-red-400">
                    nobody cares
                  </span>{' '}
                  about your opinion.
                </p>
                <div className="flex items-center gap-4 mt-4 pt-4 border-t border-gray-700">
                  <div className="flex items-center gap-2">
                    <div className="w-10 h-10 rounded-full border-2 border-red-500 flex items-center justify-center text-red-400 text-sm font-bold">
                      32
                    </div>
                    <span className="text-xs text-gray-500">Civility Score</span>
                  </div>
                  <span className="px-2 py-0.5 rounded-full bg-red-500/20 text-red-300 text-xs">Negative</span>
                  <span className="px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 text-xs">Ad Hominem</span>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24 bg-white dark:bg-gray-900/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div {...fadeUp} className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Powerful Features</h2>
            <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              Everything you need to maintain civil discourse in real-time
            </p>
          </motion.div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, i) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
              >
                <Card hover className="h-full">
                  <div className="w-12 h-12 rounded-xl bg-primary-100 dark:bg-primary-900/40 flex items-center justify-center mb-4">
                    <feature.icon className="text-primary-600" size={24} />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                  <p className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed">
                    {feature.description}
                  </p>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div {...fadeUp} className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">How It Works</h2>
            <p className="text-gray-600 dark:text-gray-400">Four simple steps to better communication</p>
          </motion.div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {steps.map((step, i) => (
              <motion.div
                key={step.step}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.15 }}
                className="text-center"
              >
                <div className="w-16 h-16 rounded-2xl bg-primary-600 text-white text-xl font-bold flex items-center justify-center mx-auto mb-4">
                  {step.step}
                </div>
                <h3 className="text-lg font-semibold mb-2">{step.title}</h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm">{step.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Technology */}
      <section id="technology" className="py-24 bg-white dark:bg-gray-900/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div {...fadeUp} className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Technology Stack</h2>
            <p className="text-gray-600 dark:text-gray-400">Built with modern, production-ready technologies</p>
          </motion.div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {techStack.map((tech, i) => (
              <motion.div
                key={tech.name}
                initial={{ opacity: 0, scale: 0.95 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
              >
                <Card className="text-center">
                  <tech.icon className="text-primary-600 mx-auto mb-3" size={32} />
                  <h3 className="font-semibold mb-1">{tech.name}</h3>
                  <p className="text-sm text-gray-500">{tech.desc}</p>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* About */}
      <section id="about" className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <motion.div {...fadeUp}>
              <h2 className="text-4xl font-bold mb-6">About CivilDialog</h2>
              <p className="text-gray-600 dark:text-gray-400 leading-relaxed mb-4">
                CivilDialog was built to address the growing challenge of toxic communication online.
                Our AI-powered platform helps individuals and teams communicate more constructively
                by providing real-time feedback, rewrite suggestions, and civility scoring.
              </p>
              <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                Whether you're moderating community forums, improving team communication, or
                simply wanting to express yourself more thoughtfully, CivilDialog gives you
                the tools to succeed.
              </p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="glass-card p-8"
            >
              <div className="grid grid-cols-2 gap-6">
                {[
                  { value: '10K+', label: 'Messages Analyzed' },
                  { value: '95%', label: 'Accuracy Rate' },
                  { value: '2.8K+', label: 'Active Users' },
                  { value: '78', label: 'Avg Civility Score' },
                ].map((stat) => (
                  <div key={stat.label} className="text-center">
                    <p className="text-3xl font-bold gradient-text">{stat.value}</p>
                    <p className="text-sm text-gray-500 mt-1">{stat.label}</p>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 bg-gradient-to-r from-primary-600 to-primary-800">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold text-white mb-4">Ready to communicate better?</h2>
          <p className="text-primary-100 mb-8 text-lg">
            Join thousands of users improving their online discourse with CivilDialog.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/register">
              <Button size="lg" variant="secondary">Create Free Account</Button>
            </Link>
            <Link to="/demo">
              <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10">
                Try Demo
              </Button>
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
