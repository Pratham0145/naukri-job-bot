'''
Naukri Auto Job Applier
config/search.py — Job search preferences and filters
'''

# ─── Search Terms ────────────────────────────────────────────────────────────
# The bot will run one search per term and apply to matching jobs
search_terms = [
    "Data Scientist",
    "ML Engineer",
    "Machine Learning Engineer",
    "AI Engineer",
    "NLP Engineer",
    "Data Science",
]

# ─── Location ────────────────────────────────────────────────────────────────
search_location = "Bengaluru"     # City to search jobs in. Leave "" for all India.

# ─── Experience Filter ───────────────────────────────────────────────────────
# Naukri experience filter (used in URL param, set both to your range)
experience_min = 2                # Minimum years (integer)
experience_max = 5                # Maximum years (integer)

# ─── How many jobs to apply per search term ──────────────────────────────────
max_applications_per_search = 30  # Bot stops this search term after N applies

# ─── Date Posted Filter ──────────────────────────────────────────────────────
# Options: "1"=24hrs, "3"=3days, "7"=1week, "15"=15days, "30"=30days, ""=any
date_posted_days = "7"

# ─── Skip Jobs containing these words in title or description ────────────────
# Case-insensitive. Add words to avoid irrelevant roles.
bad_words = [
    "intern", "internship", "unpaid", "freelance",
    "blockchain", "embedded", "hardware", ".NET", "PHP", "Ruby",
    "US Citizen", "security clearance",
]

# ─── Skip these companies ────────────────────────────────────────────────────
blacklisted_companies = [
    "Crossover", "Upwork",
]

# ─── Only apply if title contains at least one of these (leave [] to skip) ──
# If set, bot skips jobs whose title doesn't contain any good word
good_title_words = []             # e.g. ["data", "machine learning", "AI", "NLP"]

# ─── Randomize search order? ─────────────────────────────────────────────────
randomize_search_order = False    # True or False

experience_min = 2
experience_max = 5

search_location = "Bengaluru"

good_title_words = [
    "data scientist",
    "machine learning",
    "ai",
    "ml",
    "genai",
    "llm"
]