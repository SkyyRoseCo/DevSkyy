/**
 * Agent OS window manager — a pure, immutable reducer. No React, no DOM, so
 * it runs under vitest's node environment (see vitest.config.ts) and every
 * window transition is unit-tested in tests/agent-os-window-manager.test.ts.
 */

export interface OsWindow {
  id: string;
  title: string;
  x: number;
  y: number;
  z: number;
  minimized: boolean;
}

export interface WmState {
  windows: OsWindow[];
  nextZ: number;
}

export type WmAction =
  | { type: 'open'; id: string; title: string }
  | { type: 'close'; id: string }
  | { type: 'focus'; id: string }
  | { type: 'minimize'; id: string }
  | { type: 'toggle'; id: string }
  | { type: 'move'; id: string; x: number; y: number };

export const INITIAL_WM_STATE: WmState = { windows: [], nextZ: 1 };

const CASCADE_ORIGIN = { x: 32, y: 24 };
const CASCADE_STEP = 28;
const CASCADE_SLOTS = 8;

/** Topmost non-minimized window, or null when the desktop is clear. */
export function focusedWindowId(state: WmState): string | null {
  let top: OsWindow | null = null;
  for (const w of state.windows) {
    if (!w.minimized && (top === null || w.z > top.z)) top = w;
  }
  return top?.id ?? null;
}

function patch(state: WmState, id: string, change: Partial<OsWindow>): WmState {
  return { ...state, windows: state.windows.map(w => (w.id === id ? { ...w, ...change } : w)) };
}

function raise(state: WmState, id: string): WmState {
  return { ...patch(state, id, { z: state.nextZ, minimized: false }), nextZ: state.nextZ + 1 };
}

function openWindow(state: WmState, id: string, title: string): WmState {
  if (state.windows.some(w => w.id === id)) return raise(state, id);
  const slot = state.windows.length % CASCADE_SLOTS;
  const win: OsWindow = {
    id,
    title,
    x: CASCADE_ORIGIN.x + slot * CASCADE_STEP,
    y: CASCADE_ORIGIN.y + slot * CASCADE_STEP,
    z: state.nextZ,
    minimized: false,
  };
  return { windows: [...state.windows, win], nextZ: state.nextZ + 1 };
}

export function wmReducer(state: WmState, action: WmAction): WmState {
  if (action.type === 'open') return openWindow(state, action.id, action.title);

  const target = state.windows.find(w => w.id === action.id);
  if (!target) return state;

  switch (action.type) {
    case 'close':
      return { ...state, windows: state.windows.filter(w => w.id !== action.id) };
    case 'focus':
      return raise(state, action.id);
    case 'minimize':
      return patch(state, action.id, { minimized: true });
    case 'toggle':
      // Taskbar semantics: clicking the focused window minimizes it; clicking
      // a minimized or background window brings it to the front.
      return focusedWindowId(state) === action.id
        ? patch(state, action.id, { minimized: true })
        : raise(state, action.id);
    case 'move':
      return patch(state, action.id, { x: Math.max(0, action.x), y: Math.max(0, action.y) });
    default:
      return state;
  }
}
