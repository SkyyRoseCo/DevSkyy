'use client';

import { TopBar } from '@/components/console/TopBar';
import { AgentOS } from '@/components/agent-os/AgentOS';

/** Agent OS — the live `/api/v1/agents` roster as launchable apps, plus a
 *  Task Manager, System Monitor and Terminal over the tasks/monitoring APIs.
 *  See components/agent-os/AgentOS.tsx. */
export default function AgentsPage() {
  return (
    <>
      <TopBar title='Agent OS' />
      <AgentOS />
    </>
  );
}
