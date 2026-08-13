# Running this on GitHub Actions (free, scheduled, daily)

This repo is now set up to run automatically in the cloud via GitHub Actions.
Follow these steps once, then it runs itself every day.

## 1. Create a private GitHub repo and push this folder

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<your-username>/naukri-job-applier.git
git push -u origin main
```

Use a **private** repo — even though credentials are no longer hardcoded in
the code, it's still your personal job-application bot.

## 2. Rotate your Naukri password and Groq API key

The version of this project you shared had your real Naukri email/password
and Groq API key hardcoded in `config/secrets.py`. I removed them from the
code, but since they were already sitting in plaintext on disk, treat them
as compromised: change your Naukri password and regenerate your Groq API
key before going further, then use the new values below.

## 3. Add your credentials as GitHub Secrets

In your repo: **Settings → Secrets and variables → Actions → New repository
secret**. Add these three:

| Secret name | Value |
|---|---|
| `NAUKRI_EMAIL` | your Naukri login email |
| `NAUKRI_PASSWORD` | your Naukri login password |
| `GROQ_API_KEY` | your Groq API key |

These are encrypted by GitHub and only injected as environment variables
during the workflow run — they're never shown in logs.

## 4. Check the schedule

`.github/workflows/naukri-apply.yml` runs daily at 09:00 IST
(`30 3 * * *` in cron/UTC). Edit that line if you want a different time.
You can also trigger a run manually anytime from the **Actions** tab using
**Run workflow**.

## 5. First run — watch it closely

Trigger the workflow manually once (Actions tab → Naukri Auto Job Applier →
Run workflow) and check the logs. Since `pause_before_submit` and
`run_headless` are automatically forced to `False`/`True` respectively in
CI (no one's there to click through a pause, and there's no display), make
sure you've already tested the bot locally with `pause_before_submit = True`
and reviewed a few real submissions before trusting it unattended.

## 6. Where results go

- Logs and `all excels/applied_jobs.csv` / `failed_jobs.csv` are uploaded as
  a downloadable **artifact** on each run (Actions tab → pick a run →
  Artifacts).
- The workflow also commits the updated CSVs back to the repo automatically,
  so `skip_already_applied` correctly remembers what you've applied to
  across runs (GitHub Actions runners are thrown away after each run, so
  without this the bot would "forget" every day).

## Notes specific to running headless in CI

- If Naukri shows a CAPTCHA, the bot can't pause for you to solve it (there's
  no browser window to look at). It will log an error and skip that run —
  just log in manually from your own machine once in a while to keep the
  session/account healthy, and rerun.
- Playwright's Chromium runs invisibly on the runner — this is expected and
  not a bug.
