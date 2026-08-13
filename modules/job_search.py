'''
Naukri Auto Job Applier
modules/job_search.py — Searches Naukri for jobs and returns job listing URLs
'''

import time
import urllib.parse
from playwright.sync_api import Page
from config.search import (
    search_location, experience_min, experience_max,
    date_posted_days, max_applications_per_search,
    bad_words, blacklisted_companies, good_title_words,
)
from modules.helpers import log, random_sleep, contains_bad_word, contains_good_word


NAUKRI_SEARCH_BASE = "https://www.naukri.com/{keyword}-jobs"


def build_search_url(keyword: str) -> str:
    '''
    Builds a Naukri search URL for a given keyword with filters applied.
    Experience and location are appended as URL path segments (Naukri convention).
    '''
    slug = keyword.lower().replace(" ", "-")
    url = f"https://www.naukri.com/{slug}-jobs"

    params = {
        "applyType": "1"   # 🔥 ONLY Easy Apply jobs
    }

    params["jobAge"] = 3   # fresh jobs
    
    if search_location:
        params["location"] = search_location
    if experience_min is not None and experience_max is not None:
        params["experience"] = f"{experience_min}to{experience_max}"
    if date_posted_days:
        params["jobAge"] = date_posted_days

    if params:
        url += "?" + urllib.parse.urlencode(params)

    return url


def get_job_cards(page: Page) -> list[dict]:
    '''
    Scrapes job cards from the current search results page.
    Returns a list of dicts with keys: title, company, location, job_id, url.
    '''
    jobs = []
    try:
        page.wait_for_selector(".cust-job-tuple, article.jobTuple", timeout=10000)
    except Exception:
        log.warning("No job cards found on this page.")
        return jobs

    cards = page.locator(".cust-job-tuple, article.jobTuple").all()
    log.info(f"Found {len(cards)} job cards on page.")

    for card in cards:
        try:
            # Title
            title_el = card.locator("a.title, .row1 a").first
            title = title_el.inner_text(timeout=2000).strip()
            url   = title_el.get_attribute("href") or ""

            # Company
            company = ""
            try:
                company = card.locator(".comp-name, .companyInfo a").first.inner_text(timeout=2000).strip()
            except Exception:
                pass

            # Location
            location = ""
            try:
                location = card.locator(".locWdth, .location").first.inner_text(timeout=2000).strip()
            except Exception:
                pass

            # Job ID from URL
            job_id = ""
            if url:
                parts = url.rstrip("/").split("-")
                if parts and parts[-1].isdigit():
                    job_id = parts[-1]

            if title and url:
                jobs.append({
                    "title":    title,
                    "company":  company,
                    "location": location,
                    "job_id":   job_id,
                    "url":      url if url.startswith("http") else "https://www.naukri.com" + url,
                })
        except Exception as e:
            log.debug(f"Error parsing card: {e}")
            continue

    return jobs


def filter_job(job: dict) -> tuple[bool, str]:
    title = job.get("title", "").lower()
    company = job.get("company", "").lower()
    location = job.get("location", "").lower()

    text = f"{title} {company}"

    # ❌ BAD WORDS
    matched = contains_bad_word(text, bad_words)
    if matched:
        return True, f"bad word: '{matched}'"

    # ❌ BLACKLIST COMPANY
    matched = contains_bad_word(company, blacklisted_companies)
    if matched:
        return True, f"blacklisted company: '{matched}'"

    # ❌ STRICT ROLE FILTER
    valid_roles = [
        "data scientist",
        "machine learning",
        "ml engineer",
        "ai engineer",
        "genai",
        "llm",
        "nlp"
    ]

    # ✅ FLEXIBLE ROLE MATCH
    valid_keywords = [
        "data", "machine learning", "ml", "ai", "nlp", "genai", "llm"
    ]

    if not any(word in title for word in valid_keywords):
        return True, "not relevant role"

    # ❌ REMOVE SENIOR ROLES
    senior_words = [
        "lead", "manager", "director",
        "head", "architect", "principal", "vp"
    ]

    if any(word in title for word in senior_words):
        return True, "senior role"

    # ❌ LOCATION FILTER
    if "bengaluru" not in location and "bangalore" not in location:
        return True, "wrong location"

    return False, ""


def search_jobs(page: Page, keyword: str, already_applied_ids: set[str]) -> list[dict]:
    '''
    Navigates Naukri search for `keyword`, paginates through results,
    filters jobs, and returns a list of jobs to apply to.
    '''
    url = build_search_url(keyword)
    log.info(f"\n{'─'*50}")
    log.info(f"Searching: '{keyword}' | URL: {url}")
    log.info("─" * 50)

    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    random_sleep(3, 1)

    collected: list[dict] = []
    page_num = 1

    while len(collected) < max_applications_per_search:
        log.info(f"Scraping page {page_num}...")
        cards = get_job_cards(page)

        if not cards:
            log.info("No more job cards found. Ending search.")
            break

        for job in cards:
            if len(collected) >= max_applications_per_search:
                break

            # Skip already applied
            if job["job_id"] and job["job_id"] in already_applied_ids:
                log.debug(f"Skip (already applied): {job['title']}")
                continue

            # Apply filters
            skip, reason = filter_job(job)
            if skip:
                log.debug(f"Skip ({reason}): {job['title']}")
                continue

            collected.append(job)

        if len(collected) == 0:
            log.warning("⚠️ No jobs found — relaxing filter")

            # fallback: allow broader roles
            for job in cards:
                collected.append(job)
                if len(collected) >= 2:
                    break

        # Try next page
        next_btn = page.locator("a[class*='pagination']:has-text('Next'), a[title='Next']").first
        if next_btn.count() == 0:
            log.info("No next page found.")
            break

        log.info(f"Going to page {page_num + 1}...")
        next_btn.click()
        random_sleep(3, 1)
        page_num += 1

    log.info(f"Collected {len(collected)} jobs to apply for '{keyword}'")
    return collected
