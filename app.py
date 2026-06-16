import os
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, request, jsonify, session, redirect

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-dev-key-change-in-production")

app.config['SESSION_COOKIE_SECURE'] = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
app.config['SESSION_COOKIE_HTTPONLY'] = os.getenv("SESSION_COOKIE_HTTPONLY", "true").lower() == "true"
app.config['SESSION_COOKIE_SAMESITE'] = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")

log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", handlers=[logging.StreamHandler()])
logger = logging.getLogger("soclab")

SOC_SECTIONS = ["Logs", "Alert", "Triage", "Investigation", "Response", "Recovery", "Report", "Improve"]
SOC_ROUTES = ["/logs", "/alert", "/triage", "/investigation", "/response", "/recovery", "/report", "/improve"]

@app.context_processor
def inject_globals():
    return dict(SOC_SECTIONS=SOC_SECTIONS, SOC_ROUTES=SOC_ROUTES, now=datetime.now)

@app.route('/')
def index():
    hour = datetime.now().hour
    if hour < 12: greeting, icon = "Good Morning", "bi-sunrise"
    elif hour < 17: greeting, icon = "Good Afternoon", "bi-sun"
    elif hour < 21: greeting, icon = "Good Evening", "bi-moon-stars"
    else: greeting, icon = "Good Night", "bi-moon"
    return render_template('index.html', greeting=greeting, icon=icon)

@app.route('/logs')
def logs_page():
    return render_template('logs.html', section_idx=0)

@app.route('/alert')
def alert_page():
    return render_template('alert.html', section_idx=1)

@app.route('/triage')
def triage_page():
    return render_template('triage.html', section_idx=2)

@app.route('/investigation')
def investigation_page():
    return render_template('investigation.html', section_idx=3)

@app.route('/response')
def response_page():
    return render_template('response.html', section_idx=4)

@app.route('/recovery')
def recovery_page():
    return render_template('recovery.html', section_idx=5)

@app.route('/report')
def report_page():
    return render_template('report.html', section_idx=6)

@app.route('/improve')
def improve_page():
    return render_template('improve.html', section_idx=7)

if __name__ == '__main__':
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    logger.info(f"SOC Lab on {host}:{port} (debug={debug})")
    app.run(host=host, port=port, debug=debug)
