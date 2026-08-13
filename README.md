# Naukri Auto Job Applier 🤖

Automatically searches and applies to jobs on Naukri.com. Built with **Playwright** 
(no ChromeDriver, no version mismatch issues).

---

## ⚡ Quick Start (Windows)

**1. Double-click `setup.bat`** — installs everything automatically.

Or manually:
```bash
pip install playwright flask flask-cors
python -m playwright install chromium
```

**2. Configure your details** (edit these 4 files in `/config`):

| File | What to set |
|---|---|
| `secrets.py` | Your Naukri email & password |
| `personals.py` | Your name, phone, CTC, notice period, cover letter |
| `search.py` | Job keywords, location, experience range, filters |
| `settings.py` | Resume path, pause_before_submit, headless mode |

**3. Add your resume**
```
all resumes/default/resume.pdf
```

**4. Run the bot**
```bash
python runBot.py
```

**5. View applied jobs dashboard**
```bash
python app.py
# Open http://localhost:5000
```

---

## 📁 Project Structure

```
naukri_job_applier/
├── config/
│   ├── secrets.py      ← Naukri login credentials
│   ├── personals.py    ← Your personal info (CTC, notice, cover letter)
│   ├── search.py       ← Job search keywords and filters
│   └── settings.py     ← Bot behaviour settings
├── modules/
│   ├── browser.py      ← Playwright browser session
│   ├── login.py        ← Naukri login logic
│   ├── job_search.py   ← Search + scrape job listings
│   ├── apply.py        ← Apply to each job (chatbot + modal flows)
│   └── helpers.py      ← Logging, CSV, utilities
├── all resumes/
│   └── default/
│       └── resume.pdf  ← Your resume (add this!)
├── all excels/
│   ├── applied_jobs.csv   ← Auto-created — applied job history
│   └── failed_jobs.csv    ← Auto-created — failed attempts
├── logs/               ← Auto-created — timestamped run logs
├── runBot.py           ← Main entry point
├── app.py              ← Web dashboard
└── setup.bat           ← Windows one-click setup
```

---

## ⚙️ Key Settings Explained

### `config/search.py`
```python
search_terms = ["Data Scientist", "ML Engineer", "NLP Engineer"]
search_location = "Bengaluru"
experience_min = 2
experience_max = 5
date_posted_days = "7"        # Only jobs posted in last 7 days
max_applications_per_search = 30
bad_words = ["intern", "PHP", "US Citizen"]   # Skip jobs with these words
```

### `config/settings.py`
```python
pause_before_submit = True    # RECOMMENDED for first run — review before submit
run_headless = False          # False = see browser, True = runs in background
default_resume_path = "all resumes/default/resume.pdf"
```

---

## 🔄 How It Works

```
runBot.py
  → Login to Naukri
  → For each search_term:
      → Search Naukri with filters
      → Scrape job cards (paginated)
      → Filter: skip bad_words, blacklisted companies, already applied
      → For each job:
          → Click Apply
          → Detect flow: Chatbot / Modal / External
          → Auto-answer questions (CTC, notice period, experience, etc.)
          → Pause if pause_before_submit = True
          → Submit
          → Save to applied_jobs.csv
```

---

## ⚠️ Notes

- **First run**: Keep `pause_before_submit = True` and `run_headless = False` 
  so you can see what the bot is doing and review before each submit.
- **CAPTCHA**: If Naukri shows a CAPTCHA during login, the bot pauses for 
  30 seconds — solve it manually in the browser window.
- **External jobs**: Jobs that redirect to company websites are skipped 
  (Naukri doesn't support those via automation).
- This tool is for educational and personal productivity purposes. 
  Use responsibly and in compliance with Naukri's Terms of Service.

---

## 📊 Applied Jobs Dashboard

Run `python app.py` and open `http://localhost:5000` to see:
- All applied jobs with company, title, location, timestamp
- Failed applications with reasons
- Total stats

---

*Built with Playwright | No ChromeDriver needed*
