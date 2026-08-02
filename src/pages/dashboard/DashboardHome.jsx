import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { FiTrendingUp, FiMessageSquare, FiShield, FiBarChart2 } from 'react-icons/fi';
import { StatCard } from '../../components/ui/Card';
import { PageLoader, Skeleton } from '../../components/ui/Loader';
import dashboardService from '../../services/dashboardService';
import { Link } from 'react-router-dom';
import Button from '../../components/ui/Button';

export default function DashboardHome() {
  const [stats, setStats] = useState(null);
  const [activity, setActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsData, activityData] = await Promise.all([
          dashboardService.getStats(),
          dashboardService.getRecentActivity(),
        ]);
        setStats(statsData);
        setActivity(activityData);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div>
        <Skeleton className="h-8 w-48 mb-8" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-8 gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold">Dashboard</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Overview of your communication analytics
          </p>
        </div>
        <Link to="/dashboard/analyzer">
          <Button icon={FiMessageSquare}>Open Analyzer</Button>
        </Link>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Average Civility Score"
          value={stats.averageCivilityScore}
          change={5}
          icon={FiTrendingUp}
          color="primary"
        />
        <StatCard
          title="Messages Analysed"
          value={stats.messagesAnalysed.toLocaleString()}
          change={12}
          icon={FiMessageSquare}
          color="green"
        />
        <StatCard
          title="Toxic Messages Prevented"
          value={stats.toxicMessagesPrevented}
          change={8}
          icon={FiShield}
          color="red"
        />
        <StatCard
          title="Overall Improvement"
          value={`${stats.overallImprovement}%`}
          change={stats.overallImprovement}
          icon={FiBarChart2}
          color="amber"
        />
      </div>

      <div className="glass-card p-6">
        <h2 className="text-lg font-semibold mb-4">Recent Activity</h2>
        <div className="space-y-4">
          {activity.map((item) => (
            <div
              key={item.id}
              className="flex items-center justify-between py-3 border-b border-gray-100 dark:border-gray-800 last:border-0"
            >
              <div>
                <p className="font-medium text-sm">{item.action}</p>
                <p className="text-xs text-gray-500 mt-0.5">{item.time}</p>
              </div>
              <span
                className={`text-sm font-semibold ${
                  item.score >= 70 ? 'text-green-500' : item.score >= 40 ? 'text-amber-500' : 'text-red-500'
                }`}
              >
                Score: {item.score}
              </span>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
