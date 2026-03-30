import threading
import queue
import time
from datetime import datetime
import json
import sqlite3
import hashlib
import uuid

class BackgroundSecurityScanner:
    def __init__(self, db_path='behavior_analytics.db'):
        self.db_path = db_path
        self.scan_queue = queue.Queue()
        self.active_scans = {}
        self.is_running = False
        self.scan_thread = None
        
    def start_background_scanner(self):
        """Start the background scanner thread"""
        if not self.is_running:
            self.is_running = True
            self.scan_thread = threading.Thread(target=self._scanner_loop)
            self.scan_thread.daemon = True
            self.scan_thread.start()
            print("✅ Background scanner started")
            return True
        return False
    
    def stop_background_scanner(self):
        """Stop the background scanner"""
        self.is_running = False
        if self.scan_thread:
            self.scan_thread.join(timeout=5)
        print("🛑 Background scanner stopped")
    
    def _scanner_loop(self):
        """Main scanner loop"""
        while self.is_running:
            try:
                if not self.scan_queue.empty():
                    scan_task = self.scan_queue.get()
                    self._process_scan(scan_task)
                time.sleep(1)
            except Exception as e:
                print(f"Scanner loop error: {e}")
    
    def _process_scan(self, scan_task):
        """Process a single scan task"""
        scan_task['status'] = 'scanning'
        scan_task['started_at'] = datetime.now().isoformat()
        self.active_scans[scan_task['id']] = scan_task
        
        # Simulate scanning
        time.sleep(2)
        
        scan_task['status'] = 'completed'
        scan_task['completed_at'] = datetime.now().isoformat()
        scan_task['results'] = {
            'risk_level': 'SAFE',
            'score': 10,
            'checks': {
                'ssl': {'status': 'VALID'},
                'reputation': {'score': 0}
            }
        }
        
        self._save_to_database(scan_task)
        
        if scan_task['id'] in self.active_scans:
            del self.active_scans[scan_task['id']]
    
    def queue_scan(self, url, session_id=None, priority=1):
        """Queue a URL for background scanning"""
        scan_id = str(uuid.uuid4())[:8]
        
        scan_task = {
            'id': scan_id,
            'url': url,
            'session_id': session_id,
            'priority': priority,
            'queued_at': datetime.now().isoformat(),
            'status': 'queued'
        }
        
        self.scan_queue.put(scan_task)
        self._save_to_database(scan_task)
        
        return scan_id
    
    def _save_to_database(self, scan_task):
        """Save scan task to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''
                CREATE TABLE IF NOT EXISTS background_scans (
                    scan_id TEXT PRIMARY KEY,
                    url TEXT,
                    session_id TEXT,
                    priority INTEGER,
                    status TEXT,
                    queued_at TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    results TEXT
                )
            ''')
            
            c.execute('''
                INSERT OR REPLACE INTO background_scans 
                (scan_id, url, session_id, priority, status, queued_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                scan_task['id'], 
                scan_task['url'], 
                scan_task.get('session_id'),
                scan_task['priority'], 
                scan_task['status'], 
                scan_task['queued_at']
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Database save error: {e}")
    
    def get_scan_status(self, scan_id):
        """Get status of a scan"""
        if scan_id in self.active_scans:
            return self.active_scans[scan_id]
        
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('SELECT * FROM background_scans WHERE scan_id = ?', (scan_id,))
            row = c.fetchone()
            conn.close()
            
            if row:
                columns = ['scan_id', 'url', 'session_id', 'priority', 'status', 
                          'queued_at', 'started_at', 'completed_at', 'results']
                result = {}
                for i, col in enumerate(columns):
                    if i < len(row):
                        result[col] = row[i]
                return result
        except Exception as e:
            print(f"Error getting scan status: {e}")
        
        return None

# Create singleton instance
background_scanner = BackgroundSecurityScanner()