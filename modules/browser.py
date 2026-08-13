'''
Naukri Auto Job Applier
modules/browser.py — Playwright browser session management

Uses Playwright instead of Selenium — no ChromeDriver needed, no version mismatch issues.
Install: pip install playwright && python -m playwright install chromium
'''

from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from config.settings import run_headless, click_delay
from modules.helpers import log, random_sleep


_playwright = None
_browser: Browser = None
_context: BrowserContext = None
page: Page = None


def launch_browser() -> Page:
    '''
    Launches a Playwright Chromium browser and returns the first page.
    Uses a persistent context to retain cookies/session across runs if available.
    '''
    global _playwright, _browser, _context, page

    log.info("Launching browser (Playwright Chromium)...")
    _playwright = sync_playwright().start()

    _browser = _playwright.chromium.launch(
        headless=run_headless,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ],
        slow_mo=click_delay * 300,   # slow_mo in ms for human-like pacing
    )

    _context = _browser.new_context(
        viewport={"width": 1366, "height": 768},
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/146.0.7680.178 Safari/537.36"
        ),
        locale="en-IN",
    )

    # Mask webdriver fingerprint
    _context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3] });
        Object.defineProperty(navigator, 'languages', { get: () => ['en-IN','en'] });
    """)

    page = _context.new_page()
    log.info("Browser launched successfully.")
    return page


def close_browser() -> None:
    '''Closes browser and stops Playwright.'''
    global _playwright, _browser, _context, page
    try:
        if page:       page.close()
        if _context:   _context.close()
        if _browser:   _browser.close()
        if _playwright: _playwright.stop()
        log.info("Browser closed.")
    except Exception as e:
        log.warning(f"Error closing browser: {e}")


def safe_click(locator, timeout: int = 5000) -> bool:
    '''
    Safely clicks a locator. Returns True on success, False if not found.
    `locator` should be a Playwright Locator object.
    '''
    try:
        locator.wait_for(state="visible", timeout=timeout)
        random_sleep(0.3, 0.2)
        locator.click()
        return True
    except Exception:
        return False


def safe_fill(locator, value: str, timeout: int = 5000) -> bool:
    '''
    Safely fills an input field. Clears it first. Returns True on success.
    '''
    try:
        locator.wait_for(state="visible", timeout=timeout)
        locator.triple_click()
        locator.fill(value)
        random_sleep(0.2, 0.1)
        return True
    except Exception:
        return False


def wait_for_url_change(current_url: str, timeout: int = 10) -> bool:
    '''Waits up to `timeout` seconds for the page URL to change.'''
    import time
    start = time.time()
    while time.time() - start < timeout:
        if page.url != current_url:
            return True
        time.sleep(0.5)
    return False
