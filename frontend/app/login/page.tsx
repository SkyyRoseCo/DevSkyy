'use client';

import { useState, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { signIn } from 'next-auth/react';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Eye, EyeOff, Shield } from 'lucide-react';

// =============================================================================
// CONFIGURATION
// =============================================================================

const API_URL = (() => {
  const url = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  try {
    new URL(url);
    return url;
  } catch {
    // Invalid URL — fall back to default
    return 'http://localhost:8000';
  }
})();

const LOGIN_RATE_LIMIT_MS = 1000; // Minimum time between login attempts
const MAX_LOGIN_ATTEMPTS = 5; // Max attempts before temporary lockout
const LOCKOUT_DURATION_MS = 60000; // 1 minute lockout

// =============================================================================
// ZOD SCHEMAS
// =============================================================================

const LoginFormSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Please enter a valid email address')
    .max(254, 'Email is too long')
    .transform(val => val.toLowerCase().trim()),
  password: z
    .string()
    .min(1, 'Password is required')
    .min(8, 'Password must be at least 8 characters')
    .max(128, 'Password is too long'),
  rememberMe: z.boolean().optional().default(false),
});

const LoginResponseSchema = z.object({
  access_token: z.string().min(1),
  refresh_token: z.string().min(1),
  token_type: z.string().default('Bearer'),
  expires_in: z.number().optional().default(900),
});

type LoginForm = z.infer<typeof LoginFormSchema>;
type LoginResponse = z.infer<typeof LoginResponseSchema>;

// =============================================================================
// SECURITY UTILITIES
// =============================================================================

function generateNonce(): string {
  const array = new Uint8Array(16);
  crypto.getRandomValues(array);
  return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
}

function setSecureCookie(name: string, value: string, maxAge: number): void {
  const secure = window.location.protocol === 'https:' ? '; Secure' : '';
  const sameSite = '; SameSite=Strict';
  document.cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=${maxAge}${secure}${sameSite}`;
}

function clearAuthData(): void {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('token_type');
  document.cookie = 'access_token=; path=/; max-age=0';
}

// Rate limiting state (stored in memory, resets on page reload)
let loginAttempts = 0;
let lastAttemptTime = 0;
let lockoutUntil = 0;

function checkRateLimit(): { allowed: boolean; waitTime: number } {
  const now = Date.now();

  // Check if currently locked out
  if (lockoutUntil > now) {
    return { allowed: false, waitTime: Math.ceil((lockoutUntil - now) / 1000) };
  }

  // Check if attempting too fast
  if (now - lastAttemptTime < LOGIN_RATE_LIMIT_MS) {
    return { allowed: false, waitTime: 1 };
  }

  return { allowed: true, waitTime: 0 };
}

function recordLoginAttempt(success: boolean): void {
  const now = Date.now();
  lastAttemptTime = now;

  if (success) {
    loginAttempts = 0;
    lockoutUntil = 0;
  } else {
    loginAttempts++;
    if (loginAttempts >= MAX_LOGIN_ATTEMPTS) {
      lockoutUntil = now + LOCKOUT_DURATION_MS;
      loginAttempts = 0;
    }
  }
}

// =============================================================================
// COMPONENT
// =============================================================================

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [nonce, setNonce] = useState<string>('');

  // Generate CSRF nonce on mount
  useEffect(() => {
    setNonce(generateNonce());
    // Clear any stale auth data
    if (window.location.search.includes('logout=true')) {
      clearAuthData();
    }
  }, []);

  const validateForm = useCallback((): LoginForm | null => {
    const result = LoginFormSchema.safeParse({ email, password, rememberMe });

    if (!result.success) {
      const errors: Record<string, string> = {};
      result.error.issues.forEach(issue => {
        const field = issue.path[0] as string;
        if (!errors[field]) {
          errors[field] = issue.message;
        }
      });
      setFieldErrors(errors);
      return null;
    }

    setFieldErrors({});
    return result.data;
  }, [email, password, rememberMe]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Check rate limiting
    const rateCheck = checkRateLimit();
    if (!rateCheck.allowed) {
      setError(`Please wait ${rateCheck.waitTime} seconds before trying again.`);
      return;
    }

    // Validate form
    const formData = validateForm();
    if (!formData) {
      return;
    }

    setIsLoading(true);
    const controller = new AbortController();
    let timeoutId: ReturnType<typeof setTimeout> | undefined;
    const deadline = new Promise<never>((_, reject) => {
      timeoutId = setTimeout(() => {
        controller.abort();
        const timeoutError = new Error('Login deadline exceeded');
        timeoutError.name = 'AbortError';
        reject(timeoutError);
      }, 30000);
    });

    try {
      const requestBody = new URLSearchParams();
      requestBody.append('username', formData.email);
      requestBody.append('password', formData.password);
      requestBody.append('grant_type', 'password');

      const response = await Promise.race([
        fetch(`${API_URL}/api/v1/auth/token`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Request-ID': crypto.randomUUID(),
            'X-CSRF-Token': nonce,
          },
          body: requestBody.toString(),
          signal: controller.signal,
          credentials: 'include',
        }),
        deadline,
      ]);

      if (!response.ok) {
        recordLoginAttempt(false);

        // Handle specific error codes
        if (response.status === 401) {
          throw new Error('Invalid email or password');
        } else if (response.status === 429) {
          throw new Error('Too many login attempts. Please try again later.');
        } else if (response.status >= 500) {
          throw new Error('Server error. Please try again later.');
        } else {
          // Don't expose specific error details from server
          throw new Error('Login failed. Please check your credentials.');
        }
      }

      const rawData = await Promise.race([response.json(), deadline]);
      const parseResult = LoginResponseSchema.safeParse(rawData);

      if (!parseResult.success) {
        throw new Error('Invalid response from server');
      }

      const data = parseResult.data;
      // Gated dashboard routes use NextAuth's server session, not the legacy
      // bearer cookie. Establish it before publishing legacy client tokens.
      const sessionResult = await Promise.race([
        signIn('credentials', {
          email: formData.email,
          password: formData.password,
          redirect: false,
        }),
        deadline,
      ]);
      if (!sessionResult?.ok) {
        throw new Error('Unable to establish dashboard session. Please sign in again.');
      }
      recordLoginAttempt(true);

      // Store tokens securely
      const tokenExpiry = formData.rememberMe ? 2592000 : data.expires_in; // 30 days or session

      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      localStorage.setItem('token_type', data.token_type);

      // Set secure cookie for SSR
      setSecureCookie('access_token', data.access_token, tokenExpiry);

      // Regenerate nonce after successful login
      setNonce(generateNonce());

      // Redirect to dashboard
      router.push('/admin');
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        setError('Login request timed out. Please try again.');
      } else {
        setError(err instanceof Error ? err.message : 'Login failed. Please try again.');
      }
    } finally {
      clearTimeout(timeoutId);
      setIsLoading(false);
    }
  };

  return (
    <div className='min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 px-4'>
      <Card className='w-full max-w-md bg-gray-800/50 border-gray-700 backdrop-blur-sm'>
        <CardHeader className='space-y-1 text-center'>
          <div className='flex justify-center mb-4'>
            <div className='h-12 w-12 rounded-xl bg-gradient-to-br from-rose-400 to-rose-600 flex items-center justify-center'>
              <span className='text-white font-bold text-xl'>DS</span>
            </div>
          </div>
          <CardTitle className='text-2xl font-bold text-white'>Welcome back</CardTitle>
          <CardDescription className='text-gray-400'>Sign in to your DevSkyy account</CardDescription>
        </CardHeader>
        <form method='post' onSubmit={handleSubmit} noValidate>
          <input type='hidden' name='_csrf' value={nonce} />
          <CardContent className='space-y-4'>
            {error && (
              <Alert variant='destructive' className='bg-red-900/50 border-red-800' data-testid='error-message'>
                <AlertDescription className='flex items-center gap-2'>
                  <Shield className='h-4 w-4' />
                  {error}
                </AlertDescription>
              </Alert>
            )}

            <div className='space-y-2'>
              <Label htmlFor='email' className='text-gray-200'>
                Email
              </Label>
              <Input
                id='email'
                name='username'
                type='email'
                placeholder='you@example.com'
                value={email}
                onChange={e => {
                  setEmail(e.target.value);
                  if (fieldErrors.email) {
                    setFieldErrors(prev => ({ ...prev, email: '' }));
                  }
                }}
                required
                disabled={isLoading}
                autoComplete='email'
                autoFocus
                aria-invalid={!!fieldErrors.email}
                aria-describedby={fieldErrors.email ? 'email-error' : undefined}
                className={`bg-gray-700/50 border-gray-600 text-white placeholder:text-gray-400 focus:border-rose-500 focus:ring-rose-500 ${
                  fieldErrors.email ? 'border-red-500' : ''
                }`}
                data-testid='username'
              />
              {fieldErrors.email && (
                <p id='email-error' className='text-sm text-red-400'>
                  {fieldErrors.email}
                </p>
              )}
            </div>

            <div className='space-y-2'>
              <div className='flex items-center justify-between'>
                <Label htmlFor='password' className='text-gray-200'>
                  Password
                </Label>
                <a
                  href='/forgot-password'
                  className='text-sm text-rose-400 hover:text-rose-300'
                  data-testid='forgot-password'
                >
                  Forgot password?
                </a>
              </div>
              <div className='relative'>
                <Input
                  id='password'
                  name='password'
                  type={showPassword ? 'text' : 'password'}
                  placeholder='Enter your password'
                  value={password}
                  onChange={e => {
                    setPassword(e.target.value);
                    if (fieldErrors.password) {
                      setFieldErrors(prev => ({ ...prev, password: '' }));
                    }
                  }}
                  required
                  disabled={isLoading}
                  autoComplete='current-password'
                  aria-invalid={!!fieldErrors.password}
                  aria-describedby={fieldErrors.password ? 'password-error' : undefined}
                  className={`bg-gray-700/50 border-gray-600 text-white placeholder:text-gray-400 focus:border-rose-500 focus:ring-rose-500 pr-10 ${
                    fieldErrors.password ? 'border-red-500' : ''
                  }`}
                  data-testid='password'
                />
                <button
                  type='button'
                  onClick={() => setShowPassword(!showPassword)}
                  className='absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-300'
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff className='h-4 w-4' /> : <Eye className='h-4 w-4' />}
                </button>
              </div>
              {fieldErrors.password && (
                <p id='password-error' className='text-sm text-red-400'>
                  {fieldErrors.password}
                </p>
              )}
            </div>

            <div className='flex items-center space-x-2'>
              <input
                type='checkbox'
                id='remember'
                name='remember'
                checked={rememberMe}
                onChange={e => setRememberMe(e.target.checked)}
                className='h-4 w-4 rounded border-gray-600 bg-gray-700 text-rose-500 focus:ring-rose-500'
                data-testid='remember-me'
              />
              <Label htmlFor='remember' className='text-sm text-gray-400'>
                Remember me for 30 days
              </Label>
            </div>
          </CardContent>

          <CardFooter className='flex flex-col space-y-4'>
            <Button
              type='submit'
              disabled={isLoading}
              className='w-full bg-gradient-to-r from-rose-500 to-rose-600 hover:from-rose-600 hover:to-rose-700 text-white font-medium'
              data-testid='login-submit'
            >
              {isLoading ? (
                <>
                  <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                  Signing in...
                </>
              ) : (
                'Sign in'
              )}
            </Button>

            <p className='text-center text-sm text-gray-400'>
              Need owner access? Accounts are provisioned securely by the platform owner.
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
