# SOC Log Platform — Deployment

## Vercel (Current)

- URL: https://soclab-blush.vercel.app/
- Auto-deploys from GitHub master branch
- Config: `vercel.json` rewrites all routes to `api/index.py`
- Entry point: `api/index.py` → imports Flask app from `app.py`

## Render (Alternative)

- Config: `render.yaml`
- Uses Gunicorn: `gunicorn wsgi:app`
- Set env vars: SECRET_KEY, FLASK_ENV=production

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| SECRET_KEY | fallback-... | Flask session secret |
| FLASK_ENV | production | Environment mode |
| HOST | 0.0.0.0 | Bind address |
| PORT | 8000 | Port number |
| LOG_LEVEL | INFO | Logging level |
| DEBUG | false | Debug mode |
| SESSION_COOKIE_SECURE | true | Secure session cookies |
