'''
Naukri Auto Job Applier
config/settings.py — Bot behaviour settings
'''

import os

# ─── Resume ──────────────────────────────────────────────────────────────────
# Path to your resume PDF (relative to project root)
default_resume_path = "all resumes/default/resume.pdf"

# ─── Safety ──────────────────────────────────────────────────────────────────
# Set True for your first few runs — bot will pause before submitting each job
# so you can review. Set False for fully automated runs.
pause_before_submit = True        # True or False
# In CI there's no one watching to click through a pause, so force it off.
# Make sure you've done a few supervised local runs (pause_before_submit=True,
# run_headless=False) before you trust this running unattended in the cloud.
if os.environ.get("GITHUB_ACTIONS") == "true" or os.environ.get("CI") == "true":
    pause_before_submit = False

# Pause after applying search filters so you can verify results before bot clicks
pause_after_search  = False       # True or False

# ─── Browser ─────────────────────────────────────────────────────────────────
# Run browser in background (headless). False = you can see what the bot does.
# Automatically forced to True when running inside GitHub Actions (no display
# is available there), regardless of the value below.
run_headless = False              # True or False  (False recommended for first run)
if os.environ.get("GITHUB_ACTIONS") == "true" or os.environ.get("CI") == "true":
    run_headless = True

# Slow down clicks by this many seconds (helps avoid detection, 1-2 is good)
click_delay = 1                   # Seconds between actions (integer)

# ─── Logging ─────────────────────────────────────────────────────────────────
# Where to save applied jobs history
applied_jobs_csv    = "all excels/applied_jobs.csv"
failed_jobs_csv     = "all excels/failed_jobs.csv"
logs_folder         = "logs/"

# ─── Misc ────────────────────────────────────────────────────────────────────
# Skip jobs you have already applied to (reads from applied_jobs_csv)
skip_already_applied = True       # True or False

# Follow company after applying?
follow_company = False            # True or False
