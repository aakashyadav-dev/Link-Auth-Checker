# Update app.py with fixes
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import uuid
import requests
from urllib.parse import urlparse
import threading
import asyncio
import os

# Import utils
from utils.ssl_checker import ssl_checker
from utils.whois_checker import get_domain_age
from utils.url_analyzer import analyze_url_security, check_phishing_indicators, calculate_risk_level
from utils.threat_intel import threat_intel

# Import modules
from modules.background_scanner import background_scanner
from modules.biometrics import biometrics
from modules.alert_system import alert_system
from modules.cloud_phishing_db import cloud_phishing_db

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
CORS(app)

# Helper function to convert numpy types to Python native types
def convert_numpy(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    else:
        return obj

# Initialize all systems
def init_systems():
    """Initialize all security systems"""
    print("🚀 Initializing all security systems...")
    
    try:
        background_scanner.start_background_scanner()
        print("✅ Background scanner started")
    except Exception as e:
        print(f"❌ Failed to start background scanner: {e}")
    
    try:
        alert_system.start_alert_system()
        print("✅ Alert system started")
    except Exception as e:
        print(f"❌ Failed to start alert system: {e}")
    
    try:
        threading.Thread(target=biometrics.train_model).start()
        print("✅ Biometrics system initialized")
    except Exception as e:
        print(f"❌ Failed to initialize biometrics: {e}")
    
    print("✅ All systems initialized")

# Database initialization
def init_db():
    """Initialize all database tables"""
    try:
        conn = sqlite3.connect('behavior_analytics.db', check_same_thread=False)
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_agent TEXT,
                ip_address TEXT,
                risk_profile TEXT
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS url_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                url TEXT,
                risk_level TEXT,
                user_decision TEXT,
                response_time_ms INTEGER,
                hesitation_time_ms INTEGER,
                scroll_pattern TEXT,
                mouse_movements TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES user_sessions (session_id)
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS behavioral_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                phishing_susceptibility_score REAL,
                security_compliance_score REAL,
                risk_perception_score REAL,
                total_checks INTEGER,
                safe_clicks INTEGER,
                warning_clicks INTEGER,
                dangerous_clicks INTEGER,
                avg_response_time REAL,
                hesitation_pattern TEXT,
                mouse_pattern_score REAL,
                keystroke_pattern_score REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES user_sessions (session_id)
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS threat_cache (
                url_hash TEXT PRIMARY KEY,
                url TEXT,
                threat_data TEXT,
                risk_score REAL,
                checked_at TIMESTAMP,
                expires_at TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")

init_db()
init_systems()

def ensure_session_exists(session_id, user_agent=None, ip_address=None):
    """Ensure session exists in database"""
    try:
        conn = sqlite3.connect('behavior_analytics.db', check_same_thread=False)
        c = conn.cursor()
        
        c.execute('SELECT session_id FROM user_sessions WHERE session_id = ?', (session_id,))
        if not c.fetchone():
            c.execute('''
                INSERT INTO user_sessions (session_id, user_agent, ip_address)
                VALUES (?, ?, ?)
            ''', (session_id, user_agent, ip_address))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Session creation error: {e}")
        return False

def store_url_check(session_id, url, risk_level, analysis_details=None):
    """Store URL check in database"""
    try:
        ensure_session_exists(session_id)
        
        conn = sqlite3.connect('behavior_analytics.db', check_same_thread=False)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO url_checks (session_id, url, risk_level) 
            VALUES (?, ?, ?)
        ''', (session_id, url, risk_level))
        
        conn.commit()
        conn.close()
        
        try:
            cloud_result = cloud_phishing_db.check_url(url)
            if cloud_result.get('found', False):
                alert_system.create_alert(
                    title=f"URL found in phishing database: {url[:50]}",
                    message=f"URL matched known phishing patterns",
                    severity="HIGH" if cloud_result.get('confidence', 0) > 0.8 else "MEDIUM",
                    source="cloud_db",
                    metadata=cloud_result
                )
        except Exception as e:
            print(f"Cloud DB check error: {e}")
        
        try:
            background_scanner.queue_scan(url, session_id)
        except Exception as e:
            print(f"Background scan queue error: {e}")
        
        print(f"✅ Stored URL check: {url} -> {risk_level}")
        return True
    except Exception as e:
        print(f"❌ Store URL check error: {e}")
        return False

def store_user_decision(session_id, url, risk_level, decision, response_time, 
                        hesitation_time=None, scroll_pattern=None, mouse_movements=None):
    """Store user decision in database - FIXED SQL SYNTAX"""
    try:
        conn = sqlite3.connect('behavior_analytics.db', check_same_thread=False)
        c = conn.cursor()
        
        # First, find the most recent check for this URL and session
        c.execute('''
            SELECT id FROM url_checks 
            WHERE session_id = ? AND url = ? 
            ORDER BY timestamp DESC LIMIT 1
        ''', (session_id, url))
        
        result = c.fetchone()
        if not result:
            print(f"❌ No matching URL check found for decision")
            conn.close()
            return False
        
        check_id = result[0]
        
        # Update that specific record
        c.execute('''
            UPDATE url_checks 
            SET user_decision = ?, response_time_ms = ?, hesitation_time_ms = ?,
                scroll_pattern = ?, mouse_movements = ?
            WHERE id = ?
        ''', (
            decision, 
            response_time, 
            hesitation_time,
            json.dumps(scroll_pattern) if scroll_pattern else None,
            json.dumps(mouse_movements) if mouse_movements else None,
            check_id
        ))
        
        affected = c.rowcount
        conn.commit()
        conn.close()
        
        if affected > 0:
            print(f"✅ Stored user decision: {decision} for {url}")
            
            if mouse_movements:
                try:
                    biometrics.track_mouse_movement(session_id, mouse_movements)
                except Exception as e:
                    print(f"Mouse tracking error: {e}")
            
            try:
                biometrics.track_decision_pattern(session_id, {
                    'decision': decision,
                    'response_time': response_time,
                    'risk_level': risk_level,
                    'hesitation_time': hesitation_time,
                    'scroll_pattern': scroll_pattern
                })
            except Exception as e:
                print(f"Decision pattern tracking error: {e}")
            
            return True
        else:
            print(f"❌ No matching URL check found for decision")
            return False
            
    except Exception as e:
        print(f"❌ Store decision error: {e}")
        return False

def calculate_behavioral_metrics(session_id):
    """Calculate comprehensive behavioral metrics - FIXED JSON SERIALIZATION"""
    try:
        print(f"📊 Calculating metrics for session: {session_id}")
        
        conn = sqlite3.connect('behavior_analytics.db', check_same_thread=False)
        
        all_checks = pd.read_sql_query('''
            SELECT risk_level, user_decision, response_time_ms, hesitation_time_ms
            FROM url_checks 
            WHERE session_id = ?
            ORDER BY timestamp DESC
        ''', conn, params=(session_id,))
        
        conn.close()
        
        print(f"📈 Found {len(all_checks)} total checks")
        
        if len(all_checks) == 0:
            return {
                'phishing_susceptibility_score': 0,
                'security_compliance_score': 0,
                'risk_perception_score': 0,
                'total_scans': 0,
                'safe_scans': 0,
                'warning_scans': 0,
                'dangerous_scans': 0,
                'total_decisions': 0,
                'safe_decisions': 0,
                'warning_decisions': 0,
                'dangerous_decisions': 0,
                'behavioral_insights': ['No URLs scanned yet. Start scanning URLs to see your analytics.'],
                'timestamp': datetime.now().isoformat()
            }
        
        # Convert numpy types to Python native types
        total_checks = int(len(all_checks))
        safe_scans = int(len(all_checks[all_checks['risk_level'] == 'SAFE'])) if 'risk_level' in all_checks.columns else 0
        warning_scans = int(len(all_checks[all_checks['risk_level'] == 'WARNING'])) if 'risk_level' in all_checks.columns else 0
        dangerous_scans = int(len(all_checks[all_checks['risk_level'] == 'DANGEROUS'])) if 'risk_level' in all_checks.columns else 0
        
        checks_with_decisions = all_checks[all_checks['user_decision'].notna()] if 'user_decision' in all_checks.columns else pd.DataFrame()
        
        if len(checks_with_decisions) > 0:
            total_decisions = int(len(checks_with_decisions))
            
            safe_decisions = int(len(checks_with_decisions[
                (checks_with_decisions['risk_level'] == 'SAFE')
            ])) if 'risk_level' in checks_with_decisions.columns else 0
            
            warning_decisions = int(len(checks_with_decisions[
                (checks_with_decisions['risk_level'] == 'WARNING')
            ])) if 'risk_level' in checks_with_decisions.columns else 0
            
            dangerous_decisions = int(len(checks_with_decisions[
                (checks_with_decisions['risk_level'] == 'DANGEROUS')
            ])) if 'risk_level' in checks_with_decisions.columns else 0
            
            risky_proceeds = int(len(checks_with_decisions[
                (checks_with_decisions['user_decision'] == 'proceed') &
                (checks_with_decisions['risk_level'].isin(['WARNING', 'DANGEROUS']))
            ])) if 'user_decision' in checks_with_decisions.columns and 'risk_level' in checks_with_decisions.columns else 0
            
            phishing_susceptibility = float((risky_proceeds / total_decisions * 100)) if total_decisions > 0 else 0
            
            safe_avoids = int(len(checks_with_decisions[
                (checks_with_decisions['user_decision'] == 'avoid') &
                (checks_with_decisions['risk_level'].isin(['WARNING', 'DANGEROUS']))
            ])) if 'user_decision' in checks_with_decisions.columns and 'risk_level' in checks_with_decisions.columns else 0
            
            security_compliance = float((safe_avoids / total_decisions * 100)) if total_decisions > 0 else 0
            
            risky_hesitations = checks_with_decisions[
                checks_with_decisions['risk_level'].isin(['WARNING', 'DANGEROUS'])
            ]['hesitation_time_ms'].dropna() if 'hesitation_time_ms' in checks_with_decisions.columns else pd.Series()
            
            avg_risky_hesitation = float(risky_hesitations.mean()) if len(risky_hesitations) > 0 else 0
            risk_perception = float(max(0, 100 - (avg_risky_hesitation / 5000)))
            
            insights = generate_insights(total_checks, safe_scans, warning_scans, dangerous_scans,
                                       phishing_susceptibility, security_compliance, risk_perception)
            
        else:
            phishing_susceptibility = 0.0
            security_compliance = 0.0
            risk_perception = 0.0
            safe_decisions = warning_decisions = dangerous_decisions = 0
            total_decisions = 0
            
            insights = [
                f"You've scanned {total_checks} URLs",
                f"Safe: {safe_scans}, Warning: {warning_scans}, Dangerous: {dangerous_scans}",
                "Make decisions on scanned URLs to get behavioral insights"
            ]
        
        result = {
            'phishing_susceptibility_score': round(phishing_susceptibility, 1),
            'security_compliance_score': round(security_compliance, 1),
            'risk_perception_score': round(risk_perception, 1),
            'total_scans': total_checks,
            'safe_scans': safe_scans,
            'warning_scans': warning_scans,
            'dangerous_scans': dangerous_scans,
            'total_decisions': total_decisions,
            'safe_decisions': safe_decisions,
            'warning_decisions': warning_decisions,
            'dangerous_decisions': dangerous_decisions,
            'behavioral_insights': insights,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"📊 Analytics result calculated")
        return result
        
    except Exception as e:
        print(f"❌ Analytics calculation error: {e}")
        return {
            'phishing_susceptibility_score': 0,
            'security_compliance_score': 0,
            'risk_perception_score': 0,
            'total_scans': 0,
            'safe_scans': 0,
            'warning_scans': 0,
            'dangerous_scans': 0,
            'total_decisions': 0,
            'safe_decisions': 0,
            'warning_decisions': 0,
            'dangerous_decisions': 0,
            'behavioral_insights': ['Error calculating analytics'],
            'timestamp': datetime.now().isoformat()
        }

def generate_insights(total_checks, safe_scans, warning_scans, dangerous_scans,
                     phishing_susceptibility, security_compliance, risk_perception):
    """Generate behavioral insights"""
    insights = []
    
    if total_checks >= 20:
        insights.append(f"🌟 Power user: {total_checks} URLs analyzed")
    elif total_checks >= 10:
        insights.append(f"📊 Active scanner: {total_checks} URLs analyzed")
    elif total_checks >= 5:
        insights.append(f"📈 Getting started: {total_checks} URLs scanned")
    else:
        insights.append(f"🆕 Beginner: {total_checks} URLs scanned so far")
    
    if dangerous_scans > 0:
        insights.append(f"⚠️ Encountered {dangerous_scans} dangerous URLs - stay vigilant!")
    if warning_scans > 0:
        insights.append(f"⚡ Found {warning_scans} suspicious URLs needing caution")
    if safe_scans > 0:
        insights.append(f"✅ Identified {safe_scans} safe URLs")
    
    if phishing_susceptibility > 60:
        insights.append("🔴 High risk tolerance: Often proceeds with risky URLs")
    elif phishing_susceptibility < 20:
        insights.append("🟢 Security cautious: Rarely proceeds with risky URLs")
    else:
        insights.append("🟡 Moderate risk awareness")
    
    if security_compliance > 70:
        insights.append("🛡️ Excellent security compliance - you're well protected!")
    elif security_compliance < 40:
        insights.append("📚 Consider improving security compliance")
    
    if risk_perception > 70:
        insights.append("⚡ Quick risk assessment - good instincts!")
    elif risk_perception < 40:
        insights.append("🧠 Take a moment to assess risks before deciding")
    
    return insights

@app.route('/check', methods=['POST'])
def check_url():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
            
        url = data.get('url')
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        session_id = request.headers.get('X-Session-ID') or str(uuid.uuid4())
        user_agent = request.headers.get('User-Agent')
        ip_address = request.remote_addr
        
        ensure_session_exists(session_id, user_agent, ip_address)
        
        print(f"🔍 Checking URL: {url} for session: {session_id}")
        
        risk_level, phishing_score, analysis_details = calculate_risk_level(url)
        
        try:
            cloud_check = cloud_phishing_db.check_url(url)
            if cloud_check.get('found', False):
                phishing_score = max(phishing_score, 80)
                risk_level = 'DANGEROUS' if cloud_check.get('confidence', 0) > 0.8 else 'WARNING'
                analysis_details['cloud_db_match'] = cloud_check
        except Exception as e:
            print(f"Cloud DB check error: {e}")
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            threat_check = loop.run_until_complete(threat_intel.comprehensive_check(url))
            loop.close()
            
            if threat_check.get('overall_risk', {}).get('score', 0) > 50:
                risk_level = 'DANGEROUS'
                analysis_details['threat_intel'] = threat_check
        except Exception as e:
            print(f"Threat intel error: {e}")
        
        store_url_check(session_id, url, risk_level, analysis_details)
        
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '') if parsed.netloc else 'Unknown'
        
        result = {
            'domain': domain,
            'input_url': url,
            'final_url': url,
            'ssl': analysis_details.get('ssl_status', 'Unknown'),
            'domain_age': analysis_details.get('domain_age', 'Unknown'),
            'redirects': [],
            'phishing_score': phishing_score,
            'risk': risk_level,
            'security_analysis': {
                'suspicious_patterns': analysis_details.get('suspicious_score', 0),
                'pattern_warnings': analysis_details.get('warnings', []),
                'phishing_indicators': analysis_details.get('indicators', []),
                'calculated_score': analysis_details.get('total_score', 0),
                'cloud_db_match': cloud_check.get('found', False) if 'cloud_check' in locals() else False,
                'threat_intel': threat_check.get('overall_risk', {}) if 'threat_check' in locals() else {}
            },
            'behavioral_context': {
                'session_id': session_id,
                'recommended_action': get_recommended_action(risk_level)
            }
        }
        
        print(f"✅ Analysis complete: {risk_level} (Phishing: {phishing_score}%)")
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Check URL error: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/user_decision', methods=['POST'])
def track_user_decision():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data'}), 400
            
        session_id = data.get('session_id')
        url = data.get('url')
        risk_level = data.get('risk_level')
        user_decision = data.get('decision')
        response_time = data.get('response_time')
        hesitation_time = data.get('hesitation_time')
        scroll_pattern = data.get('scroll_pattern')
        mouse_movements = data.get('mouse_movements')
        
        if not all([session_id, url, risk_level, user_decision]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        print(f"📝 Tracking decision: {user_decision} for {url}")
        
        success = store_user_decision(
            session_id, url, risk_level, user_decision, response_time,
            hesitation_time, scroll_pattern, mouse_movements
        )
        
        if data.get('keystrokes'):
            try:
                biometrics.track_keystrokes(session_id, data['keystrokes'])
            except Exception as e:
                print(f"Keystroke tracking error: {e}")
        
        if user_decision == 'proceed' and risk_level == 'DANGEROUS':
            try:
                alert_system.create_alert(
                    title="User Proceeded to Dangerous URL",
                    message=f"User decided to proceed to a dangerous URL: {url[:100]}",
                    severity="HIGH",
                    source="user_decision",
                    metadata={
                        'session_id': session_id,
                        'url': url,
                        'response_time': response_time,
                        'hesitation_time': hesitation_time
                    }
                )
            except Exception as e:
                print(f"Alert creation error: {e}")
        
        if success:
            return jsonify({'status': 'success', 'message': 'Decision recorded successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to record decision'}), 500
            
    except Exception as e:
        print(f"❌ Track decision error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/behavioral_analytics/<session_id>')
def get_behavioral_analytics(session_id):
    """Get comprehensive behavioral analytics"""
    try:
        analytics = calculate_behavioral_metrics(session_id)
        # Convert any remaining numpy types
        analytics = json.loads(json.dumps(analytics, default=convert_numpy))
        return jsonify(analytics)
        
    except Exception as e:
        print(f"❌ Analytics endpoint error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/scan_history/<session_id>')
def get_scan_history(session_id):
    """Get detailed scan history"""
    try:
        conn = sqlite3.connect('behavior_analytics.db', check_same_thread=False)
        c = conn.cursor()
        
        c.execute('''
            SELECT url, risk_level, user_decision, response_time_ms, 
                   hesitation_time_ms, timestamp 
            FROM url_checks 
            WHERE session_id = ?
            ORDER BY timestamp DESC
        ''', (session_id,))
        
        history = c.fetchall()
        conn.close()
        
        return jsonify({
            'session_id': session_id,
            'total_scans': len(history),
            'scan_history': [
                {
                    'url': row[0],
                    'risk_level': row[1],
                    'user_decision': row[2],
                    'response_time': row[3],
                    'hesitation_time': row[4],
                    'timestamp': row[5]
                } for row in history
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/background_scan', methods=['POST'])
def queue_background_scan():
    """Queue a URL for background scanning"""
    try:
        data = request.get_json()
        url = data.get('url')
        session_id = data.get('session_id')
        
        if not url:
            return jsonify({'error': 'URL required'}), 400
        
        scan_id = background_scanner.queue_scan(url, session_id)
        
        return jsonify({
            'status': 'queued',
            'scan_id': scan_id,
            'message': 'URL queued for background scanning'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/background_scan/<scan_id>')
def get_scan_status(scan_id):
    """Get background scan status"""
    try:
        status = background_scanner.get_scan_status(scan_id)
        if status:
            return jsonify(status)
        return jsonify({'error': 'Scan not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/alerts')
def get_alerts():
    """Get active alerts"""
    try:
        active = alert_system.get_active_alerts()
        history = alert_system.get_alert_history(limit=50)
        
        return jsonify({
            'active': active,
            'recent': history
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/alerts/<alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id):
    """Resolve an alert"""
    try:
        data = request.get_json()
        resolved_by = data.get('resolved_by', 'system')
        
        alert_system.resolve_alert(alert_id, resolved_by)
        
        return jsonify({'status': 'success', 'message': 'Alert resolved'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cloud_db/check', methods=['POST'])
def check_cloud_db():
    """Check URL against cloud phishing database"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL required'}), 400
        
        result = cloud_phishing_db.check_url(url)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cloud_db/add', methods=['POST'])
def add_to_cloud_db():
    """Manually add URL to cloud database"""
    try:
        data = request.get_json()
        url = data.get('url')
        threat_type = data.get('threat_type', 'phishing')
        confidence = data.get('confidence', 0.9)
        
        if not url:
            return jsonify({'error': 'URL required'}), 400
        
        result = cloud_phishing_db.add_to_database(url, threat_type, confidence, source='api')
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cloud_db/stats')
def get_cloud_db_stats():
    """Get cloud database statistics"""
    try:
        stats = cloud_phishing_db.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/biometrics/verify', methods=['POST'])
def verify_biometrics():
    """Verify user based on behavioral biometrics"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        behavior = data.get('behavior', {})
        
        if not session_id:
            return jsonify({'error': 'Session ID required'}), 400
        
        result = biometrics.verify_user(session_id, behavior)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/system/status')
def system_status():
    """Get system status"""
    try:
        scanner_status = {
            'queue_size': background_scanner.scan_queue.qsize() if hasattr(background_scanner, 'scan_queue') else 0,
            'active_scans': len(background_scanner.active_scans) if hasattr(background_scanner, 'active_scans') else 0
        }
        
        alert_status = {
            'active_alerts': len(alert_system.active_alerts) if hasattr(alert_system, 'active_alerts') else 0
        }
        
        cloud_stats = cloud_phishing_db.get_stats() if hasattr(cloud_phishing_db, 'get_stats') else {}
        
        conn = sqlite3.connect('behavior_analytics.db')
        c = conn.cursor()
        
        c.execute('SELECT COUNT(*) FROM url_checks')
        total_checks = c.fetchone()[0]
        
        c.execute('SELECT COUNT(DISTINCT session_id) FROM user_sessions')
        total_users = c.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'status': 'operational',
            'timestamp': datetime.now().isoformat(),
            'background_scanner': scanner_status,
            'alert_system': alert_status,
            'cloud_database': cloud_stats,
            'statistics': {
                'total_checks': total_checks,
                'total_users': total_users
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'modules': {
            'background_scanner': 'active',
            'biometrics': 'active',
            'alert_system': 'active',
            'cloud_phishing_db': 'active'
        }
    })

def get_recommended_action(risk_level):
    """Get recommended action based on risk level"""
    actions = {
        'SAFE': '✅ This URL appears safe to visit. Always stay vigilant!',
        'WARNING': '⚠️ Proceed with caution. Verify the website before entering any sensitive information.',
        'DANGEROUS': '🚨 DANGER! Avoid visiting this URL. It poses significant security risks.'
    }
    return actions.get(risk_level, '🔍 Use caution when visiting unknown URLs')

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║     🚀 LINK AUTH CHECKER - ADVANCED SECURITY SUITE 2.0       ║
    ╚══════════════════════════════════════════════════════════════╝
    
    📊 Modules Loaded:
    ├── 🔍 URL Security Scanner
    ├── 📈 Behavioral Analytics
    ├── 🔐 SSL/TLS Certificate Checker
    ├── 🌐 WHOIS Domain Age Analysis
    ├── 🧠 Threat Intelligence Integration
    ├── ⚡ Background Security Scanner
    ├── 👤 Behavioral Biometrics Module
    ├── 🚨 Real-time Alert System
    └── ☁️ Cloud Phishing Database
    
    📁 Database: behavior_analytics.db
    🌐 Server: http://localhost:5001
    
    Press CTRL+C to stop server
    """)
    
    app.run(debug=True, port=5001, host='0.0.0.0', threaded=True)