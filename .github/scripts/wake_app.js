const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  console.log('Navigating to app...');
  await page.goto('https://zoning-report-card.streamlit.app/', { waitUntil: 'networkidle', timeout: 30000 });

  // Look for Streamlit's "wake app" button
  const wakeButton = page.getByRole('button', { name: /yes, get this app back up|wake app/i });

  if (await wakeButton.isVisible()) {
    console.log('App is sleeping — clicking wake button...');
    await wakeButton.click();
    // Wait for the app to start loading after the click
    await page.waitForTimeout(15000);
    console.log('Wake signal sent.');
  } else {
    console.log('App is already awake.');
  }

  await browser.close();
})();
