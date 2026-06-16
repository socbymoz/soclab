import os
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, request, jsonify, session, redirect
import json

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-dev-key-change-in-production")

app.config['SESSION_COOKIE_SECURE'] = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
app.config['SESSION_COOKIE_HTTPONLY'] = os.getenv("SESSION_COOKIE_HTTPONLY", "true").lower() == "true"
app.config['SESSION_COOKIE_SAMESITE'] = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")

log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", handlers=[logging.StreamHandler()])
logger = logging.getLogger("soclab")

CURRICULUM = [
    {
        "id": 1, "title": "SOC Fundamentals", "icon": "bi-shield-fill", "color": "primary",
        "desc": "Core concepts — CIA triad, SOC roles, incident lifecycle, and foundational cybersecurity principles every analyst must know.",
        "lessons": ["CIA Triad (Confidentiality, Integrity, Availability)", "Types of Threats & Threat Actors", "SOC Tiers (L1/L2/L3) & Responsibilities", "Incident Response Lifecycle", "SIEM & EDR Basics", "Common Security Frameworks (NIST, ISO 27001)"],
        "questions": [
            {"q": "What does the 'C' in CIA triad stand for?", "options": ["Confidentiality", "Compliance", "Certification", "Control"], "answer": 0},
            {"q": "Which SOC tier performs initial triage?", "options": ["L3", "L2", "L1", "Management"], "answer": 2}
        ]
    },
    {
        "id": 2, "title": "Cyber Kill Chain", "icon": "bi-link-45deg", "color": "danger",
        "desc": "Understand the 7 phases of a cyber attack — from reconnaissance to exfiltration — and how to detect each stage.",
        "lessons": ["Reconnaissance — scanning & OSINT", "Weaponization — creating the exploit", "Delivery — phishing, USB, drive-by", "Exploitation — triggering the vulnerability", "Installation — backdoors & persistence", "Command & Control (C2) — beaconing", "Actions on Objectives — data theft, ransomware"],
        "questions": [
            {"q": "Which phase comes after exploitation in the Cyber Kill Chain?", "options": ["Reconnaissance", "Installation", "Delivery", "Weaponization"], "answer": 1},
            {"q": "At which stage does an attacker establish C2?", "options": ["Delivery", "Exploitation", "Actions on Objectives", "Command & Control"], "answer": 3}
        ]
    },
    {
        "id": 3, "title": "MITRE ATT&CK Framework", "icon": "bi-grid-3x3-gap-fill", "color": "warning",
        "desc": "Industry-standard knowledge base of adversary tactics and techniques mapped to real-world attacks.",
        "lessons": ["What is MITRE ATT&CK? (tactics vs techniques vs procedures)", "Enterprise ATT&CK Matrix Overview", "Common Techniques: T1078 (Valid Accounts), T1059 (Command & Scripting), T1047 (WMI)", "Mapping alerts to MITRE techniques", "Using ATT&CK for threat intelligence & detection"],
        "questions": [
            {"q": "In MITRE ATT&CK, what is a 'Tactic'?", "options": ["A specific tool used by attackers", "The 'why' — the goal of a technique", "A detection rule", "A vulnerability"], "answer": 1},
            {"q": "What does T1078 (Valid Accounts) enable?", "options": ["Phishing", "SQL Injection", "Using legitimate credentials to move laterally", "Network scanning"], "answer": 2}
        ]
    },
    {
        "id": 4, "title": "Phishing Email Analysis", "icon": "bi-envelope-exclamation-fill", "color": "danger",
        "desc": "Learn to dissect phishing emails — analyze headers, links, attachments, and report malicious campaigns.",
        "lessons": ["Email Header Analysis (SPF, DKIM, DMARC)", "URL Analysis — hovering vs clicking", "Attachment Analysis — macros, payloads", "Phishing Kit Detection", "Reporting & Blocking Procedures"],
        "questions": [
            {"q": "What email security mechanism verifies the sender's domain?", "options": ["SSL", "SPF", "HTTP", "DNS"], "answer": 1},
            {"q": "Which is a red flag in a phishing email?", "options": ["Personalized greeting", "Urgent call to action with a link", "Company logo", "Professional signature"], "answer": 1}
        ]
    },
    {
        "id": 5, "title": "Detecting Web Attacks", "icon": "bi-globe2", "color": "primary",
        "desc": "Identify web-based attacks: SQL injection, XSS, path traversal, file upload abuse, and more from web server logs.",
        "lessons": ["SQL Injection Patterns (1=1, UNION SELECT, blind)", "Cross-Site Scripting (XSS) detection", "Path Traversal (../, %2e%2e/)", "File Upload Abuse (shell.php, webshell)", "Log Analysis: access.log, error.log review"],
        "questions": [
            {"q": "Which request pattern indicates SQL injection?", "options": ["GET /index.html", "POST /login.php?id=1' OR '1'='1", "GET /images/logo.png", "POST /api/data"], "answer": 1},
            {"q": "What does '?page=../../etc/passwd' suggest?", "options": ["SQL Injection", "Path Traversal", "XSS", "CSRF"], "answer": 1}
        ]
    },
    {
        "id": 6, "title": "Advanced Web Attack Detection", "icon": "bi-code-slash", "color": "danger",
        "desc": "Deeper dive into web attacks: SSRF, deserialization, API abuse, and WAF bypass techniques.",
        "lessons": ["Server-Side Request Forgery (SSRF)", "Insecure Deserialization", "API Abuse (broken auth, rate limiting)", "WAF Bypass Techniques", "HTTP Request Smuggling"],
        "questions": [
            {"q": "What does SSRF allow an attacker to do?", "options": ["Steal session cookies", "Make server-side requests to internal systems", "Modify client-side code", "Bypass password auth"], "answer": 1},
            {"q": "Which attack targets serialized objects?", "options": ["XSS", "SQLi", "Insecure Deserialization", "CSRF"], "answer": 2}
        ]
    },
    {
        "id": 7, "title": "Investigate Web Attack", "icon": "bi-search", "color": "info",
        "desc": "Full web attack investigation: correlate logs, identify the vulnerability, and determine the scope of compromise.",
        "lessons": ["Correlating web, firewall, and WAF logs", "Identifying the initial infection vector", "Tracing attacker actions post-compromise", "Determining data exposure scope", "Root cause analysis"],
        "questions": [
            {"q": "What is the first step in investigating a web attack?", "options": ["Patch the server", "Identify the initial access vector", "Reset all passwords", "Notify management"], "answer": 1},
            {"q": "Which logs are most critical for web attack investigation?", "options": ["DNS logs only", "Web server + WAF + firewall logs", "Email logs only", "System event logs"], "answer": 1}
        ]
    },
    {
        "id": 8, "title": "How to Investigate a SIEM Alert", "icon": "bi-bell-fill", "color": "warning",
        "desc": "Practical methodology for investigating SIEM alerts: enrichment, context gathering, and escalation decision-making.",
        "lessons": ["Alert Triage: TP vs FP vs BP", "Enriching alerts with threat intelligence", "Querying SIEM for related events", "Building a timeline from SIEM data", "Escalation criteria & procedures"],
        "questions": [
            {"q": "What does enrichment add to an alert?", "components": ["geo-IP", "threat intel", "asset ownership"], "options": ["Color coding", "Context like geo-location and threat intel", "Auto-remediation", "Alert suppression"], "answer": 1},
            {"q": "What is the first question to ask when investigating a SIEM alert?", "options": ["Who is the attacker?", "Is this a true positive?", "What is the financial impact?", "Should we shut down the server?"], "answer": 1}
        ]
    },
    {
        "id": 9, "title": "Malware Analysis Fundamentals", "icon": "bi-bug-fill", "color": "danger",
        "desc": "Static and dynamic malware analysis — hash lookups, strings analysis, sandbox execution, and IOC extraction.",
        "lessons": ["Static Analysis: hashes (MD5/SHA1/SHA256), strings, file metadata", "Dynamic Analysis: sandbox execution, network behavior", "PE Structure Analysis (sections, imports, exports)", "YARA Rules for malware classification", "Extracting IOCs from malware samples"],
        "questions": [
            {"q": "What is static analysis?", "options": ["Running malware in a VM", "Analyzing malware without executing it", "Network traffic analysis", "Reverse engineering assembly code"], "answer": 1},
            {"q": "Which tool is used for hash lookups?", "options": ["Wireshark", "VirusTotal", "nmap", "tcpdump"], "answer": 1}
        ]
    },
    {
        "id": 10, "title": "Malware — Event ID 77", "icon": "bi-filetype-exe", "color": "danger",
        "desc": "Deep analysis of a specific malware case (Event ID 77) — understand process injection and evasion techniques.",
        "lessons": ["Event ID 77: Process Injection Detected", "Common Injection Techniques (CreateRemoteThread, APC, Process Hollowing)", "Analyzing the injection chain", "Detecting evasion techniques", "Remediation steps"],
        "questions": [
            {"q": "What does Event ID 77 typically indicate?", "options": ["Normal process creation", "Process injection detected", "File deletion", "Network connection"], "answer": 1},
            {"q": "Which API is commonly used for process injection?", "options": ["socket()", "CreateRemoteThread()", "fopen()", "regedit()"], "answer": 1}
        ]
    },
    {
        "id": 11, "title": "Dynamic Malware Analysis", "icon": "bi-play-circle-fill", "color": "info",
        "desc": "Execute malware in a sandbox, monitor registry/file/network changes, and extract behavioral IOCs.",
        "lessons": ["Setting up a malware analysis lab", "Monitoring registry changes (RegShot, ProcMon)", "Network traffic capture during execution", "Process and DLL monitoring", "Persistence mechanism analysis"],
        "questions": [
            {"q": "Which tool monitors real-time process activity?", "options": ["VirusTotal", "Process Monitor (ProcMon)", "Wireshark", "RegShot"], "answer": 1},
            {"q": "What should you check first after running malware in a sandbox?", "options": ["CPU temperature", "Registry and network changes", "Screen brightness", "USB connections"], "answer": 1}
        ]
    },
    {
        "id": 12, "title": "MSHTML Analysis", "icon": "bi-filetype-html", "color": "warning",
        "desc": "Analyze MSHTML (Trident) engine-based attacks — CVE-2021-40444 and similar browser engine exploits.",
        "lessons": ["What is MSHTML? (Internet Explorer rendering engine)", "MSHTML Exploit Mechanism", "CVE-2021-40444 Deep Dive", "Detecting MSHTML exploitation in logs", "Mitigation & Patch Management"],
        "questions": [
            {"q": "What is MSHTML?", "options": ["A Windows service", "Internet Explorer's rendering engine", "A malware strain", "A firewall rule"], "answer": 1},
            {"q": "How are MSHTML exploits typically delivered?", "options": ["USB drives", "Phishing emails with malicious Office docs", "Network scanning", "DNS poisoning"], "answer": 1}
        ]
    },
    {
        "id": 13, "title": "Malicious Document Analysis", "icon": "bi-file-earmark-binary-fill", "color": "danger",
        "desc": "Analyze malicious Office documents, PDFs, and other file types — extract macros, OLE objects, and payloads.",
        "lessons": ["Office Document Structure (OLE, VBA macros)", "Macro Analysis: Auto_Open, Shell(), PowerShell invocation", "PDF Analysis (JavaScript, embedded files)", "Tools: oledump, olevba, pdf-parser", "Extracting embedded payloads"],
        "questions": [
            {"q": "What VBA function is commonly used to execute commands?", "options": ["MsgBox", "Shell()", "InputBox", "Format()"], "answer": 1},
            {"q": "Which tool extracts VBA macros from Office files?", "options": ["Wireshark", "oledump / olevba", "nmap", "tcpdump"], "answer": 1}
        ]
    },
    {
        "id": 14, "title": "Security Solutions", "icon": "bi-shield-check", "color": "success",
        "desc": "Overview of enterprise security solutions: EDR, NGFW, IDS/IPS, WAF, DLP, and how they work together.",
        "lessons": ["EDR (CrowdStrike, Defender, SentinelOne)", "NGFW & IDS/IPS (Palo Alto, Snort, Suricata)", "WAF (Cloudflare, ModSecurity)", "DLP & Email Security", "SIEM Correlation & SOAR Automation"],
        "questions": [
            {"q": "What does EDR stand for?", "options": ["Endpoint Detection & Response", "Extended Data Recovery", "Encrypted Data Routing", "Early Detection Report"], "answer": 0},
            {"q": "Which solution blocks malicious web requests at the application layer?", "options": ["EDR", "NGFW", "WAF", "DLP"], "answer": 2}
        ]
    },
    {
        "id": 15, "title": "Network Log Analysis", "icon": "bi-diagram-3-fill", "color": "primary",
        "desc": "Analyze firewall, proxy, DNS, and netflow logs to detect C2 beaconing, data exfiltration, and lateral movement.",
        "lessons": ["Firewall Log Analysis (allowed/blocked connections)", "DNS Log Analysis (DGA domains, tunneling)", "Proxy Log Analysis (user-agent anomalies)", "NetFlow Analysis (bandwidth spikes, beaconing)", "Detecting C2 communication patterns"],
        "questions": [
            {"q": "Which network log is best for detecting C2 beaconing?", "options": ["Email logs", "Firewall logs (outbound connections)", "System event logs", "File audit logs"], "answer": 1},
            {"q": "What does a DNS query to a DGA domain look like?", "options": ["Normal domain like google.com", "Random-looking subdomain like a3k8x.example.com", "IP address in domain", "HTTPS request"], "answer": 1}
        ]
    },
    {
        "id": 16, "title": "SIEM 101", "icon": "bi-layers-fill", "color": "info",
        "desc": "SIEM fundamentals: log ingestion, parsing, correlation rules, dashboards, and alert tuning.",
        "lessons": ["What is a SIEM? (Splunk, Elastic, QRadar, Sentinel)", "Log Ingestion & Normalization", "Correlation Rules (threshold, aggregation, sequence)", "Building Effective Dashboards", "Alert Tuning (reducing false positives)"],
        "questions": [
            {"q": "What does SIEM stand for?", "options": ["Security Information & Event Management", "System Integration & Enterprise Management", "Security Intelligence & Event Monitoring", "Standard Incident Escalation Model"], "answer": 0},
            {"q": "What is the purpose of a correlation rule?", "options": ["Delete old logs", "Combine multiple events to detect attack patterns", "Format log timestamps", "Compress log files"], "answer": 1}
        ]
    },
    {
        "id": 17, "title": "Incident Management 101", "icon": "bi-exclamation-octagon-fill", "color": "danger",
        "desc": "Full incident lifecycle: detection, containment, eradication, recovery, lessons learned — with practical workflows.",
        "lessons": ["Incident Classification (SEV1-SEV4)", "Containment Strategies (isolation, blocking)", "Eradication & Remediation", "Recovery & Validation", "Post-Incident Review (PIR)"],
        "questions": [
            {"q": "What is the priority during containment?", "options": ["Find the attacker", "Stop the spread of damage", "Patch all systems", "Notify the media"], "answer": 1},
            {"q": "What is a Post-Incident Review (PIR)?", "options": ["A technical analysis of malware", "A review of what went wrong and how to improve", "A financial audit", "A performance review"], "answer": 1}
        ]
    },
    {
        "id": 18, "title": "Splunk for SOC Analysts", "icon": "bi-terminal-fill", "color": "warning",
        "desc": "Hands-on Splunk: SPL queries, dashboards, alert creation, and log investigation techniques.",
        "lessons": ["SPL Basics (search, index, sourcetype)", "Common SPL Commands (stats, timechart, transaction)", "Creating Alerts & Dashboards", "Threat Hunting with Splunk", "Lookups & Data Models"],
        "questions": [
            {"q": "Which SPL command counts events by field?", "options": ["table", "stats count by field", "eval", "rename"], "answer": 1},
            {"q": "What is a sourcetype in Splunk?", "options": ["A type of database", "A classification of log data format", "A user role", "A search command"], "answer": 1}
        ]
    },
    {
        "id": 19, "title": "Cyber Threat Intelligence", "icon": "bi-globe", "color": "primary",
        "desc": "CTI fundamentals: OSINT, threat feeds, indicators (IOCs), TTPs, and operationalizing intelligence.",
        "lessons": ["CTI Types (Strategic, Tactical, Operational, Technical)", "OSINT Sources & Collection", "IOC Lifecycle (extract, validate, share)", "Threat Feeds (AlienVault OTX, MISP, VirusTotal)", "Attribution & Actor Profiling"],
        "questions": [
            {"q": "What is an IOC?", "options": ["Internet Operations Center", "Indicator of Compromise", "Internal Operations Control", "Incident Oversight Committee"], "answer": 1},
            {"q": "Which platform is used for sharing threat intel?", "options": ["Splunk", "MISP", "Wireshark", "nmap"], "answer": 1}
        ]
    },
    {
        "id": 20, "title": "VirusTotal for SOC Analysts", "icon": "bi-search-heart", "color": "success",
        "desc": "Master VirusTotal for hash lookups, file analysis, behavior reports, and community intelligence.",
        "lessons": ["Hash Lookups (MD5, SHA256)", "File Upload & Analysis", "Behavior Tab Interpretation", "Graphs & Relationships", "API Automation for SOC Workflows"],
        "questions": [
            {"q": "What color indicates a malicious file in VirusTotal?", "options": ["Green", "Red", "Yellow", "Blue"], "answer": 1},
            {"q": "What can you find in the 'Behavior' tab?", "options": ["File metadata only", "Sandbox execution results showing processes, files, network", "The file's source code", "User reviews"], "answer": 1}
        ]
    },
    {
        "id": 21, "title": "Malware — Event ID 76", "icon": "bi-filetype-exe", "color": "danger",
        "desc": "Analyze Event ID 76 (Detection of process creation with unusual characteristics) — spotting stealthy malware.",
        "lessons": ["Event ID 76: Process Creation with Anomalies", "Detecting Unsigned Processes Running from Temp", "Parent-Child Process Chain Analysis", "Live Investigation Techniques", "Remediation & Hardening"],
        "questions": [
            {"q": "What does Event ID 76 detect?", "options": ["Network connections", "Process creation with suspicious characteristics", "File deletions", "Registry modifications"], "answer": 1},
            {"q": "Which is a red flag in process creation?", "options": ["notepad.exe running from System32", "powershell.exe running from Temp folder", "explorer.exe running at startup", "svchost.exe running normally"], "answer": 1}
        ]
    },
    {
        "id": 22, "title": "IT Security Basics for Corporates", "icon": "bi-building", "color": "primary",
        "desc": "Enterprise security essentials: Active Directory, group policy, network segmentation, and access control models.",
        "lessons": ["Active Directory Security (Kerberos, LDAP, GPO)", "Network Segmentation (VLANs, DMZ, Zero Trust)", "Access Control Models (RBAC, ABAC, MAC)", "Patch Management & Vulnerability Scanning", "Compliance Frameworks (GDPR, HIPAA, PCI-DSS)"],
        "questions": [
            {"q": "What protocol does Active Directory use for authentication?", "options": ["HTTP", "Kerberos", "FTP", "SNMP"], "answer": 1},
            {"q": "What is the principle of least privilege?", "options": ["Give users full admin access", "Grant only the minimum permissions needed", "No passwords required", "All users are administrators"], "answer": 1}
        ]
    },
    {
        "id": 23, "title": "Detecting Brute Force Attacks", "icon": "bi-shield-exclamation", "color": "warning",
        "desc": "Identify and respond to brute force attacks across SSH, RDP, web logins, and VPN services.",
        "lessons": ["SSH Brute Force Detection (auth.log patterns)", "RDP Brute Force (Event ID 4625 analysis)", "Web Login Brute Force (HTTP 401/429)", "Account Lockout Policy Tuning", "Rate Limiting & Fail2Ban"],
        "questions": [
            {"q": "What Event ID indicates a failed Windows logon?", "options": ["4624", "4625", "4720", "4688"], "answer": 1},
            {"q": "Which tool automatically blocks brute force attempts on Linux?", "options": ["FirewallD", "Fail2Ban", "SELinux", "AppArmor"], "answer": 1}
        ]
    },
    {
        "id": 24, "title": "Building a Malware Analysis Lab", "icon": "bi-tools", "color": "info",
        "desc": "Set up a safe, isolated malware analysis lab with REMnux, Flare VM, and custom sandbox environments.",
        "lessons": ["Lab Architecture (host isolation, networking)", "Tools: REMnux, Flare VM, Cuckoo Sandbox", "Network Simulation (INetSim, FakeDNS)", "File & Registry Monitoring Setup", "Safe Malware Handling Procedures"],
        "questions": [
            {"q": "Which VM is designed for malware analysis on Windows?", "options": ["Kali Linux", "Flare VM", "Ubuntu", "CentOS"], "answer": 1},
            {"q": "What does INetSim simulate?", "options": ["Malware execution", "Internet services for isolated analysis", "Network scanning", "Vulnerability scanning"], "answer": 1}
        ]
    },
    {
        "id": 25, "title": "Building a SOC Lab at Home", "icon": "bi-houses-fill", "color": "success",
        "desc": "Create a home SOC lab with SIEM, EDR, firewalls, and attack simulation for hands-on practice.",
        "lessons": ["Architecture Overview (SIEM + EDR + Firewall)", "Setting up Wazuh (Open Source SIEM)", "Deploying Security Onion", "Installing & Configuring EDR", "Attack Simulation (Atomic Red Team, Caldera)"],
        "questions": [
            {"q": "Which open-source SIEM is commonly used for home labs?", "options": ["Splunk", "Wazuh / Elastic Stack", "QRadar", "ArcSight"], "answer": 1},
            {"q": "What tool simulates attacks for testing detection?", "options": ["Wireshark", "Atomic Red Team", "nmap", "Metasploit (with authorization)"], "answer": 1}
        ]
    }
]

@app.route('/')
def index():
    completed = session.get('completed_topics', [])
    total = len(CURRICULUM)
    progress = len(completed)
    hour = datetime.now().hour
    if hour < 12: greeting, icon = "Good Morning", "bi-sunrise"
    elif hour < 17: greeting, icon = "Good Afternoon", "bi-sun"
    elif hour < 21: greeting, icon = "Good Evening", "bi-moon-stars"
    else: greeting, icon = "Good Night", "bi-moon"
    return render_template('index.html', curriculum=CURRICULUM, completed=completed, progress=progress, total=total, greeting=greeting, icon=icon)

@app.route('/complete_topic/<int:tid>')
def complete_topic(tid):
    completed = session.get('completed_topics', [])
    if tid not in completed:
        completed.append(tid)
        session['completed_topics'] = completed
    return jsonify({"completed": completed, "progress": len(completed), "total": len(CURRICULUM)})

@app.route('/uncomplete_topic/<int:tid>')
def uncomplete_topic(tid):
    completed = session.get('completed_topics', [])
    if tid in completed:
        completed.remove(tid)
        session['completed_topics'] = completed
    return jsonify({"completed": completed, "progress": len(completed), "total": len(CURRICULUM)})

@app.route('/reset_progress')
def reset_progress():
    session['completed_topics'] = []
    return redirect('/')

@app.errorhandler(404)
def not_found(e):
    return '<!DOCTYPE html><html><body style="background:#0a0e14;color:#9ca3af;display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;"><div style="text-align:center"><h1 style="color:#0d6efd">404</h1><p>Page not found</p><a href="/" style="color:#0d6efd">Go home</a></div></body></html>', 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"500 error: {e}")
    return '<!DOCTYPE html><html><body style="background:#0a0e14;color:#9ca3af;display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;"><div style="text-align:center"><h1 style="color:#dc3545">500</h1><p>Something went wrong</p><a href="/" style="color:#0d6efd">Go home</a></div></body></html>', 500

if __name__ == '__main__':
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    logger.info(f"SOC Lab on {host}:{port} (debug={debug})")
    app.run(host=host, port=port, debug=debug)
