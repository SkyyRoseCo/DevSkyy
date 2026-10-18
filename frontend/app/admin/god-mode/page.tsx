import type { Metadata } from 'next';
import Link from 'next/link';
import { Suspense } from 'react';

import { getAdminSession } from '@/lib/require-admin-session';
import projection from './registry.generated.json';
import RuntimeWorkspace from './runtime-workspace';

export const metadata: Metadata = {
  title: 'GOD MODE · SkyyRose Operations',
  description: 'GOD MODE oversight, Fashion Theme Team skills and source synchronization.',
};

interface RegistryProjection {
  schemaVersion: number;
  generatedAt: string;
  generation: { command: string; sourceRevision: string | null };
  orchestrator: {
    name: string;
    version: string;
    status: string;
    skillCount: number;
    mcpToolCount: number;
    cliVersion: string;
  };
  team: { name: string; version: string; controller: string; skillCount: number };
  skills: {
    id: string;
    name: string;
    description: string;
    category: string;
    source: string;
    sha256: string;
    status: string;
  }[];
  tools: { id: string; name: string; description: string; kind: string; scope: string; status: string }[];
  workflow: { id: string; label: string; owner: string; gate: string }[];
  synchronization: { target: string; status: string; checkedAt: string | null; detail: string }[];
  limitations: string[];
}

const data: RegistryProjection = projection;
const panel = 'rounded-xl border border-white/10 bg-[#101014] p-5 sm:p-6';
const eyebrow = 'font-mono text-[10px] uppercase tracking-[0.18em] text-[#D7A3AB]';
const links = [
  {
    href: '/admin/scene-authority',
    title: 'Scene authority',
    detail: 'Identity, product fidelity and production gates',
  },
  { href: '/admin/elite-studio', title: 'Creative studio', detail: 'Campaign and design workspace' },
  { href: '/admin/catalog', title: 'Product catalog', detail: 'Collection and product source records' },
  { href: '/admin/mcp', title: 'MCP connections', detail: 'Inspect dashboard connector status' },
  { href: '/admin/jobs', title: 'Jobs', detail: 'Existing job queue and execution records' },
  { href: '/admin/qa', title: 'Quality review', detail: 'Review work against acceptance criteria' },
];

function Badge({ value }: { value: string }) {
  return (
    <span className='inline-flex max-w-full break-words rounded border border-[#D7A3AB]/25 bg-[#D7A3AB]/[0.06] px-2 py-1 font-mono text-[10px] leading-4 text-[#E3BDC3]'>
      {value.replaceAll('_', ' ')}
    </span>
  );
}

async function Workspace() {
  const session = await getAdminSession();
  if (!session) {
    return (
      <div className={`${panel} mx-4 my-8 sm:mx-8`}>
        <h2 className='text-lg text-white'>Sign in to open GOD MODE</h2>
        <p className='mt-2 text-sm text-[#B7B7C2]'>
          Your dashboard session protects the skill inventory and orchestration records.
        </p>
        <Link
          href='/login'
          className='mt-5 inline-block rounded border border-[#D7A3AB]/40 px-4 py-2 text-sm text-[#EDC9CE]'
        >
          Open sign in
        </Link>
      </div>
    );
  }
  const groups = [...new Set(data.skills.map(skill => skill.category))].sort();
  return (
    <div className='mx-auto max-w-[1440px] space-y-6 px-4 py-6 sm:px-8 sm:py-8'>
      <section
        className='relative overflow-hidden rounded-2xl border border-[#D7A3AB]/25 bg-gradient-to-br from-[#291B25] via-[#15121A] to-[#0D0D12] p-6 sm:p-9'
        aria-labelledby='mission-heading'
      >
        <div className='flex flex-wrap items-center justify-between gap-3'>
          <p className={eyebrow}>One accountable mission owner</p>
          <Badge value={data.orchestrator.status} />
        </div>
        <h2
          id='mission-heading'
          className='mt-5 max-w-3xl text-3xl font-semibold tracking-tight text-white sm:text-5xl'
        >
          Intention. Direction.
          <br />
          <span className='text-[#D7A3AB]'>Verified execution.</span>
        </h2>
        <p className='mt-5 max-w-2xl text-sm leading-7 text-[#CAC5D1]'>
          GOD MODE directs the Fashion Theme Team. The team owns SkyyRose specialist skills, carries the current brand
          canon into each workflow, and returns evidence for independent review.
        </p>
        <div className='mt-7 flex flex-wrap gap-3'>
          <a href='#skill-library' className='rounded-lg bg-[#D7A3AB] px-4 py-2.5 text-sm font-semibold text-[#191018]'>
            Explore the skill library
          </a>
          <a href='#workflow' className='rounded-lg border border-white/20 px-4 py-2.5 text-sm text-white'>
            Inspect the workflow
          </a>
        </div>
      </section>

      <section aria-label='Control hierarchy' className='grid gap-3 md:grid-cols-3'>
        {[
          {
            label: '01 · Mission control',
            name: data.orchestrator.name,
            detail: `Version ${data.orchestrator.version} · ${data.orchestrator.skillCount} orchestration skills`,
          },
          {
            label: '02 · Specialist team',
            name: data.team.name,
            detail: `Version ${data.team.version} · reports to ${data.team.controller}`,
          },
          {
            label: '03 · SkyyRose practice',
            name: `${data.team.skillCount} team skills`,
            detail: 'Canon, product fidelity, creative production and commerce',
          },
        ].map(level => (
          <div key={level.label} className={panel}>
            <p className={eyebrow}>{level.label}</p>
            <h3 className='mt-3 text-xl font-semibold text-white'>{level.name}</h3>
            <p className='mt-2 text-sm leading-6 text-[#B7B7C2]'>{level.detail}</p>
          </div>
        ))}
      </section>

      <RuntimeWorkspace />

      <section id='workflow' className={panel} aria-labelledby='workflow-heading'>
        <p className={eyebrow}>Workflow before production</p>
        <h2 id='workflow-heading' className='mt-2 text-xl font-semibold text-white'>
          Every handoff has an owner and a gate
        </h2>
        <ol className='mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-3'>
          {data.workflow.map((step, index) => (
            <li key={step.id} className='rounded-lg border border-white/[0.07] bg-black/20 p-4'>
              <span className='font-mono text-xs text-[#D7A3AB]'>{String(index + 1).padStart(2, '0')}</span>
              <h3 className='mt-2 font-semibold text-white'>{step.label}</h3>
              <p className='mt-2 text-xs leading-5 text-[#B7B7C2]'>Owner: {step.owner}</p>
              <p className='mt-1 text-xs leading-5 text-[#B7B7C2]'>Gate: {step.gate}</p>
            </li>
          ))}
        </ol>
      </section>

      <section id='skill-library' aria-labelledby='skills-heading'>
        <div className='mb-4 flex flex-wrap items-end justify-between gap-3'>
          <div>
            <p className={eyebrow}>Fashion Theme Team · specialist library</p>
            <h2 id='skills-heading' className='mt-2 text-2xl font-semibold text-white'>
              Source-bound skills
            </h2>
          </div>
          <p className='text-xs text-[#B7B7C2]'>
            {data.skills.length} records · expand a practice to inspect its sources
          </p>
        </div>
        <div className='space-y-3'>
          {groups.map(category => (
            <details key={category} className={`${panel} group`}>
              <summary className='cursor-pointer text-base font-semibold text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-[#D7A3AB]'>
                {category}
                <span className='ml-3 font-mono text-xs font-normal text-[#B7B7C2]'>
                  {data.skills.filter(skill => skill.category === category).length} skills
                </span>
              </summary>
              <div className='mt-5 grid gap-3 lg:grid-cols-2'>
                {data.skills
                  .filter(skill => skill.category === category)
                  .map(skill => (
                    <article key={skill.id} className='min-w-0 rounded-lg border border-white/[0.07] bg-black/20 p-4'>
                      <h3 className='text-sm font-semibold text-white'>{skill.name}</h3>
                      <p className='mt-2 text-sm leading-6 text-[#B7B7C2]'>{skill.description}</p>
                      <div className='mt-3'>
                        <Badge value={skill.status} />
                      </div>
                      <p className='mt-3 break-all font-mono text-[10px] leading-5 text-[#A6A0B1]'>
                        Source: {skill.source}
                      </p>
                      <p className='mt-1 break-all font-mono text-[10px] leading-5 text-[#A6A0B1]'>
                        SHA-256: {skill.sha256}
                      </p>
                    </article>
                  ))}
              </div>
            </details>
          ))}
        </div>
      </section>

      <section className={panel} aria-labelledby='tools-heading'>
        <p className={eyebrow}>Actual registered capabilities</p>
        <h2 id='tools-heading' className='mt-2 text-xl font-semibold text-white'>
          Tools and host connections
        </h2>
        <p className='mt-2 text-sm leading-6 text-[#B7B7C2]'>
          LOCAL describes a local GOD MODE handler. HOST ONLY describes a host connector reference and does not expose a
          dashboard executor.
        </p>
        <div className='mt-5 grid gap-3 lg:grid-cols-2'>
          {data.tools.map(tool => (
            <article key={tool.id} className='min-w-0 rounded-lg border border-white/[0.07] p-4'>
              <div className='flex flex-wrap items-start justify-between gap-2'>
                <h3 className='text-sm font-semibold text-white'>{tool.name}</h3>
                <Badge value={tool.kind} />
              </div>
              <p className='mt-2 text-sm leading-6 text-[#B7B7C2]'>{tool.description}</p>
              <p className='mt-2 text-xs leading-5 text-[#B7B7C2]'>Scope: {tool.scope}</p>
              <p className='mt-1 break-words font-mono text-[10px] leading-5 text-[#D7A3AB]'>
                {tool.status.replaceAll('_', ' ')}
              </p>
            </article>
          ))}
        </div>
      </section>

      <section className={panel} aria-labelledby='sync-heading'>
        <p className={eyebrow}>Versioned source projection</p>
        <h2 id='sync-heading' className='mt-2 text-xl font-semibold text-white'>
          Synchronization evidence
        </h2>
        <p className='mt-3 text-sm leading-6 text-[#B7B7C2]'>
          Snapshot generated {data.generatedAt}. Source hashes describe this snapshot; they do not prove a running
          session has reloaded or an output has passed visual review.
        </p>
        <ul className='mt-4 space-y-3'>
          {data.synchronization.map(target => (
            <li key={target.target} className='rounded-lg border border-white/[0.07] p-4'>
              <div className='flex flex-wrap justify-between gap-2'>
                <h3 className='min-w-0 break-words text-sm font-semibold text-white'>{target.target}</h3>
                <Badge value={target.status} />
              </div>
              <p className='mt-2 break-words text-sm leading-6 text-[#B7B7C2]'>{target.detail}</p>
              {target.checkedAt && (
                <p className='mt-2 font-mono text-[10px] text-[#A6A0B1]'>Checked: {target.checkedAt}</p>
              )}
            </li>
          ))}
        </ul>
        <p className='mt-4 break-all font-mono text-[10px] leading-5 text-[#A6A0B1]'>
          Refresh command: {data.generation.command}
          <br />
          Source revision: {data.generation.sourceRevision ?? 'Uncommitted source snapshot'} · projection schema{' '}
          {data.schemaVersion}
        </p>
      </section>

      <section aria-labelledby='workspaces-heading'>
        <h2 id='workspaces-heading' className='mb-4 text-xl font-semibold text-white'>
          Continue in the dashboard
        </h2>
        <div className='grid gap-3 sm:grid-cols-2 xl:grid-cols-3'>
          {links.map(link => (
            <Link
              key={link.href}
              href={link.href}
              className={`${panel} transition-colors hover:border-[#D7A3AB]/50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#D7A3AB]`}
            >
              <h3 className='font-semibold text-white'>
                {link.title}{' '}
                <span aria-hidden className='text-[#D7A3AB]'>
                  ↗
                </span>
              </h3>
              <p className='mt-2 text-sm leading-6 text-[#B7B7C2]'>{link.detail}</p>
            </Link>
          ))}
        </div>
      </section>
      <section
        className='rounded-xl border border-amber-300/20 bg-amber-300/[0.03] p-5'
        aria-labelledby='limits-heading'
      >
        <h2 id='limits-heading' className='text-sm font-semibold text-amber-100'>
          Qualification limits
        </h2>
        <ul className='mt-3 list-disc space-y-2 pl-5 text-sm leading-6 text-[#C8BEAC]'>
          {data.limitations.map(limit => (
            <li key={limit}>{limit}</li>
          ))}
        </ul>
      </section>
    </div>
  );
}

export default function GodModePage() {
  return (
    <>
      <header className='border-b border-white/[0.06] px-4 py-5 sm:px-8'>
        <p className={eyebrow}>SkyyRose Operations</p>
        <h1 className='mt-2 text-xl font-semibold tracking-[0.12em] text-white'>GOD MODE</h1>
      </header>
      <Suspense
        fallback={
          <p role='status' className='p-8 text-sm text-[#B7B7C2]'>
            Opening your governed workspace…
          </p>
        }
      >
        <Workspace />
      </Suspense>
    </>
  );
}
