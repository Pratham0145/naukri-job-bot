'''
Naukri Auto Job Applier
modules/helpers.py — Utility functions used across the bot
'''

import os
import csv
import time
import random
import logging
from datetime import datetime
from config.settings import logs_folder, applied_jobs_csv, failed_jobs_csv, click_delay


# ─── Logging Setup ───────────────────────────────────────────────────────────

def setup_logger() -> logging.Logger:
    '''
    Sets up and returns a logger that writes to both console and a dated log file.
    '''
    os.makedirs(logs_folder, exist_ok=True)
    log_file = os.path.join(logs_folder, f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

    logger = logging.getLogger("naukri_bot")
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s", datefmt="%H:%M:%S")

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(fmt)

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


log = setup_logger()


# ─── CSV Helpers ─────────────────────────────────────────────────────────────

APPLIED_HEADERS = ["timestamp", "job_title", "company", "location", "job_id", "url"]
FAILED_HEADERS  = ["timestamp", "job_title", "company", "location", "job_id", "url", "reason"]


def _ensure_csv(path: str, headers: list[str]) -> None:
    '''Creates the CSV file with headers if it does not exist.'''
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(headers)


def load_applied_job_ids() -> set[str]:
    '''Returns a set of job IDs already applied to (read from CSV).'''
    _ensure_csv(applied_jobs_csv, APPLIED_HEADERS)
    ids = set()
    with open(applied_jobs_csv, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("job_id"):
                ids.add(row["job_id"])
    return ids


def save_applied_job(job: dict) -> None:
    '''Appends a successfully applied job record to the CSV.'''
    _ensure_csv(applied_jobs_csv, APPLIED_HEADERS)
    with open(applied_jobs_csv, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=APPLIED_HEADERS)
        w.writerow({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "job_title": job.get("title", ""),
            "company":   job.get("company", ""),
            "location":  job.get("location", ""),
            "job_id":    job.get("job_id", ""),
            "url":       job.get("url", ""),
        })
    log.info(f"✅  Saved: {job.get('title')} @ {job.get('company')}")


def save_failed_job(job: dict, reason: str) -> None:
    '''Appends a failed application record to the failed CSV.'''
    _ensure_csv(failed_jobs_csv, FAILED_HEADERS)
    with open(failed_jobs_csv, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FAILED_HEADERS)
        w.writerow({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "job_title": job.get("title", ""),
            "company":   job.get("company", ""),
            "location":  job.get("location", ""),
            "job_id":    job.get("job_id", ""),
            "url":       job.get("url", ""),
            "reason":    reason,
        })
    log.warning(f"❌  Failed: {job.get('title')} @ {job.get('company')} — {reason}")


# ─── Timing / Human-like Delays ──────────────────────────────────────────────

def random_sleep(base: float = None, variance: float = 0.5) -> None:
    '''
    Sleeps for a randomized duration around `base` seconds to mimic human behavior.
    Defaults to click_delay from settings if base is not given.
    '''
    base = base if base is not None else click_delay
    duration = max(0.3, base + random.uniform(-variance, variance))
    time.sleep(duration)


# ─── String Filters ──────────────────────────────────────────────────────────

def contains_bad_word(text: str, bad_words: list[str]) -> str | None:
    '''
    Returns the first matched bad word if `text` contains any word from bad_words,
    else returns None. Case-insensitive.
    '''
    text_lower = text.lower()
    for word in bad_words:
        if word.lower() in text_lower:
            return word
    return None


def contains_good_word(text: str, good_words: list[str]) -> bool:
    '''
    Returns True if `text` contains at least one word from good_words,
    or if good_words is empty (no filter applied).
    '''
    if not good_words:
        return True
    text_lower = text.lower()
    return any(w.lower() in text_lower for w in good_words)


# ─── Session Summary ─────────────────────────────────────────────────────────

def print_summary(applied: int, failed: int, skipped: int) -> None:
    '''Prints a session summary to console and log.'''
    log.info("─" * 50)
    log.info(f"SESSION SUMMARY")
    log.info(f"  Applied  : {applied}")
    log.info(f"  Failed   : {failed}")
    log.info(f"  Skipped  : {skipped}")
    log.info(f"  Total    : {applied + failed + skipped}")
    log.info("─" * 50)
