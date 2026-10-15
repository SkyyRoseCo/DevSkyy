import { describe, expect, it } from 'vitest';

import { INITIAL_WM_STATE, focusedWindowId, wmReducer, type WmState } from '@/lib/agent-os/window-manager';

function open(state: WmState, id: string, title = id): WmState {
  return wmReducer(state, { type: 'open', id, title });
}

describe('wmReducer', () => {
  it('opens a window on top and focuses it', () => {
    const s = open(open(INITIAL_WM_STATE, 'a'), 'b');
    expect(s.windows.map(w => w.id)).toEqual(['a', 'b']);
    expect(focusedWindowId(s)).toBe('b');
  });

  it('cascades new windows instead of stacking them on one point', () => {
    const s = open(open(INITIAL_WM_STATE, 'a'), 'b');
    const [a, b] = s.windows;
    expect(b.x).toBeGreaterThan(a.x);
    expect(b.y).toBeGreaterThan(a.y);
  });

  it('re-opening an existing window restores and focuses it without duplicating', () => {
    let s = open(open(INITIAL_WM_STATE, 'a'), 'b');
    s = wmReducer(s, { type: 'minimize', id: 'a' });
    s = open(s, 'a');
    expect(s.windows).toHaveLength(2);
    expect(s.windows.find(w => w.id === 'a')?.minimized).toBe(false);
    expect(focusedWindowId(s)).toBe('a');
  });

  it('focus raises z-order above every other window', () => {
    let s = open(open(open(INITIAL_WM_STATE, 'a'), 'b'), 'c');
    s = wmReducer(s, { type: 'focus', id: 'a' });
    const a = s.windows.find(w => w.id === 'a');
    expect(Math.max(...s.windows.map(w => w.z))).toBe(a?.z);
  });

  it('minimize removes a window from focus', () => {
    let s = open(open(INITIAL_WM_STATE, 'a'), 'b');
    s = wmReducer(s, { type: 'minimize', id: 'b' });
    expect(focusedWindowId(s)).toBe('a');
  });

  it('toggle minimizes the focused window and restores a minimized one', () => {
    let s = open(open(INITIAL_WM_STATE, 'a'), 'b');
    s = wmReducer(s, { type: 'toggle', id: 'b' });
    expect(s.windows.find(w => w.id === 'b')?.minimized).toBe(true);
    s = wmReducer(s, { type: 'toggle', id: 'b' });
    expect(focusedWindowId(s)).toBe('b');
  });

  it('toggle on an open but unfocused window focuses it instead of minimizing', () => {
    let s = open(open(INITIAL_WM_STATE, 'a'), 'b');
    s = wmReducer(s, { type: 'toggle', id: 'a' });
    expect(s.windows.find(w => w.id === 'a')?.minimized).toBe(false);
    expect(focusedWindowId(s)).toBe('a');
  });

  it('close removes the window', () => {
    const s = wmReducer(open(INITIAL_WM_STATE, 'a'), { type: 'close', id: 'a' });
    expect(s.windows).toEqual([]);
    expect(focusedWindowId(s)).toBeNull();
  });

  it('move never places a window at negative coordinates', () => {
    const s = wmReducer(open(INITIAL_WM_STATE, 'a'), { type: 'move', id: 'a', x: -50, y: -10 });
    expect(s.windows[0]).toMatchObject({ x: 0, y: 0 });
  });

  it('does not mutate the previous state', () => {
    const before = open(INITIAL_WM_STATE, 'a');
    const snapshot = JSON.stringify(before);
    wmReducer(before, { type: 'move', id: 'a', x: 300, y: 300 });
    wmReducer(before, { type: 'close', id: 'a' });
    expect(JSON.stringify(before)).toBe(snapshot);
  });

  it('ignores actions for unknown windows', () => {
    const s = open(INITIAL_WM_STATE, 'a');
    expect(wmReducer(s, { type: 'focus', id: 'nope' })).toBe(s);
    expect(wmReducer(s, { type: 'move', id: 'nope', x: 1, y: 1 })).toBe(s);
  });
});
