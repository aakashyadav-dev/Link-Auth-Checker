
import json
import sqlite3
from datetime import datetime, timedelta
import threading
import queue
import uuid

class AlertSystem:
    def __init__(self, db_path='behavior_analytics.db'):
        self.db_path = db_path
        self.alert_queue = queue.Queue()
        self.active_alerts = {}
        self.alert_history = []
        self.is_running = False
        self.alert_thread = None
        self.init_database()
        self.add_sample_alerts()  # Add sample alerts for testing
        
    def init_database(self):
        """Initialize alert database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT UNIQUE,
                    title TEXT,
                    message TEXT,
                    severity TEXT,
                    source TEXT,
                    metadata TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP,
                    acknowledged_by TEXT,
                    acknowledged_at TIMESTAMP
                )
            ''')
            
            # Create index for faster queries
            c.execute('CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity)')
            
            conn.commit()
            conn.close()
            print("✅ Alert system database initialized")
        except Exception as e:
            print(f"❌ Alert DB init error: {e}")
    
    def add_sample_alerts(self):
        """Add sample alerts for demonstration"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Check if we already have alerts
            c.execute("SELECT COUNT(*) FROM alerts")
            count = c.fetchone()[0]
            
            if count > 0:
                print(f"✅ {count} alerts already exist in database")
                conn.close()
                # Load existing alerts into memory
                self.load_active_alerts()
                return
            
            # Sample alerts
            sample_alerts = [
                {
                    'id': str(uuid.uuid4())[:8],
                    'title': 'Suspicious URL Detected',
                    'message': 'A user attempted to access a known phishing site: http://paypal-verify.tk',
                    'severity': 'HIGH',
                    'source': 'url_scanner',
                    'metadata': {'url': 'http://paypal-verify.tk', 'risk_level': 'DANGEROUS'},
                    'status': 'active',
                    'created_at': datetime.now().isoformat()
                },
                {
                    'id': str(uuid.uuid4())[:8],
                    'title': 'Multiple Dangerous URLs',
                    'message': 'User accessed 3 dangerous URLs in the last 5 minutes',
                    'severity': 'MEDIUM',
                    'source': 'behavioral_analytics',
                    'metadata': {'count': 3, 'time_window': '5 minutes'},
                    'status': 'active',
                    'created_at': (datetime.now() - timedelta(minutes=10)).isoformat()
                },
                {
                    'id': str(uuid.uuid4())[:8],
                    'title': 'Unusual Behavior Detected',
                    'message': 'Behavioral biometrics detected unusual mouse movement patterns',
                    'severity': 'MEDIUM',
                    'source': 'biometrics',
                    'metadata': {'anomaly_score': 0.85, 'pattern': 'erratic_movement'},
                    'status': 'active',
                    'created_at': (datetime.now() - timedelta(minutes=25)).isoformat()
                },
                {
                    'id': str(uuid.uuid4())[:8],
                    'title': 'Cloud DB Match Found',
                    'message': 'URL matched entry in cloud phishing database',
                    'severity': 'HIGH',
                    'source': 'cloud_db',
                    'metadata': {'url': 'http://secure-banking-verify.xyz', 'confidence': 0.95},
                    'status': 'active',
                    'created_at': (datetime.now() - timedelta(hours=1)).isoformat()
                },
                {
                    'id': str(uuid.uuid4())[:8],
                    'title': 'SSL Certificate Expiring',
                    'message': 'SSL certificate for example.com expires in 3 days',
                    'severity': 'LOW',
                    'source': 'ssl_checker',
                    'metadata': {'domain': 'example.com', 'days_left': 3},
                    'status': 'resolved',
                    'created_at': (datetime.now() - timedelta(days=2)).isoformat(),
                    'resolved_at': (datetime.now() - timedelta(days=1)).isoformat()
                }
            ]
            
            now = datetime.now()
            for alert in sample_alerts:
                c.execute('''
                    INSERT INTO alerts 
                    (alert_id, title, message, severity, source, metadata, status, created_at, resolved_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    alert['id'],
                    alert['title'],
                    alert['message'],
                    alert['severity'],
                    alert['source'],
                    json.dumps(alert['metadata']),
                    alert['status'],
                    alert['created_at'],
                    alert.get('resolved_at')
                ))
                
                # Add to active alerts if status is active
                if alert['status'] == 'active':
                    self.active_alerts[alert['id']] = alert
            
            conn.commit()
            conn.close()
            print(f"✅ Added {len(sample_alerts)} sample alerts to database")
            
        except Exception as e:
            print(f"❌ Error adding sample alerts: {e}")
    
    def load_active_alerts(self):
        """Load active alerts from database into memory"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''
                SELECT alert_id, title, message, severity, source, metadata, created_at
                FROM alerts 
                WHERE status = 'active'
                ORDER BY created_at DESC
            ''')
            
            rows = c.fetchall()
            self.active_alerts = {}
            
            for row in rows:
                self.active_alerts[row[0]] = {
                    'id': row[0],
                    'title': row[1],
                    'message': row[2],
                    'severity': row[3],
                    'source': row[4],
                    'metadata': json.loads(row[5]) if row[5] else {},
                    'created_at': row[6],
                    'status': 'active'
                }
            
            conn.close()
            print(f"✅ Loaded {len(self.active_alerts)} active alerts from database")
            
        except Exception as e:
            print(f"❌ Error loading active alerts: {e}")
    
    def start_alert_system(self):
        """Start the alert processing system"""
        if not self.is_running:
            self.is_running = True
            self.alert_thread = threading.Thread(target=self._process_alerts)
            self.alert_thread.daemon = True
            self.alert_thread.start()
            print("✅ Alert system started")
    
    def stop_alert_system(self):
        """Stop the alert system"""
        self.is_running = False
        if self.alert_thread:
            self.alert_thread.join(timeout=5)
        print("🛑 Alert system stopped")
    
    def _process_alerts(self):
        """Main alert processing loop"""
        while self.is_running:
            try:
                # Process queued alerts
                while not self.alert_queue.empty():
                    alert = self.alert_queue.get_nowait()
                    self._store_alert(alert)
                
                # Check for alert conditions (every 10 seconds)
                self.check_alert_conditions()
                
                # Sleep to prevent CPU overload
                import time
                time.sleep(10)
                
            except Exception as e:
                print(f"Alert processing error: {e}")
                time.sleep(5)
    
    def create_alert(self, title, message, severity='MEDIUM', source='system', metadata=None):
        """Create a new alert"""
        alert_id = str(uuid.uuid4())[:8]
        
        alert = {
            'id': alert_id,
            'title': title,
            'message': message,
            'severity': severity,
            'source': source,
            'metadata': metadata or {},
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        # Add to queue for processing
        self.alert_queue.put(alert)
        
        # Add to active alerts immediately
        self.active_alerts[alert_id] = alert
        
        print(f"🚨 Alert created: {title} [{severity}]")
        
        return alert_id
    
    def _store_alert(self, alert):
        """Store alert in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''
                INSERT INTO alerts 
                (alert_id, title, message, severity, source, metadata, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert['id'],
                alert['title'],
                alert['message'],
                alert['severity'],
                alert['source'],
                json.dumps(alert['metadata']),
                alert['status'],
                alert['created_at']
            ))
            
            conn.commit()
            conn.close()
            print(f"✅ Alert {alert['id']} stored in database")
            
        except Exception as e:
            print(f"❌ Alert storage error: {e}")
    
    def check_alert_conditions(self):
        """Check for conditions that should trigger alerts"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Check for dangerous URLs in the last 5 minutes
            five_min_ago = datetime.now() - timedelta(minutes=5)
            c.execute('''
                SELECT COUNT(*) FROM url_checks 
                WHERE risk_level = 'DANGEROUS' AND timestamp > ?
            ''', (five_min_ago,))
            
            dangerous_count = c.fetchone()[0] or 0
            
            if dangerous_count >= 3:
                # Check if we already created this alert recently
                alert_exists = False
                for alert in self.active_alerts.values():
                    if (alert['title'] == 'Multiple Dangerous URLs Detected' and 
                        (datetime.now() - datetime.fromisoformat(alert['created_at'])).seconds < 300):
                        alert_exists = True
                        break
                
                if not alert_exists:
                    self.create_alert(
                        title='Multiple Dangerous URLs Detected',
                        message=f'{dangerous_count} dangerous URLs detected in the last 5 minutes',
                        severity='HIGH',
                        source='monitoring',
                        metadata={'count': dangerous_count, 'time_window': '5 minutes'}
                    )
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error checking alert conditions: {e}")
    
    def resolve_alert(self, alert_id, resolved_by='system'):
        """Mark an alert as resolved"""
        if alert_id in self.active_alerts:
            # Remove from active alerts
            alert = self.active_alerts.pop(alert_id)
            alert['status'] = 'resolved'
            alert['resolved_at'] = datetime.now().isoformat()
            alert['resolved_by'] = resolved_by
            
            # Add to history
            self.alert_history.append(alert)
            
            # Update in database
            try:
                conn = sqlite3.connect(self.db_path)
                c = conn.cursor()
                
                c.execute('''
                    UPDATE alerts 
                    SET status = 'resolved', resolved_at = ?
                    WHERE alert_id = ?
                ''', (datetime.now().isoformat(), alert_id))
                
                conn.commit()
                conn.close()
                print(f"✅ Alert {alert_id} resolved by {resolved_by}")
                
            except Exception as e:
                print(f"❌ Error updating alert in database: {e}")
    
    def acknowledge_alert(self, alert_id, user):
        """Acknowledge an alert"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id]['acknowledged_at'] = datetime.now().isoformat()
            self.active_alerts[alert_id]['acknowledged_by'] = user
            
            try:
                conn = sqlite3.connect(self.db_path)
                c = conn.cursor()
                
                c.execute('''
                    UPDATE alerts 
                    SET acknowledged_at = ?, acknowledged_by = ?
                    WHERE alert_id = ?
                ''', (datetime.now().isoformat(), user, alert_id))
                
                conn.commit()
                conn.close()
                print(f"✅ Alert {alert_id} acknowledged by {user}")
                
            except Exception as e:
                print(f"❌ Error acknowledging alert: {e}")
    
    def get_active_alerts(self):
        """Get all active alerts"""
        # Convert dictionary to list and sort by severity
        alerts = list(self.active_alerts.values())
        
        # Sort by severity (CRITICAL > HIGH > MEDIUM > LOW) and then by date
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        alerts.sort(key=lambda x: (severity_order.get(x['severity'], 4), x['created_at']), reverse=True)
        
        return alerts
    
    def get_alert_history(self, limit=50):
        """Get alert history"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''
                SELECT alert_id, title, message, severity, source, status, created_at, resolved_at
                FROM alerts 
                WHERE status = 'resolved'
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = c.fetchall()
            conn.close()
            
            alerts = []
            for row in rows:
                alerts.append({
                    'id': row[0],
                    'title': row[1],
                    'message': row[2],
                    'severity': row[3],
                    'source': row[4],
                    'status': row[5],
                    'created_at': row[6],
                    'resolved_at': row[7]
                })
            
            return alerts
            
        except Exception as e:
            print(f"❌ Error getting alert history: {e}")
            return []
    
    def cleanup_old_alerts(self):
        """Clean up old resolved alerts"""
        try:
            cutoff = datetime.now() - timedelta(days=7)
            
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''
                DELETE FROM alerts 
                WHERE status = 'resolved' 
                AND resolved_at < ?
            ''', (cutoff,))
            
            deleted = c.rowcount
            conn.commit()
            conn.close()
            
            if deleted > 0:
                print(f"🧹 Cleaned up {deleted} old resolved alerts")
                
        except Exception as e:
            print(f"❌ Error cleaning up old alerts: {e}")

# Singleton instance
alert_system = AlertSystem()
