import { expect, test } from '@playwright/test';

test.describe('Core Flow: Login → Contacts → Globe → Graph', () => {
  test('login page renders correctly', async ({ page }) => {
    await page.goto('/login');

    await expect(page.getByRole('heading', { name: 'Login' })).toBeVisible();
    await expect(page.getByText('Login page placeholder')).toBeVisible();
  });

  test('main layout renders with navigation', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByRole('heading', { name: 'Globe CRM' })).toBeVisible();

    // Verify all nav links are present (side nav for desktop)
    const globeLink = page.getByRole('link', { name: 'Globe' });
    const graphLink = page.getByRole('link', { name: 'Graph' });
    const contactsLink = page.getByRole('link', { name: 'Contacts' });
    const settingsLink = page.getByRole('link', { name: 'Settings' });

    await expect(globeLink).toBeVisible();
    await expect(graphLink).toBeVisible();
    await expect(contactsLink).toBeVisible();
    await expect(settingsLink).toBeVisible();
  });

  test('navigate through core flow: Globe → Contacts → Graph', async ({ page }) => {
    // Start at Globe (home)
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'Globe CRM' })).toBeVisible();

    // Globe nav link should be active (aria-current="page")
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
    // Auth layout should not have the main navigation
    await page.goto('/login');
    await expect(page.getByRole('heading', { name: 'Login' })).toBeVisible();

    // Nav links should not be visible on the login page
    await expect(page.getByRole('link', { name: 'Globe' })).not.toBeVisible();
  });

  test('navigation active state updates on route change', async ({ page }) => {
    await page.goto('/');

    // Globe should be active on home page
    const globeLink = page.getByRole('link', { name: 'Globe' });
    await expect(globeLink).toHaveAttribute('aria-current', 'page');

    // Navigate to Contacts
    await page.getByRole('link', { name: 'Contacts' }).click();
    await page.waitForURL('/contacts');

    // Globe should no longer be active
    await expect(globeLink).not.toHaveAttribute('aria-current', 'page');

    // Contacts link should now be active
    const contactsLink = page.getByRole('link', { name: 'Contacts' });
    await expect(contactsLink).toHaveAttribute('aria-current', 'page');
  });
});
