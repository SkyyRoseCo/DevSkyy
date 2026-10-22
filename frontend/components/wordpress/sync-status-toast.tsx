'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, XCircle, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface Toast {
  id: string;
  type: 'success' | 'error';
  postId?: number;
  error?: string;
}

export function SyncStatusToast() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  useEffect(() => {
    const handleSuccess = (e: Event) => {
      const event = e as CustomEvent;
      const { resultId, postId } = event.detail;
      setToasts(prev => [...prev, { id: resultId, type: 'success', postId }]);
      setTimeout(() => setToasts(prev => prev.filter(t => t.id !== resultId)), 5000);
    };

    const handleError = (e: Event) => {
      const event = e as CustomEvent;
      const { resultId, error } = event.detail;
      setToasts(prev => [...prev, { id: resultId, type: 'error', error }]);
      setTimeout(() => setToasts(prev => prev.filter(t => t.id !== resultId)), 8000);
    };

    window.addEventListener('wp-sync-success', handleSuccess);
    window.addEventListener('wp-sync-error', handleError);

    return () => {
      window.removeEventListener('wp-sync-success', handleSuccess);
      window.removeEventListener('wp-sync-error', handleError);
    };
  }, []);

  return (
    <div className='fixed bottom-4 right-4 z-50 space-y-2'>
      <AnimatePresence>
        {toasts.map(toast => (
          <motion.div
            key={toast.id}
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 100 }}
            className={`p-4 rounded-lg shadow-lg ${
              toast.type === 'success'
                ? 'bg-green-500/10 border border-green-500/30'
                : 'bg-red-500/10 border border-red-500/30'
            }`}
          >
            <div className='flex items-center gap-3'>
              {toast.type === 'success' ? (
                <CheckCircle2 className='h-5 w-5 text-green-400' />
              ) : (
                <XCircle className='h-5 w-5 text-red-400' />
              )}
              <div>
                <p className='font-semibold'>{toast.type === 'success' ? 'Synced to WordPress' : 'Sync Failed'}</p>
                {toast.postId && (
                  <Button
                    variant='link'
                    size='sm'
                    className='p-0 h-auto text-green-400 hover:text-green-300'
                    onClick={() => {
                      const wpUrl = process.env.NEXT_PUBLIC_WORDPRESS_URL;
                      window.open(`${wpUrl}/wp-admin/post.php?post=${toast.postId}&action=edit`, '_blank');
                    }}
                  >
                    View Published Post <ExternalLink className='ml-1 h-3 w-3' />
                  </Button>
                )}
                {toast.error && <p className='text-sm text-red-300'>{toast.error}</p>}
              </div>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
