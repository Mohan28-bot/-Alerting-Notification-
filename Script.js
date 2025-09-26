function fetchAlerts() {
    fetch('/api/alerts')
        .then(response => response.json())
        .then(alerts => {
            const container = document.getElementById('alerts-container');
            container.innerHTML = '';
            alerts.forEach(item => {
                const alert = item.alert;
                const pref = item.pref;
                const card = document.createElement('div');
                card.className = `alert-card ${alert.severity.toLowerCase()}`;
                card.innerHTML = `
                    <h3>${alert.title} (${alert.severity})</h3>
                    <p>${alert.message}</p>
                    <p>Expires: ${alert.expiry_time}</p>
                    <p>Status: ${pref.read ? 'Read' : 'Unread'} ${pref.snoozed_until ? `(Snoozed until ${new Date(pref.snoozed_until).toLocaleDateString()})` : ''}</p>
                    <button onclick="markRead(${alert.id}, ${pref.read})">${pref.read ? 'Mark Unread' : 'Mark Read'}</button>
                    <button onclick="snooze(${alert.id})">${pref.snoozed_until ? 'Unsnooze' : 'Snooze for Today'}</button>
                `;
                container.appendChild(card);
            });
        });
}

function markRead(alertId, isRead) {
    fetch('/api/mark_read', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 1, alert_id: alertId, read: !isRead })
    }).then(() => fetchAlerts());
}

function snooze(alertId) {
    fetch('/api/snooze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 1, alert_id: alertId })
    }).then(() => fetchAlerts());
}

function fetchAnalytics() {
    fetch('/api/analytics')
        .then(response => response.json())
        .then(analytics => {
            const ctx = document.getElementById('severityChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Info', 'Warning', 'Critical'],
                    datasets: [
                        {
                            label: 'Delivered',
                            data: [
                                analytics.severity_breakdown.delivered.Info,
                                analytics.severity_breakdown.delivered.Warning,
                                analytics.severity_breakdown.delivered.Critical
                            ],
                            backgroundColor: ['#36A2EB', '#FFCE56', '#FF6384']
                        },
                        {
                            label: 'Read',
                            data: [
                                analytics.severity_breakdown.read.Info,
                                analytics.severity_breakdown.read.Warning,
                                analytics.severity_breakdown.read.Critical
                            ],
                            backgroundColor: ['#36A2EB80', '#FFCE5680', '#FF638480']
                        }
                    ]
                },
                options: {
                    responsive: true,
                    scales: { y: { beginAtZero: true } }
                }
            });
        });
}

document.addEventListener('DOMContentLoaded', () => {
    fetchAlerts();
    fetchAnalytics();
});