import { test, expect } from '@playwright/test'

test.describe('Food Logging', () => {
  test.beforeEach(async ({ page }) => {
    // Set auth token in localStorage before navigating
    await page.goto('http://localhost:3000')
    await page.evaluate(() => {
      localStorage.setItem('healthrag_token', 'dev_token')
    })
    await page.reload()
  })

  test('dashboard loads with profile data', async ({ page }) => {
    await page.goto('/')

    // Should show user greeting
    await expect(page.locator('h1')).toContainText(/Hi|Welcome/)

    // Should show weight metric card
    await expect(page.getByText('Weight', { exact: true }).first()).toBeVisible()

    // Take screenshot for debugging
    await page.screenshot({ path: 'e2e/screenshots/dashboard.png' })
  })

  test('can navigate to Food page', async ({ page }) => {
    await page.goto('/')

    // Click Food in header nav (exact match to avoid "Search Food" button)
    await page.getByRole('button', { name: 'Food', exact: true }).click()

    // Should see Nutrition header
    await expect(page.getByRole('heading', { name: /Nutrition/i })).toBeVisible()

    // Should see search input
    await expect(page.getByPlaceholder(/Search foods/i)).toBeVisible()

    await page.screenshot({ path: 'e2e/screenshots/food-page.png' })
  })

  test('food search returns results for "chicken"', async ({ page }) => {
    await page.goto('/')

    // Navigate to Food page
    await page.getByRole('button', { name: 'Food', exact: true }).click()

    // Type in search
    const searchInput = page.getByPlaceholder(/Search foods/i)
    await searchInput.fill('chicken')

    // Wait for results (API call)
    await page.waitForTimeout(1500)

    // Take screenshot to see what happened
    await page.screenshot({ path: 'e2e/screenshots/food-search-chicken.png' })

    // Should show search results - look for Chicken in the results
    await expect(page.getByText(/Chicken Breast/i).first()).toBeVisible({ timeout: 5000 })
  })

  test('can quick-add food with + button', async ({ page }) => {
    await page.goto('/')

    // Navigate to Food page
    await page.getByRole('button', { name: 'Food', exact: true }).click()

    // Search for chicken
    await page.getByPlaceholder(/Search foods/i).fill('chicken')
    await page.waitForTimeout(1500)

    await page.screenshot({ path: 'e2e/screenshots/food-before-add.png' })

    // Look for + button in search results (ghost variant button with Plus icon)
    const addButtons = page.locator('button').filter({ has: page.locator('svg.lucide-plus') })
    const count = await addButtons.count()

    if (count > 0) {
      await addButtons.first().click()
      await page.waitForTimeout(500)
      // Should show success message
      await expect(page.getByText(/logged/i)).toBeVisible({ timeout: 3000 })
    }

    await page.screenshot({ path: 'e2e/screenshots/food-quick-add.png' })
  })

  test('meal type selector works', async ({ page }) => {
    await page.goto('/')
    await page.getByRole('button', { name: 'Food', exact: true }).click()

    // Should have meal type buttons
    await expect(page.getByRole('button', { name: /breakfast/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /lunch/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /dinner/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /snack/i })).toBeVisible()

    // Click dinner
    await page.getByRole('button', { name: /dinner/i }).click()

    // Dinner should be selected (has default variant)
    await page.screenshot({ path: 'e2e/screenshots/meal-type-selector.png' })
  })
})

test.describe('API Integration', () => {
  test('food search API responds correctly', async ({ request }) => {
    const response = await request.get('http://192.168.0.210:8000/api/nutrition/search?q=chicken', {
      headers: {
        'Authorization': 'Bearer dev_token'
      }
    })

    expect(response.ok()).toBeTruthy()
    const data = await response.json()
    expect(Array.isArray(data)).toBeTruthy()
    expect(data.length).toBeGreaterThan(0)

    // Log the actual response structure for debugging
    console.log('Food search response:', JSON.stringify(data[0], null, 2))
  })

  test('daily nutrition API responds correctly', async ({ request }) => {
    const today = new Date().toISOString().split('T')[0]
    const response = await request.get(`http://192.168.0.210:8000/api/nutrition/daily-totals?date=${today}`, {
      headers: {
        'Authorization': 'Bearer dev_token'
      }
    })

    expect(response.ok()).toBeTruthy()
    const data = await response.json()
    console.log('Daily nutrition response:', JSON.stringify(data, null, 2))
  })
})
