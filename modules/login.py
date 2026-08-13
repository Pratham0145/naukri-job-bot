'''
Naukri Auto Job Applier
modules/login.py — Handles Naukri login
'''

import os
import time
from playwright.sync_api import Page
from config.secrets import email, password
from config.secrets import EMAIL, PASSWORD
from modules.helpers import log, random_sleep
from modules.browser import safe_click, safe_fill

_IN_CI = os.environ.get("GITHUB_ACTIONS") == "true" or os.environ.get("CI") == "true"


NAUKRI_HOME = "https://www.naukri.com/"
LOGIN_URL    = "https://www.naukri.com/nlogin/login"


def is_logged_in(page: Page) -> bool:
    '''
    Returns True if user appears to be already logged in
    by checking for the profile avatar / user name element.
    '''
    try:
        page.wait_for_selector(".nI-gNb-drawer__bars", timeout=3000)
        # Check for logged-in indicator (avatar or "My Naukri" text)
        logged_in = page.locator("[class*='view-profile-container'], [class*='nI-gNb-sb__icon--user']").count() > 0
        return logged_in
    except Exception:
        return False


def login(page: Page) -> bool:
    '''
    Logs in to Naukri using credentials from config/secrets.py.
    Returns True on success, False on failure.
    '''
    log.info("Navigating to Naukri login page...")
    page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=30000)

    random_sleep(2, 0.5)

    # Already logged in check
    if is_logged_in(page):
        log.info("Already logged in.")
        return True

    try:
        log.info("Filling login credentials...")

        # ---- EMAIL ----
        email_field = page.get_by_role("textbox", name="Email ID / Username")
        email_field.wait_for(timeout=10000)
        email_field.click()
        email_field.fill("")
        email_field.type(EMAIL, delay=100)

        page.keyboard.press("Tab")
        random_sleep(1)

        # ---- CLICK NEXT ----
        next_btn = page.locator(
            "button:has-text('Next'), button:has-text('Continue'), button[type='submit']"
        )

        if next_btn.count() > 0:
            next_btn.first.click()
            log.info("Clicked Next/Continue button")

        random_sleep(2)

        # ---- PASSWORD ----
        pwd_field = page.locator("input[type='password']")
        pwd_field.first.wait_for(timeout=10000)
        pwd_field.first.fill(PASSWORD)

        random_sleep(1)

        # ---- LOGIN BUTTON ----
        login_btn = page.locator("button:has-text('Login'), button[type='submit']")
        login_btn.first.click()

        log.info("Waiting for login to complete...")
        time.sleep(5)

        # ---- SUCCESS CHECK (robust) ----
        if page.locator("text=Jobs").count() > 0 or "naukri.com" in page.url:
            log.info("Login successful!")
            return True

        # ---- CAPTCHA / MANUAL ----
        if "login" in page.url.lower():
            if _IN_CI:
                # page.pause() opens an interactive inspector — there's no one
                # around to use it on a GitHub Actions runner, so it would just
                # hang until the job times out. Fail fast and clearly instead.
                log.error(
                    "CAPTCHA or manual verification required, but the bot is "
                    "running unattended in CI. Skipping this run — log in "
                    "manually on your own machine once, then retry."
                )
                return False
            log.warning("CAPTCHA or manual login required...")
            page.pause()

        # Final check
        if is_logged_in(page):
            log.info("Login successful!")
            return True
        else:
            log.error("Login failed.")
            return False

    except Exception as e:
        log.error(f"Login error: {e}")
        return False
