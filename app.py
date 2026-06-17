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

MODULES = [
    {
        "id": 1, "title": "Blue Team Introduction", "icon": "bi-shield-fill", "color": "primary",
        "desc": "Start your defensive security journey by exploring the Blue Team — understand the SOC role, and how humans and systems can be attack vectors.",
        "lessons": ["Junior Security Analyst Intro", "SOC Role in Blue Team", "Humans as Attack Vectors", "Systems as Attack Vectors"],
        "questions": [
            {"q": "What is the primary role of a Blue Team?", "options": ["Offensive security", "Defensive security and protection", "Penetration testing", "Vulnerability research"], "answer": 1},
            {"q": "Which SOC tier performs initial alert triage?", "options": ["L3", "L2", "L1", "Management"], "answer": 2},
            {"q": "What is a human attack vector?", "options": ["A software vulnerability", "Social engineering targeting people", "A network exploit", "A hardware flaw"], "answer": 1},
            {"q": "What is a system attack vector?", "options": ["Phishing emails", "Unpatched software or misconfigured services", "Tailgating", "Phone calls"], "answer": 1},
            {"q": "What does a Junior SOC Analyst typically do?", "options": ["Reverse engineer malware", "Monitor alerts and triage incidents", "Build detection rules", "Manage firewalls"], "answer": 1},
            {"q": "What is the CIA triad?", "options": ["Confidentiality, Integrity, Availability", "Control, Identity, Access", "Code, Integration, Analysis", "Confidentiality, Identity, Authentication"], "answer": 0},
            {"q": "What is social engineering?", "options": ["Exploiting software bugs", "Manipulating people to reveal information", "Network scanning", "Password cracking"], "answer": 1},
            {"q": "What is an example of a system attack?", "options": ["CEO fraud", "Exploiting an unpatched vulnerability", "Shoulder surfing", "Vishing"], "answer": 1},
            {"q": "What is the first phase of the incident response lifecycle?", "options": ["Detection", "Preparation", "Containment", "Recovery"], "answer": 1},
            {"q": "What is phishing?", "options": ["A network attack", "A social engineering attack via email", "A physical attack", "A database attack"], "answer": 1}
        ]},
    {
        "id": 2, "title": "SOC Team Internals", "icon": "bi-people-fill", "color": "info",
        "desc": "Explore essential SOC analyst skills — triage, classify, and escalate alerts in real-world SOC environments.",
        "lessons": ["SOC L1 Alert Triage", "SOC L1 Alert Reporting", "SOC Workbooks and Lookups", "SOC Metrics and Objectives", "SOC Simulator: Introduction to Phishing"],
        "questions": [
            {"q": "What is alert triage?", "options": ["Deleting alerts", "Prioritizing and classifying incoming alerts", "Creating alerts", "Ignoring alerts"], "answer": 1},
            {"q": "What is a true positive?", "options": ["An alert that fires incorrectly", "An alert that correctly identifies malicious activity", "A test alert", "System normal behavior"], "answer": 1},
            {"q": "What is a false positive?", "options": ["A real attack", "An alert that incorrectly fires for benign activity", "A critical alert", "An ignored alert"], "answer": 1},
            {"q": "What is a SOC workbook?", "options": ["A textbook", "A structured document for tracking investigations", "A firewall config", "A password manager"], "answer": 1},
            {"q": "What is alert escalation?", "options": ["Deleting the alert", "Raising confirmed alerts to higher tiers", "Lowering alert priority", "Creating more alerts"], "answer": 1},
            {"q": "What is a SOC metric?", "options": ["A measurement of SOC performance", "A type of malware", "A network protocol", "A firewall rule"], "answer": 0},
            {"q": "What is MTTR?", "options": ["Mean Time to Recover", "Malware Threat Triage Report", "Managed Threat Response", "Maximum Triage Time"], "answer": 0},
            {"q": "What is a phishing simulator used for?", "options": ["Creating real phishing attacks", "Training employees to identify phishing", "Hacking email servers", "Blocking all emails"], "answer": 1},
            {"q": "What should be included in an alert report?", "options": ["Only the attacker IP", "Timeline, IOCs, actions taken, and escalation path", "Just the alert ID", "Nothing"], "answer": 1},
            {"q": "What is a benign positive?", "options": ["A real attack", "Expected suspicious behavior that is not malicious", "A false positive", "A critical alert"], "answer": 1}
        ]},
    {
        "id": 3, "title": "Core SOC Solutions", "icon": "bi-layers-fill", "color": "success",
        "desc": "Understand SIEM, EDR, and SOAR — the core security solutions used in a modern SOC.",
        "lessons": ["Introduction to EDR", "Introduction to SIEM", "Splunk: The Basics", "Elastic Stack: The Basics", "Introduction to SOAR"],
        "questions": [
            {"q": "What does EDR stand for?", "options": ["Endpoint Detection & Response", "Encrypted Data Recovery", "Early Detection Report", "External Data Routing"], "answer": 0},
            {"q": "What does SIEM stand for?", "options": ["Security Information & Event Management", "System Integration & Enterprise Management", "Security Intelligence & Event Monitoring", "Standard Incident Escalation Model"], "answer": 0},
            {"q": "What does SOAR stand for?", "options": ["Security Orchestration Automation & Response", "System Operations and Recovery", "Security Observation Analysis Report", "Standard Operating Automated Response"], "answer": 0},
            {"q": "Which is a popular SIEM tool?", "options": ["CrowdStrike", "Splunk", "ModSecurity", "Wireshark"], "answer": 1},
            {"q": "What is Splunk's query language called?", "options": ["SQL", "SPL (Search Processing Language)", "Python", "JSON"], "answer": 1},
            {"q": "What is Elasticsearch?", "options": ["A search engine and analytics engine", "A firewall", "An EDR tool", "A password manager"], "answer": 0},
            {"q": "What does an EDR agent do?", "options": ["Blocks all network traffic", "Monitors endpoint activity and detects threats", "Manages user accounts", "Routes network packets"], "answer": 1},
            {"q": "What is SOAR used for?", "options": ["Manual incident response", "Automating repetitive SOC workflows", "Replacing the SOC team", "Blocking IPs"], "answer": 1},
            {"q": "What is Kibana?", "options": ["A SIEM tool", "A visualization dashboard for Elasticsearch", "An EDR agent", "A firewall"], "answer": 1},
            {"q": "What is Logstash?", "options": ["A data processing pipeline for Elastic Stack", "A security tool", "A network scanner", "A password cracker"], "answer": 0}
        ]},
    {
        "id": 4, "title": "Cyber Defence Frameworks", "icon": "bi-grid-3x3-gap-fill", "color": "warning",
        "desc": "Learn how Pyramind of Pain, Cyber Kill Chain, Unified Kill Chain, and MITRE ATT&CK help you understand adversarial behavior.",
        "lessons": ["Pyramid of Pain", "Cyber Kill Chain", "Unified Kill Chain", "MITRE ATT&CK", "Summit", "Eviction"],
        "questions": [
            {"q": "What is the Pyramid of Pain?", "options": ["A hacking tool", "A model showing the difficulty of changing different IOCs", "A type of malware", "A firewall"], "answer": 1},
            {"q": "Which is hardest for an attacker to change?", "options": ["Hash values", "IP addresses", "TTPs", "Domain names"], "answer": 2},
            {"q": "How many phases are in the Cyber Kill Chain?", "options": ["5", "7", "10", "3"], "answer": 1},
            {"q": "What is the first phase of the Cyber Kill Chain?", "options": ["Delivery", "Weaponization", "Reconnaissance", "Exploitation"], "answer": 2},
            {"q": "What is MITRE ATT&CK?", "options": ["A vulnerability database", "A knowledge base of adversary tactics and techniques", "An antivirus", "A network protocol"], "answer": 1},
            {"q": "In MITRE, what is a Tactic?", "options": ["A specific tool", "The goal of a technique", "A vulnerability", "A detection rule"], "answer": 1},
            {"q": "In MITRE, what is a Technique?", "options": ["The goal", "The method used to achieve a tactic", "The victim", "The tool"], "answer": 1},
            {"q": "What is the Unified Kill Chain?", "options": ["A single-phase model", "A framework combining multiple kill chain models", "A type of attack", "A tool"], "answer": 1},
            {"q": "What does TTP stand for?", "options": ["Tactics, Techniques, and Procedures", "Threat Tracking Protocol", "Target Testing Process", "Technical Threat Profile"], "answer": 0},
            {"q": "What is the Diamond Model?", "options": ["A malware type", "An intrusion analysis model with adversary, capability, infrastructure, victim", "A network topology", "A encryption method"], "answer": 1}
        ]},
    {
        "id": 5, "title": "Phishing Analysis", "icon": "bi-envelope-exclamation-fill", "color": "danger",
        "desc": "Analyze and defend against phishing emails — investigate headers, links, attachments, and real-world phishing campaigns.",
        "lessons": ["Phishing Analysis", "Phishing Prevention", "Real-Phish Investigations"],
        "questions": [
            {"q": "Which email header verifies the sender domain?", "options": ["SSL", "SPF", "HTTP", "DNS"], "answer": 1},
            {"q": "What does DMARC do?", "options": ["Encrypts email content", "Publishes policy for SPF/DKIM failures", "Scans for viruses", "Stores emails"], "answer": 1},
            {"q": "What is a red flag in a phishing email?", "options": ["Personalized greeting", "Urgent call to action with a suspicious link", "Company logo", "Professional signature"], "answer": 1},
            {"q": "What tool extracts VBA macros from Office files?", "options": ["Wireshark", "olevba", "nmap", "tcpdump"], "answer": 1},
            {"q": "What is a phishing kit?", "options": ["An email client", "A pre-built fake login page that steals credentials", "A security training tool", "An antivirus"], "answer": 1},
            {"q": "What is DKIM?", "options": ["A cryptographic email signature", "A firewall rule", "A password policy", "A network protocol"], "answer": 0},
            {"q": "What does SPF 'fail' mean?", "options": ["Email is encrypted", "Sending server is unauthorized for that domain", "Email is too large", "Attachment is infected"], "answer": 1},
            {"q": "What is a homograph attack?", "options": ["Using lookalike characters in URLs", "A type of virus", "A network attack", "A password attack"], "answer": 0},
            {"q": "What should you do after confirming a phishing email?", "options": ["Click the link to verify", "Report it via the org's reporting mechanism", "Forward it to all colleagues", "Ignore it"], "answer": 1},
            {"q": "What is the best defense against phishing?", "options": ["Antivirus", "User awareness training and email filtering", "Firewall", "Complex passwords"], "answer": 1}
        ]},
    {
        "id": 6, "title": "Network Traffic Analysis", "icon": "bi-diagram-3-fill", "color": "primary",
        "desc": "Analyze network traffic with Wireshark and TShark to detect anomalies, C2 beaconing, and malicious patterns.",
        "lessons": ["Wireshark Basics & Deep Dives", "TShark Challenge I: Teamwork", "TShark Challenge II: Directory"],
        "questions": [
            {"q": "What is Wireshark used for?", "options": ["Blocking traffic", "Network packet capture and analysis", "Scanning ports", "Managing firewalls"], "answer": 1},
            {"q": "What is a packet capture?", "options": ["A screenshot", "A recorded file of network traffic", "A log file", "A configuration file"], "answer": 1},
            {"q": "What is TShark?", "options": ["A GUI for Wireshark", "The command-line version of Wireshark", "A firewall", "A protocol"], "answer": 1},
            {"q": "What filter shows HTTP traffic in Wireshark?", "options": ["tcp", "http", "dns", "ip"], "answer": 1},
            {"q": "What protocol is used for DNS queries?", "options": ["TCP", "UDP port 53", "HTTP", "FTP"], "answer": 1},
            {"q": "What does a beacon in network traffic look like?", "options": ["Random traffic spikes", "Regular periodic connections to an external IP", "Constant high bandwidth", "No traffic"], "answer": 1},
            {"q": "What is a TLS handshake?", "options": ["A greeting protocol", "The process of establishing an encrypted connection", "A routing protocol", "A DNS query"], "answer": 1},
            {"q": "What port does HTTPS use?", "options": ["80", "443", "22", "53"], "answer": 1},
            {"q": "What does TCP SYN scan detect?", "options": ["Open ports", "Malware", "DNS queries", "Email traffic"], "answer": 0},
            {"q": "What is netflow?", "options": ["A file format", "Network traffic metadata (IPs, ports, bytes)", "An antivirus", "A firewall rule"], "answer": 1}
        ]},
    {
        "id": 7, "title": "Network Security Monitoring", "icon": "bi-shield-fill", "color": "info",
        "desc": "Monitor network traffic with Snort and IDS/IPS tools to detect and alert on malicious activity.",
        "lessons": ["Snort Basics and Rules", "Network Monitoring Labs"],
        "questions": [
            {"q": "What is Snort?", "options": ["A web server", "An open-source network IDS/IPS", "A firewall", "A packet generator"], "answer": 1},
            {"q": "What is an IDS?", "options": ["Intrusion Detection System — monitors and alerts", "Internet Domain Service", "Integrated Data Storage", "Internal Directory Service"], "answer": 0},
            {"q": "What is an IPS?", "options": ["Intrusion Prevention System — blocks threats inline", "Internet Protocol System", "Internal Processing Service", "Integrated Platform"], "answer": 0},
            {"q": "What is a Snort rule?", "options": ["A firewall policy", "A signature pattern to detect malicious traffic", "A routing rule", "A password policy"], "answer": 1},
            {"q": "What does 'alert tcp any any -> any 80' do?", "options": ["Blocks all HTTP traffic", "Alerts on any TCP traffic to port 80", "Logs all UDP traffic", "Drops all packets"], "answer": 1},
            {"q": "What is Suricata?", "options": ["A web browser", "A high-performance IDS/IPS engine", "A database", "A file server"], "answer": 1},
            {"q": "What is Zeek?", "options": ["A web browser", "A network analysis framework", "A game", "A text editor"], "answer": 1},
            {"q": "What does alerting on port 22 detect?", "options": ["Web traffic", "SSH connections and potential brute force", "DNS queries", "Email traffic"], "answer": 1},
            {"q": "What is a false negative in IDS?", "options": ["An alert for benign traffic", "A missed attack that should have been detected", "A correctly identified attack", "An alert that fired"], "answer": 1},
            {"q": "What is the difference between IDS and IPS?", "options": ["No difference", "IDS monitors and alerts, IPS actively blocks", "IPS only logs", "IDS blocks traffic"], "answer": 1}
        ]},
    {
        "id": 8, "title": "Web Security Monitoring", "icon": "bi-globe2", "color": "warning",
        "desc": "Monitor web traffic and detect web shells, SQL injection, XSS, and other web-based attacks.",
        "lessons": ["Detecting Web Shells", "Web Attack Investigation Rooms"],
        "questions": [
            {"q": "What is a web shell?", "options": ["A type of antivirus", "A malicious script uploaded to run commands on a server", "A firewall rule", "A backup file"], "answer": 1},
            {"q": "Which request pattern indicates SQL injection?", "options": ["GET /index.html", "POST /login?id=1' OR '1'='1", "GET /images/logo.png", "POST /api/data"], "answer": 1},
            {"q": "What does '?page=../../etc/passwd' suggest?", "options": ["SQL Injection", "Path Traversal", "XSS", "CSRF"], "answer": 1},
            {"q": "What is reflected XSS?", "options": ["A permanent script stored on the server", "A script that appears in the URL/request", "A SQL query", "A network scan"], "answer": 1},
            {"q": "What is stored XSS?", "options": ["Script that runs once in URL", "Script permanently stored on server", "A phishing email", "A brute force"], "answer": 1},
            {"q": "What does a 403 status code indicate?", "options": ["OK", "Forbidden", "Not Found", "Server Error"], "answer": 1},
            {"q": "What does a 500 status code indicate?", "options": ["OK", "Forbidden", "Not Found", "Internal Server Error"], "answer": 3},
            {"q": "What is a WAF?", "options": ["Web Application Firewall", "Wide Area Network", "Windows Authentication Framework", "Web Access Filter"], "answer": 0},
            {"q": "What user agent is suspicious in web logs?", "options": ["Mozilla/5.0", "curl/7.68 or wget", "Chrome/91", "Safari/605"], "answer": 1},
            {"q": "What is a common web shell detection method?", "options": ["Port scanning", "Monitoring for unusual file access and cmd execution via web", "DNS analysis", "Email filtering"], "answer": 1}
        ]},
    {
        "id": 9, "title": "Windows Security Monitoring", "icon": "bi-windows", "color": "primary",
        "desc": "Monitor Windows endpoints — understand Windows logging, Event IDs, and threat detection on Windows systems.",
        "lessons": ["Windows Logging for SOC", "Windows Threat Detection 1", "Windows Threat Detection 2", "Windows Threat Detection 3"],
        "questions": [
            {"q": "What Event ID indicates a successful Windows logon?", "options": ["4624", "4625", "4720", "4688"], "answer": 0},
            {"q": "What Event ID indicates a failed Windows logon?", "options": ["4624", "4625", "4720", "4688"], "answer": 1},
            {"q": "What Event ID logs process creation?", "options": ["4624", "4625", "4688", "4720"], "answer": 2},
            {"q": "What is Sysmon?", "options": ["A system monitor tool", "A Windows system monitoring driver that logs detailed activity", "A firewall", "A antivirus"], "answer": 1},
            {"q": "What is Sysmon Event ID 1?", "options": ["Network connection", "Process creation", "File creation", "Driver load"], "answer": 1},
            {"q": "What is Sysmon Event ID 3?", "options": ["Process creation", "Network connection", "File creation", "Registry modification"], "answer": 1},
            {"q": "Why is execution from %TEMP% suspicious?", "options": ["%TEMP% is read-only", "Malware often runs from Temp to evade detection", "%TEMP% is encrypted", "%TEMP% is a system folder"], "answer": 1},
            {"q": "What is an unsigned process?", "options": ["A process with a valid signature", "A process without a digital signature", "A system process", "A Microsoft process"], "answer": 1},
            {"q": "What parent-child chain is suspicious?", "options": ["explorer.exe -> notepad.exe", "Microsoft Word -> cmd.exe -> powershell.exe", "svchost.exe -> services.exe", "System -> smss.exe"], "answer": 1},
            {"q": "What is Windows Event Log?", "options": ["A text file", "A centralized logging service in Windows", "A backup tool", "A registry key"], "answer": 1}
        ]},
    {
        "id": 10, "title": "Linux Security Monitoring", "icon": "bi-terminal-fill", "color": "success",
        "desc": "Monitor Linux endpoints — understand logging, auth logs, system calls, and threat detection on Linux systems.",
        "lessons": ["Linux Logging for SOC", "Linux Threat Detection 1", "Linux Threat Detection 2", "Linux Threat Detection 3"],
        "questions": [
            {"q": "Where are SSH login attempts logged on Linux?", "options": ["/var/log/httpd", "/var/log/auth.log or /var/log/secure", "/var/log/mail.log", "/var/log/boot.log"], "answer": 1},
            {"q": "What is the Linux system logger?", "options": ["Event Viewer", "syslog/rsyslog", "taskmgr", "regedit"], "answer": 1},
            {"q": "What does /var/log/messages contain?", "options": ["Email logs", "General system messages and errors", "Web server logs", "Database logs"], "answer": 1},
            {"q": "What is a Linux auditd?", "options": ["A web server", "The Linux audit daemon for system call monitoring", "A package manager", "A text editor"], "answer": 1},
            {"q": "What is /var/log/auth.log used for?", "options": ["Application logs", "Authentication and authorization events", "Kernel messages", "Web server logs"], "answer": 1},
            {"q": "What is auditd Event ID for user login?", "options": ["1", "100", "1100", "5000"], "answer": 2},
            {"q": "What is a suspicious cron job?", "options": ["A scheduled system task", "An unexpected scheduled task pointing to /tmp or unusual locations", "A logging tool", "A backup tool"], "answer": 1},
            {"q": "What is sudo log monitoring used for?", "options": ["Password recovery", "Detecting privilege escalation attempts", "Network monitoring", "Package updates"], "answer": 1},
            {"q": "Where are failed sudo attempts logged?", "options": ["/var/log/sudo.log or auth.log", "/var/log/httpd", "/var/log/dpkg.log", "/home/user/.bash_history"], "answer": 0},
            {"q": "What is a reverse shell?", "options": ["A remote connection from victim to attacker", "A standard SSH connection", "A web request", "A DNS query"], "answer": 0}
        ]},
    {
        "id": 11, "title": "Malware Concepts for SOC", "icon": "bi-bug-fill", "color": "danger",
        "desc": "Understand malware fundamentals — static and dynamic analysis, IOCs, and how to detect malicious software in a SOC.",
        "lessons": ["Malware Analysis Fundamentals", "Malware Detection in SOC Context"],
        "questions": [
            {"q": "What is static analysis?", "options": ["Running malware in a VM", "Analyzing malware without executing it", "Network traffic analysis", "Reverse engineering assembly"], "answer": 1},
            {"q": "What is dynamic analysis?", "options": ["Analyzing file metadata", "Executing malware in a sandbox and observing behavior", "Reading source code", "Checking file signatures"], "answer": 1},
            {"q": "What tool is used for hash lookups?", "options": ["Wireshark", "VirusTotal", "nmap", "tcpdump"], "answer": 1},
            {"q": "What is a YARA rule?", "options": ["A network protocol", "A pattern-matching rule for malware classification", "A firewall rule", "A password policy"], "answer": 1},
            {"q": "What is a PE file?", "options": ["Portable Executable — Windows binary format", "Protected Email", "Private Encryption", "Public Endpoint"], "answer": 0},
            {"q": "What is an IOC?", "options": ["Internet Operations Center", "Indicator of Compromise", "Internal Operations Control", "Incident Oversight"], "answer": 1},
            {"q": "What is a sandbox?", "options": ["A type of firewall", "An isolated environment for safe malware execution", "A backup tool", "A logging system"], "answer": 1},
            {"q": "What does 'strings' analysis show?", "options": ["Network packets", "Readable text embedded in a binary", "CPU instructions", "Memory addresses"], "answer": 1},
            {"q": "What is process injection?", "options": ["Running a new process", "Injecting code into a running process to evade detection", "Installing a new program", "Updating software"], "answer": 1},
            {"q": "What is a persistence mechanism?", "options": ["A backup tool", "A method malware uses to survive reboots", "An antivirus", "A firewall"], "answer": 1}
        ]},
    {
        "id": 12, "title": "Threat Analysis Tools", "icon": "bi-search-heart", "color": "warning",
        "desc": "Use cyber threat intelligence tools — VirusTotal, MISP, and OSINT sources to enrich investigations.",
        "lessons": ["Intro to Cyber Threat Intel", "File and Hash Threat Intel", "IP and Domain Threat Intel", "Invite Only"],
        "questions": [
            {"q": "What is CTI?", "options": ["Computer Technical Information", "Cyber Threat Intelligence", "Central Technical Interface", "Configuration Testing"], "answer": 1},
            {"q": "What is OSINT?", "options": ["Operating System Integration", "Open Source Intelligence", "Online Security Tool", "Offline Storage"], "answer": 1},
            {"q": "What is MISP?", "options": ["Malware Information Sharing Platform", "Microsoft Security Protocol", "Multi-Internet Service Provider", "Managed Incident Response"], "answer": 0},
            {"q": "What does VirusTotal do?", "options": ["Scans files with multiple antivirus engines", "Blocks malware", "Manages passwords", "Monitors networks"], "answer": 0},
            {"q": "What is a threat feed?", "options": ["A news website", "A stream of IOCs from a provider", "A type of malware", "A backup tool"], "answer": 1},
            {"q": "What color indicates malicious on VirusTotal?", "options": ["Green", "Red", "Yellow", "Blue"], "answer": 1},
            {"q": "What is an IP reputation check?", "options": ["Checking if an IP is known for malicious activity", "Routing traffic", "Assigning IPs", "Configuring DNS"], "answer": 0},
            {"q": "What is a domain reputation check?", "options": ["Web hosting", "Checking if a domain is associated with malware or phishing", "Domain registration", "DNS resolution"], "answer": 1},
            {"q": "What is passive DNS?", "options": ["A DNS server", "Historical DNS resolution data to find related domains", "A DNS protocol", "A firewall"], "answer": 1},
            {"q": "What is attribution in CTI?", "options": ["Assigning blame", "Identifying which threat actor is behind an attack", "Network mapping", "User identification"], "answer": 1}
        ]},
    {
        "id": 13, "title": "SIEM Triage for SOC", "icon": "bi-bell-fill", "color": "info",
        "desc": "Investigate SIEM alerts — perform log analysis, enrich with context, triage, and determine escalation paths.",
        "lessons": ["Log Analysis with SIEM", "Alert Triage with Splunk", "Alert Triage with Elastic", "ItsyBitsy", "Benign", "Monday Monitor", "Friday Overtime", "Retracted"],
        "questions": [
            {"q": "What is the first step when investigating a SIEM alert?", "options": ["Shut down the server", "Is this a true positive?", "Notify management", "Reboot the system"], "answer": 1},
            {"q": "What is alert enrichment?", "options": ["Deleting old alerts", "Adding context like geo-location and threat intel", "Creating new rules", "Ignoring the alert"], "answer": 1},
            {"q": "What is a SIEM timeline?", "options": ["A list of all emails", "Events from multiple sources ordered by time", "A backup schedule", "A shift calendar"], "answer": 1},
            {"q": "When should you escalate an alert?", "options": ["Always", "When confirmed as TP beyond L1 capability", "Never", "Only during business hours"], "answer": 1},
            {"q": "What is alert tuning?", "options": ["Making alerts louder", "Adjusting rules to reduce false positives", "Deleting all alerts", "Disabling the SIEM"], "answer": 1},
            {"q": "What is correlation in SIEM?", "options": ["Sorting logs by date", "Combining multiple events to detect attack patterns", "Deleting old data", "Creating backups"], "answer": 1},
            {"q": "What is an example of a correlation rule?", "options": ["Count failed logins > 10 in 5 minutes", "A firewall rule", "A password policy", "A network route"], "answer": 0},
            {"q": "What does a SIEM dashboard show?", "options": ["System settings", "Visual display of security metrics and alerts", "User passwords", "Network topology"], "answer": 1},
            {"q": "What is a false negative in SIEM?", "options": ["An alert that fires incorrectly", "An attack that was not detected by the SIEM", "A correct detection", "A benign event"], "answer": 1},
            {"q": "What is an example of SIEM data source?", "options": ["Windows Event Logs", "Only network traffic", "Only email", "Only DNS"], "answer": 0}
        ]},
    {
        "id": 14, "title": "SOC Level 1 Capstone Challenges", "icon": "bi-trophy-fill", "color": "danger",
        "desc": "Apply everything you've learned in multi-step incident investigations across pcaps, SIEM data, email artifacts, and more.",
        "lessons": ["Tempest", "Boogeyman 1", "Boogeyman 2", "Boogeyman 3", "Hidden Hooks", "Open Door", "Upload and Conquer", "BlackCat"],
        "questions": [
            {"q": "What is the first step in a capstone investigation?", "options": ["Patch all systems", "Identify the initial access vector from available evidence", "Reset all passwords", "Notify the media"], "answer": 1},
            {"q": "What sources should you correlate in an investigation?", "options": ["Only network logs", "PCAPs, SIEM logs, email artifacts, and endpoint data", "Only email", "Only DNS logs"], "answer": 1},
            {"q": "What is root cause analysis?", "options": ["Deleting logs", "Determining how the breach initially occurred", "Formatting the hard drive", "Installing patches"], "answer": 1},
            {"q": "What is the purpose of a timeline in investigation?", "options": ["Scheduling meetings", "Reconstructing the sequence of events in the attack", "Tracking work hours", "Logging backups"], "answer": 1},
            {"q": "What should you look for in a PCAP?", "options": ["Only HTTP traffic", "C2 beaconing, data exfiltration, and attacker commands", "Only DNS queries", "Only email headers"], "answer": 1},
            {"q": "What is a containment step for an active breach?", "options": ["Ignore", "Isolate affected systems from the network", "Format the drive", "Pay the ransom"], "answer": 1},
            {"q": "What should you document during an investigation?", "options": ["Nothing", "Timeline, IOCs, actions taken, and evidence found", "Only the attacker IP", "Only the date"], "answer": 1},
            {"q": "What is a post-incident review?", "options": ["A performance review", "A review of what went wrong and how to improve", "A software update", "A backup restore"], "answer": 1},
            {"q": "What is evidence preservation?", "options": ["Deleting old files", "Safely collecting and storing forensic data without modification", "Formatting drives", "Rebooting systems"], "answer": 1},
            {"q": "What is the final step of an investigation?", "options": ["Close the case", "Remediation, recovery, and lessons learned report", "Delete all evidence", "Ignore findings"], "answer": 1}
        ]},
]

@app.context_processor
def inject_globals():
    return dict(CURRICULUM=MODULES, now=datetime.now, PASS_SCORE=PASS_SCORE)

@app.route('/')
def index():
    return render_template('index.html', greeting='Good Day')

@app.route('/topic/<int:topic_id>')
def topic_page(topic_id):
    topic = next((t for t in MODULES if t['id'] == topic_id), None)
    if not topic:
        abort(404)
    prev_topic = next((t for t in MODULES if t['id'] == topic_id - 1), None)
    next_topic = next((t for t in MODULES if t['id'] == topic_id + 1), None)
    return render_template('topic.html', topic=topic, topic_idx=topic_id - 1, prev_topic=prev_topic, next_topic=next_topic)

@app.route('/check-quiz', methods=['POST'])
def check_quiz():
    data = request.get_json()
    topic = next((t for t in MODULES if t['id'] == data['topic_id']), None)
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
