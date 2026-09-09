# Favour Job Agent — Final Hostable Package

This package is a deployable foundation for a daily remote-job discovery and application-management dashboard.

## Final search criteria
- 10 strongest jobs per daily run
- Minimum salary: NGN 500,000/month equivalent
- Fully remote only
- No hybrid or onsite
- Worldwide remote where the employer permits work from Nigeria
- Data Analyst and closely related analytics roles
- Entry-level Data Scientist
- Full-time, contract and freelance
- Experience should match the candidate profile
- Relevant industries
- Jobs posted within the last 24 hours prioritized
- Tailored CV and cover letter
- Application tracking

## Included
- Streamlit dashboard
- Job-source adapter architecture
- Adzuna live-job adapter
- Remote/eligibility filtering
- Salary conversion layer
- Fit scoring
- Daily top-10 ranking
- SQLite tracking database
- CV/cover-letter tailoring through OpenAI API
- GitHub Actions daily scheduler
- Docker deployment
- Configuration file for future changes

## Important limitation
Automatic final submission to third-party job sites is intentionally review-first. The app can prepare and track an application, but it should not blindly submit applications or fabricate answers to screening questions.

## GitHub deployment
1. Create a GitHub repository.
2. Upload this package.
3. Add repository secrets:
   ADZUNA_APP_ID
   ADZUNA_APP_KEY
   OPENAI_API_KEY (optional, required for AI tailoring)
   OPENAI_MODEL (optional; defaults to gpt-5-mini)
4. Open Actions and run `Daily Job Scan` once.
5. The scheduled workflow runs at 08:00 UTC, which is 09:00 Lagos/WAT.
6. Deploy `app.py` to Streamlit Community Cloud, or use the included Dockerfile.

## Streamlit deployment
Set the main file to `app.py` and add the same secrets in the hosting platform.

## Docker
Copy `.env.example` to `.env`, fill the keys, then run:
docker compose up --build

The dashboard is exposed on port 8501.

## Updating the agent
Edit `config.py` and push to GitHub. The live dashboard redeploys and the next scheduled scan uses the new criteria.

## Production upgrade
For larger scale, replace SQLite with PostgreSQL and add additional permitted job APIs/career feeds through `sources.py`.
