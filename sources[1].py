import os, re, hashlib, requests
from config import COUNTRIES

def clean_html(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()

def normalize(x, country):
    company = (x.get("company") or {}).get("display_name", "")
    location = (x.get("location") or {}).get("display_name", "")
    title = x.get("title", "")
    url = x.get("redirect_url", "")
    jid = hashlib.sha256((title + company + url).encode()).hexdigest()[:24]
    return {
        "id": jid, "title": title, "company": company, "location": location,
        "url": url, "source": f"Adzuna-{country.upper()}",
        "posted": x.get("created", ""), "description": clean_html(x.get("description","")),
        "salary_min": float(x.get("salary_min") or 0),
        "salary_max": float(x.get("salary_max") or 0),
        "currency": (x.get("salary_currency") or "").upper(),
        "country": country
    }

def adzuna_search(country, query):
    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")
    if not app_id or not app_key:
        raise RuntimeError("ADZUNA_APP_ID and ADZUNA_APP_KEY are required.")
    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
    params = {
        "app_id": app_id, "app_key": app_key, "results_per_page": 50,
        "what": query, "sort_by": "date", "max_days_old": 1
    }
    r = requests.get(url, params=params, timeout=45)
    r.raise_for_status()
    return [normalize(x, country) for x in r.json().get("results", [])]

def collect():
    queries = [
        "data analyst remote", "business analyst remote",
        "business intelligence analyst remote", "product analyst remote",
        "analytics consultant remote", "research analyst remote",
        "data scientist remote", "junior data scientist remote"
    ]
    out = []
    for country in COUNTRIES:
        for q in queries:
            try:
                out.extend(adzuna_search(country, q))
            except Exception as e:
                print("Source error:", country, q, e)
    return out
