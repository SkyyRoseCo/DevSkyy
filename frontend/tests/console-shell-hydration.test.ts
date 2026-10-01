import { createRequire } from 'node:module';
import { act, createElement } from 'react';
import { hydrateRoot, type Root } from 'react-dom/client';
import { renderToString } from 'react-dom/server';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SessionContext, type SessionContextValue } from 'next-auth/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

const { replace, listAgents } = vi.hoisted(() => ({ replace: vi.fn(), listAgents: vi.fn() }));
vi.mock('next/navigation', () => ({
  usePathname: () => '/admin/journey-analytics',
  useRouter: () => ({ replace }),
}));
vi.mock('@/lib/api', () => ({ api: { agents: { list: listAgents } } }));

import { ConsoleShell } from '@/components/console/ConsoleShell';

// The repository root declares jsdom; this suite keeps the configured Node
// environment and supplies only the DOM needed for actual React hydration.
type FixtureWindow = Pick<Window & typeof globalThis, 'document' | 'navigator' | 'HTMLElement' | 'Node' | 'close'>;
const { JSDOM } = createRequire(import.meta.url)('jsdom') as {
  JSDOM: new (html: string, options: { url: string }) => { window: FixtureWindow };
};

let root: Root | undefined;
let fixture: { window: FixtureWindow } | undefined;
const clients: QueryClient[] = [];

function client() {
  const result = new QueryClient({ defaultOptions: { queries: { retry: false, gcTime: Infinity } } });
  result.setQueryData(['console-agents-count'], { agents: [] });
  result.setQueryData(['console-orders-count'], 0);
  clients.push(result);
  return result;
}

function shell(session: SessionContextValue) {
  return createElement(
    QueryClientProvider,
    { client: client() },
    createElement(
      SessionContext.Provider,
      { value: session },
      createElement(ConsoleShell, null, createElement('p', null, 'Reporting content'))
    )
  );
}

function createContainer(html: string) {
  fixture = new JSDOM('<!doctype html><html><body><div id="root"></div></body></html>', {
    url: 'http://localhost/admin/journey-analytics',
  });
  vi.stubGlobal('window', fixture.window);
  vi.stubGlobal('self', fixture.window);
  vi.stubGlobal('document', fixture.window.document);
  vi.stubGlobal('navigator', fixture.window.navigator);
  vi.stubGlobal('HTMLElement', fixture.window.HTMLElement);
  vi.stubGlobal('Node', fixture.window.Node);
  vi.stubGlobal('IS_REACT_ACT_ENVIRONMENT', true);
  const container = fixture.window.document.getElementById('root');
  if (!container) throw new Error('Hydration fixture container missing.');
  container.innerHTML = html;
  return container;
}

afterEach(async () => {
  if (root) await act(() => root?.unmount());
  root = undefined;
  clients.splice(0).forEach(queryClient => queryClient.clear());
  fixture?.window.close();
  fixture = undefined;
  vi.unstubAllGlobals();
  vi.clearAllMocks();
});

describe('ConsoleShell identity hydration', () => {
  it('hydrates the actual server shell when its session is already authenticated on the client', async () => {
    const server = renderToString(shell({ data: null, status: 'loading', update: async () => null }));
    expect(server).not.toContain('fixture');
    const container = createContainer(server);
    const recoverableErrors = vi.fn();
    await act(async () => {
      root = hydrateRoot(
        container,
        shell({
          data: { user: { email: 'fixture@example.test' }, expires: '2099-01-01T00:00:00Z' },
          status: 'authenticated',
          update: async () => null,
        }),
        { onRecoverableError: recoverableErrors }
      );
    });
    expect(recoverableErrors).not.toHaveBeenCalled();
    expect(container.querySelector('aside')?.textContent).toContain('fixture');
    expect(container.querySelector('main')?.textContent).toBe('Reporting content');
    expect(replace).not.toHaveBeenCalled();
    expect(listAgents).not.toHaveBeenCalled();
  });

  it('preserves the unauthenticated redirect while displaying the server identity', async () => {
    const server = renderToString(shell({ data: null, status: 'loading', update: async () => null }));
    const container = createContainer(server);
    const recoverableErrors = vi.fn();
    await act(async () => {
      root = hydrateRoot(container, shell({ data: null, status: 'unauthenticated', update: async () => null }), {
        onRecoverableError: recoverableErrors,
      });
    });
    expect(recoverableErrors).not.toHaveBeenCalled();
    expect(container.querySelector('aside')?.textContent).toContain('Operator');
    expect(replace).toHaveBeenCalledWith('/login');
  });
});
