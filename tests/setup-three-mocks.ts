import threeMock from './__mocks__/three.cjs';

if (!threeMock.CanvasTexture) {
  throw new Error('three.cjs mock is missing CanvasTexture export');
}

Object.assign(globalThis, { THREE: threeMock });

// Node 26 exposes storage globals even without a backing file. Browser tests
// must use their JSDOM window's storage, not the host Node process's storage.
const browserWindow = (globalThis as typeof globalThis & { jsdom?: { window: Window } }).jsdom?.window;
if (browserWindow) {
  for (const name of ['localStorage', 'sessionStorage'] as const) {
    Object.defineProperty(globalThis, name, {
      configurable: true,
      writable: true,
      value: browserWindow[name],
    });
  }
}
