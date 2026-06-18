# SOC Log Platform — Architecture

## Separation of Concerns

```
soc-log-platform/
├── frontend/           # UI layer (templates, static assets)
│   ├── templates/      # Jinja2 HTML templates
│   └── static/         # CSS, JS, images
├── backend/            # API & business logic
│   ├── app.py          # Flask factory (create_app)
│   ├── config.py       # App configuration
│   ├── routes.py       # HTTP route handlers (Blueprint)
│   ├── curriculum.py   # Curriculum data & helpers
│   └── quiz.py         # Quiz logic (scoring, validation)
├── database/           # Data layer
│   ├── models.py       # Data models/dataclasses
│   ├── queries.py      # Query helpers
│   └── seed.py         # Seed/export utilities
├── security/           # Auth & audit
│   ├── auth.py         # Password hashing/verification
│   └── audit.py        # Audit logging
├── docs/               # Documentation
├── api/                # Vercel serverless entry point
│   └── index.py
├── app.py              # Root entry point (thin wrapper)
├── wsgi.py             # WSGI server entry point
└── vercel.json         # Vercel deployment config
```

## Data Flow

1. Request → Vercel/WSGI → `app.py` → `backend.create_app()`
2. Flask factory configures app, registers Blueprint, context processor
3. Routes in `backend/routes.py` handle requests
4. Curriculum data served from `backend/curriculum.py` (data layer)
5. Templates rendered from `frontend/templates/`
6. Static assets served from `frontend/static/`
