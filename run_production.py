import sys, os
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()
from app import app
import waitress

host = os.getenv('HOST', '0.0.0.0')
port = int(os.getenv('PORT', 8000))
print(f"Starting SOC Log Lab (production) on {host}:{port}")
print(f"Secret key loaded: {'Yes' if app.secret_key != 'fallback-dev-key-change-in-production' else 'NO - USING FALLBACK!'}")
waitress.serve(app, host=host, port=port, threads=4)
