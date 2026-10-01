import { Suspense } from 'react';
import { getOwnerReport } from '@/lib/governor/server';
import { ReportAccessError } from '@/lib/governor/report-client';

async function GovernorStatus() {
  let result;
  try {
    result = await getOwnerReport();
  } catch (error) {
    return (
      <p role='status' className='rounded-xl border border-amber-400/40 p-5 text-amber-200'>
        {error instanceof ReportAccessError ? error.message : 'Verified report evidence unavailable'}
      </p>
    );
  }
  const { report, observedAt } = result;
  return (
    <div className='space-y-6'>
      <section aria-labelledby='evidence-title' className='rounded-xl border border-gray-600 p-5'>
        <h2 id='evidence-title' className='text-xl font-semibold'>
          Verified accounting snapshot
        </h2>
        <p className='mt-2'>Evidence mode: {report.evidence_mode}</p>
        <p>
          Observed at: <time dateTime={observedAt}>{observedAt}</time>
        </p>
        <p className='break-all'>
          Job: {report.job_id} · Grant: {report.grant_id}
        </p>
        <p>Ledger sequence: {report.ledger.head_sequence}</p>
        <p>
          Grant revoked: {String(report.revoked)} · Job stopped: {String(report.stopped)} · Job closed:{' '}
          {String(report.closed)}
        </p>
        <p className='mt-3 text-amber-200'>
          Owner acceptance is unverified. Provider execution and actual spend are unavailable.
        </p>
        <p className='text-gray-300'>This snapshot is fetched on page load. Reload to obtain current evidence.</p>
      </section>
      <section aria-labelledby='resource-title'>
        <h2 id='resource-title' className='mb-3 text-xl font-semibold'>
          Resource accounting
        </h2>
        <div className='grid gap-4 sm:grid-cols-2 xl:grid-cols-3'>
          {Object.entries(report.resources).map(([name, units]) => (
            <div key={name} className='min-w-0 rounded-xl border border-gray-600 p-4'>
              <h3 className='font-semibold'>{name.replaceAll('_', ' ')}</h3>
              <dl>
                {Object.entries(units).map(([unit, value]) => (
                  <div key={unit} className='mt-2 flex flex-wrap justify-between gap-2'>
                    <dt>{unit.replaceAll('_', ' ')}</dt>
                    <dd className='break-all font-mono'>{value}</dd>
                  </div>
                ))}
              </dl>
              {Object.keys(units).length === 0 && <p>No resources recorded.</p>}
            </div>
          ))}
        </div>
      </section>
      <section aria-labelledby='operations-title'>
        <h2 id='operations-title' className='mb-3 text-xl font-semibold'>
          Recorded operations
        </h2>
        {report.operations.length === 0 ? (
          <p>No operations recorded for this scope.</p>
        ) : (
          <ul className='space-y-3'>
            {report.operations.map(op => (
              <li key={op.operation_id} className='rounded-xl border border-gray-600 p-4'>
                <p className='break-all font-mono'>{op.operation_id}</p>
                <p>
                  State: {op.state} · Billing: {op.billing_state}
                </p>
                <p>
                  Billing unknown: {String(op.billing_unknown)} · Review: {op.review_state}
                </p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
export default function GovernorPage() {
  return (
    <main className='space-y-6 p-4 text-gray-100 sm:p-6'>
      <header>
        <h1 className='text-3xl font-semibold'>Governor</h1>
        <p className='mt-2 text-gray-300'>Owner-only read-only accounting evidence.</p>
      </header>
      <Suspense fallback={<p role='status'>Loading verified report…</p>}>
        <GovernorStatus />
      </Suspense>
    </main>
  );
}
