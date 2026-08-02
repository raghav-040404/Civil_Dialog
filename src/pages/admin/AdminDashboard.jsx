import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { FiUsers, FiMessageSquare, FiTrendingUp, FiAlertTriangle } from 'react-icons/fi';
import { StatCard } from '../../components/ui/Card';
import { Skeleton } from '../../components/ui/Loader';
import PieChartWidget from '../../components/charts/PieChartWidget';
import BarChartWidget from '../../components/charts/BarChartWidget';
import { ActivityChart } from '../../components/charts/LineChartWidget';
import { adminService } from '../../services/userService';
import Badge from '../../components/ui/Badge';

const severityVariant = {
  Critical: 'danger',
  High: 'warning',
  Medium: 'primary',
  Low: 'default',
};

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [dailyActivity, setDailyActivity] = useState([]);
  const [sentiment, setSentiment] = useState([]);
  const [toxicWords, setToxicWords] = useState([]);
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsData, activity, sentimentData, words, reportsData] = await Promise.all([
          adminService.getStats(),
          adminService.getDailyActivity(),
          adminService.getSentimentDistribution(),
          adminService.getTopToxicWords(),
          adminService.getRecentReports(),
        ]);
        setStats(statsData);
        setDailyActivity(activity);
        setSentiment(sentimentData);
        setToxicWords(words);
        setReports(reportsData);
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
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-32" />)}
        </div>
      </div>
    );
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div className="mb-8">
        <h1 className="text-2xl sm:text-3xl font-bold">Admin Dashboard</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Platform-wide analytics and moderation overview</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard title="Total Users" value={stats.totalUsers.toLocaleString()} icon={FiUsers} color="primary" />
        <StatCard title="Total Messages" value={stats.totalMessages.toLocaleString()} icon={FiMessageSquare} color="green" />
        <StatCard title="Average Score" value={stats.averageScore} icon={FiTrendingUp} color="amber" />
        <StatCard title="Toxic Messages" value={stats.toxicMessages.toLocaleString()} icon={FiAlertTriangle} color="red" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <ActivityChart data={dailyActivity} title="Daily Activity" />
        <PieChartWidget data={sentiment} title="Sentiment Distribution" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <BarChartWidget data={toxicWords} title="Top Toxic Words" dataKey="count" xKey="word" />
      </div>

      <div className="glass-card p-6 overflow-x-auto">
        <h3 className="text-lg font-semibold mb-4">Recent Reports</h3>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 dark:border-gray-700">
              <th className="text-left py-3 px-4 font-medium text-gray-500">User</th>
              <th className="text-left py-3 px-4 font-medium text-gray-500">Description</th>
              <th className="text-left py-3 px-4 font-medium text-gray-500">Severity</th>
              <th className="text-left py-3 px-4 font-medium text-gray-500">Date</th>
            </tr>
          </thead>
          <tbody>
            {reports.map((report) => (
              <tr key={report.id} className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50">
                <td className="py-3 px-4 font-mono text-xs">{report.user}</td>
                <td className="py-3 px-4">{report.text}</td>
                <td className="py-3 px-4">
                  <Badge variant={severityVariant[report.severity] || 'default'}>{report.severity}</Badge>
                </td>
                <td className="py-3 px-4 text-gray-500">{report.date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
}
