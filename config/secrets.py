'''
Naukri Auto Job Applier
config/secrets.py — Login credentials

Credentials are read from environment variables first (so they can be
injected securely via GitHub Actions secrets, or a local .env file loaded
by your shell). If the environment variable isn't set, it falls back to
the literal below — handy for quick local testing, but do NOT commit real
credentials here if this repo is ever pushed to GitHub (public or private).
'''

import os

email    = os.environ.get("NAUKRI_EMAIL", "")
password = os.environ.get("NAUKRI_PASSWORD", "")
EMAIL    = email
PASSWORD = password
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")