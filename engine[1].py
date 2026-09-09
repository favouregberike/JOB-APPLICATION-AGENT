import re
from datetime import datetime, timezone
from dateutil import parser
from config import *

FX_TO_USD = {
    "USD": 1.0, "GBP": 1.27, "EUR": 1.09, "CAD": .74,
    "AUD": .66, "ZAR": .055, "KES": .0067, "INR": .012,
    "NGN": 1/1500
}
NGN_PER_USD = 1500

def monthly_ngn(job):
    value = job.get("salary_max") or job.get("salary_min") or 0
    if not value:
        return None
    currency = job.get("currency","").upper()
    if currency in FX_TO_USD:
        return value * FX_TO_USD[currency] * NGN_PER_USD
    return None

def fresh(job):
    try:
        dt = parser.parse(job["posted"])
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).total_seconds() <= 86400
    except Exception:
        return False

def score(job):
    text = (job["title"] + " " + job["description"] + " " + job["location"]).lower()
    title = job["title"].lower()
    s = 0
    if any(r in title for r in TARGET_ROLES): s += 25
    s += min(25, sum(2 for x in SKILLS if x in text))
    if any(x in text for x in REMOTE_TERMS): s += 20
    if any(x in text for x in NIGERIA_TERMS): s += 12
    if any(x in text for x in MATCH_INDUSTRIES): s += 8
    if fresh(job): s += 10
    years = [int(x) for x in re.findall(r"(\d+)\+?\s*(?:years?|yrs?)", text)]
    required = max(years, default=0)
    if required > CV_EXPERIENCE_YEARS + MAX_EXTRA_EXPERIENCE_YEARS: s -= 25
    elif required <= CV_EXPERIENCE_YEARS: s += 8
    if any(x in text for x in EXCLUDE_TERMS): s -= 70
    salary = monthly_ngn(job)
    if salary is not None:
        s += 15 if salary >= MIN_MONTHLY_NGN else -35
    return max(0, min(100, s))

def qualifies(job):
    text = (job["title"] + " " + job["description"] + " " + job["location"]).lower()
    if not any(x in text for x in REMOTE_TERMS): return False
    if any(x in text for x in EXCLUDE_TERMS): return False
    salary = monthly_ngn(job)
    if salary is not None and salary < MIN_MONTHLY_NGN: return False
    return True
