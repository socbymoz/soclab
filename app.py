import os
import logging
import random
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, request, jsonify, session, redirect, abort

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-dev-key-change-in-production")

app.config['SESSION_COOKIE_SECURE'] = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
app.config['SESSION_COOKIE_HTTPONLY'] = os.getenv("SESSION_COOKIE_HTTPONLY", "true").lower() == "true"
app.config['SESSION_COOKIE_SAMESITE'] = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")

log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", handlers=[logging.StreamHandler()])
logger = logging.getLogger("soclab")

PASS_SCORE = 9

CURRICULUM = [
    {"id": 1, "title": "SOC Fundamentals", "icon": "bi-shield-fill", "color": "primary", "desc": "Core concepts — CIA triad, SOC roles, incident lifecycle, and foundational cybersecurity principles every analyst must know.", "lessons": ["CIA Triad (Confidentiality, Integrity, Availability)", "Types of Threats & Threat Actors", "SOC Tiers (L1/L2/L3) & Responsibilities", "Incident Response Lifecycle", "SIEM & EDR Basics", "Common Security Frameworks (NIST, ISO 27001)"], "questions": [
        {"q": "What does the 'C' in CIA triad stand for?", "options": ["Confidentiality", "Compliance", "Certification", "Control"], "answer": 0},
        {"q": "Which SOC tier performs initial triage?", "options": ["L3", "L2", "L1", "Management"], "answer": 2},
        {"q": "Which phase comes first in the NIST IR lifecycle?", "options": ["Detection", "Preparation", "Containment", "Recovery"], "answer": 1},
        {"q": "What does ransomware do to data?", "options": ["Deletes it", "Encrypts it and demands payment", "Copies it to the cloud", "Logs keystrokes"], "answer": 1},
        {"q": "What is the principle of least privilege?", "options": ["Full admin for everyone", "Minimum permissions needed to do the job", "No passwords required", "All users are administrators"], "answer": 1},
        {"q": "What type of threat actor is APT29?", "options": ["Script kiddie", "Nation-state", "Insider", "Hacktivist"], "answer": 1},
        {"q": "What does EDR stand for?", "options": ["Endpoint Detection & Response", "Encrypted Data Recovery", "Early Detection Report", "External Data Routing"], "answer": 0},
        {"q": "Which NIST CSF function comes after Detect?", "options": ["Identify", "Protect", "Respond", "Recover"], "answer": 2},
        {"q": "What is an insider threat?", "options": ["A threat from outside the org", "A trusted person misusing access", "A nation-state attack", "A DDoS attack"], "answer": 1},
        {"q": "What is the CIA triad used for?", "options": ["Network topology", "Foundational security model", "Password management", "Incident classification"], "answer": 1}
    ]},
    {"id": 2, "title": "Cyber Kill Chain", "icon": "bi-link-45deg", "color": "danger", "desc": "Understand the 7 phases of a cyber attack — from reconnaissance to exfiltration — and how to detect each stage.", "lessons": ["Reconnaissance — scanning & OSINT", "Weaponization — creating the exploit", "Delivery — phishing, USB, drive-by", "Exploitation — triggering the vulnerability", "Installation — backdoors & persistence", "Command & Control (C2) — beaconing", "Actions on Objectives — data theft, ransomware"], "questions": [
        {"q": "Which phase comes after exploitation in the Cyber Kill Chain?", "options": ["Reconnaissance", "Installation", "Delivery", "Weaponization"], "answer": 1},
        {"q": "At which stage does an attacker establish C2?", "options": ["Delivery", "Exploitation", "Actions on Objectives", "Command & Control"], "answer": 3},
        {"q": "What happens during reconnaissance?", "options": ["Delivering malware", "Gathering target info", "Encrypting data", "Deleting logs"], "answer": 1},
        {"q": "What is weaponization?", "options": ["Scanning ports", "Creating the exploit payload", "Stealing data", "Patching systems"], "answer": 1},
        {"q": "Which is a common delivery method?", "options": ["Port scanning", "Phishing email", "Hash cracking", "Log analysis"], "answer": 1},
        {"q": "What happens during exploitation?", "options": ["Installing backdoors", "Triggering the vulnerability", "Scanning for open ports", "Exfiltrating data"], "answer": 1},
        {"q": "What is a backdoor?", "options": ["A firewall rule", "A method to maintain access", "A type of encryption", "A logging tool"], "answer": 1},
        {"q": "What is data exfiltration?", "options": ["Deleting data", "Stealing data from the network", "Encrypting data", "Backing up data"], "answer": 1},
        {"q": "What is a C2 server?", "options": ["A file server", "A command & control server for attackers", "A configuration server", "A certificate authority"], "answer": 1},
        {"q": "What is the first phase of the Cyber Kill Chain?", "options": ["Delivery", "Weaponization", "Reconnaissance", "Exploitation"], "answer": 2}
    ]},
    {"id": 3, "title": "MITRE ATT&CK Framework", "icon": "bi-grid-3x3-gap-fill", "color": "warning", "desc": "Industry-standard knowledge base of adversary tactics and techniques mapped to real-world attacks.", "lessons": ["What is MITRE ATT&CK? (tactics vs techniques vs procedures)", "Enterprise ATT&CK Matrix Overview", "Common Techniques: T1078 (Valid Accounts), T1059 (Command & Scripting), T1047 (WMI)", "Mapping alerts to MITRE techniques", "Using ATT&CK for threat intelligence & detection"], "questions": [
        {"q": "In MITRE ATT&CK, what is a 'Tactic'?", "options": ["A specific tool used by attackers", "The why — the goal of a technique", "A detection rule", "A vulnerability"], "answer": 1},
        {"q": "What does T1078 (Valid Accounts) enable?", "options": ["Phishing", "SQL Injection", "Using legitimate credentials", "Network scanning"], "answer": 2},
        {"q": "What is a 'Technique' in MITRE ATT&CK?", "options": ["The goal of an attack", "The 'how' — method used to achieve a tactic", "A vulnerability", "A tool"], "answer": 1},
        {"q": "How many tactics columns are in the Enterprise ATT&CK Matrix?", "options": ["7", "14", "21", "5"], "answer": 1},
        {"q": "What does T1059 map to?", "options": ["Command & Scripting", "Valid Accounts", "Phishing", "Exploitation"], "answer": 0},
        {"q": "Which tactic is about avoiding detection?", "options": ["Initial Access", "Defense Evasion", "Exfiltration", "Impact"], "answer": 1},
        {"q": "What does T1047 (WMI) allow?", "options": ["File upload", "Remote code execution via WMI", "Email spoofing", "DNS poisoning"], "answer": 1},
        {"q": "What is a 'Procedure' in ATT&CK?", "options": ["A vulnerability", "The specific implementation of a technique", "A firewall rule", "An encryption algorithm"], "answer": 1},
        {"q": "Which tactic is about stealing data?", "options": ["Initial Access", "Exfiltration", "Execution", "Privilege Escalation"], "answer": 1},
        {"q": "What is MITRE ATT&CK used for?", "options": ["Password management", "Mapping adversary behavior and detection gaps", "Network design", "Vulnerability scanning"], "answer": 1}
    ]},
    {"id": 4, "title": "Phishing Email Analysis", "icon": "bi-envelope-exclamation-fill", "color": "danger", "desc": "Learn to dissect phishing emails — analyze headers, links, attachments, and report malicious campaigns.", "lessons": ["Email Header Analysis (SPF, DKIM, DMARC)", "URL Analysis — hovering vs clicking", "Attachment Analysis — macros, payloads", "Phishing Kit Detection", "Reporting & Blocking Procedures"], "questions": [
        {"q": "What email security mechanism verifies the sender's domain?", "options": ["SSL", "SPF", "HTTP", "DNS"], "answer": 1},
        {"q": "Which is a red flag in a phishing email?", "options": ["Personalized greeting", "Urgent call to action with a link", "Company logo", "Professional signature"], "answer": 1},
        {"q": "What does DMARC do?", "options": ["Encrypts email content", "Publishes policy for SPF/DKIM failures", "Scans for viruses", "Stores emails"], "answer": 1},
        {"q": "What is a homograph attack?", "options": ["Using lookalike characters in URLs", "A type of virus", "A network attack", "A password attack"], "answer": 0},
        {"q": "Why should you hover over links in emails?", "options": ["To open the link", "To preview the actual destination URL", "To download the file", "To reply to sender"], "answer": 1},
        {"q": "What tool extracts VBA macros from Office files?", "options": ["Wireshark", "olevba", "nmap", "tcpdump"], "answer": 1},
        {"q": "What is a phishing kit?", "options": ["An email client", "A pre-built fake login page that steals credentials", "A security training tool", "An antivirus"], "answer": 1},
        {"q": "What should you do after identifying a phishing email?", "options": ["Click the link to verify", "Report it via the org's reporting mechanism", "Forward it to all colleagues", "Ignore it"], "answer": 1},
        {"q": "What is DKIM?", "options": ["A cryptographic email signature", "A firewall rule", "A password policy", "A network protocol"], "answer": 0},
        {"q": "What does SPF 'fail' mean?", "options": ["Email is encrypted", "Sending server is not authorized to send for that domain", "Email is too large", "Attachment is infected"], "answer": 1}
    ]},
    {"id": 5, "title": "Detecting Web Attacks", "icon": "bi-globe2", "color": "primary", "desc": "Identify web-based attacks: SQL injection, XSS, path traversal, file upload abuse, and more from web server logs.", "lessons": ["SQL Injection Patterns (1=1, UNION SELECT, blind)", "Cross-Site Scripting (XSS) detection", "Path Traversal (../, %2e%2e/)", "File Upload Abuse (shell.php, webshell)", "Log Analysis: access.log, error.log review"], "questions": [
        {"q": "Which request pattern indicates SQL injection?", "options": ["GET /index.html", "POST /login?id=1' OR '1'='1", "GET /images/logo.png", "POST /api/data"], "answer": 1},
        {"q": "What does '?page=../../etc/passwd' suggest?", "options": ["SQL Injection", "Path Traversal", "XSS", "CSRF"], "answer": 1},
        {"q": "What is reflected XSS?", "options": ["A permanent script stored on the server", "A script that appears in the URL/request", "A SQL query", "A network scan"], "answer": 1},
        {"q": "What is a webshell?", "options": ["A type of antivirus", "A malicious script uploaded to run commands on a server", "A firewall rule", "A backup file"], "answer": 1},
        {"q": "What does UNION SELECT do in SQL injection?", "options": ["Deletes tables", "Combines original query with attacker's query", "Adds a new user", "Changes passwords"], "answer": 1},
        {"q": "What is stored XSS?", "options": ["Script that runs once in URL", "Script permanently stored on server", "A phishing email", "A brute force"], "answer": 1},
        {"q": "What status code might indicate a successful SQL injection?", "options": ["404", "200", "500", "403"], "answer": 1},
        {"q": "What does URL encoding %2e%2e%2f decode to?", "options": ["../../", "....//", "%%..", "//.."], "answer": 0},
        {"q": "What is a common file upload abuse?", "options": ["Uploading large files", "Uploading a webshell with .php extension", "Uploading images", "Downloading logs"], "answer": 1},
        {"q": "Which user agent is suspicious in logs?", "options": ["Mozilla/5.0", "curl/7.68", "Chrome/91", "Safari/605"], "answer": 1}
    ]},
    {"id": 6, "title": "Advanced Web Attack Detection", "icon": "bi-code-slash", "color": "danger", "desc": "Deeper dive into web attacks: SSRF, deserialization, API abuse, and WAF bypass techniques.", "lessons": ["Server-Side Request Forgery (SSRF)", "Insecure Deserialization", "API Abuse (broken auth, rate limiting)", "WAF Bypass Techniques", "HTTP Request Smuggling"], "questions": [
        {"q": "What does SSRF allow an attacker to do?", "options": ["Steal session cookies", "Make server-side requests to internal systems", "Modify client-side code", "Bypass password auth"], "answer": 1},
        {"q": "Which attack targets serialized objects?", "options": ["XSS", "SQLi", "Insecure Deserialization", "CSRF"], "answer": 2},
        {"q": "What is the AWS metadata endpoint?", "options": ["http://aws.com/meta", "http://169.254.169.254/latest/meta-data", "http://metadata.aws.com", "http://192.168.1.1/meta"], "answer": 1},
        {"q": "What is IDOR?", "options": ["A type of firewall", "Accessing another user's data by changing an ID parameter", "A virus", "A password attack"], "answer": 1},
        {"q": "What does credential stuffing use?", "options": ["Stolen username/password pairs from other breaches", "Random password guessing", "Brute force", "Keylogging"], "answer": 0},
        {"q": "How can attackers bypass WAF case filters?", "options": ["Using lower case", "Using mixed case like UnIoN", "Using numbers", "Using spaces"], "answer": 1},
        {"q": "What is HTTP parameter pollution?", "options": ["Adding too many headers", "Sending multiple parameters with same name to confuse WAF", "Deleting headers", "Changing HTTP methods"], "answer": 1},
        {"q": "What does insecure deserialization target?", "options": ["Encrypted traffic", "Serialized objects/cookies", "DNS queries", "Email headers"], "answer": 1},
        {"q": "What is API rate limiting abuse?", "options": ["Sending too many requests to brute force endpoints", "Using wrong HTTP methods", "Forging headers", "DNS spoofing"], "answer": 0},
        {"q": "What does a 429 status code indicate?", "options": ["Not Found", "Too Many Requests (rate limited)", "Internal Server Error", "Forbidden"], "answer": 1}
    ]},
    {"id": 7, "title": "Investigate Web Attack", "icon": "bi-search", "color": "info", "desc": "Full web attack investigation: correlate logs, identify the vulnerability, and determine the scope of compromise.", "lessons": ["Correlating web, firewall, and WAF logs", "Identifying the initial infection vector", "Tracing attacker actions post-compromise", "Determining data exposure scope", "Root cause analysis"], "questions": [
        {"q": "What is the first step in investigating a web attack?", "options": ["Patch the server", "Identify the initial access vector", "Reset all passwords", "Notify management"], "answer": 1},
        {"q": "Which logs are most critical for web attack investigation?", "options": ["DNS logs only", "Web server + WAF + firewall logs", "Email logs only", "System event logs"], "answer": 1},
        {"q": "How do you find the initial access vector?", "options": ["Check the latest log entry", "Find the earliest suspicious request from attacker IP", "Run antivirus", "Rebuild the server"], "answer": 1},
        {"q": "What is root cause analysis?", "options": ["Deleting logs", "Determining why the breach happened", "Formatting the hard drive", "Installing patches"], "answer": 1},
        {"q": "What should you check for data exposure scope?", "options": ["CPU usage", "Database query logs and outbound data transfers", "Screen brightness", "Email inbox"], "answer": 1},
        {"q": "What does correlating logs mean?", "options": ["Deleting unnecessary logs", "Connecting events from multiple sources to build a timeline", "Sorting logs by date", "Compressing log files"], "answer": 1},
        {"q": "What is a remediation?", "options": ["An attack", "A fix to prevent reoccurrence", "A type of malware", "A log format"], "answer": 1},
        {"q": "What does a 302 redirect in web logs indicate?", "options": ["File not found", "Successful login redirect", "Server error", "Forbidden access"], "answer": 1},
        {"q": "After a breach, when should systems be recovered?", "options": ["Immediately after detection", "After threat is contained and root cause fixed", "Never", "Only after paying ransom"], "answer": 1},
        {"q": "What is a post-incident review?", "options": ["A performance review", "A review of what went wrong and how to improve", "A software update", "A backup restore"], "answer": 1}
    ]},
    {"id": 8, "title": "How to Investigate a SIEM Alert", "icon": "bi-bell-fill", "color": "warning", "desc": "Practical methodology for investigating SIEM alerts: enrichment, context gathering, and escalation decision-making.", "lessons": ["Alert Triage: TP vs FP vs BP", "Enriching alerts with threat intelligence", "Querying SIEM for related events", "Building a timeline from SIEM data", "Escalation criteria & procedures"], "questions": [
        {"q": "What does enrichment add to an alert?", "options": ["Color coding", "Context like geo-location and threat intel", "Auto-remediation", "Alert suppression"], "answer": 1},
        {"q": "What is the first question when investigating a SIEM alert?", "options": ["Who is the attacker?", "Is this a true positive?", "What is the financial impact?", "Should we shut down the server?"], "answer": 1},
        {"q": "What is a True Positive?", "options": ["An alert that fired by mistake", "An alert that correctly identifies malicious activity", "A test alert", "System normal behavior"], "answer": 1},
        {"q": "What is a False Positive?", "options": ["A real attack", "An alert that incorrectly fires for benign activity", "A critical alert", "An ignored alert"], "answer": 1},
        {"q": "What is a Benign Positive?", "options": ["Expected behavior that looks suspicious", "A virus", "A false alarm", "A missed attack"], "answer": 0},
        {"q": "What is threat intelligence enrichment?", "options": ["Adding context from external sources about IOCs", "Deleting old alerts", "Creating new dashboards", "Writing reports"], "answer": 0},
        {"q": "What is a SIEM timeline?", "options": ["A list of all emails", "Events from multiple sources ordered by time", "A backup schedule", "A shift calendar"], "answer": 1},
        {"q": "When should you escalate an alert?", "options": ["Always", "When confirmed as TP beyond L1 capability", "Never", "Only during business hours"], "answer": 1},
        {"q": "What does BP stand for in triage?", "options": ["Bad Practice", "Benign Positive", "Backup Process", "Base Protocol"], "answer": 1},
        {"q": "What is alert tuning?", "options": ["Making alerts louder", "Adjusting detection rules to reduce FPs", "Deleting all alerts", "Disabling the SIEM"], "answer": 1}
    ]},
    {"id": 9, "title": "Malware Analysis Fundamentals", "icon": "bi-bug-fill", "color": "danger", "desc": "Static and dynamic malware analysis — hash lookups, strings analysis, sandbox execution, and IOC extraction.", "lessons": ["Static Analysis: hashes, strings, metadata", "Dynamic Analysis: sandbox, behavior, network", "PE Structure Analysis", "YARA Rules", "Extracting IOCs"], "questions": [
        {"q": "What is static analysis?", "options": ["Running malware in a VM", "Analyzing malware without executing it", "Network traffic analysis", "Reverse engineering assembly"], "answer": 1},
        {"q": "Which tool is used for hash lookups?", "options": ["Wireshark", "VirusTotal", "nmap", "tcpdump"], "answer": 1},
        {"q": "What is dynamic analysis?", "options": ["Analyzing file metadata", "Executing malware in a sandbox and observing behavior", "Reading source code", "Checking file signatures"], "answer": 1},
        {"q": "What is a YARA rule?", "options": ["A network protocol", "A pattern-matching rule for malware classification", "A firewall rule", "A password policy"], "answer": 1},
        {"q": "What is a PE file?", "options": ["Portable Executable — Windows binary format", "Protected Email", "Private Encryption", "Public Endpoint"], "answer": 0},
        {"q": "What is an IOC?", "options": ["Internet Operations Center", "Indicator of Compromise", "Internal Operations Control", "Incident Oversight"], "answer": 1},
        {"q": "What does 'strings' analysis show?", "options": ["Network packets", "Readable text embedded in a binary", "CPU instructions", "Memory addresses"], "answer": 1},
        {"q": "What is a sandbox?", "options": ["A type of firewall", "An isolated environment for safe malware execution", "A backup tool", "A logging system"], "answer": 1},
        {"q": "What is a hash used for?", "options": ["Encrypting data", "Uniquely identifying a file", "Network routing", "User authentication"], "answer": 1},
        {"q": "What is the first step in malware analysis?", "options": ["Dynamic analysis", "Static analysis (check hashes, strings, metadata)", "Reverse engineering", "Network capture"], "answer": 1}
    ]},
    {"id": 10, "title": "Malware — Event ID 77", "icon": "bi-filetype-exe", "color": "danger", "desc": "Deep analysis of a specific malware case (Event ID 77) — understand process injection and evasion techniques.", "lessons": ["Event ID 77: Process Injection Detected", "Common Injection Techniques", "Analyzing the injection chain", "Detecting evasion", "Remediation steps"], "questions": [
        {"q": "What does Event ID 77 typically indicate?", "options": ["Normal process creation", "Process injection detected", "File deletion", "Network connection"], "answer": 1},
        {"q": "Which API is commonly used for process injection?", "options": ["socket()", "CreateRemoteThread()", "fopen()", "regedit()"], "answer": 1},
        {"q": "What is process hollowing?", "options": ["Deleting a process", "Replacing a legitimate process's memory with malicious code", "Creating a new process", "Emptying the recycle bin"], "answer": 1},
        {"q": "What does Event ID 4688 show?", "options": ["Logon events", "Process creation events", "Network connections", "File changes"], "answer": 1},
        {"q": "What is APC injection?", "options": ["Asynchronous Procedure Call injection", "A type of virus", "A network protocol", "A logging method"], "answer": 0},
        {"q": "What is a common evasion technique?", "options": ["Using loud exploits", "Running from %TEMP% with unsigned binaries", "Using standard system tools", "Creating admin accounts"], "answer": 1},
        {"q": "How do you remediate process injection?", "options": ["Reboot the server", "Kill process, remove persistence, reimage if needed", "Ignore the alert", "Update antivirus"], "answer": 1},
        {"q": "What parent-child process chain is suspicious?", "options": ["explorer.exe → notepad.exe", "WINWORD.EXE → cmd.exe → powershell.exe", "svchost.exe → services.exe", "System → smss.exe"], "answer": 1},
        {"q": "What is CreateRemoteThread used for?", "options": ["Creating a new thread in another process", "Starting a new service", "Opening a network socket", "Writing to registry"], "answer": 0},
        {"q": "Which Event ID tracks Sysmon process injection?", "options": ["1", "3", "77", "11"], "answer": 2}
    ]},
    {"id": 11, "title": "Dynamic Malware Analysis", "icon": "bi-play-circle-fill", "color": "info", "desc": "Execute malware in a sandbox, monitor registry/file/network changes, and extract behavioral IOCs.", "lessons": ["Setting up a malware analysis lab", "Monitoring registry changes", "Network traffic capture", "Process and DLL monitoring", "Persistence mechanism analysis"], "questions": [
        {"q": "Which tool monitors real-time process activity?", "options": ["VirusTotal", "Process Monitor (ProcMon)", "Wireshark", "RegShot"], "answer": 1},
        {"q": "What should you check first after running malware?", "options": ["CPU temperature", "Registry and network changes", "Screen brightness", "USB connections"], "answer": 1},
        {"q": "What does RegShot do?", "options": ["Takes screenshots", "Compares registry snapshots before/after execution", "Records network traffic", "Monitors processes"], "answer": 1},
        {"q": "What is a persistence mechanism?", "options": ["A backup tool", "A method to survive reboots (registry keys, scheduled tasks)", "An antivirus", "A firewall"], "answer": 1},
        {"q": "Why capture network traffic during analysis?", "options": ["To monitor internet speed", "To detect C2 communication and exfiltration attempts", "To block websites", "To test bandwidth"], "answer": 1},
        {"q": "What does ProcMon show that Task Manager doesn't?", "options": ["CPU usage", "Detailed registry, file system, and process activity", "Memory usage", "Network speed"], "answer": 1},
        {"q": "What is a DLL?", "options": ["Dynamic-Link Library — shared code module", "Disk Label List", "Data Loss Prevention", "Domain Level Login"], "answer": 0},
        {"q": "What is DLL injection?", "options": ["Loading a DLL into a running process", "Deleting a DLL", "Updating a DLL", "Creating a DLL"], "answer": 0},
        {"q": "What tool captures network traffic?", "options": ["ProcMon", "Wireshark", "RegShot", "Process Hacker"], "answer": 1},
        {"q": "Why take a VM snapshot before analysis?", "options": ["To save disk space", "To restore clean state after malware execution", "To speed up the VM", "To enable networking"], "answer": 1}
    ]},
    {"id": 12, "title": "MSHTML Analysis", "icon": "bi-filetype-html", "color": "warning", "desc": "Analyze MSHTML (Trident) engine-based attacks — CVE-2021-40444 and similar browser engine exploits.", "lessons": ["What is MSHTML?", "MSHTML Exploit Mechanism", "CVE-2021-40444 Deep Dive", "Detecting exploitation in logs", "Mitigation"], "questions": [
        {"q": "What is MSHTML?", "options": ["A Windows service", "Internet Explorer's rendering engine", "A malware strain", "A firewall rule"], "answer": 1},
        {"q": "How are MSHTML exploits typically delivered?", "options": ["USB drives", "Phishing emails with malicious Office docs", "Network scanning", "DNS poisoning"], "answer": 1},
        {"q": "What is CVE-2021-40444?", "options": ["A Linux kernel bug", "An MSHTML remote code execution vulnerability", "A Windows update", "A SQL injection flaw"], "answer": 1},
        {"q": "What application is abused in MSHTML attacks?", "options": ["Notepad", "Microsoft Office (Word)", "Chrome", "Spotify"], "answer": 1},
        {"q": "What does an MSHTML exploit execute?", "options": ["JavaScript in the browser", "Arbitrary code via the Trident engine", "HTML rendering", "CSS styling"], "answer": 1},
        {"q": "How to detect MSHTML exploitation in logs?", "options": ["Look for Event ID 4625", "Look for Microsoft Office spawning unexpected child processes (cmd.exe, powershell.exe)", "Look for port scans", "Check firewall rules"], "answer": 1},
        {"q": "What is the mitigation for MSHTML exploits?", "options": ["Disable all Office macros", "Apply Microsoft security patches for the CVE", "Uninstall Internet Explorer", "Disable all email"], "answer": 1},
        {"q": "What is the Trident engine?", "options": ["A 3D rendering engine", "MSHTML — Internet Explorer's rendering engine", "A database engine", "A game engine"], "answer": 1},
        {"q": "What user interaction is needed for MSHTML exploit?", "options": ["Rebooting the computer", "Opening a malicious Office document", "Disabling antivirus", "Changing passwords"], "answer": 1},
        {"q": "What child process from WINWORD.EXE is suspicious?", "options": ["winword.exe itself", "cmd.exe or powershell.exe", "explorer.exe", "taskmgr.exe"], "answer": 1}
    ]},
    {"id": 13, "title": "Malicious Document Analysis", "icon": "bi-file-earmark-binary-fill", "color": "danger", "desc": "Analyze malicious Office documents, PDFs, and other file types — extract macros, OLE objects, and payloads.", "lessons": ["Office Document Structure", "Macro Analysis", "PDF Analysis", "Tools: oledump, olevba, pdf-parser", "Extracting payloads"], "questions": [
        {"q": "What VBA function is commonly used to execute commands?", "options": ["MsgBox", "Shell()", "InputBox", "Format()"], "answer": 1},
        {"q": "Which tool extracts VBA macros from Office files?", "options": ["Wireshark", "olevba", "nmap", "tcpdump"], "answer": 1},
        {"q": "What is Auto_Open in VBA?", "options": ["An automatic macro that runs when a document opens", "A manual execution command", "A network function", "A file save function"], "answer": 0},
        {"q": "What is a malicious PDF?", "options": ["A PDF that can't be opened", "A PDF containing JavaScript or embedded exploits", "A PDF with many pages", "A PDF without text"], "answer": 1},
        {"q": "What is OLE?", "options": ["Object Linking and Embedding — used in Office docs", "A programming language", "A network protocol", "An encryption standard"], "answer": 0},
        {"q": "What does pdf-parser do?", "options": ["Creates PDFs", "Analyzes PDF structure for malicious content", "Reads PDF text", "Converts PDF to Word"], "answer": 1},
        {"q": "What is a double extension file?", "options": ["invoice.doc.js (malicious JavaScript disguised as doc)", "A valid Office format", "A compressed file", "An image file"], "answer": 0},
        {"q": "What does Shell() in VBA do?", "options": ["Opens a file", "Executes a system command", "Sends an email", "Displays a message"], "answer": 1},
        {"q": "What is oledump used for?", "options": ["Dumping passwords", "Analyzing OLE streams in Office files", "Network capture", "Hash cracking"], "answer": 1},
        {"q": "What is a macro?", "options": ["A network tool", "A script that automates tasks in Office", "An antivirus", "A firewall rule"], "answer": 1}
    ]},
    {"id": 14, "title": "Security Solutions", "icon": "bi-shield-check", "color": "success", "desc": "Overview of enterprise security solutions: EDR, NGFW, IDS/IPS, WAF, DLP, and how they work together.", "lessons": ["EDR (CrowdStrike, Defender, SentinelOne)", "NGFW & IDS/IPS", "WAF (Cloudflare, ModSecurity)", "DLP & Email Security", "SIEM & SOAR"], "questions": [
        {"q": "What does EDR stand for?", "options": ["Endpoint Detection & Response", "Extended Data Recovery", "Encrypted Data Routing", "Early Detection Report"], "answer": 0},
        {"q": "Which solution blocks malicious web requests at the application layer?", "options": ["EDR", "NGFW", "WAF", "DLP"], "answer": 2},
        {"q": "What does DLP protect against?", "options": ["Viruses", "Data loss and unauthorized data transfer", "Network attacks", "Password theft"], "answer": 1},
        {"q": "What is an NGFW?", "options": ["Next-Generation Firewall with application visibility", "A basic packet filter", "A router", "A switch"], "answer": 0},
        {"q": "What is SOAR?", "options": ["Security Orchestration Automation and Response", "A type of firewall", "An antivirus", "A backup tool"], "answer": 0},
        {"q": "What does Snort/Suricata do?", "options": ["Blocks emails", "Network-based IDS/IPS detection", "Manages passwords", "Encrypts data"], "answer": 1},
        {"q": "What is an example of EDR?", "options": ["ModSecurity", "CrowdStrike Falcon", "Cloudflare", "Snort"], "answer": 1},
        {"q": "What is the primary purpose of a SIEM?", "options": ["Endpoint protection", "Log aggregation and correlation for detection", "Network routing", "Email filtering"], "answer": 1},
        {"q": "What does WAF protect?", "options": ["Email servers", "Web applications from attacks like SQLi and XSS", "File servers", "DNS servers"], "answer": 1},
        {"q": "What is email security gateway?", "options": ["A physical door lock", "A solution filtering spam, phishing, and malware in email", "A network switch", "A backup system"], "answer": 1}
    ]},
    {"id": 15, "title": "Network Log Analysis", "icon": "bi-diagram-3-fill", "color": "primary", "desc": "Analyze firewall, proxy, DNS, and netflow logs to detect C2 beaconing, data exfiltration, and lateral movement.", "lessons": ["Firewall Log Analysis", "DNS Log Analysis", "Proxy Log Analysis", "NetFlow Analysis", "Detecting C2 patterns"], "questions": [
        {"q": "Which network log is best for detecting C2 beaconing?", "options": ["Email logs", "Firewall logs (outbound connections)", "System event logs", "File audit logs"], "answer": 1},
        {"q": "What does a DNS query to a DGA domain look like?", "options": ["Normal domain like google.com", "Random-looking subdomain", "IP address in domain", "HTTPS request"], "answer": 1},
        {"q": "What is NetFlow?", "options": ["A file transfer protocol", "Network traffic metadata (IPs, ports, bytes)", "A firewall rule", "A DNS record type"], "answer": 1},
        {"q": "What is a beacon in network traffic?", "options": ["A lighthouse signal", "Regular periodic connections from malware to C2", "A type of firewall", "An email alert"], "answer": 1},
        {"q": "What does DNS tunneling do?", "options": ["Speeds up DNS", "Encodes data in DNS queries for covert C2", "Blocks DNS", "Encrypts DNS"], "answer": 1},
        {"q": "What is a proxy log?", "options": ["A log of web requests made through a proxy server", "A firewall log", "A DNS log", "A system event log"], "answer": 0},
        {"q": "What does a spike in outbound data indicate?", "options": ["System update", "Possible data exfiltration", "Normal traffic", "Backup running"], "answer": 1},
        {"q": "What is a DGA?", "options": ["Domain Generation Algorithm — used by malware to generate many C2 domains", "A firewall type", "A protocol", "An encryption method"], "answer": 0},
        {"q": "What port does DNS use?", "options": ["80", "53", "443", "22"], "answer": 1},
        {"q": "What is lateral movement?", "options": ["Moving from one compromised system to another within the network", "External attack", "Data exfiltration", "Port scanning"], "answer": 0}
    ]},
    {"id": 16, "title": "SIEM 101", "icon": "bi-layers-fill", "color": "info", "desc": "SIEM fundamentals: log ingestion, parsing, correlation rules, dashboards, and alert tuning.", "lessons": ["What is a SIEM?", "Log Ingestion & Normalization", "Correlation Rules", "Dashboards", "Alert Tuning"], "questions": [
        {"q": "What does SIEM stand for?", "options": ["Security Information & Event Management", "System Integration & Enterprise Management", "Security Intelligence & Event Monitoring", "Standard Incident Escalation Model"], "answer": 0},
        {"q": "What is the purpose of a correlation rule?", "options": ["Delete old logs", "Combine multiple events to detect attack patterns", "Format log timestamps", "Compress log files"], "answer": 1},
        {"q": "What is log normalization?", "options": ["Deleting logs", "Converting different log formats into a common format", "Encrypting logs", "Sorting logs"], "answer": 1},
        {"q": "What is an example of a SIEM platform?", "options": ["CrowdStrike", "Splunk", "ModSecurity", "Wireshark"], "answer": 1},
        {"q": "What is alert tuning?", "options": ["Making alerts louder", "Adjusting rules to reduce false positives", "Deleting all alerts", "Disabling detection"], "answer": 1},
        {"q": "What is a threshold correlation rule?", "options": ["Alerts when count exceeds a limit in a time window", "A firewall rule", "A DNS rule", "A password policy"], "answer": 0},
        {"q": "What is a SIEM dashboard?", "options": ["A physical screen", "A visual display of security metrics and alerts", "A configuration file", "A log format"], "answer": 1},
        {"q": "What is log ingestion?", "options": ["Deleting logs", "Collecting logs from various sources into the SIEM", "Archiving logs", "Compressing logs"], "answer": 1},
        {"q": "What does a SIEM do with raw logs?", "options": ["Deletes them", "Parses and normalizes for analysis", "Prints them", "Converts to PDF"], "answer": 1},
        {"q": "What is a false positive?", "options": ["A real threat detected", "An alert that fires for benign activity", "A missed attack", "A critical incident"], "answer": 1}
    ]},
    {"id": 17, "title": "Incident Management 101", "icon": "bi-exclamation-octagon-fill", "color": "danger", "desc": "Full incident lifecycle: detection, containment, eradication, recovery, lessons learned — with practical workflows.", "lessons": ["Incident Classification", "Containment Strategies", "Eradication & Remediation", "Recovery & Validation", "Post-Incident Review"], "questions": [
        {"q": "What is the priority during containment?", "options": ["Find the attacker", "Stop the spread of damage", "Patch all systems", "Notify the media"], "answer": 1},
        {"q": "What is a Post-Incident Review (PIR)?", "options": ["A technical analysis of malware", "A review of what went wrong and how to improve", "A financial audit", "A performance review"], "answer": 1},
        {"q": "What is SEV1 classification?", "options": ["Low priority", "Critical incident requiring immediate response", "Routine maintenance", "Scheduled update"], "answer": 1},
        {"q": "What is eradication?", "options": ["Containing the attack", "Removing the threat (malware, persistence)", "Restoring from backup", "Writing a report"], "answer": 1},
        {"q": "What is the first containment step for an infected endpoint?", "options": ["Format the hard drive", "Isolate from the network", "Call the attacker", "Pay the ransom"], "answer": 1},
        {"q": "What is recovery validation?", "options": ["Verifying the system is clean and secure before production use", "Deleting backups", "Formatting the drive", "Reinstalling Windows"], "answer": 0},
        {"q": "What should be done after eradication?", "options": ["Close the case", "Recovery — restore and validate", "Ignore", "Celebrate"], "answer": 1},
        {"q": "What is lessons learned?", "options": ["A training course", "Documenting gaps and improvements after an incident", "A penalty", "A meeting"], "answer": 1},
        {"q": "What is containment?", "options": ["Actions to prevent incident spread", "Removing malware", "Restoring data", "Investigating"], "answer": 0},
        {"q": "Who should be notified first for a SEV1?", "options": ["All employees", "SOC manager and incident response team", "Customers", "Media"], "answer": 1}
    ]},
    {"id": 18, "title": "Splunk for SOC Analysts", "icon": "bi-terminal-fill", "color": "warning", "desc": "Hands-on Splunk: SPL queries, dashboards, alert creation, and log investigation techniques.", "lessons": ["SPL Basics", "Common SPL Commands", "Creating Alerts & Dashboards", "Threat Hunting", "Lookups & Data Models"], "questions": [
        {"q": "Which SPL command counts events by field?", "options": ["table", "stats count by field", "eval", "rename"], "answer": 1},
        {"q": "What is a sourcetype in Splunk?", "options": ["A type of database", "A classification of log data format", "A user role", "A search command"], "answer": 1},
        {"q": "What does 'index' mean in Splunk?", "options": ["A database of logs", "A file format", "A user group", "A network port"], "answer": 0},
        {"q": "What is the Splunk search bar for?", "options": ["System settings", "Writing SPL queries to search logs", "User management", "Network config"], "answer": 1},
        {"q": "What does 'timechart' do in SPL?", "options": ["Creates a time-based chart", "Shows table of events", "Counts events", "Filters results"], "answer": 0},
        {"q": "What is a Splunk dashboard?", "options": ["A configuration file", "Visual display of searches and charts", "A log file", "A script"], "answer": 1},
        {"q": "What is a lookup in Splunk?", "options": ["A search command", "Enriching events with external data", "A dashboard", "An alert"], "answer": 1},
        {"q": "What does 'transaction' command do?", "options": ["Groups related events into a single transaction", "Deletes events", "Renames fields", "Creates charts"], "answer": 0},
        {"q": "What is a Splunk alert?", "options": ["A saved search that triggers actions", "A log entry", "A field", "An index"], "answer": 0},
        {"q": "What is Splunk's query language called?", "options": ["SQL", "SPL (Search Processing Language)", "Python", "JSON"], "answer": 1}
    ]},
    {"id": 19, "title": "Cyber Threat Intelligence", "icon": "bi-globe", "color": "primary", "desc": "CTI fundamentals: OSINT, threat feeds, indicators (IOCs), TTPs, and operationalizing intelligence.", "lessons": ["CTI Types", "OSINT Sources", "IOC Lifecycle", "Threat Feeds", "Attribution"], "questions": [
        {"q": "What is an IOC?", "options": ["Internet Operations Center", "Indicator of Compromise", "Internal Operations Control", "Incident Oversight Committee"], "answer": 1},
        {"q": "Which platform is used for sharing threat intel?", "options": ["Splunk", "MISP", "Wireshark", "nmap"], "answer": 1},
        {"q": "What is OSINT?", "options": ["Operating System Integration", "Open Source Intelligence — public info gathering", "Online Security Tool", "Offline Storage"], "answer": 1},
        {"q": "What is a threat feed?", "options": ["A news website", "A stream of IOCs from a provider", "A type of malware", "A backup tool"], "answer": 1},
        {"q": "What is strategic CTI?", "options": ["Technical IOCs", "High-level intelligence for executives", "Malware analysis", "Network logs"], "answer": 1},
        {"q": "What is tactical CTI?", "options": ["Executive reports", "TTPs, tools, and techniques of adversaries", "Financial data", "HR records"], "answer": 1},
        {"q": "What is operational CTI?", "options": ["Specific upcoming attacks", "General threat trends", "Vulnerability scans", "Log analysis"], "answer": 0},
        {"q": "What is technical CTI?", "options": ["IOCs like hashes, IPs, domains", "Business risk analysis", "Employee training", "Policy documents"], "answer": 0},
        {"q": "What does MISP stand for?", "options": ["Malware Information Sharing Platform", "Microsoft Security Protocol", "Multi-Internet Service Provider", "Managed Incident Response"], "answer": 0},
        {"q": "What is attribution in CTI?", "options": ["Assigning blame", "Identifying which threat actor is behind an attack", "Network mapping", "User identification"], "answer": 1}
    ]},
    {"id": 20, "title": "VirusTotal for SOC Analysts", "icon": "bi-search-heart", "color": "success", "desc": "Master VirusTotal for hash lookups, file analysis, behavior reports, and community intelligence.", "lessons": ["Hash Lookups", "File Upload & Analysis", "Behavior Tab", "Graphs & Relationships", "API Automation"], "questions": [
        {"q": "What color indicates a malicious file in VirusTotal?", "options": ["Green", "Red", "Yellow", "Blue"], "answer": 1},
        {"q": "What can you find in the 'Behavior' tab?", "options": ["File metadata only", "Sandbox execution results (processes, files, network)", "File's source code", "User reviews"], "answer": 1},
        {"q": "What does VirusTotal scan files with?", "options": ["One antivirus", "60+ antivirus engines", "A firewall", "A packet analyzer"], "answer": 1},
        {"q": "What is a VirusTotal hash lookup?", "options": ["Checking if a file hash is known as malicious", "Creating a new hash", "Encrypting a file", "Downloading a file"], "answer": 0},
        {"q": "What does the 'Details' tab show?", "options": ["Process behavior", "File metadata (hashes, size, type, signatures)", "Network traffic", "Registry changes"], "answer": 1},
        {"q": "What is the 'Relations' tab?", "options": ["Family relationships", "Connections between files, domains, IPs, and URLs", "User accounts", "File versions"], "answer": 1},
        {"q": "What is VirusTotal's API used for?", "options": ["Automated file analysis from scripts", "Manual file upload", "Email checking", "Password cracking"], "answer": 0},
        {"q": "What does 0 detections mean?", "options": ["File is safe", "No antivirus flagged it (but could be unknown malware)", "File is encrypted", "File is too large"], "answer": 1},
        {"q": "What is a positive detection ratio?", "options": ["Number of AV engines that flagged the file", "File size", "File type", "Upload date"], "answer": 0},
        {"q": "What is the 'Community' tab?", "options": ["Social media", "Comments and analysis from other security researchers", "File downloads", "User settings"], "answer": 1}
    ]},
    {"id": 21, "title": "Malware — Event ID 76", "icon": "bi-filetype-exe", "color": "danger", "desc": "Analyze Event ID 76 (Detection of process creation with unusual characteristics) — spotting stealthy malware.", "lessons": ["Event ID 76: Process Creation with Anomalies", "Unsigned from Temp", "Parent-Child Chain", "Live Investigation", "Remediation"], "questions": [
        {"q": "What does Event ID 76 detect?", "options": ["Network connections", "Suspicious process creation characteristics", "File deletions", "Registry modifications"], "answer": 1},
        {"q": "Which is a red flag in process creation?", "options": ["notepad.exe from System32", "powershell.exe running from Temp folder", "explorer.exe at startup", "svchost.exe normally"], "answer": 1},
        {"q": "What is an unsigned process?", "options": ["A process with a valid signature", "A process without a digital signature (could be malware)", "A system process", "A Microsoft process"], "answer": 1},
        {"q": "What parent-child chain is suspicious?", "options": ["explorer.exe → calc.exe", "Microsoft Word → cmd.exe → powershell.exe", "svchost.exe → services.exe", "winlogon.exe → userinit.exe"], "answer": 1},
        {"q": "What does Event ID 4688 log?", "options": ["Network connection", "Process creation", "File change", "Registry change"], "answer": 1},
        {"q": "Why is execution from %TEMP% suspicious?", "options": ["%TEMP% is a system folder", "Malware often runs from Temp to evade detection", "%TEMP% is read-only", "%TEMP% is encrypted"], "answer": 1},
        {"q": "What tool can capture process creation logs?", "options": ["Wireshark", "Sysmon (Event ID 1)", "nmap", "ping"], "answer": 1},
        {"q": "What is Sysmon Event ID 1?", "options": ["Network connection", "Process creation", "File creation", "Driver load"], "answer": 1},
        {"q": "What is a parent process?", "options": ["The oldest process", "The process that created the current process", "The kernel", "The system idle process"], "answer": 1},
        {"q": "What is a child process of a document editor suspicious?", "options": ["Spawning cmd.exe or powershell.exe", "Spawning notepad.exe", "Spawning calc.exe", "Spawning explorer.exe"], "answer": 0}
    ]},
    {"id": 22, "title": "IT Security Basics for Corporates", "icon": "bi-building", "color": "primary", "desc": "Enterprise security essentials: Active Directory, group policy, network segmentation, and access control models.", "lessons": ["Active Directory Security", "Network Segmentation", "Access Control Models", "Patch Management", "Compliance Frameworks"], "questions": [
        {"q": "What protocol does Active Directory use for authentication?", "options": ["HTTP", "Kerberos", "FTP", "SNMP"], "answer": 1},
        {"q": "What is the principle of least privilege?", "options": ["Give users full admin access", "Grant only minimum needed permissions", "No passwords required", "All users are admins"], "answer": 1},
        {"q": "What is a VLAN used for?", "options": ["Virtual LAN for network segmentation", "A type of firewall", "A protocol", "An encryption method"], "answer": 0},
        {"q": "What is RBAC?", "options": ["Role-Based Access Control", "A firewall type", "A routing protocol", "A backup method"], "answer": 0},
        {"q": "What does Zero Trust mean?", "options": ["Trust no one by default, verify every request", "Trust everyone", "No passwords", "Open network"], "answer": 0},
        {"q": "What is a GPO?", "options": ["Group Policy Object — manages settings in AD", "A firewall rule", "A network protocol", "A file format"], "answer": 0},
        {"q": "What is patch management?", "options": ["Systematically applying updates to fix vulnerabilities", "Deleting files", "Creating users", "Network monitoring"], "answer": 0},
        {"q": "What does GDPR protect?", "options": ["Personal data of EU citizens", "Corporate financial data", "Network infrastructure", "Physical security"], "answer": 0},
        {"q": "What is PCI-DSS?", "options": ["Payment Card Industry Data Security Standard", "A firewall standard", "A network protocol", "A programming language"], "answer": 0},
        {"q": "What is Kerberos?", "options": ["A network authentication protocol used in AD", "A firewall", "A virus", "A database"], "answer": 0}
    ]},
    {"id": 23, "title": "Detecting Brute Force Attacks", "icon": "bi-shield-exclamation", "color": "warning", "desc": "Identify and respond to brute force attacks across SSH, RDP, web logins, and VPN services.", "lessons": ["SSH Brute Force Detection", "RDP Brute Force", "Web Login Brute Force", "Account Lockout Policies", "Rate Limiting & Fail2Ban"], "questions": [
        {"q": "What Event ID indicates a failed Windows logon?", "options": ["4624", "4625", "4720", "4688"], "answer": 1},
        {"q": "Which tool automatically blocks brute force attempts on Linux?", "options": ["FirewallD", "Fail2Ban", "SELinux", "AppArmor"], "answer": 1},
        {"q": "What does Event ID 4624 mean?", "options": ["Failed logon", "Successful logon", "User created", "Process created"], "answer": 1},
        {"q": "What is credential stuffing?", "options": ["Using stolen credentials from other breaches", "Guessing passwords randomly", "Keylogging", "Phishing"], "answer": 0},
        {"q": "What is a common SSH brute force log pattern?", "options": ["Single login attempt", "Many failed password attempts from same IP", "Successful login on first try", "No log entries"], "answer": 1},
        {"q": "What does HTTP 429 mean?", "options": ["Not Found", "Too Many Requests (rate limited)", "Internal Error", "Forbidden"], "answer": 1},
        {"q": "What is an account lockout policy?", "options": ["Locks account after X failed attempts to prevent brute force", "Password expiration", "Session timeout", "Screen saver"], "answer": 0},
        {"q": "What is Fail2Ban?", "options": ["A password manager", "A tool that bans IPs after X failed login attempts", "A firewall", "An antivirus"], "answer": 1},
        {"q": "Where are SSH login attempts logged?", "options": ["/var/log/auth.log or /var/log/secure", "C:\\Windows\\System32\\winevt\\Logs", "/var/log/httpd", "/var/log/mail.log"], "answer": 0},
        {"q": "What is rate limiting?", "options": ["Limiting the speed of network traffic", "Restricting request frequency to prevent brute force", "Limiting file size", "Limiting user count"], "answer": 1}
    ]},
    {"id": 24, "title": "Building a Malware Analysis Lab", "icon": "bi-tools", "color": "info", "desc": "Set up a safe, isolated malware analysis lab with REMnux, Flare VM, and custom sandbox environments.", "lessons": ["Lab Architecture", "Tools: REMnux, Flare VM, Cuckoo", "Network Simulation", "File & Registry Monitoring", "Safe Handling Procedures"], "questions": [
        {"q": "Which VM is designed for malware analysis on Windows?", "options": ["Kali Linux", "Flare VM", "Ubuntu", "CentOS"], "answer": 1},
        {"q": "What does INetSim simulate?", "options": ["Malware execution", "Internet services for isolated analysis", "Network scanning", "Vulnerability scanning"], "answer": 1},
        {"q": "What is Cuckoo Sandbox?", "options": ["A game", "Automated malware analysis system", "A firewall", "A web server"], "answer": 1},
        {"q": "What is REMnux?", "options": ["A Linux distro for malware analysis", "A Windows analysis tool", "A network scanner", "A password cracker"], "answer": 0},
        {"q": "Why use host-only networking in analysis VMs?", "options": ["To access the internet", "To prevent malware from spreading or calling out", "To share files", "To enable printing"], "answer": 1},
        {"q": "What is FakeDNS?", "options": ["A real DNS server", "A tool that intercepts all DNS queries in the lab", "A malware strain", "A protocol"], "answer": 1},
        {"q": "Why take a VM snapshot before analysis?", "options": ["To save space", "To restore clean state after malware execution", "To network", "To install software"], "answer": 1},
        {"q": "What is the first rule of malware analysis safety?", "options": ["Use the fastest computer", "Never analyze on a production machine", "Always use Wi-Fi", "Share files with colleagues"], "answer": 1},
        {"q": "What tool analyzes PE files?", "options": ["Wireshark", "PE Studio / CFF Explorer", "nmap", "curl"], "answer": 1},
        {"q": "What is a jump box in malware analysis?", "options": ["A gaming console", "An intermediary VM to safely transfer samples into the lab", "A network router", "A type of malware"], "answer": 1}
    ]},
    {"id": 25, "title": "Building a SOC Lab at Home", "icon": "bi-houses-fill", "color": "success", "desc": "Create a home SOC lab with SIEM, EDR, firewalls, and attack simulation for hands-on practice.", "lessons": ["Architecture Overview", "Setting up Wazuh SIEM", "Deploying Security Onion", "Installing EDR", "Attack Simulation"], "questions": [
        {"q": "Which open-source SIEM is commonly used for home labs?", "options": ["Splunk", "Wazuh / Elastic Stack", "QRadar", "ArcSight"], "answer": 1},
        {"q": "What tool simulates attacks for testing detection?", "options": ["Wireshark", "Atomic Red Team", "nmap", "Metasploit"], "answer": 1},
        {"q": "What is Security Onion?", "options": ["A Linux distro", "A network security monitoring platform with IDS/IPS", "A firewall", "A password manager"], "answer": 1},
        {"q": "What does Atomic Red Team do?", "options": ["Runs safe atomic tests that map to MITRE ATT&CK techniques", "Analyzes malware", "Blocks network traffic", "Manages passwords"], "answer": 0},
        {"q": "What is Caldera?", "options": ["A volcano", "An automated adversary emulation system", "A firewall", "A web server"], "answer": 1},
        {"q": "What is Wazuh?", "options": ["A free open-source SIEM and XDR platform", "A commercial SIEM", "A firewall", "A network switch"], "answer": 0},
        {"q": "How much RAM is recommended for a home SOC lab?", "options": ["4GB", "32GB", "2GB", "8GB"], "answer": 1},
        {"q": "What is the Wazuh agent?", "options": ["A firewall", "Endpoint monitoring software installed on clients", "A router", "A switch"], "answer": 1},
        {"q": "What is Suricata in Security Onion?", "options": ["A web server", "An IDS/IPS engine", "A database", "A file server"], "answer": 1},
        {"q": "What is Zeek in Security Onion?", "options": ["A web browser", "A network analysis framework", "A game", "A text editor"], "answer": 1}
    ]},
]

@app.context_processor
def inject_globals():
    return dict(CURRICULUM=CURRICULUM, now=datetime.now, PASS_SCORE=PASS_SCORE)

@app.route('/')
def index():
    return render_template('index.html', greeting='Good Day')

@app.route('/topic/<int:topic_id>')
def topic_page(topic_id):
    topic = next((t for t in CURRICULUM if t['id'] == topic_id), None)
    if not topic:
        abort(404)
    prev_topic = next((t for t in CURRICULUM if t['id'] == topic_id - 1), None)
    next_topic = next((t for t in CURRICULUM if t['id'] == topic_id + 1), None)
    return render_template('topic.html', topic=topic, topic_idx=topic_id - 1, prev_topic=prev_topic, next_topic=next_topic)

@app.route('/check-quiz', methods=['POST'])
def check_quiz():
    data = request.get_json()
    topic = next((t for t in CURRICULUM if t['id'] == data['topic_id']), None)
    if not topic:
        return jsonify({'error': 'Topic not found'}), 404
    q = topic['questions'][data['question_idx']]
    correct = q['answer'] == data['selected']
    return jsonify({'correct': correct, 'correct_option': q['answer']})

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    logger.info(f"SOC Lab on {host}:{port} (debug={debug})")
    app.run(host=host, port=port, debug=debug)
