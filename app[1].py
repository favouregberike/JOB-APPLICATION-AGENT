import os, requests
import streamlit as st
from db import jobs, status, upsert_jobs
from sources import collect
from engine import score, qualifies
from config import DAILY_TARGET, MIN_MONTHLY_NGN

st.set_page_config(page_title="Favour Job Agent", layout="wide")
st.title("Favour — Job Application Command Center")
st.caption("Fully remote • Worldwide/Nigeria compatible • ₦500,000/month minimum • Top 10 daily")

if "msg" not in st.session_state:
    st.session_state.msg = ""

with st.sidebar:
    st.header("Agent controls")
    st.metric("Daily target", DAILY_TARGET)
    st.metric("Minimum salary", f"₦{MIN_MONTHLY_NGN:,.0f}/month")
    st.write("Remote only • No hybrid/onsite")
    if st.button("Run live search"):
        with st.spinner("Searching live job feed..."):
            raw = collect()
            accepted = []
            for j in raw:
                if qualifies(j):
                    j["score"] = score(j)
                    accepted.append(j)
            upsert_jobs(accepted)
        st.session_state.msg = f"Search complete. {len(accepted)} qualifying jobs found."
        st.rerun()

if st.session_state.msg:
    st.success(st.session_state.msg)

rows = jobs()
top, alltab, tracker, tailor = st.tabs(["Top 10", "All Jobs", "Tracker", "Tailor Application"])

with top:
    if not rows:
        st.info("Run the live search to populate jobs.")
    for r in rows[:DAILY_TARGET]:
        with st.container(border=True):
            st.subheader(f"{r['title']} — {r['company']}")
            st.write(f"**Fit:** {r['score']:.0f}/100 | **Status:** {r['status']} | **Location:** {r['location']}")
            st.caption(f"{r['source']} • Posted: {r['posted']}")
            if r["salary_min"] or r["salary_max"]:
                st.write(f"Advertised salary: {r['salary_min']:,.0f} – {r['salary_max']:,.0f} {r['currency']}")
            st.write(r["description"][:900] + ("..." if len(r["description"]) > 900 else ""))
            st.link_button("Open vacancy", r["url"])
            c1,c2,c3 = st.columns(3)
            if c1.button("Review", key="review"+r["id"]):
                status(r["id"], "Review"); st.rerun()
            if c2.button("Applied", key="applied"+r["id"]):
                status(r["id"], "Applied"); st.rerun()
            if c3.button("Rejected", key="rejected"+r["id"]):
                status(r["id"], "Rejected"); st.rerun()

with alltab:
    st.dataframe([
        {"Title":r["title"],"Company":r["company"],"Fit":r["score"],
         "Location":r["location"],"Status":r["status"],"Posted":r["posted"],"URL":r["url"]}
        for r in rows
    ], use_container_width=True)

with tracker:
    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"],0)+1
    st.write(counts)
    st.write("Pipeline: New → Review → Tailored → Applied → Interview → Offer/Rejected")

with tailor:
    cv = st.text_area("Paste master CV", height=300)
    if rows:
        opts = [(r["id"],r["title"],r["company"]) for r in rows[:50]]
        selected = st.selectbox("Choose job", opts, format_func=lambda x:f"{x[1]} — {x[2]}")
        if st.button("Generate tailored CV + cover letter"):
            row = next(r for r in rows if r["id"] == selected[0])
            key = os.getenv("OPENAI_API_KEY")
            if not key:
                st.error("Add OPENAI_API_KEY to your hosting secrets.")
            else:
                prompt = f"""Tailor this CV to the job below. Never invent employers,
dates, qualifications, skills, metrics or achievements.

MASTER CV:
{cv}

JOB:
{row['title']} — {row['company']}
{row['description']}

Return:
1) ATS-friendly tailored CV
2) concise cover letter
3) five matching keywords
"""
                response = requests.post(
                    "https://api.openai.com/v1/responses",
                    headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
                    json={"model":os.getenv("OPENAI_MODEL","gpt-5-mini"),"input":prompt},
                    timeout=90
                )
                response.raise_for_status()
                st.text_area("Tailored application package",
                             response.json().get("output_text",""), height=650)
                st.warning("Review every statement before submitting.")
