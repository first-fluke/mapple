import { expect, test } from '@playwright/test';

test.describe('Core Flow: Login → Contacts → Globe → Graph', () => {
  test('login page renders correctly', async ({ page }) => {
    await page.goto('/login');

    await expect(page.getByRole('heading', { name: 'Login' })).toBeVisible();
  });

  test('main layout renders with navigation', async ({ page }) => {
    await page.goto('/');

    // If auth redirects to login, skip navigation tests
    if (page.url().includes('/login')) {
      test.skip(true, 'Auth redirect — navigation tests in smoke.spec.ts');
      return;
    }

    await expect(page.getByRole('heading', { name: 'Globe CRM' })).toBeVisible();

    for (const name of ['Globe', 'Graph', 'Contacts', 'Settings']) {
      await expect(page.getByRole('link', { name })).toBeVisible();
    }
  });

  test('navigate through core flow: Globe → Contacts → Graph', async ({ page }) => {
    await page.goto('/');
    if (page.url().includes('/login')) {
      test.skip(true, 'Auth required');
      return;
    }

    await expect(page.getByRole('heading', { name: 'Globe CRM' })).toBeVisible();

    const globeLink = page.getByRole('link', { name: 'Globe' });
    await expect(globeLink).toHaveAttribute('aria-current', 'page');

    // Navigate to Contacts
    await page.getByRole('link', { name: 'Contacts' }).click();
    await page.waitForURL('/contacts');
    expect(page.url()).toContain('/contacts');

    // Navigate to Graph
    await page.getByRole('link', { name: 'Graph' }).click();
    await page.waitForURL('/graph');
    expect(page.url()).toContain('/graph');

    // Navigate back to Globe
    await page.getByRole('link', { name: 'Globe' }).click();
    await page.waitForURL('/');
    await expect(page.getByRole('heading', { name: 'Globe CRM' })).toBeVisible();
  });

  test('auth layout is separate from main layout', async ({ page }) => {
    await page.goto('/login');
    await expect(page.getByRole('heading', { name: 'Login' })).toBeVisible();

    // Nav links should not be visible on the login page
    await expect(page.getByRole('link', { name: 'Globe' })).not.toBeVisible();
  });

  test('navigation active state updates on route change', async ({ page }) => {
    await page.goto('/');
    if (page.url().includes('/login')) {
      test.skip(true, 'Auth required');
      return;
    }

    const globeLink = page.getByRole('link', { name: 'Globe' });
    await expect(globeLink).toHaveAttribute('aria-current', 'page');

    await page.getByRole('link', { name: 'Contacts' }).click();
    await page.waitForURL('/contacts');

    await expect(globeLink).not.toHaveAttribute('aria-current', 'page');

    const contactsLink = page.getByRole('link', { name: 'Contacts' });
    await expect(contactsLink).toHaveAttribute('aria-current', 'page');
  });
});
