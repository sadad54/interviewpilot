import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';
const browser = await chromium.launch();
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  page.setDefaultTimeout(20000);
  await mkdir('screenshots', { recursive: true });
  await page.goto('http://localhost:5173');
  await page.getByPlaceholder('How should we address you?').fill('Demo candidate');
  await page.getByRole('button', { name: 'Enter interview room' }).click();
  await page.waitForURL('**/mock-interview/**');
  await page.locator('.live-answer textarea').fill('I would measure retrieval quality using a held-out dataset and investigate failure cases.');
  await page.getByRole('button', { name: 'Submit answer' }).click();
  await page.locator('.spine-transcript details summary').first().click();
  await page.getByText(/Demo heuristic score/).first().waitFor();
  await page.screenshot({ path: 'screenshots/demo-interview.png', fullPage: true });
  page.on('dialog', dialog => dialog.accept());
  await page.getByRole('button', { name: 'Finish early' }).click();
  await page.waitForURL('**/report/**');
  await page.getByText(/do not assess technical correctness/).first().waitFor();
  await page.screenshot({ path: 'screenshots/demo-report.png', fullPage: true });
  console.log('Real backend demo interview and report passed');
} finally { await browser.close(); }
