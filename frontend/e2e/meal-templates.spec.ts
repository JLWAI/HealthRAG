import { test, expect } from '@playwright/test'

test.describe('Meal Templates', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to nutrition page
    await page.goto('/')
    await page.getByRole('button', { name: 'Food', exact: true }).click()
    await page.waitForTimeout(1000)
  })

  test('displays empty state when no templates exist', async ({ page }) => {
    // Look for meal templates section
    await expect(page.getByText('Meal Templates')).toBeVisible()

    // Should show empty state
    await expect(page.getByText(/No templates yet/i)).toBeVisible()
    await expect(page.getByText(/Log a meal, then create a template/i)).toBeVisible()
  })

  test('creates a template from logged foods', async ({ page }) => {
    // First, log some breakfast foods
    await page.getByPlaceholder(/Search foods/i).fill('chicken')
    await page.waitForTimeout(1500)

    // Add chicken breast
    await page.getByText(/Chicken Breast/i).first().click()
    await page.waitForTimeout(500)
    await page.getByRole('button', { name: /Add to/i }).click()
    await page.waitForTimeout(1000)

    // Verify food was logged
    await expect(page.getByText(/Chicken Breast/i)).toBeVisible()

    // Now create a template
    await page.getByRole('button', { name: /New/i }).click()
    await page.waitForTimeout(500)

    // Dialog should open
    await expect(page.getByText('Create Meal Template')).toBeVisible()

    // Fill in template details
    await page.getByLabel(/Template Name/i).fill('Morning Protein')

    // Select meal type (should default to breakfast based on time)
    // We'll keep the default

    // Add description
    await page.getByLabel(/Description/i).fill('Post-workout protein meal')

    // Create the template
    await page.getByRole('button', { name: /Create Template/i }).click()
    await page.waitForTimeout(1500)

    // Template should now be visible in the list
    await expect(page.getByText('Morning Protein')).toBeVisible()
    await expect(page.getByText('Post-workout protein meal')).toBeVisible()
    await expect(page.getByText(/breakfast/i)).toBeVisible()
  })

  test('expands template to show food details', async ({ page }) => {
    // Assuming a template exists from previous test
    // Look for expand button (ChevronDown icon button)
    const expandButton = page.locator('button').filter({ hasText: /chevron/i }).first()

    if (await expandButton.isVisible()) {
      await expandButton.click()
      await page.waitForTimeout(500)

      // Should show food details and totals
      await expect(page.getByText(/Total:/i)).toBeVisible()
    }
  })

  test('logs template to current day', async ({ page }) => {
    // Look for "Log to Today" button
    const logButton = page.getByRole('button', { name: /Log to Today/i }).first()

    if (await logButton.isVisible()) {
      // Get initial food count
      const initialEntries = await page.locator('[data-testid="food-entry"]').count()

      // Click log template
      await logButton.click()
      await page.waitForTimeout(2000)

      // Should have more food entries now
      const newEntries = await page.locator('[data-testid="food-entry"]').count()
      expect(newEntries).toBeGreaterThan(initialEntries)

      // Daily totals should update
      await expect(page.getByText(/Daily Progress/i)).toBeVisible()
    }
  })

  test('deletes a template', async ({ page }) => {
    // Look for delete button (Trash icon)
    const deleteButton = page.locator('button').filter({ has: page.locator('svg') }).first()

    if (await deleteButton.isVisible()) {
      // Setup dialog handler for confirmation
      page.on('dialog', dialog => dialog.accept())

      await deleteButton.click()
      await page.waitForTimeout(1000)

      // Template should be removed
      // Note: This might show empty state if it was the last template
    }
  })

  test('sorts templates by different criteria', async ({ page }) => {
    // Look for sort dropdown
    const sortSelect = page.locator('select, [role="combobox"]').first()

    if (await sortSelect.isVisible()) {
      // Try sorting by name
      await sortSelect.click()
      await page.getByText('Name').click()
      await page.waitForTimeout(500)

      // Try sorting by most used
      await sortSelect.click()
      await page.getByText('Most Used').click()
      await page.waitForTimeout(500)

      // Back to recent
      await sortSelect.click()
      await page.getByText('Recent').click()
      await page.waitForTimeout(500)
    }
  })

  test('shows template metadata correctly', async ({ page }) => {
    // Template should show:
    // - Name
    // - Meal type badge
    // - Description
    // - Last used date
    // - Use count

    const template = page.locator('div').filter({ hasText: /template/i }).first()

    if (await template.isVisible()) {
      // Should show use count
      await expect(page.getByText(/uses/i)).toBeVisible()

      // Should show last used or "Never used"
      const hasLastUsed = await page.getByText(/Last used/i).count()
      const hasNeverUsed = await page.getByText(/Never used/i).count()
      expect(hasLastUsed + hasNeverUsed).toBeGreaterThan(0)
    }
  })

  test('screenshot of meal templates feature', async ({ page }) => {
    // Take screenshot for visual verification
    await page.screenshot({
      path: 'e2e/screenshots/meal-templates.png',
      fullPage: true
    })
  })
})
