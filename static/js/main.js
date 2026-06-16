let correctCount = 0;
let attemptedCount = 0;

document.addEventListener('DOMContentLoaded', function () {
    initLogBackground();
    initCharts();
    updateFlaggedList();
});

function initLogBackground() {
    const bg = document.getElementById('logBackground');
    if (!bg) return;
    const sampleLogs = [
        "192.168.1.50 - - [15/Jun/2026:08:15:22] \"POST /wp-login.php\" 200 345",
        "45.33.32.156 - - [15/Jun/2026:08:10:03] \"GET /index.php?id=1' OR '1'='1\" 200 8901",
        "EventID:4625 | User: unknown | Failed Logon | Source: 192.168.1.50",
        "EventID:4720 | User: Administrator | User Created: backup_admin",
        "SRC:10.10.10.50:49152 -> DST:34.253.159.159:4444 | TCP ALLOW",
        "sshd[2837]: Failed password for root from 45.33.32.156 port 54321",
        "sshd[2837]: Failed password for stansimon from 45.33.32.156 port 54322",
        "EventID:4688 | Process: powershell.exe | Cmd: Invoke-Expression(...)",
        "EventID:1102 | Audit Log Cleared by backup_admin",
        "powershell.exe (PID:2345) connected to 34.253.159.159:4444",
        "cmd.exe -> net localgroup Administrators hacker /add",
        "SRC:10.10.10.50 -> DST:185.220.101.1:9050 | Tor Connection",
        "File Created: C:\\Users\\Public\\exfil_data.zip",
        "EventID:4657 | Registry: HKLM\\...\\Run\\MaliciousBackdoor",
        "GET /shell.php?cmd=cat%20/etc/shadow 200 2345",
        "POST /upload.php 200 234 - File upload detected",
        "WARNING: 92.168.1.50 - Directory brute force detected",
        "CRITICAL: Data exfiltration to 34.253.159.159:80",
        "sshd[2840]: Accepted password for stansimon from 45.33.32.156",
        "EventID:4732 | backup_admin added to Administrators group",
    ];

    for (let i = 0; i < 30; i++) {
        const line = document.createElement('div');
        line.className = 'log-line';
        line.textContent = sampleLogs[i % sampleLogs.length];
        line.style.left = (Math.random() * 40) + '%';
        line.style.animationDelay = (i * 2.5) + 's';
        line.style.animationDuration = (60 + Math.random() * 40) + 's';
        line.style.opacity = 0.15 + Math.random() * 0.2;
        bg.appendChild(line);
    }
}

function initCharts() {
    const severityChart = document.getElementById('severityChart');
    if (severityChart) {
        fetch('/api/stats')
            .then(r => r.json())
            .then(data => {
                new Chart(severityChart, {
                    type: 'doughnut',
                    data: {
                        labels: ['Info', 'Warning', 'High', 'Critical'],
                        datasets: [{
                            data: [data.by_severity.info, data.by_severity.warning, data.by_severity.high, data.by_severity.critical],
                            backgroundColor: ['#198754', '#ffc107', '#dc3545', '#212529'],
                            borderColor: ['#1a1d23', '#1a1d23', '#1a1d23', '#1a1d23']
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: { legend: { position: 'bottom', labels: { color: '#e0e0e0' } } }
                    }
                });
            });
    }

    document.querySelectorAll('canvas[id^="severityChart_"]').forEach(function (canvas) {
        const logType = canvas.id.replace('severityChart_', '');
        fetch('/api/logs/' + logType)
            .then(r => r.json())
            .then(data => {
                const sev = { info: 0, warning: 0, high: 0, critical: 0 };
                data.forEach(e => { if (sev[e.severity] !== undefined) sev[e.severity]++; });
                new Chart(canvas, {
                    type: 'bar',
                    data: {
                        labels: ['Info', 'Warning', 'High', 'Critical'],
                        datasets: [{
                            label: 'Events',
                            data: [sev.info, sev.warning, sev.high, sev.critical],
                            backgroundColor: ['#198754', '#ffc107', '#dc3545', '#212529']
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: { legend: { display: false } },
                        scales: {
                            y: { beginAtZero: true, ticks: { color: '#e0e0e0', stepSize: 1 } },
                            x: { ticks: { color: '#e0e0e0' } }
                        }
                    }
                });
            });
    });

    const quizChart = document.getElementById('quizProgressChart');
    if (quizChart) {
        new Chart(quizChart, {
            type: 'doughnut',
            data: {
                labels: ['Not Attempted', 'Attempted'],
                datasets: [{
                    data: [10, 0],
                    backgroundColor: ['#3a4049', '#0d6efd'],
                    borderColor: ['#1a1d23', '#1a1d23']
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { position: 'bottom', labels: { color: '#e0e0e0' } } }
            }
        });
    }
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if (sidebar.classList.contains('closed')) {
        sidebar.classList.remove('closed');
        sidebar.classList.add('open');
        overlay.classList.add('show');
    } else {
        sidebar.classList.remove('open');
        sidebar.classList.add('closed');
        overlay.classList.remove('show');
    }
}

function searchLogs() {
    const input = document.getElementById('searchInput').value.toLowerCase();
    document.querySelectorAll('.log-row').forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(input) ? '' : 'none';
    });
}

function applyFilters() {
    const severity = document.getElementById('severityFilter').value;
    const suspiciousOnly = document.getElementById('suspiciousToggle').checked;
    document.querySelectorAll('.log-row').forEach(row => {
        const sevBadge = row.querySelector('.badge');
        const isSuspicious = row.classList.contains('table-danger');
        let show = true;
        if (severity && sevBadge) show = sevBadge.textContent.trim() === severity;
        if (suspiciousOnly && !isSuspicious) show = false;
        row.style.display = show ? '' : 'none';
    });
}

function filterSeverity(sev) {
    const sel = document.getElementById('severityFilter');
    if (sel) { sel.value = sev; applyFilters(); }
}

function filterSuspicious() {
    const tog = document.getElementById('suspiciousToggle');
    if (tog) { tog.checked = !tog.checked; applyFilters(); }
}

function flagEvent(btn, event, time, severity) {
    btn.classList.toggle('btn-danger');
    btn.classList.toggle('btn-outline-danger');
    const flagged = JSON.parse(sessionStorage.getItem('flagged') || '[]');
    const entry = { event: event.substring(0, 80), time: time, severity: severity };
    const idx = flagged.findIndex(f => f.event === entry.event && f.time === time);
    if (idx === -1) flagged.push(entry);
    else flagged.splice(idx, 1);
    sessionStorage.setItem('flagged', JSON.stringify(flagged));
    updateFlaggedList();
}

function updateFlaggedList() {
    const list = document.getElementById('flaggedList');
    if (!list) return;
    const flagged = JSON.parse(sessionStorage.getItem('flagged') || '[]');
    if (flagged.length === 0) {
        list.innerHTML = '<em class="text-muted">No events flagged yet. Click the flag icon on suspicious rows.</em>';
    } else {
        let html = '<div class="list-group list-group-flush">';
        flagged.forEach(f => {
            html += '<div class="list-group-item bg-dark text-light py-1 px-2"><small>';
            html += '<span class="badge bg-danger me-1">' + f.severity + '</span> ';
            html += f.time + ' - ' + f.event.substring(0, 50);
            html += '</small></div>';
        });
        html += '</div><div class="mt-2"><small class="text-muted">Total: ' + flagged.length + ' flagged events</small></div>';
        list.innerHTML = html;
    }
}

function clearFlags() {
    sessionStorage.setItem('flagged', '[]');
    updateFlaggedList();
    document.querySelectorAll('.flag-btn').forEach(b => {
        b.classList.remove('btn-danger');
        b.classList.add('btn-outline-danger');
    });
}

function checkAnswer(btn) {
    const card = btn.closest('.quiz-card');
    const qIdx = parseInt(card.dataset.question);
    const selected = card.querySelector('input[type="radio"]:checked');
    const feedback = card.querySelector('.result-feedback');

    if (!selected) {
        feedback.style.display = 'block';
        feedback.className = 'result-feedback wrong mt-2';
        feedback.textContent = 'Please select an answer first.';
        return;
    }

    const answer = parseInt(selected.value);
    const qData = window.currentQuizData ? window.currentQuizData[qIdx] : null;

    if (!qData) {
        feedback.style.display = 'block';
        feedback.className = 'result-feedback wrong mt-2';
        feedback.textContent = 'Error: Quiz data not loaded.';
        return;
    }

    const isCorrect = answer === qData.answer;

    const options = card.querySelectorAll('.quiz-option');
    options.forEach((o, i) => {
        o.disabled = true;
        if (i === qData.answer) {
            o.nextElementSibling.innerHTML = qData.options[i] + ' (Correct)';
            o.nextElementSibling.style.color = '#75b798';
        } else if (i === answer && !isCorrect) {
            o.nextElementSibling.innerHTML = qData.options[i] + ' (Your answer)';
            o.nextElementSibling.style.color = '#ea868f';
        }
    });

    feedback.style.display = 'block';
    if (isCorrect) {
        feedback.className = 'result-feedback correct mt-2';
        feedback.innerHTML = '<strong>Correct!</strong> ' + qData.explanation;
    } else {
        feedback.className = 'result-feedback wrong mt-2';
        feedback.innerHTML = '<strong>Incorrect.</strong> ' + qData.explanation;
    }

    attemptedCount++;
    if (isCorrect) correctCount++;
    document.getElementById('scoreDisplay').textContent = 'Score: ' + correctCount + '/' + attemptedCount;

    updateAchievements();
    updateQuizChart();
}

function updateAchievements() {
    const set = function (id, done) {
        document.getElementById(id).className = 'badge bg-' + (done ? 'success' : 'secondary') + ' me-2';
        document.getElementById(id).textContent = done ? '✓' : '?';
    };
    if (attemptedCount >= 1) set('ach-first', true);
    if (correctCount >= 5) set('ach-half', true);
    if (attemptedCount >= 10) set('ach-all', true);
    if (correctCount >= 10 && attemptedCount >= 10) {
        document.getElementById('ach-perfect').className = 'badge bg-warning text-dark me-2';
        document.getElementById('ach-perfect').textContent = 'Trophy';
    }
}

function updateQuizChart() {
    const chart = document.getElementById('quizProgressChart');
    if (!chart) return;
    const chartInstance = Chart.getChart(chart);
    if (chartInstance) {
        chartInstance.data.datasets[0].data = [Math.max(10 - attemptedCount, 0), Math.min(attemptedCount, 10)];
        chartInstance.update();
    }
}
