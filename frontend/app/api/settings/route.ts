import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { withAuth } from '@/lib/api-auth';

const SETTINGS_FILE = process.env.SETTINGS_FILE || path.join(process.cwd(), 'data', 'settings.json');

async function getSettings() {
  try {
    const data = await fs.readFile(SETTINGS_FILE, 'utf-8');
    return JSON.parse(data);
  } catch (error) {
    // Default settings if file doesn't exist.
    //
    // WordPress/WooCommerce values seed from the server environment rather
    // than shipping as empty strings, so a fresh deploy shows its real
    // wiring instead of a blank form the operator has to retype from
    // .env.wordpress. Never hardcode these — env only.
    //
    // Deliberately NOT masked. GET feeds controlled inputs in
    // app/admin/settings/page.tsx, and POST writes the whole object back
    // verbatim; returning `cs_••••1234` would persist the mask over the
    // real credential on the next save. Masking safely requires POST to
    // ignore unchanged secret fields first — see the note in the buglog.
    return {
      wordpress: {
        url: process.env.WORDPRESS_SITE_URL || process.env.NEXT_PUBLIC_WORDPRESS_URL || '',
        consumerKey: process.env.WOOCOMMERCE_KEY || '',
        consumerSecret: process.env.WOOCOMMERCE_SECRET || '',
        autoSync: true,
      },
      vercel: {
        projectId: '',
        apiToken: '',
        orgId: '',
      },
      autonomous: {
        enabled: true,
        circuitBreakerThreshold: 5,
        retryAttempts: 3,
        retryDelay: 2000,
      },
      ui: {
        theme: 'dark',
        typography: 'playfair',
        accentColor: '#B76E79',
      },
      system: {
        apiTimeout: 30000,
        maxConcurrentRequests: 10,
        logLevel: 'info',
      },
    };
  }
}

async function isAuthenticated() {
  const session = await getServerSession(authOptions);
  return Boolean(session?.user?.email);
}

async function getHandler(request: NextRequest) {
  if (!(await isAuthenticated())) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const settings = await getSettings();
  return NextResponse.json(settings);
}

export const GET = withAuth(getHandler);

async function postHandler(req: NextRequest) {
  if (!(await isAuthenticated())) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const settings = await req.json();

    // Ensure data directory exists
    await fs.mkdir(path.dirname(SETTINGS_FILE), { recursive: true });

    // Write to file
    await fs.writeFile(SETTINGS_FILE, JSON.stringify(settings, null, 2), { mode: 0o600 });

    return NextResponse.json(settings);
  } catch (error) {
    console.error('Failed to save settings:', error);
    return NextResponse.json({ error: 'Failed to save settings' }, { status: 500 });
  }
}

export const POST = withAuth(postHandler);
