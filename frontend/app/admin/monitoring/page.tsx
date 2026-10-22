'use client';

import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Activity,
  AlertCircle,
  CheckCircle2,
  Clock,
  TrendingUp,
  Zap,
  RefreshCw,
  Cpu,
  HardDrive,
  MemoryStick,
} from 'lucide-react';
import { useMonitoring } from '@/hooks/useMonitoring';
import type { ServiceHealthStatus, HealthEvent } from '@/lib/api/types';

function formatTimestamp(iso: string): string {
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return new Date(iso).toLocaleDateString();
}

function ServiceStatusIcon({ status }: { status: ServiceHealthStatus['status'] }) {
  if (status === 'healthy') return <CheckCircle2 className='h-5 w-5 text-green-400' />;
  if (status === 'degraded') return <AlertCircle className='h-5 w-5 text-yellow-400' />;
  return <AlertCircle className='h-5 w-5 text-red-400' />;
}

function ServiceStatusBadge({ status }: { status: ServiceHealthStatus['status'] }) {
  const cls = {
    healthy: 'bg-green-500/10 text-green-400 border-green-500/30',
    degraded: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30',
    down: 'bg-red-500/10 text-red-400 border-red-500/30',
  }[status];
  return <Badge className={`${cls} border`}>{status.charAt(0).toUpperCase() + status.slice(1)}</Badge>;
}

function CircuitBreakerBadge({ state }: { state: ServiceHealthStatus['circuit_breaker'] }) {
  const cls = {
    closed: 'bg-green-500/10 text-green-400 border-green-500/30',
    'half-open': 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30',
    open: 'bg-red-500/10 text-red-400 border-red-500/30',
  }[state];
  const label =
    state === 'closed' ? 'Closed (Normal)' : state === 'half-open' ? 'Half-Open (Testing)' : 'Open (Failed)';
  return <Badge className={`${cls} border`}>{label}</Badge>;
}

function ActivityIcon({ type }: { type: HealthEvent['type'] }) {
  if (type === 'success') return <CheckCircle2 className='h-4 w-4 text-green-400' />;
  if (type === 'warning') return <AlertCircle className='h-4 w-4 text-yellow-400' />;
  return <AlertCircle className='h-4 w-4 text-red-400' />;
}

function ServiceCardSkeleton() {
  return (
    <Card className='bg-gray-900 border-gray-800 animate-pulse'>
      <CardContent className='pt-6'>
        <div className='h-5 w-32 bg-gray-700 rounded mb-4' />
        <div className='space-y-2'>
          <div className='h-4 w-full bg-gray-800 rounded' />
          <div className='h-4 w-3/4 bg-gray-800 rounded' />
          <div className='h-4 w-1/2 bg-gray-800 rounded' />
        </div>
      </CardContent>
    </Card>
  );
}

export default function MonitoringPage() {
  const { data, loading, error, refresh } = useMonitoring();

  return (
    <div className='container mx-auto py-8 space-y-8'>
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <div className='flex items-center justify-between mb-8'>
          <div>
            <h1 className='font-display text-4xl luxury-text-gradient mb-2'>System Monitoring</h1>
            <p className='text-gray-400'>Real-time health and performance metrics</p>
          </div>
          <Button onClick={refresh} disabled={loading} variant='outline' className='border-gray-700'>
            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            {loading ? 'Refreshing...' : 'Refresh'}
          </Button>
        </div>

        {error && (
          <div className='mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm'>{error}</div>
        )}

        {/* Service Health Grid */}
        <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8'>
          {loading && !data
            ? Array.from({ length: 4 }).map((_, i) => <ServiceCardSkeleton key={i} />)
            : (data?.services ?? []).map((service, index) => (
                <motion.div
                  key={service.name}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                >
                  <Card className='bg-gray-900 border-gray-800'>
                    <CardContent className='pt-6'>
                      <div className='flex items-center justify-between mb-4'>
                        <div className='flex items-center gap-3'>
                          <ServiceStatusIcon status={service.status} />
                          <h3 className='font-semibold'>{service.name}</h3>
                        </div>
                        <ServiceStatusBadge status={service.status} />
                      </div>
                      <div className='space-y-2 text-sm'>
                        <div className='flex justify-between'>
                          <span className='text-gray-400'>Uptime</span>
                          <span className='font-semibold'>{service.uptime_pct}%</span>
                        </div>
                        <div className='flex justify-between'>
                          <span className='text-gray-400'>Response Time</span>
                          <span className='font-semibold'>
                            {service.response_ms != null ? `${service.response_ms}ms` : '—'}
                          </span>
                        </div>
                        <div className='flex justify-between'>
                          <span className='text-gray-400'>Last Check</span>
                          <span className='text-xs text-gray-500'>{formatTimestamp(service.last_check)}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
        </div>

        <div className='grid grid-cols-1 lg:grid-cols-2 gap-8'>
          {/* Circuit Breaker Status */}
          <Card className='bg-gray-900 border-gray-800'>
            <CardHeader>
              <CardTitle className='flex items-center gap-2'>
                <Zap className='h-5 w-5 text-rose-400' />
                Circuit Breaker Status
              </CardTitle>
              <CardDescription>Self-healing service protection</CardDescription>
            </CardHeader>
            <CardContent>
              <div className='space-y-4'>
                {(data?.services ?? []).map(svc => (
                  <div key={svc.name} className='flex items-center justify-between p-4 bg-gray-800/50 rounded-lg'>
                    <div>
                      <p className='font-semibold mb-1'>{svc.name}</p>
                      <p className='text-sm text-gray-400'>{svc.uptime_pct}% uptime</p>
                    </div>
                    <CircuitBreakerBadge state={svc.circuit_breaker} />
                  </div>
                ))}
                {!loading && !data && <p className='text-sm text-gray-500 text-center py-4'>No data</p>}
              </div>
            </CardContent>
          </Card>

          {/* System Metrics */}
          <Card className='bg-gray-900 border-gray-800'>
            <CardHeader>
              <CardTitle className='flex items-center gap-2'>
                <Activity className='h-5 w-5 text-rose-400' />
                System Metrics
              </CardTitle>
              <CardDescription>Performance and resource usage</CardDescription>
            </CardHeader>
            <CardContent>
              <div className='space-y-4'>
                <div className='flex items-center justify-between p-4 bg-gray-800/50 rounded-lg'>
                  <div className='flex items-center gap-3'>
                    <TrendingUp className='h-5 w-5 text-green-400' />
                    <div>
                      <p className='font-semibold'>API Requests/min</p>
                      <p className='text-sm text-gray-400'>Last 60 seconds</p>
                    </div>
                  </div>
                  <span className='text-2xl font-bold'>{data ? data.system.req_per_min : '—'}</span>
                </div>

                <div className='flex items-center justify-between p-4 bg-gray-800/50 rounded-lg'>
                  <div className='flex items-center gap-3'>
                    <CheckCircle2 className='h-5 w-5 text-green-400' />
                    <div>
                      <p className='font-semibold'>Success Rate</p>
                      <p className='text-sm text-gray-400'>Last 60 seconds</p>
                    </div>
                  </div>
                  <span className='text-2xl font-bold'>{data ? `${data.system.success_rate}%` : '—'}</span>
                </div>

                <div className='flex items-center justify-between p-4 bg-gray-800/50 rounded-lg'>
                  <div className='flex items-center gap-3'>
                    <Clock className='h-5 w-5 text-blue-400' />
                    <div>
                      <p className='font-semibold'>Avg Response Time</p>
                      <p className='text-sm text-gray-400'>Last 60 seconds</p>
                    </div>
                  </div>
                  <span className='text-2xl font-bold'>{data ? `${data.system.avg_latency_ms}ms` : '—'}</span>
                </div>

                <div className='grid grid-cols-3 gap-3 pt-2'>
                  <div className='p-3 bg-gray-800/50 rounded-lg text-center'>
                    <Cpu className='h-4 w-4 text-rose-400 mx-auto mb-1' />
                    <p className='text-xs text-gray-400'>CPU</p>
                    <p className='font-semibold text-sm'>{data ? `${data.system.cpu_pct}%` : '—'}</p>
                  </div>
                  <div className='p-3 bg-gray-800/50 rounded-lg text-center'>
                    <MemoryStick className='h-4 w-4 text-rose-400 mx-auto mb-1' />
                    <p className='text-xs text-gray-400'>Memory</p>
                    <p className='font-semibold text-sm'>{data ? `${data.system.memory_pct}%` : '—'}</p>
                  </div>
                  <div className='p-3 bg-gray-800/50 rounded-lg text-center'>
                    <HardDrive className='h-4 w-4 text-rose-400 mx-auto mb-1' />
                    <p className='text-xs text-gray-400'>Disk</p>
                    <p className='font-semibold text-sm'>{data ? `${data.system.disk_pct}%` : '—'}</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Activity Log */}
        <Card className='bg-gray-900 border-gray-800 mt-8'>
          <CardHeader>
            <CardTitle className='flex items-center gap-2'>
              <Activity className='h-5 w-5 text-rose-400' />
              Recent Activity
            </CardTitle>
            <CardDescription>Latest health check events</CardDescription>
          </CardHeader>
          <CardContent>
            <div className='space-y-3'>
              {(data?.events ?? []).map(event => (
                <div
                  key={event.id}
                  className='flex items-start gap-3 p-4 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition-colors'
                >
                  <ActivityIcon type={event.type} />
                  <div className='flex-1'>
                    <div className='flex items-center justify-between mb-1'>
                      <p className='font-semibold'>{event.service}</p>
                      <span className='text-xs text-gray-500'>{formatTimestamp(event.timestamp)}</span>
                    </div>
                    <p className='text-sm text-gray-400'>{event.message}</p>
                  </div>
                </div>
              ))}
              {!loading && (data?.events ?? []).length === 0 && (
                <p className='text-sm text-gray-500 text-center py-4'>
                  No events yet — check back after first health poll
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
