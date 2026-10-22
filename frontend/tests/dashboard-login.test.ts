// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act, createElement } from 'react';
import { createRoot, type Root } from 'react-dom/client';

const mocks = vi.hoisted(() => ({ signIn: vi.fn(), push: vi.fn(), refresh: vi.fn() }));
vi.mock('next-auth/react', () => ({ signIn: mocks.signIn }));
vi.mock('next/navigation', () => ({ useRouter: () => ({ push: mocks.push, refresh: mocks.refresh }) }));

import LoginPage from '@/app/login/page';

let clock = Date.now();
let root: Root;
let container: HTMLDivElement;
beforeEach(() => {
  vi.spyOn(Date, 'now').mockReturnValue((clock += 2_000));
  mocks.signIn.mockReset().mockResolvedValue({ ok: true, error: undefined, status: 200, url: '/admin' });
  mocks.push.mockReset();
  mocks.refresh.mockReset();
  localStorage.clear();
  vi.stubGlobal('IS_REACT_ACT_ENVIRONMENT', true);
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('Unexpected browser fetch')));
  container = document.createElement('div');
  document.body.append(container);
  root = createRoot(container);
});
afterEach(() => {
  act(() => root.unmount());
  container.remove();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

async function submit() {
  act(() => root.render(createElement(LoginPage)));
  const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')!.set!;
  for (const [selector, value] of [
    ['#email', 'operator@example.test'],
    ['#password', 'Synthetic-password-123'],
  ]) {
    const field = container.querySelector<HTMLInputElement>(selector)!;
    act(() => {
      setter.call(field, value);
      field.dispatchEvent(new Event('input', { bubbles: true }));
    });
  }
  await act(async () => {
    container.querySelector('form')!.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
  });
}

describe('dashboard credentials sign-in', () => {
  it('creates a NextAuth session without requesting or storing backend tokens in the browser', async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
    await submit();
    expect(mocks.push).toHaveBeenCalledWith('/admin');
    expect(mocks.signIn).toHaveBeenCalledWith('credentials', {
      email: 'operator@example.test',
      password: 'Synthetic-password-123',
      redirect: false,
      callbackUrl: '/admin',
    });
    expect(fetchMock).not.toHaveBeenCalled();
    expect(localStorage.getItem('access_token')).toBeNull();
    expect(localStorage.getItem('refresh_token')).toBeNull();
    expect(document.cookie).not.toContain('access_token=');
  });

  it('keeps rejected credentials on the login page without exposing provider details', async () => {
    mocks.signIn.mockResolvedValue({ ok: false, error: 'CredentialsSignin', status: 401, url: null });
    await submit();
    expect(container.querySelector('[role=alert]')?.textContent).toContain('Invalid email or password');
    expect(mocks.push).not.toHaveBeenCalled();
    expect(document.body.textContent).not.toContain('CredentialsSignin');
  });

  it('clears credentials left by the legacy login', () => {
    localStorage.setItem('access_token', 'synthetic-legacy-access');
    localStorage.setItem('refresh_token', 'synthetic-legacy-refresh');
    localStorage.setItem('token_type', 'Bearer');
    document.cookie = 'access_token=synthetic-legacy-access; path=/';
    act(() => root.render(createElement(LoginPage)));
    expect(localStorage.getItem('access_token')).toBeNull();
    expect(localStorage.getItem('refresh_token')).toBeNull();
    expect(localStorage.getItem('token_type')).toBeNull();
    expect(document.cookie).not.toContain('access_token=');
  });
});
