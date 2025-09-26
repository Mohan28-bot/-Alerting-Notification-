from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
from enum import Enum

class Severity(Enum):
    INFO = "Info"
    WARNING = "Warning"
    CRITICAL = "Critical"

class DeliveryType(Enum):
    IN_APP = "In-App"

class VisibilityType(Enum):
    ORG = "Organization"
    TEAM = "Team"
    USER = "User"

class Team:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

class User:
    def __init__(self, id: int, name: str, team: Team = None):
        self.id = id
        self.name = name
        self.team = team

class Alert:
    def __init__(self, id: int, title: str, message: str, severity: Severity, delivery_type: DeliveryType,
                 start_time: datetime, expiry_time: datetime, reminder_frequency: int = 7200):
        self.id = id
        self.title = title
        self.message = message
        self.severity = severity
        self.delivery_type = delivery_type
        self.start_time = start_time
        self.expiry_time = expiry_time
        self.reminder_frequency = reminder_frequency
        self.active = True
        self.visibility = [(VisibilityType.ORG, None)]

class UserAlertPreference:
    def __init__(self, user_id: int, alert_id: int):
        self.user_id = user_id
        self.alert_id = alert_id
        self.read = False
        self.snoozed_until = None

class NotificationDelivery:
    def __init__(self, alert_id: int, user_id: int, delivery_time: datetime, channel: DeliveryType):
        self.alert_id = alert_id
        self.user_id = user_id
        self.delivery_time = delivery_time
        self.channel = channel

class AlertSystem:
    def __init__(self):
        self.alerts = {}
        self.users = {1: User(1, "Bob"), 2: User(2, "Alice")}
        self.preferences = {}
        self.deliveries = []
        self.next_alert_id = 1
        self.current_time = datetime(2025, 9, 26, 10, 0, 0)

    def create_alert(self, title, message, severity, delivery_type, start_time, expiry_time):
        alert_id = self.next_alert_id
        self.next_alert_id += 1
        alert = Alert(alert_id, title, message, severity, delivery_type, start_time, expiry_time)
        self.alerts[alert_id] = alert
        return alert

    def fetch_alerts(self, user_id, current_time):
        if user_id not in self.users:
            return []
        return [{"alert": a, "pref": self._get_or_create_preference(user_id, a.id)} for a in self.alerts.values()
                if self.current_time >= a.start_time and self.current_time < a.expiry_time]

    def _get_or_create_preference(self, user_id, alert_id):
        key = (user_id, alert_id)
        if key not in self.preferences:
            self.preferences[key] = UserAlertPreference(user_id, alert_id)
        return self.preferences[key]

    def mark_read(self, user_id, alert_id, read):
        pref = self._get_or_create_preference(user_id, alert_id)
        pref.read = read

    def snooze_alert(self, user_id, alert_id, current_time):
        pref = self._get_or_create_preference(user_id, alert_id)
        pref.snoozed_until = current_time.date() + timedelta(days=1)

    def get_analytics(self):
        return {
            "severity_breakdown": {
                "delivered": {"Info": 3, "Warning": 6, "Critical": 8},
                "read": {"Info": 0, "Warning": 0, "Critical": 1}
            }
        }

app = Flask(__name__)
system = AlertSystem()

now = system.current_time
expiry = now + timedelta(days=2)
system.create_alert("System Outage", "Servers down!", Severity.CRITICAL, DeliveryType.IN_APP, now, expiry)
system.create_alert("Personal Reminder", "Check your email.", Severity.WARNING, DeliveryType.IN_APP, now, expiry)
system.create_alert("Budget Update", "Review Q4 budget.", Severity.WARNING, DeliveryType.IN_APP, now, expiry)

@app.route('/')
def index():
    return render_template('index.html', user_name="Bob", current_time=system.current_time.isoformat())

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    user_id = 1
    alerts = system.fetch_alerts(user_id, system.current_time)
    return jsonify(alerts)

@app.route('/api/mark_read', methods=['POST'])
def mark_read():
    data = request.json
    system.mark_read(data['user_id'], data['alert_id'], data['read'])
    return jsonify({"status": "success"})

@app.route('/api/snooze', methods=['POST'])
def snooze():
    data = request.json
    system.snooze_alert(data['user_id'], data['alert_id'], system.current_time)
    return jsonify({"status": "success"})

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    return jsonify(system.get_analytics())

if __name__ == '__main__':
    app.run(debug=True)