'''
save_login_session.py — run this LOCALLY (not in CI), once.

Opens a real, visible Chromium window, lets you log in to Naukri by hand
(solve any CAPTCHA, 2FA, etc. yourself), then saves the authenticated
session to storage_state.json. Copy that file's contents into a GitHub
Actions secret (e.g. NAUKRI_STORAGE_STATE) so the CI workflow can write it
to disk before running the bot — bypassing the login form entirely.

Usage:
    python save_login_session.py

Re-run this whenever the saved session expires (you'll see the bot fall
back to the login form and fail again in the CI logs).
'''

from playwright.sync_api import sync_playwright

LOGIN_URL = "https://www.naukri.com/nlogin/login"
OUTPUT_PATH = "storage_state.json"


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            locale="en-IN",
        )
        page = context.new_page()
        page.goto(LOGIN_URL)

        print("\nA browser window has opened.")
        print("Log in to Naukri manually (solve any CAPTCHA if shown).")
        input("Once you're logged in and see your Naukri homepage, press Enter here... ")

        context.storage_state(path=OUTPUT_PATH)
        print(f"\nSaved session to {OUTPUT_PATH}")
        print("Next steps:")
        print(f"  1. cat {OUTPUT_PATH}")
        print("  2. Copy the ENTIRE contents.")
        print("  3. In your GitHub repo: Settings -> Secrets and variables -> Actions")
        print("     -> New repository secret -> name it NAUKRI_STORAGE_STATE -> paste it in.")
        print(f"  4. Do NOT commit {OUTPUT_PATH} itself to the repo (it contains live session cookies).")

        browser.close()


if __name__ == "__main__":
    main()
