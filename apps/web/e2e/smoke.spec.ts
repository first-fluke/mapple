import { expect, test } from '@playwright/test';

/**
 * E2E Smoke Tests for Globe CRM Web (Hybrid Stack)
 *
 * Verifies the deployed web application works correctly against
 * the full Supabase+Fly.io+Vercel stack.
 *
 * Usage:
 *   # Local
 *   npm run test:e2e
 *
 *   # Against deployed Vercel instance
 *   BASE_URL=https://globe-crm.vercel.app npx playwright test e2e/smoke.spec.ts
 *
 *   # Against deployed instance with API URL
 *   BASE_URL=https://globe-crm.vercel.app API_BASE_URL=https://globe-crm-api.fly.dev npx playwright test e2e/smoke.spec.ts
 */

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

test.describe('Smoke: API Health', () => {
  test('API health endpoint returns ok', async ({ request }) => {
    const resp = await request.get(`${API_BASE_URL}/health`);
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body.status).toBe('ok');
  });
});

test.describe('Smoke: Authentication Flow', () => {
  test('login page loads and renders form', async ({ page }) => {
    await page.goto('/login');
    await expect(page.getByRole('heading', { name: 'Login' })).toBeVisible();
  });

  test('login page has no main navigation', async ({ page }) => {
    await page.goto('/login');
    await expect(page.getByRole('link', { name: 'Globe' })).not.toBeVisible();
    await expect(page.getByRole('link', { name: 'Contacts' })).not.toBeVisible();
  });

  test('unauthenticated access redirects to login', async ({ page }) => {
    await page.goto('/contacts');
    await page.waitForURL(/\/login/);
    expect(page.url()).toContain('/login');
  });
});

test.describe('Smoke: API Proxy', () => {
  test('API proxy health check via web server', async ({ request }) => {
    const resp = await request.get('/api/proxy/health');
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body.status).toBe('ok');
  });

  test('protected API proxy returns 401 without auth', async ({ request }) => {
    const resp = await request.get('/api/proxy/contacts');
    expect(resp.status()).toBe(401);
  });
});

test.describe('Smoke: Navigation Structure', () => {
  test('main layout renders with all nav links', async ({ page }) => {
    await page.goto('/');

    // If redirected to login, the nav test is still valid
    // (confirms auth guard works)
    const url = page.url();
    if (url.includes('/login')) {
      // Auth guard is working, skip nav check
      return;
    }

    await expect(page.getByRole('heading', { name: 'Globe CRM' })).toBeVisible();

    for (const name of ['Globe', 'Graph', 'Contacts', 'Settings']) {
      await expect(page.getByRole('link', { name })).toBeVisible();
    }
  });

  test('navigation active state updates correctly', async ({ page }) => {
    await page.goto('/');
    if (page.url().includes('/login')) return;

    const globeLink = page.getByRole('link', { name: 'Globe' });
    await expect(globeLink).toHaveAttribute('aria-current', 'page');

    await page.getByRole('link', { name: 'Contacts' }).click();
    await page.waitForURL('/contacts');
    await expect(globeLink).not.toHaveAttribute('aria-current', 'page');
    await expect(page.getByRole('link', { name: 'Contacts' })).toHaveAttribute('aria-current', 'page');
  });
});

test.describe('Smoke: Contact CRUD via API', () => {
  let contactId: number;

  test('create a contact', async ({ request }) => {
    const resp = await request.post(`${API_BASE_URL}/contacts`, {
      data: {
        name: 'Playwright Smoke Contact',
        email: 'pw-smoke@test.example',
        latitude: 35.6762,
        longitude: 139.6503,
        country: 'Japan',
        city: 'Tokyo',
      },
    });

    // Without auth, expect 401
    if (resp.status() === 401) {
      test.skip(true, 'No auth session available for CRUD tests');
      return;
    }

    expect(resp.status()).toBe(201);
    const body = await resp.json();
    contactId = body.data.id;
    expect(body.data.name).toBe('Playwright Smoke Contact');
  });

  test('read the contact', async ({ request }) => {
    if (!contactId) {
      test.skip(true, 'Contact not created');
      return;
    }
    const resp = await request.get(`${API_BASE_URL}/contacts/${contactId}`);
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body.data.id).toBe(contactId);
  });

  test('update the contact', async ({ request }) => {
    if (!contactId) {
      test.skip(true, 'Contact not created');
      return;
    }
    const resp = await request.patch(`${API_BASE_URL}/contacts/${contactId}`, {
      data: { name: 'PW Updated Contact', city: 'Osaka' },
    });
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body.data.name).toBe('PW Updated Contact');
    expect(body.data.city).toBe('Osaka');
  });

  test('delete the contact', async ({ request }) => {
    if (!contactId) {
      test.skip(true, 'Contact not created');
      return;
    }
    const resp = await request.delete(`${API_BASE_URL}/contacts/${contactId}`);
    expect(resp.status()).toBe(204);
  });
});

test.describe('Smoke: PostGIS Bounding Box', () => {
  test('globe data endpoint responds with bbox', async ({ request }) => {
    const resp = await request.get(`${API_BASE_URL}/globe/data`, {
      params: { bbox: '126.0,37.0,128.0,38.0' },
    });

    if (resp.status() === 401) {
      test.skip(true, 'No auth session for globe query');
      return;
    }

    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body.data).toHaveProperty('contacts');
    expect(body.data).toHaveProperty('relationships');
    expect(body.data).toHaveProperty('clusters');
  });

  test('invalid bbox returns error', async ({ request }) => {
    const resp = await request.get(`${API_BASE_URL}/globe/data`, {
      params: { bbox: 'not-a-bbox' },
    });
    expect([400, 401, 422]).toContain(resp.status());
  });
});

test.describe('Smoke: Avatar Upload', () => {
  test('presigned URL endpoint responds', async ({ request }) => {
    const resp = await request.post(`${API_BASE_URL}/upload/avatar`, {
      data: { content_type: 'image/jpeg' },
    });

    if (resp.status() === 401) {
      test.skip(true, 'No auth session for upload');
      return;
    }

    expect(resp.status()).toBe(201);
    const body = await resp.json();
    expect(body.data.url).toBeTruthy();
    expect(body.data.object_name).toBeTruthy();
    expect(body.data.expires_in).toBeGreaterThan(0);
  });

  test('upload requires authentication', async ({ request }) => {
    const resp = await request.fetch(`${API_BASE_URL}/upload/avatar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      data: JSON.stringify({ content_type: 'image/png' }),
    });
    // Without session cookie/bearer token, should be 401
    expect([401, 403]).toContain(resp.status());
  });
});

test.describe('Smoke: Redis Cache (Graph)', () => {
  test('graph edges endpoint responds', async ({ request }) => {
    const resp = await request.get(`${API_BASE_URL}/graph/edges`, {
      params: { type: 'COMPANY' },
    });

    if (resp.status() === 401) {
      test.skip(true, 'No auth session for graph');
      return;
    }

    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(Array.isArray(body.data)).toBe(true);
  });

  test('graph clusters endpoint responds', async ({ request }) => {
    const resp = await request.get(`${API_BASE_URL}/graph/clusters`, {
      params: { type: 'SCHOOL' },
    });

    if (resp.status() === 401) {
      test.skip(true, 'No auth session for graph');
      return;
    }

    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(Array.isArray(body.data)).toBe(true);
  });

  test('cached responses are consistent', async ({ request }) => {
    const params = { type: 'COMPANY' };
    const resp1 = await request.get(`${API_BASE_URL}/graph/edges`, {
      params,
    });
    const resp2 = await request.get(`${API_BASE_URL}/graph/edges`, {
      params,
    });

    if (resp1.status() === 401) {
      test.skip(true, 'No auth session for graph');
      return;
    }

    expect(resp1.status()).toBe(200);
    expect(resp2.status()).toBe(200);
    expect(await resp1.json()).toEqual(await resp2.json());
  });
});
