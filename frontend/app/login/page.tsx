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
});

type LoginForm = z.infer<typeof LoginFormSchema>;

function clearAuthData(): void {
  // Remove browser-readable credentials left by the legacy login.
  for (const name of ['access_token', 'refresh_token', 'token_type']) localStorage.removeItem(name);
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
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    clearAuthData();
  }, []);

  const validateForm = useCallback((): LoginForm | null => {
    const result = LoginFormSchema.safeParse({ email, password });

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
  }, [email, password]);

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

    try {
      const result = await signIn('credentials', {
        email: formData.email,
        password: formData.password,
        redirect: false,
        callbackUrl: '/admin',
      });
      if (!result?.ok || result.error) {
        recordLoginAttempt(false);
        setError('Invalid email or password');
        return;
      }
      recordLoginAttempt(true);
      clearAuthData();
      router.push('/admin');
      router.refresh();
    } catch {
      recordLoginAttempt(false);
      setError('Unable to sign in. Please try again.');
    } finally {
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
        <form onSubmit={handleSubmit} noValidate>
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

            <p className='text-sm text-gray-400'>For your security, sign in again after 15 minutes.</p>
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
