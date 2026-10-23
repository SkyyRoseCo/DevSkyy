// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act, createElement } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { useWebSocket } from '@/hooks/useWebSocket';

let root: Root;
let container: HTMLDivElement;
const opened = vi.fn();
class MockWebSocket {
  static OPEN = 1;
  readyState = 0;
  constructor(url: string) {
    opened(url);
  }
  close() {}
}
function Harness({ channel }: { channel: string }) {
  useWebSocket(channel);
  return null;
}
beforeEach(() => {
  vi.stubGlobal('IS_REACT_ACT_ENVIRONMENT', true);
  vi.stubGlobal('WebSocket', MockWebSocket);
  localStorage.setItem('access_token', 'synthetic.legacy.bearer');
  opened.mockClear();
  container = document.createElement('div');
  document.body.append(container);
  root = createRoot(container);
});
afterEach(() => {
  act(() => root.unmount());
  container.remove();
  localStorage.clear();
  vi.unstubAllGlobals();
});
describe('dashboard WebSocket credential handling', () => {
  it('retains the existing channel handshake without putting a backend bearer in the URL', () => {
    act(() => root.render(createElement(Harness, { channel: 'round_table' })));
    expect(opened).toHaveBeenCalledOnce();
    const url = new URL(opened.mock.calls[0][0]);
    expect(url.pathname).toBe('/api/ws/round_table');
    expect(url.search).toBe('');
    expect(String(url)).not.toContain('synthetic');
  });
  it('still rejects an invalid channel before opening a connection', () => {
    act(() => root.render(createElement(Harness, { channel: '../private' })));
    expect(opened).not.toHaveBeenCalled();
  });
});
