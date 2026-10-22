'use client';

/**
 * /admin/renders/review — render approval queue.
 *
 * Approve / flag / comment each OAI render. Annotations are REVERSIBLE and shared
 * with the standalone CLI board (same renders/oai/_review/review-state.json).
 * SOT promotion (making an approved render the canonical product image) is a
 * separate, irreversible CLI step — surfaced here read-only, never executed.
 */

import { useState, useEffect, useMemo, useCallback } from 'react';
import { motion } from 'motion/react';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import {
  RefreshCw,
  Search,
  ScanEye,
  CheckCircle2,
  Flag,
  AlertCircle,
  ImageOff,
  Save,
  Check,
  Terminal,
} from 'lucide-react';

interface RenderVerdict {
  passed: boolean;
  tags: string[];
  reason: string;
}

interface ReviewEntry {
  approved: boolean;
  comment: string;
  flagged: boolean;
  updated: string;
}

interface RenderRecord {
  key: string;
  slug: string;
  file: string;
  view: string;
  sku: string | null;
  name: string | null;
  verdict: RenderVerdict | null;
  review: ReviewEntry | null;
}

interface Summary {
  total: number;
  approved: number;
  flagged: number;
  pending: number;
  withVerdict: number;
}

type StatusFilter = 'all' | 'pending' | 'approved' | 'flagged';
type SaveState = 'idle' | 'saving' | 'saved' | 'error';

interface Draft {
  approved: boolean;
  flagged: boolean;
  comment: string;
}

function recordStatus(r: RenderRecord): StatusFilter {
  if (r.review?.flagged) return 'flagged';
  if (r.review?.approved) return 'approved';
  return 'pending';
}

export default function RendersReviewPage() {
  const [records, setRecords] = useState<RenderRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState('');

  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');

  // Per-render local draft + save state, keyed by record key.
  const [drafts, setDrafts] = useState<Record<string, Draft>>({});
  const [saveStates, setSaveStates] = useState<Record<string, SaveState>>({});

  const loadQueue = useCallback(async () => {
    setLoading(true);
    setLoadError('');
    try {
      const res = await fetch('/api/renders', { cache: 'no-store' });
      const json = await res.json();
      if (!res.ok || !json.success) throw new Error(json.error || `Request failed (${res.status})`);
      if (!json?.data || !Array.isArray(json.data.records)) {
        throw new Error('Unexpected response shape');
      }
      const recs = json.data.records as RenderRecord[];
      setRecords(recs);
      setDrafts(
        Object.fromEntries(
          recs.map(r => [
            r.key,
            {
              approved: r.review?.approved ?? false,
              flagged: r.review?.flagged ?? false,
              comment: r.review?.comment ?? '',
            },
          ])
        )
      );
      setSaveStates({});
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : 'Failed to load renders');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadQueue();
  }, [loadQueue]);

  const updateDraft = useCallback((key: string, patch: Partial<Draft>) => {
    setDrafts(prev => ({ ...prev, [key]: { ...prev[key], ...patch } }));
    setSaveStates(prev => ({ ...prev, [key]: 'idle' }));
  }, []);

  const isDirty = useCallback(
    (r: RenderRecord): boolean => {
      const d = drafts[r.key];
      if (!d) return false;
      return (
        d.approved !== (r.review?.approved ?? false) ||
        d.flagged !== (r.review?.flagged ?? false) ||
        d.comment !== (r.review?.comment ?? '')
      );
    },
    [drafts]
  );

  const save = useCallback(
    async (r: RenderRecord) => {
      const d = drafts[r.key];
      if (!d) return;
      setSaveStates(prev => ({ ...prev, [r.key]: 'saving' }));
      try {
        const res = await fetch('/api/renders/review', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            slug: r.slug,
            file: r.file,
            approved: d.approved,
            flagged: d.flagged,
            comment: d.comment,
          }),
        });
        const json = await res.json();
        if (!res.ok || !json.success) throw new Error(json.error || `Save failed (${res.status})`);
        const entry = json.data.entry as ReviewEntry;
        setRecords(prev => prev.map(x => (x.key === r.key ? { ...x, review: entry } : x)));
        setSaveStates(prev => ({ ...prev, [r.key]: 'saved' }));
      } catch {
        setSaveStates(prev => ({ ...prev, [r.key]: 'error' }));
      }
    },
    [drafts]
  );

  // Summary is fully derived from records — no separate state to keep in sync.
  const summary = useMemo<Summary>(
    () => ({
      total: records.length,
      approved: records.filter(r => r.review?.approved).length,
      flagged: records.filter(r => r.review?.flagged).length,
      pending: records.filter(r => !r.review || (!r.review.approved && !r.review.flagged)).length,
      withVerdict: records.filter(r => r.verdict).length,
    }),
    [records]
  );

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return records.filter(r => {
      if (statusFilter !== 'all' && recordStatus(r) !== statusFilter) return false;
      if (!q) return true;
      return (
        r.slug.toLowerCase().includes(q) ||
        r.file.toLowerCase().includes(q) ||
        (r.sku ?? '').toLowerCase().includes(q) ||
        (r.name ?? '').toLowerCase().includes(q)
      );
    });
  }, [records, search, statusFilter]);

  const grouped = useMemo(() => {
    const map = new Map<string, RenderRecord[]>();
    for (const r of filtered) {
      const arr = map.get(r.slug) ?? [];
      arr.push(r);
      map.set(r.slug, arr);
    }
    return Array.from(map.entries());
  }, [filtered]);

  return (
    <div className='container mx-auto space-y-6 py-8'>
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
        <div className='mb-6 flex items-center justify-between'>
          <div>
            <h1 className='font-display luxury-text-gradient mb-2 flex items-center gap-3 text-4xl'>
              <ScanEye className='h-8 w-8 text-rose-400' />
              Renders Review
            </h1>
            <p className='text-gray-400'>Approve or flag product renders before they&apos;re promoted to the SOT.</p>
          </div>
          <Button onClick={loadQueue} variant='outline' disabled={loading} className='border-gray-700 text-gray-300'>
            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Reload
          </Button>
        </div>

        {records.length > 0 && (
          <div className='mb-6 grid grid-cols-2 gap-3 sm:grid-cols-5'>
            <StatCard label='Total' value={summary.total} tone='gray' />
            <StatCard label='Pending' value={summary.pending} tone='amber' />
            <StatCard label='Approved' value={summary.approved} tone='green' />
            <StatCard label='Flagged' value={summary.flagged} tone='rose' />
            <StatCard label='QC scored' value={summary.withVerdict} tone='gray' />
          </div>
        )}

        <PromotionNote />

        {loadError && (
          <div className='mb-6 flex items-center gap-3 rounded-lg border border-red-500/30 bg-red-500/10 p-4'>
            <AlertCircle className='h-5 w-5 text-red-400' />
            <p className='text-red-400'>{loadError}</p>
          </div>
        )}

        <div className='mb-6 flex flex-col gap-3 sm:flex-row'>
          <div className='relative flex-1'>
            <Search className='absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500' />
            <Input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder='Search slug, SKU, name, file…'
              className='border-gray-700 bg-gray-800 pl-9'
            />
          </div>
          <select
            value={statusFilter}
            onChange={e => setStatusFilter(e.target.value as StatusFilter)}
            className='rounded-md border border-gray-700 bg-gray-800 px-3 py-2 text-sm'
          >
            <option value='all'>All statuses</option>
            <option value='pending'>Pending</option>
            <option value='approved'>Approved</option>
            <option value='flagged'>Flagged</option>
          </select>
        </div>

        {loading && <p className='p-4 text-sm text-gray-500'>Loading renders…</p>}
        {!loading && filtered.length === 0 && (
          <p className='p-8 text-center text-sm text-gray-500'>No renders match.</p>
        )}

        <div className='space-y-6'>
          {grouped.map(([slug, recs]) => (
            <Card key={slug} className='border-gray-800 bg-gray-900'>
              <CardHeader className='pb-3'>
                <CardTitle className='flex items-center gap-2 text-base'>
                  <span className='font-mono text-gray-300'>{slug}</span>
                  {recs[0]?.sku && (
                    <Badge variant='outline' className='border-gray-700 font-mono text-xs text-gray-400'>
                      {recs[0].sku}
                    </Badge>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent className='grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3'>
                {recs.map(r => (
                  <RenderCard
                    key={r.key}
                    record={r}
                    draft={drafts[r.key]}
                    dirty={isDirty(r)}
                    saveState={saveStates[r.key] ?? 'idle'}
                    onChange={patch => updateDraft(r.key, patch)}
                    onSave={() => save(r)}
                  />
                ))}
              </CardContent>
            </Card>
          ))}
        </div>
      </motion.div>
    </div>
  );
}

function StatCard({ label, value, tone }: { label: string; value: number; tone: 'gray' | 'amber' | 'green' | 'rose' }) {
  const toneClass =
    tone === 'amber'
      ? 'text-amber-300'
      : tone === 'green'
        ? 'text-green-300'
        : tone === 'rose'
          ? 'text-rose-300'
          : 'text-gray-200';
  return (
    <div className='rounded-lg border border-gray-800 bg-gray-900/60 p-3'>
      <div className={`text-2xl font-semibold ${toneClass}`}>{value}</div>
      <div className='text-xs text-gray-500'>{label}</div>
    </div>
  );
}

function PromotionNote() {
  return (
    <div className='mb-6 rounded-lg border border-rose-500/20 bg-rose-500/5 p-4'>
      <div className='mb-2 flex items-center gap-2 text-sm font-medium text-rose-300'>
        <Terminal className='h-4 w-4' />
        Approving ≠ promoting to SOT
      </div>
      <p className='text-sm text-gray-400'>
        Approve / flag here are reversible annotations (shared with the CLI board). Making an approved render the
        canonical product image is a separate, irreversible step — run it from the CLI:
      </p>
      <pre className='mt-2 overflow-x-auto rounded bg-gray-950 p-3 font-mono text-xs text-gray-400'>
        {`python3 scripts/stage_review.py <sku>
python3 -c "from skyyrose.core.review import approve; approve('<sku>')"
make sot-manifest`}
      </pre>
    </div>
  );
}

function RenderCard({
  record,
  draft,
  dirty,
  saveState,
  onChange,
  onSave,
}: {
  record: RenderRecord;
  draft: Draft | undefined;
  dirty: boolean;
  saveState: SaveState;
  onChange: (patch: Partial<Draft>) => void;
  onSave: () => void;
}) {
  if (!draft) return null;
  return (
    <div className='flex flex-col gap-3 rounded-lg border border-gray-800 bg-gray-950/40 p-3'>
      <RenderImage slug={record.slug} file={record.file} alt={`${record.slug} ${record.view}`} />

      <div className='flex items-center justify-between'>
        <span className='font-mono text-xs text-gray-400'>{record.view}</span>
        <VerdictBadge verdict={record.verdict} />
      </div>

      <div className='flex flex-wrap gap-4'>
        <label className='flex items-center gap-2 text-sm text-gray-300'>
          <Switch checked={draft.approved} onCheckedChange={v => onChange({ approved: v })} />
          <span className='flex items-center gap-1'>
            <CheckCircle2 className='h-3.5 w-3.5 text-green-400' /> Approved
          </span>
        </label>
        <label className='flex items-center gap-2 text-sm text-gray-300'>
          <Switch checked={draft.flagged} onCheckedChange={v => onChange({ flagged: v })} />
          <span className='flex items-center gap-1'>
            <Flag className='h-3.5 w-3.5 text-rose-400' /> Flag
          </span>
        </label>
      </div>

      <Textarea
        value={draft.comment}
        onChange={e => onChange({ comment: e.target.value })}
        placeholder="What's wrong (or right) with this render…"
        rows={2}
        className='border-gray-700 bg-gray-800 text-sm'
      />

      <div className='flex items-center justify-between'>
        <SaveLabel saveState={saveState} updated={record.review?.updated} />
        <Button
          size='sm'
          onClick={onSave}
          disabled={!dirty || saveState === 'saving'}
          className='bg-rose-500 hover:bg-rose-600 disabled:opacity-40'
        >
          {saveState === 'saving' ? (
            <RefreshCw className='mr-1 h-3.5 w-3.5 animate-spin' />
          ) : saveState === 'saved' && !dirty ? (
            <Check className='mr-1 h-3.5 w-3.5' />
          ) : (
            <Save className='mr-1 h-3.5 w-3.5' />
          )}
          Save
        </Button>
      </div>
    </div>
  );
}

function VerdictBadge({ verdict }: { verdict: RenderVerdict | null }) {
  if (!verdict) {
    return (
      <Badge variant='outline' className='border-gray-700 text-xs text-gray-500'>
        no QC record
      </Badge>
    );
  }
  if (verdict.passed) {
    return <Badge className='bg-green-500/20 text-xs text-green-300'>QC pass</Badge>;
  }
  const tag = verdict.tags[0] ?? 'fail';
  return (
    <Badge className='bg-red-500/20 text-xs text-red-300' title={verdict.reason}>
      QC fail · {tag}
    </Badge>
  );
}

function SaveLabel({ saveState, updated }: { saveState: SaveState; updated?: string }) {
  if (saveState === 'error') {
    return <span className='text-xs text-red-400'>save failed</span>;
  }
  if (saveState === 'saved') {
    return <span className='text-xs text-green-500'>saved</span>;
  }
  if (updated) {
    return <span className='text-xs text-gray-600'>updated {new Date(updated).toLocaleDateString()}</span>;
  }
  return <span className='text-xs text-gray-600'>not reviewed</span>;
}

function RenderImage({ slug, file, alt }: { slug: string; file: string; alt: string }) {
  const [broken, setBroken] = useState(false);
  const src = `/api/renders/image?slug=${encodeURIComponent(slug)}&file=${encodeURIComponent(file)}`;

  if (broken) {
    return (
      <div className='flex aspect-[2/3] items-center justify-center rounded-md border border-gray-800 bg-gray-800/40'>
        <ImageOff className='h-6 w-6 text-gray-600' />
      </div>
    );
  }
  return (
    // Render PNGs are streamed from disk by /api/renders/image (outside public/),
    // so next/image can't optimize them — a plain <img> with onError fallback is
    // the correct tool here.
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={src}
      alt={alt}
      loading='lazy'
      onError={() => setBroken(true)}
      className='aspect-[2/3] w-full rounded-md border border-gray-800 bg-black object-cover'
    />
  );
}
