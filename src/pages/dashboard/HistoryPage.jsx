import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { FiSearch, FiTrash2, FiEye, FiFilter } from 'react-icons/fi';
import Input from '../../components/ui/Input';
import Select from '../../components/ui/Select';
import Button from '../../components/ui/Button';
import Modal from '../../components/ui/Modal';
import { SentimentBadge } from '../../components/ui/Badge';
import { Skeleton } from '../../components/ui/Loader';
import historyService from '../../services/historyService';
import { formatDate, truncateText, getCivilityColor } from '../../utils/helpers';
import { useToast } from '../../context/ToastContext';
import { ITEMS_PER_PAGE } from '../../utils/constants';

export default function HistoryPage() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState(null);
  const [deleteId, setDeleteId] = useState(null);
  const { addToast } = useToast();

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const data = await historyService.getHistory({ search, filter, page, limit: ITEMS_PER_PAGE });
      setItems(data.items);
      setTotal(data.total);
      setTotalPages(data.totalPages);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [search, filter, page]);

  const handleDelete = async (id) => {
    try {
      await historyService.deleteHistory(id);
      addToast('History item deleted', 'success');
      setDeleteId(null);
      fetchHistory();
    } catch {
      addToast('Failed to delete', 'error');
    }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div className="mb-8">
        <h1 className="text-2xl sm:text-3xl font-bold">Analysis History</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          View and manage your previous text analyses
        </p>
      </div>

      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="flex-1">
          <Input
            placeholder="Search analyses..."
            icon={FiSearch}
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          />
        </div>
        <Select
          options={[
            { value: 'all', label: 'All' },
            { value: 'toxic', label: 'Toxic' },
            { value: 'positive', label: 'Positive' },
          ]}
          value={filter}
          onChange={(e) => { setFilter(e.target.value); setPage(1); }}
          className="w-full sm:w-40"
        />
      </div>

      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-20" />)}
        </div>
      ) : items.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <FiFilter className="mx-auto text-gray-400 mb-4" size={40} />
          <p className="text-gray-500">No analyses found</p>
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass-card p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center gap-4"
            >
              <div
                className="w-12 h-12 rounded-xl flex items-center justify-center text-lg font-bold shrink-0"
                style={{ backgroundColor: `${getCivilityColor(item.score)}20`, color: getCivilityColor(item.score) }}
              >
                {item.score}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{truncateText(item.text, 80)}</p>
                <div className="flex items-center gap-3 mt-1">
                  <SentimentBadge sentiment={item.sentiment} />
                  <span className="text-xs text-gray-500">{formatDate(item.createdAt)}</span>
                </div>
              </div>
              <div className="flex gap-2 shrink-0">
                <Button size="sm" variant="ghost" icon={FiEye} onClick={() => setSelectedItem(item)}>
                  View
                </Button>
                <Button size="sm" variant="ghost" icon={FiTrash2} onClick={() => setDeleteId(item.id)}>
                  Delete
                </Button>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-6">
          <p className="text-sm text-gray-500">
            Showing {items.length} of {total} results
          </p>
          <div className="flex gap-2">
            <Button size="sm" variant="secondary" disabled={page <= 1} onClick={() => setPage(page - 1)}>
              Previous
            </Button>
            <Button size="sm" variant="secondary" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>
              Next
            </Button>
          </div>
        </div>
      )}

      <Modal isOpen={!!selectedItem} onClose={() => setSelectedItem(null)} title="Analysis Details" size="lg">
        {selectedItem && (
          <div className="space-y-4">
            <div>
              <p className="text-sm font-medium text-gray-500 mb-1">Original Text</p>
              <p className="p-4 rounded-xl bg-gray-50 dark:bg-gray-800 text-sm leading-relaxed">{selectedItem.text}</p>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div>
                <p className="text-xs text-gray-500">Score</p>
                <p className="text-2xl font-bold" style={{ color: getCivilityColor(selectedItem.score) }}>
                  {selectedItem.score}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Toxicity</p>
                <p className="text-lg font-semibold">{Math.round(selectedItem.toxicity * 100)}%</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Sentiment</p>
                <SentimentBadge sentiment={selectedItem.sentiment} />
              </div>
              <div>
                <p className="text-xs text-gray-500">Date</p>
                <p className="text-sm">{formatDate(selectedItem.createdAt)}</p>
              </div>
            </div>
            {selectedItem.fallacies?.length > 0 && (
              <div>
                <p className="text-sm font-medium text-gray-500 mb-2">Fallacies</p>
                <div className="flex flex-wrap gap-2">
                  {selectedItem.fallacies.map((f) => (
                    <span key={f} className="px-2 py-1 rounded-full bg-amber-100 dark:bg-amber-900/30 text-amber-800 dark:text-amber-300 text-xs">
                      {f}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </Modal>

      <Modal isOpen={!!deleteId} onClose={() => setDeleteId(null)} title="Delete Analysis">
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Are you sure you want to delete this analysis? This action cannot be undone.
        </p>
        <div className="flex gap-3 justify-end">
          <Button variant="secondary" onClick={() => setDeleteId(null)}>Cancel</Button>
          <Button variant="danger" onClick={() => handleDelete(deleteId)}>Delete</Button>
        </div>
      </Modal>
    </motion.div>
  );
}
