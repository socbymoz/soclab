# SOC Log Platform — Workflow Guide

## Adding a New Module

1. Add module data in `backend/curriculum.py` under `MODULES` list
2. Each module needs: id, title, icon, color, desc, lessons, questions
3. Create topic detail template: `frontend/templates/topics/topic{id}.html`
4. Update the module count in `frontend/templates/base.html` sidebar label

## Quiz System

- Questions stored in `backend/curriculum.py` under each module
- Each question: q (string), options (list of 4), answer (0-based index)
- Client-side quiz: questions embedded as JSON in `topic.html`
- Pass threshold: `PASS_SCORE = 9` in `backend/config.py`

## Running Locally

```bash
pip install -r requirements.txt
python app.py
```

## Deploying to Vercel

Push to GitHub master branch → Vercel auto-deploys.
