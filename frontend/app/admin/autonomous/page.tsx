'use client'

import Link from 'next/link'

import { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog'
import {
    Activity,
    Play,
    Square,
    RefreshCw,
    Loader2,
    AlertTriangle,
    CheckCircle2,
    XCircle,
    Clock,
} from 'lucide-react'
import { useAutonomous } from '@/hooks/useAutonomous'
import type { AutonomousOperation, AutonomousHistoryEntry } from '@/lib/api/types'

function StatusBadge({ status }: { status: AutonomousOperation['status'] }) {
    switch (status) {
        case 'running':
            return <Badge className="bg-green-500/20 text-green-400 border-green-500/30">Running</Badge>
        case 'stopped':
            return <Badge className="bg-gray-500/20 text-gray-400 border-gray-500/30">Stopped</Badge>
        case 'error':
            return <Badge className="bg-red-500/20 text-red-400 border-red-500/30">Error</Badge>
    }
}

function StatusIcon({ status }: { status: AutonomousOperation['status'] }) {
    switch (status) {
        case 'running':
            return <CheckCircle2 className="h-5 w-5 text-green-400 shrink-0" />
        case 'stopped':
            return <XCircle className="h-5 w-5 text-gray-500 shrink-0" />
        case 'error':
            return <AlertTriangle className="h-5 w-5 text-red-400 shrink-0" />
    }
}

function HistoryActionBadge({ action }: { action: AutonomousHistoryEntry['action'] }) {
    switch (action) {
        case 'start':
            return <Badge className="bg-green-500/20 text-green-400 text-xs shrink-0">started</Badge>
        case 'stop':
            return <Badge className="bg-gray-500/20 text-gray-400 text-xs shrink-0">stopped</Badge>
        case 'error':
            return <Badge className="bg-red-500/20 text-red-400 text-xs shrink-0">error</Badge>
    }
}

export default function AutonomousAgentsPage() {
    const { operations, total, loading, error, actionLoading, refresh, start, stop, fetchHistory } =
        useAutonomous()
    const [confirmStop, setConfirmStop] = useState<AutonomousOperation | null>(null)
    const [history, setHistory] = useState<AutonomousHistoryEntry[]>([])
    const [historyLoading, setHistoryLoading] = useState(false)

    const loadHistory = useCallback(
        async (ops: AutonomousOperation[]) => {
            if (ops.length === 0) return
            setHistoryLoading(true)
            try {
                const results = await Promise.all(ops.map((op) => fetchHistory(op.id, 20)))
                const merged = results
                    .flat()
                    .sort(
                        (a, b) =>
                            new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime(),
                    )
                    .slice(0, 50)
                setHistory(merged)
            } catch {
                // history is non-critical
            } finally {
                setHistoryLoading(false)
            }
        },
        [fetchHistory],
    )

    useEffect(() => {
        if (operations.length > 0) {
            void loadHistory(operations)
        }
    }, [operations, loadHistory])

    const handleStartStop = (op: AutonomousOperation) => {
        if (op.status === 'running') {
            if (op.critical) {
                setConfirmStop(op)
            } else {
                void stop(op.id)
            }
        } else {
            void start(op.id)
        }
    }

    const confirmAndStop = async () => {
        if (!confirmStop) return
        await stop(confirmStop.id)
        setConfirmStop(null)
    }

    const handleRefresh = () => {
        void refresh()
        void loadHistory(operations)
    }

    const runningCount = operations.filter((o) => o.status === 'running').length
    const errorCount = operations.filter((o) => o.status === 'error').length

    return (
        <div className="container mx-auto py-8 space-y-8">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="font-display text-4xl luxury-text-gradient">
                        Autonomous Agents
                    </h1>
                    <p className="text-gray-400 mt-2">
                        Monitor and control autonomous operations across the DevSkyy platform.
                    </p>
                </div>
                <Button
                    variant="outline"
                    size="sm"
                    onClick={handleRefresh}
                    disabled={loading}
                    className="gap-2"
                >
                    <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                    Refresh
                </Button>
            </div>

            {error && (
                <div className="rounded-lg border border-red-800 bg-red-900/20 p-4 text-red-400 text-sm">
                    {error}
                </div>
            )}

            <Link href="/admin/god-mode" className="inline-block rounded bg-rose-600 px-4 py-3 font-semibold">Run a God Mode mission</Link>

            {/* Summary */}
            <div className="grid grid-cols-3 gap-4">
                <Card>
                    <CardContent className="pt-6">
                        <div className="text-2xl font-bold text-white">{total}</div>
                        <div className="text-sm text-gray-400">Total Operations</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="pt-6">
                        <div className="text-2xl font-bold text-green-400">{runningCount}</div>
                        <div className="text-sm text-gray-400">Running</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="pt-6">
                        <div className="text-2xl font-bold text-red-400">{errorCount}</div>
                        <div className="text-sm text-gray-400">Errors</div>
                    </CardContent>
                </Card>
            </div>

            {/* Operations */}
            <div className="space-y-3">
                <div className="flex items-center gap-2">
                    <Activity className="h-5 w-5 text-purple-400" />
                    <h2 className="text-lg font-semibold">Operations</h2>
                </div>

                {loading && operations.length === 0 ? (
                    <div className="flex items-center justify-center py-12 text-gray-500">
                        <Loader2 className="h-6 w-6 animate-spin mr-2" />
                        Loading operations&hellip;
                    </div>
                ) : (
                    <div className="grid gap-3">
                        {operations.map((op) => {
                            const isActing = actionLoading === op.id
                            const isRunning = op.status === 'running'
                            return (
                                <Card key={op.id}>
                                    <CardContent className="py-4">
                                        <div className="flex items-center justify-between gap-4">
                                            <div className="flex items-start gap-3 min-w-0">
                                                <StatusIcon status={op.status} />
                                                <div className="min-w-0">
                                                    <div className="flex items-center gap-2 flex-wrap">
                                                        <p className="font-semibold">{op.name}</p>
                                                        {op.critical && (
                                                            <Badge className="bg-orange-500/20 text-orange-400 border-orange-500/30 text-xs">
                                                                critical
                                                            </Badge>
                                                        )}
                                                        <StatusBadge status={op.status} />
                                                    </div>
                                                    <p className="text-sm text-gray-400 mt-0.5">
                                                        {op.description}
                                                    </p>
                                                    {op.last_event && (
                                                        <p className="text-xs text-gray-600 mt-1">
                                                            {op.last_event}
                                                            {op.last_event_at && (
                                                                <span className="ml-1">
                                                                    &mdash;{' '}
                                                                    {new Date(
                                                                        op.last_event_at,
                                                                    ).toLocaleTimeString()}
                                                                </span>
                                                            )}
                                                        </p>
                                                    )}
                                                </div>
                                            </div>
                                            <Button
                                                variant={isRunning ? 'destructive' : 'default'}
                                                size="sm"
                                                onClick={() => handleStartStop(op)}
                                                disabled={isActing}
                                                className="gap-2 min-w-[90px] shrink-0"
                                            >
                                                {isActing ? (
                                                    <Loader2 className="h-4 w-4 animate-spin" />
                                                ) : isRunning ? (
                                                    <>
                                                        <Square className="h-4 w-4" />
                                                        Stop
                                                    </>
                                                ) : (
                                                    <>
                                                        <Play className="h-4 w-4" />
                                                        Start
                                                    </>
                                                )}
                                            </Button>
                                        </div>
                                    </CardContent>
                                </Card>
                            )
                        })}
                    </div>
                )}
            </div>

            {/* Activity Log */}
            <Card>
                <CardHeader>
                    <div className="flex items-center gap-2">
                        <Clock className="h-5 w-5 text-blue-400" />
                        <CardTitle>Activity Log</CardTitle>
                    </div>
                </CardHeader>
                <CardContent>
                    {historyLoading ? (
                        <div className="flex items-center gap-2 text-gray-500 py-4">
                            <Loader2 className="h-4 w-4 animate-spin" />
                            Loading history&hellip;
                        </div>
                    ) : history.length === 0 ? (
                        <p className="text-gray-500 py-4">No activity recorded yet.</p>
                    ) : (
                        <div className="space-y-2">
                            {history.map((entry) => (
                                <div
                                    key={entry.id}
                                    className="flex items-start gap-3 p-3 rounded-lg bg-gray-900/50 border border-gray-800"
                                >
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2 flex-wrap">
                                            <span className="font-medium text-sm">
                                                {entry.operation_name}
                                            </span>
                                            <HistoryActionBadge action={entry.action} />
                                            <span className="text-xs text-gray-500 ml-auto">
                                                {new Date(entry.timestamp).toLocaleString()}
                                            </span>
                                        </div>
                                        <p className="text-xs text-gray-400 mt-0.5 truncate">
                                            {entry.message}
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Critical op confirmation dialog */}
            <Dialog
                open={confirmStop !== null}
                onOpenChange={(open) => {
                    if (!open) setConfirmStop(null)
                }}
            >
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle className="flex items-center gap-2">
                            <AlertTriangle className="h-5 w-5 text-orange-400" />
                            Stop Critical Operation
                        </DialogTitle>
                        <DialogDescription>
                            <strong>{confirmStop?.name}</strong> is marked as critical. Stopping it
                            may affect platform reliability. Are you sure?
                        </DialogDescription>
                    </DialogHeader>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setConfirmStop(null)}>
                            Cancel
                        </Button>
                        <Button
                            variant="destructive"
                            onClick={() => void confirmAndStop()}
                            disabled={actionLoading !== null}
                        >
                            {actionLoading ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                                'Stop Operation'
                            )}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    )
}
