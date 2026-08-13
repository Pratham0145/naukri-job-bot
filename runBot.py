'''
Naukri Auto Job Applier
runBot.py — Main entry point

Usage:
    python runBot.py

Requirements:
    pip install playwright
    python -m playwright install chromium
'''

import random
import sys
from config.search   import search_terms, randomize_search_order
from config.settings import skip_already_applied, pause_before_submit
from modules.helpers import log, random_sleep, load_applied_job_ids, save_applied_job, save_failed_job, print_summary
from modules.browser import launch_browser, close_browser
from modules.login   import login
from modules.job_search import search_jobs
from modules.apply   import apply_to_job


def main():
    log.info("=" * 60)
    log.info("  NAUKRI AUTO JOB APPLIER — Starting")
    log.info("=" * 60)

    if pause_before_submit:
        log.info("⚠️   pause_before_submit = True — bot will ask before each submit")
    else:
        log.info("🚀  pause_before_submit = False — bot will auto-submit all applications")

    # Launch browser
    page = launch_browser()

    # Login
    if not login(page):
        log.error("Login failed. Exiting.")
        close_browser()
        sys.exit(1)

    # Load already-applied job IDs
    already_applied = load_applied_job_ids() if skip_already_applied else set()
    log.info(f"Loaded {len(already_applied)} previously applied job IDs to skip.")

    # Stats
    total_applied = 0
    total_failed  = 0
    total_skipped = 0

    terms = list(search_terms)
    if randomize_search_order:
        random.shuffle(terms)

    for keyword in terms:
        # Search and collect jobs for this keyword
        jobs = search_jobs(page, keyword, already_applied)

        for job in jobs:
            try:
                success, reason = apply_to_job(page, job)

                if success:
                    save_applied_job(job)
                    already_applied.add(job["job_id"])
                    total_applied += 1
                else:
                    if "skipped" in reason.lower() or "already" in reason.lower() or "external" in reason.lower():
                        total_skipped += 1
                        log.info(f"  ↷  Skipped: {reason}")
                    else:
                        save_failed_job(job, reason)
                        total_failed += 1

                random_sleep(2, 1)

            except KeyboardInterrupt:
                log.info("\nInterrupted by user. Saving summary...")
                break
            except Exception as e:
                log.error(f"Unexpected error on job '{job.get('title')}': {e}")
                save_failed_job(job, str(e))
                total_failed += 1
                continue

    # Done
    close_browser()
    print_summary(total_applied, total_failed, total_skipped)


if __name__ == "__main__":
    main()
