# WSGI entry point for production - used by Waitress/Gunicorn
# Run: waitress-serve --port=8000 wsgi:app

from app import app

if __name__ == "__main__":
    app.run()
