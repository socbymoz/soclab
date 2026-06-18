MODULES = [
    {
        "id": 1, "title": "Networking Fundamentals", "icon": "bi-diagram-3-fill", "color": "primary",
        "desc": "Master the OSI and TCP/IP models, protocols, subnetting, and network traffic analysis — the foundation of all SOC operations.",
        "lessons": ["OSI & TCP/IP Models", "Network Protocols (HTTP, DNS, DHCP, ARP)", "Subnetting & CIDR", "Packet Analysis with Wireshark", "Network Traffic Baselining", "Firewall & NAC Fundamentals"],
        "questions": [
            {"q": "Which OSI layer does IP operate at?", "options": ["Layer 2", "Layer 3", "Layer 4", "Layer 7"], "answer": 1},
            {"q": "What port does DNS use?", "options": ["25", "53", "80", "443"], "answer": 1},
            {"q": "What is the purpose of ARP?", "options": ["Resolve IP to MAC", "Resolve MAC to IP", "Assign IP addresses", "Route packets"], "answer": 0},
            {"q": "What does a SYN flood target?", "options": ["Application layer", "TCP handshake process", "DNS resolution", "Routing table"], "answer": 1},
            {"q": "What protocol provides reliable data delivery?", "options": ["UDP", "TCP", "ICMP", "ARP"], "answer": 1},
            {"q": "What is a broadcast MAC address?", "options": ["00:00:00:00:00:00", "FF:FF:FF:FF:FF:FF", "01:01:01:01:01:01", "AA:AA:AA:AA:AA:AA"], "answer": 1},
            {"q": "What does TTL in IP header prevent?", "options": ["Fragmentation", "Routing loops", "Packet loss", "Congestion"], "answer": 1},
            {"q": "What is a default gateway?", "options": ["A DNS server", "The router that forwards traffic to other networks", "A DHCP server", "A firewall"], "answer": 1},
            {"q": "What layer do firewalls typically operate at?", "options": ["Layer 2 only", "Layers 3 and 4", "Layer 7 only", "All layers"], "answer": 1},
            {"q": "What is a VLAN used for?", "options": ["Encrypting traffic", "Segmenting a network logically", "Routing between subnets", "Assigning IPs"], "answer": 1}
        ]},
    {
        "id": 2, "title": "Linux Fundamentals", "icon": "bi-terminal-fill", "color": "success",
        "desc": "Build Linux proficiency for SOC operations — command line, file system, permissions, process management, and security tools.",
        "lessons": ["Linux CLI Basics", "File System Hierarchy", "User & Permission Management", "Process & Service Management", "Logging: syslog, auth.log, journald", "Linux Security Tools: auditd, chkrootkit"],
        "questions": [
            {"q": "What command changes file ownership?", "options": ["chmod", "chown", "chgrp", "usermod"], "answer": 1},
            {"q": "Where are system logs stored on most Linux distros?", "options": ["/etc/log", "/var/log", "/usr/log", "/opt/log"], "answer": 1},
            {"q": "What does 'chmod 755' grant?", "options": ["Owner rwx, group rx, others rx", "Owner rw, group r, others r", "Owner rwx, group rw, others r", "All rwx"], "answer": 0},
            {"q": "What command shows running processes?", "options": ["ls", "ps", "cat", "echo"], "answer": 1},
            {"q": "What is the root user UID?", "options": ["0", "1", "1000", "65534"], "answer": 0},
            {"q": "What does 'grep' do?", "options": ["Lists files", "Searches text using patterns", "Deletes files", "Compresses data"], "answer": 1},
            {"q": "What is a symlink?", "options": ["A hard link to inode", "A special file pointing to another file", "A directory entry", "A process"], "answer": 1},
            {"q": "What port does SSH use?", "options": ["21", "22", "23", "443"], "answer": 1},
            {"q": "What command views the last few lines of a file?", "options": ["head", "tail", "less", "more"], "answer": 1},
            {"q": "What file defines network interfaces on Linux?", "options": ["/etc/hosts", "/etc/network/interfaces", "/etc/resolv.conf", "/etc/hostname"], "answer": 1}
        ]},
    {
        "id": 3, "title": "Windows Fundamentals", "icon": "bi-windows", "color": "primary",
        "desc": "Understand Windows internals, Event Log, Sysmon, Active Directory, and security mechanisms essential for SOC analysts.",
        "lessons": ["Windows OS Architecture", "Event Viewer & Event IDs", "Sysmon Deep Dive", "Active Directory Basics", "Windows Security: Defender, AppLocker, BitLocker", "PowerShell Logging & Security"],
        "questions": [
            {"q": "What Event ID indicates a successful logon?", "options": ["4624", "4625", "4634", "4647"], "answer": 0},
            {"q": "What Event ID indicates a failed logon?", "options": ["4624", "4625", "4634", "4647"], "answer": 1},
            {"q": "What Sysmon Event ID tracks process creation?", "options": ["1", "3", "7", "11"], "answer": 0},
            {"q": "What is Sysmon Event ID 3 for?", "options": ["Process creation", "Network connection", "File creation", "Driver load"], "answer": 1},
            {"q": "What is Active Directory?", "options": ["A firewall", "A directory service for Windows domain networks", "A web server", "A database"], "answer": 1},
            {"q": "What registry hive stores user settings?", "options": ["HKEY_LOCAL_MACHINE", "HKEY_CURRENT_USER", "HKEY_CLASSES_ROOT", "HKEY_USERS"], "answer": 1},
            {"q": "What does Windows Event ID 4688 indicate?", "options": ["Logon", "Logoff", "Process creation", "Service install"], "answer": 2},
            {"q": "What tool monitors process creations and network connections?", "options": ["Task Manager", "Sysmon", "Defender", "BitLocker"], "answer": 1},
            {"q": "What is PowerShell script block logging?", "options": ["Logs all PowerShell commands", "Logs only errors", "Logs network traffic", "Logs file access"], "answer": 0},
            {"q": "What is AppLocker used for?", "options": ["Encrypting files", "Application whitelisting/blacklisting", "Network monitoring", "User authentication"], "answer": 1}
        ]},
    {
        "id": 4, "title": "Log Analysis", "icon": "bi-file-earmark-text-fill", "color": "warning",
        "desc": "Master log collection, parsing, correlation, and analysis across Windows, Linux, network, and application logs.",
        "lessons": ["Log Sources & Formats (syslog, JSON, EVTX)", "Windows Event Log Deep Analysis", "Linux Log Analysis", "Web Server Logs (Apache, Nginx, IIS)", "Firewall & Proxy Logs", "Log Correlation Techniques"],
        "questions": [
            {"q": "What format does Windows Event Log use?", "options": ["syslog", "EVTX", "CSV", "JSON"], "answer": 1},
            {"q": "What syslog facility is used for auth messages?", "options": ["kern", "auth", "daemon", "user"], "answer": 1},
            {"q": "What log entry indicates a 404 error?", "options": ["Access log with 404 status", "Error log with PHP warning", "Auth log with failed login", "Syslog with kernel panic"], "answer": 0},
            {"q": "What field in a firewall log indicates allowed traffic?", "options": ["DROP", "ACCEPT", "REJECT", "DENY"], "answer": 1},
            {"q": "What is log rotation?", "options": ["Deleting old logs", "Archiving and compressing old logs to manage disk space", "Encrypting logs", "Indexing logs"], "answer": 1},
            {"q": "What does a proxy log reveal?", "options": ["Email content", "Web requests made by users", "Database queries", "File contents"], "answer": 1},
            {"q": "What is a log aggregator?", "options": ["A tool that deletes logs", "A centralized system collecting logs from multiple sources", "A firewall", "An antivirus"], "answer": 1},
            {"q": "What timestamp format is ISO 8601?", "options": ["2024-01-01T12:00:00Z", "01/01/2024 12:00:00", "Jan 1 12:00:00", "20240101120000"], "answer": 0},
            {"q": "What does a 5xx HTTP status code indicate?", "options": ["Client error", "Server error", "Success", "Redirection"], "answer": 1},
            {"q": "What is a SIEM lookup table used for?", "options": ["Storing raw logs", "Enriching alerts with context data", "Deleting old data", "Creating reports"], "answer": 1}
        ]},
    {
        "id": 5, "title": "SIEM Fundamentals", "icon": "bi-bell-fill", "color": "info",
        "desc": "Learn SIEM architecture, log ingestion, search queries, alert creation, and dashboard building with Splunk and Elastic.",
        "lessons": ["SIEM Architecture & Components", "Log Ingestion & Parsing", "Splunk SPL Queries", "Elastic Stack (ELK) Queries", "Alert & Correlation Rules", "Dashboard & Report Building"],
        "questions": [
            {"q": "What does SIEM stand for?", "options": ["Security Information & Event Management", "System Integration & Enterprise Management", "Security Intelligence & Event Monitoring", "Standard Incident Escalation Model"], "answer": 0},
            {"q": "What is a SIEM forwarder?", "options": ["A central server", "A lightweight agent that collects and sends logs", "A firewall", "A database"], "answer": 1},
            {"q": "What Splunk command searches across time?", "options": ["search", "timechart", "stats", "eval"], "answer": 0},
            {"q": "What Elastic component stores and indexes data?", "options": ["Logstash", "Elasticsearch", "Kibana", "Beats"], "answer": 1},
            {"q": "What is a correlation rule?", "options": ["A firewall rule", "A SIEM rule that matches patterns across multiple log sources", "A routing rule", "A password policy"], "answer": 1},
            {"q": "What does Kibana provide?", "options": ["Data indexing", "Visualization and dashboards", "Log collection", "Alert execution"], "answer": 1},
            {"q": "What is a SIEM use case?", "options": ["A software license", "A documented detection scenario mapped to logs and rules", "A hardware requirement", "A network topology"], "answer": 1},
            {"q": "What is Logstash used for?", "options": ["Visualization", "Log parsing and transformation", "Alerting", "Indexing"], "answer": 1},
            {"q": "What is a SIEM parser?", "options": ["A network tool", "A component that normalizes raw logs into a common format", "A dashboard", "An alert"], "answer": 1},
            {"q": "What is a false positive in SIEM?", "options": ["A correctly identified attack", "An alert that fires for benign activity", "A missed attack", "A system error"], "answer": 1}
        ]},
    {
        "id": 6, "title": "SOC Workflow", "icon": "bi-people-fill", "color": "success",
        "desc": "Master SOC tier operations, alert triage, escalation procedures, shift handovers, and SOC metrics.", "lessons": ["SOC Tiers (L1, L2, L3)", "Alert Triage Process", "Escalation Procedures", "Shift Handover & Documentation", "SOC Metrics (MTTR, MTTA)", "Communication & Reporting"],
        "questions": [
            {"q": "What does SOC L1 do?", "options": ["Reverse engineer malware", "Monitor and triage initial alerts", "Build detection rules", "Manage team"], "answer": 1},
            {"q": "What is alert triage?", "options": ["Deleting alerts", "Prioritizing and classifying incoming alerts", "Creating alerts", "Ignoring alerts"], "answer": 1},
            {"q": "What is MTTR?", "options": ["Mean Time to Recover", "Malware Threat Triage Report", "Managed Threat Response", "Maximum Triage Time"], "answer": 0},
            {"q": "When should an alert be escalated to L2?", "options": ["Always", "When confirmed as a true positive requiring deeper analysis", "Never", "Only during business hours"], "answer": 1},
            {"q": "What is a SOC playbook?", "options": ["A textbook", "A documented step-by-step response procedure", "A firewall config", "A password manager"], "answer": 1},
            {"q": "What is a false positive?", "options": ["A real attack", "An alert that incorrectly fires for benign activity", "A critical alert", "A system error"], "answer": 1},
            {"q": "What is a SOC ticket?", "options": ["A support request", "A tracked record of an incident investigation", "A network ticket", "A license key"], "answer": 1},
            {"q": "What is shift handover?", "options": ["Changing passwords", "Transferring active investigations to the next shift", "System reboot", "Network maintenance"], "answer": 1},
            {"q": "What is a true positive?", "options": ["An alert that fires incorrectly", "An alert that correctly identifies malicious activity", "A test alert", "Normal behavior"], "answer": 1},
            {"q": "What is a SOC KPI?", "options": ["A software tool", "A measurable value showing SOC effectiveness", "A vulnerability", "A network device"], "answer": 1}
        ]},
    {
        "id": 7, "title": "Threat Detection", "icon": "bi-shield-exclamation", "color": "danger",
        "desc": "Build detection logic using Sigma rules, YARA, IoCs, and behavioral analytics to identify threats across the enterprise.",
        "lessons": ["Detection Methodology", "Sigma Rules (Universal Detection)", "YARA Rules (Malware Identification)", "IoC & TTP-Based Detection", "Behavioral vs Signature Detection", "Detection Engineering Pipeline"],
        "questions": [
            {"q": "What is a Sigma rule?", "options": ["A firewall rule", "A generic signature format for SIEM detections", "A YARA rule", "A Snort rule"], "answer": 1},
            {"q": "What is YARA used for?", "options": ["Network monitoring", "Malware pattern matching and classification", "Log analysis", "User management"], "answer": 1},
            {"q": "What is an Indicator of Compromise (IoC)?", "options": ["A security tool", "Artifacts observed indicating a breach", "A vulnerability", "A patch"], "answer": 1},
            {"q": "What is behavioral detection?", "options": ["Matching known signatures", "Detecting anomalies based on deviation from normal behavior", "Blocking IPs", "Scanning ports"], "answer": 1},
            {"q": "What is a detection rule false positive?", "options": ["A missed attack", "Benign activity that triggers the rule", "A correct detection", "A system error"], "answer": 1},
            {"q": "What is TTPS in detection?", "options": ["Tools, Techniques, and Procedures", "Tactics, Techniques, and Procedures", "Threat Testing Protocol", "Technical Threat Profile"], "answer": 1},
            {"q": "What is a detection gap?", "options": ["A missing patch", "An attack vector not covered by current detection rules", "A network outage", "A log source failure"], "answer": 1},
            {"q": "What is alert enrichment?", "options": ["Deleting alerts", "Adding contextual data to alerts for better triage", "Creating new rules", "Disabling rules"], "answer": 1},
            {"q": "What is a honeypot?", "options": ["A security patch", "A decoy system to attract attackers", "A firewall rule", "A logging tool"], "answer": 1},
            {"q": "What is detection as code?", "options": ["Writing detection rules in Python", "Managing detection content with version control and CI/CD", "A programming language", "A compiler"], "answer": 1}
        ]},
    {
        "id": 8, "title": "MITRE ATT&CK Framework", "icon": "bi-grid-3x3-gap-fill", "color": "warning",
        "desc": "Map adversary behavior using MITRE ATT&CK — understand tactics, techniques, and how to use the framework for detection and gap analysis.",
        "lessons": ["MITRE ATT&CK Overview & Matrix", "Enterprise Tactics (TA0001–TA0043)", "Common Techniques per Tactic", "Using ATT&CK for Detection Gap Analysis", "ATT&CK Navigator & Heatmaps", "Atomic Red Team Testing"],
        "questions": [
            {"q": "What is MITRE ATT&CK?", "options": ["A vulnerability database", "A knowledge base of adversary tactics and techniques", "An antivirus", "A network protocol"], "answer": 1},
            {"q": "What is a Tactic in MITRE ATT&CK?", "options": ["A specific tool", "The goal or reason for a technique", "A vulnerability", "A detection rule"], "answer": 1},
            {"q": "What is a Technique in MITRE?", "options": ["The goal", "The method used to achieve a tactic", "The victim", "The tool"], "answer": 1},
            {"q": "What is the TA0001 Tactic?", "options": ["Execution", "Persistence", "Initial Access", "Defense Evasion"], "answer": 2},
            {"q": "What is T1566?", "options": ["Phishing", "Brute Force", "Valid Accounts", "Spearphishing Attachment"], "answer": 0},
            {"q": "What is ATT&CK Navigator?", "options": ["A car navigation system", "A web tool for visualizing ATT&CK coverage", "A detection tool", "A firewall"], "answer": 1},
            {"q": "What is Atomic Red Team?", "options": ["A red team tool", "A library of MITRE-mapped tests to validate detections", "A vulnerability scanner", "A SIEM"], "answer": 1},
            {"q": "What is T1059?", "options": ["Command and Scripting Interpreter", "SQL Injection", "Bootkit", "XSS"], "answer": 0},
            {"q": "What is the Pyramid of Pain?", "options": ["A hacking tool", "A model showing difficulty of changing IOCs", "A malware", "A firewall"], "answer": 1},
            {"q": "What is a detection gap in MITRE context?", "options": ["Missing firewall rules", "Unmonitored techniques with no detection coverage", "Network bandwidth", "Staff shortage"], "answer": 1}
        ]},
    {
        "id": 9, "title": "Incident Response", "icon": "bi-shield-fill-check", "color": "danger",
        "desc": "Master the incident response lifecycle — preparation, detection, containment, eradication, recovery, and lessons learned.",
        "lessons": ["IR Lifecycle (NIST 800-61)", "Preparation & Playbooks", "Detection & Analysis", "Containment & Eradication", "Recovery & Post-Incident Activity", "Forensic Acquisition & Chain of Custody"],
        "questions": [
            {"q": "What is the first phase of NIST IR lifecycle?", "options": ["Detection", "Preparation", "Containment", "Recovery"], "answer": 1},
            {"q": "What is containment?", "options": ["Deleting logs", "Isolating affected systems to prevent spread", "Rebooting servers", "Patching vulnerabilities"], "answer": 1},
            {"q": "What is eradication?", "options": ["Strengthening defenses", "Removing the threat from affected systems", "Rebuilding systems", "Monitoring"], "answer": 1},
            {"q": "What is a post-mortem?", "options": ["A medical procedure", "A review of what happened, why, and how to improve", "A system reboot", "A backup"], "answer": 1},
            {"q": "What is chain of custody?", "options": ["A physical chain", "Documentation of evidence handling from collection to court", "A security tool", "A forensic image"], "answer": 1},
            {"q": "What is a playbook?", "options": ["A textbook", "A step-by-step IR procedure document", "A network diagram", "A software tool"], "answer": 1},
            {"q": "What is a runbook?", "options": ["A fictional book", "An automated or semi-automated response procedure", "A log file", "A policy document"], "answer": 1},
            {"q": "What is the difference between IR and SOC?", "options": ["No difference", "SOC is continuous monitoring; IR is activated for specific incidents", "SOC handles physical security", "IR is daily operations"], "answer": 1},
            {"q": "What is a tabletop exercise?", "options": ["A board game", "A simulated IR scenario to test processes", "A software test", "A network scan"], "answer": 1},
            {"q": "What is a lessons learned report?", "options": ["A financial report", "A document capturing improvements after an incident", "A system log", "A vulnerability scan"], "answer": 1}
        ]},
    {
        "id": 10, "title": "Threat Hunting", "icon": "bi-search-heart", "color": "info",
        "desc": "Proactively search for threats using hypothesis-driven hunting, IoCs, TTPs, and data analytics across the enterprise.",
        "lessons": ["Hunting Methodology (Hypothesis-Driven)", "Data Sources for Hunting", "IoC & TTP-Based Hunting", "Threat Intelligence Integration", "Hunting with Jupyter Notebooks", "Automating Hunts"],
        "questions": [
            {"q": "What is threat hunting?", "options": ["Reacting to alerts", "Proactively searching for undetected threats", "Blocking IPs", "Patching systems"], "answer": 1},
            {"q": "What is a hunting hypothesis?", "options": ["A confirmed attack", "An educated guess about potential adversary behavior", "A firewall rule", "A detection rule"], "answer": 1},
            {"q": "What data is most useful for hunting?", "options": ["Only network logs", "Endpoint logs, network logs, and threat intelligence", "Only email", "Only DNS"], "answer": 1},
            {"q": "What is a TTP-based hunt?", "options": ["Hunting by IP address", "Hunting based on adversary behavior patterns", "Hash-based hunting", "Domain-based hunting"], "answer": 1},
            {"q": "What is the Hunting Loop?", "options": ["A network topology", "The iterative process of hypothesis → investigation → analytics → resolution", "A detection tool", "A programming concept"], "answer": 1},
            {"q": "What is threat intelligence?", "options": ["Company gossip", "Actionable information about threats to inform defense", "Social media", "News articles"], "answer": 1},
            {"q": "What is a threat intelligence feed?", "options": ["A news website", "A stream of IOCs and threat data", "A type of malware", "A backup tool"], "answer": 1},
            {"q": "What is a hunting MTTD?", "options": ["Mean Time to Detect", "Mean Time to Respond", "Mean Time to Triage", "Malware Threat Tracking"], "answer": 0},
            {"q": "What is a diamond model in hunting?", "options": ["A malware type", "An intrusion analysis model with adversary, capability, infrastructure, victim", "A network topology", "An encryption method"], "answer": 1},
            {"q": "What is a hunting maturity model?", "options": ["A software version", "A framework measuring an organization's hunting capabilities", "A hardware spec", "A network standard"], "answer": 1}
        ]},
    {
        "id": 11, "title": "Digital Forensics", "icon": "bi-fingerprint", "color": "warning",
        "desc": "Learn forensic acquisition, analysis, memory forensics, disk forensics, and forensic reporting for investigations.",
        "lessons": ["Forensic Principles (Order of Volatility)", "Disk Forensics (FTK Imager, Autopsy)", "Memory Forensics (Volatility)", "Network Forensics", "Registry & Artifact Analysis", "Forensic Reporting"],
        "questions": [
            {"q": "What is the order of volatility?", "options": ["Collect data from most volatile to least volatile", "Collect data from least volatile first", "Delete volatile data", "Ignore volatile data"], "answer": 0},
            {"q": "What tool is used for memory forensics?", "options": ["FTK Imager", "Volatility", "Wireshark", "Autopsy"], "answer": 1},
            {"q": "What is a forensic image?", "options": ["A screenshot", "A bit-for-bit copy of a storage device", "A photograph", "A backup"], "answer": 1},
            {"q": "What is RAM analysis used for?", "options": ["Finding files", "Detecting running processes, network connections, and injected code", "Analyzing hard drives", "Recovering emails"], "answer": 1},
            {"q": "What is Autopsy?", "options": ["A medical tool", "A digital forensics platform for disk analysis", "A network tool", "A memory tool"], "answer": 1},
            {"q": "What is string analysis in forensics?", "options": ["Analyzing binary file contents", "Extracting readable text from a binary file", "Network packet analysis", "Registry analysis"], "answer": 1},
            {"q": "What is registry analysis?", "options": ["Analyzing Linux logs", "Examining Windows Registry for startup programs, user activity, and configuration", "Network traffic analysis", "Memory analysis"], "answer": 1},
            {"q": "What is the first rule of digital forensics?", "options": ["Delete evidence", "Preserve the original evidence without modification", "Share evidence publicly", "Reboot the system"], "answer": 1},
            {"q": "What is write blocker?", "options": ["A software that deletes data", "A hardware/software tool preventing modification of evidence drives", "A firewall", "An antivirus"], "answer": 1},
            {"q": "What is forensic soundness?", "options": ["The volume of evidence", "The admissibility and reliability of evidence in legal proceedings", "The speed of analysis", "The cost of tools"], "answer": 1}
        ]},
    {
        "id": 12, "title": "SOC Projects", "icon": "bi-tools", "color": "primary",
        "desc": "Build real SOC infrastructure from scratch — deploy SIEM, configure logging, build dashboards, and automate response.",
        "lessons": ["Building a SOC Lab (ELK/Wazuh)", "SIEM Deployment & Configuration", "Custom Dashboard Building", "Automation with Shuffle/Playbooks", "Detection Rule Development", "Purple Team Exercises"],
        "questions": [
            {"q": "What is the first step in building a SOC lab?", "options": ["Buy expensive hardware", "Define objectives and scope", "Install all tools", "Hire staff"], "answer": 1},
            {"q": "What is Wazuh?", "options": ["A firewall", "An open-source SIEM/XDR platform", "A web server", "A database"], "answer": 1},
            {"q": "What is Shuffle?", "options": ["A game", "An open-source SOAR platform", "A firewall", "A SIEM"], "answer": 1},
            {"q": "What is a purple team exercise?", "options": ["Red team only", "Collaborative testing where red and blue teams work together", "Blue team only", "A vulnerability scan"], "answer": 1},
            {"q": "What is a SOC maturity assessment?", "options": ["A software test", "An evaluation of SOC capabilities and processes", "A network scan", "A hardware audit"], "answer": 1},
            {"q": "What is a detection rule pipeline?", "options": ["A plumbing system", "The workflow from detection idea to deployed rule", "A network topology", "A hiring process"], "answer": 1},
            {"q": "What is a SOC automation workflow?", "options": ["Manual processes", "Automated response actions triggered by alerts", "Paperwork", "Network maintenance"], "answer": 1},
            {"q": "What is a SOC dashboard?", "options": ["A physical display", "A visual interface showing key security metrics", "A command line", "A configuration file"], "answer": 1},
            {"q": "What is the Lockheed Martin Cyber Kill Chain?", "options": ["A physical chain", "A 7-step model for understanding cyber attacks", "A detection tool", "A firewall"], "answer": 1},
            {"q": "What is a SOC health check?", "options": ["A medical exam", "A review of SOC tools, processes, and team performance", "A security scan", "A backup test"], "answer": 1}
        ]},
    {
        "id": 13, "title": "Career Preparation", "icon": "bi-rocket-takeoff-fill", "color": "success",
        "desc": "Prepare for SOC analyst roles — certifications, resume building, interview preparation, and continuous learning roadmaps.",
        "lessons": ["SOC Career Paths (L1 to CISO)", "Certifications: CompTIA Sec+, CySA+, CISSP", "Resume & Portfolio Building", "Technical Interview Prep", "Blue Team Skill Roadmap", "Networking & Professional Growth"],
        "questions": [
            {"q": "What is the typical first SOC certification?", "options": ["CISSP", "CompTIA Security+", "OSCP", "CEH"], "answer": 1},
            {"q": "What is a SOC L1 analyst expected to know?", "options": ["Reverse engineering", "Alert triage and basic analysis", "Penetration testing", "Incident response management"], "answer": 1},
            {"q": "What is the best way to gain SOC experience?", "options": ["Read books only", "Build a home lab and practice with real tools", "Watch videos only", "Take a single course"], "answer": 1},
            {"q": "What is a SOC analyst's primary tool?", "options": ["Metasploit", "SIEM platform", "Burp Suite", "Nmap"], "answer": 1},
            {"q": "What is a blue team certification?", "options": ["OSCP", "CompTIA CySA+", "CEH", "OSWP"], "answer": 1},
            {"q": "What is a portfolio project?", "options": ["A school assignment", "A practical security project demonstrating skills to employers", "A financial report", "A certificate"], "answer": 1},
            {"q": "What is most important in a SOC interview?", "options": ["Knowing every tool", "Demonstrating analytical thinking and methodology", "Having all certifications", "Being fast"], "answer": 1},
            {"q": "What is a home lab?", "options": ["A home network", "A personal security lab for practicing skills", "A gaming PC", "A media server"], "answer": 1},
            {"q": "What is continuous learning in cybersecurity?", "options": ["One-time training", "Ongoing skill development through labs, courses, and certifications", "Reading the news", "Attending one conference"], "answer": 1},
            {"q": "What is a SOC team lead responsible for?", "options": ["Only monitoring", "Team management, escalations, and process improvement", "Only reporting", "Only training"], "answer": 1}
        ]},
]


def get_module(module_id):
    return next((m for m in MODULES if m['id'] == module_id), None)


def get_prev_module(module_id):
    return next((m for m in MODULES if m['id'] == module_id - 1), None)


def get_next_module(module_id):
    return next((m for m in MODULES if m['id'] == module_id + 1), None)
