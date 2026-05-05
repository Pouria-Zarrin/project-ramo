const { test, devices } = require('@playwright/test');

test.use({ ...devices['iPhone 13'] });

const cases = [
  { name: 'en-home', path: '/en/' },
  { name: 'fa-home', path: '/fa/' },
  { name: 'fa-products', path: '/product-category-therapeutics/category-page.html' },
  { name: 'fa-about', path: '/about-us/history.html' },
  { name: 'fa-news', path: '/news-page/news-highlights.html' },
  { name: 'fa-magazine', path: '/fa/magazine/' },
];

for (const c of cases) {
  test(`mobile header visual ${c.name}`, async ({ page }) => {
    await page.goto(`http://127.0.0.1:4174${c.path}`, { waitUntil: 'networkidle' });
    await page.screenshot({ path: `tools/screenshots/mobile-${c.name}.png`, fullPage: false });
  });
}
