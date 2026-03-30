import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import sqlite3
import hashlib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import threading
import time

class BehavioralBiometrics:
    def __init__(self, db_path='behavior_analytics.db'):
        self.db_path = db_path
        self.user_profiles = {}
        self.model = None
        self.scaler = StandardScaler()
        self.is_training = False
        self.init_database()
        self.load_model()
        
    def init_database(self):
        """Initialize biometrics database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # User interaction patterns
            c.execute('''
                CREATE TABLE IF NOT EXISTS biometric_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    feature_type TEXT,
                    feature_vector TEXT,
                    pattern_hash TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    confidence_score REAL,
                    is_anomaly BOOLEAN DEFAULT 0,
                    FOREIGN KEY (session_id) REFERENCES user_sessions (session_id)
                )
            ''')
            
            # Mouse movement patterns
            c.execute('''
                CREATE TABLE IF NOT EXISTS mouse_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    movement_sequence TEXT,
                    avg_speed REAL,
                    max_speed REAL,
                    acceleration REAL,
                    jerk REAL,
                    curvature REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES user_sessions (session_id)
                )
            ''')
            
            # Keystroke dynamics
            c.execute('''
                CREATE TABLE IF NOT EXISTS keystroke_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    key_sequence TEXT,
                    hold_times TEXT,
                    interkey_times TEXT,
                    typing_speed REAL,
                    error_rate REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES user_sessions (session_id)
                )
            ''')
            
            # Decision patterns
            c.execute('''
                CREATE TABLE IF NOT EXISTS decision_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    decision_type TEXT,
                    response_time_ms INTEGER,
                    risk_level TEXT,
                    hesitation_time_ms INTEGER,
                    scroll_pattern TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES user_sessions (session_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Biometrics database initialized")
        except Exception as e:
            print(f"❌ Biometrics DB init error: {e}")
    
    def load_model(self):
        """Load or create ML model"""
        try:
            self.model = joblib.load('biometrics_model.pkl')
            print("✅ Loaded existing biometrics model")
        except:
            self.create_model()
    
    def create_model(self):
        """Create new ML model"""
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        print("✅ Created new biometrics model")
    
    def train_model(self, training_data=None):
        """Train the biometrics model"""
        if self.is_training:
            return
        
        self.is_training = True
        
        try:
            if training_data is None:
                training_data = self.get_training_data()
            
            if len(training_data) > 10:
                features = self.extract_features(training_data)
                labels = self.generate_labels(training_data)
                
                # Scale features
                features_scaled = self.scaler.fit_transform(features)
                
                # Train model
                self.model.fit(features_scaled, labels)
                
                # Save model
                joblib.dump(self.model, 'biometrics_model.pkl')
                joblib.dump(self.scaler, 'biometrics_scaler.pkl')
                
                print(f"✅ Model trained on {len(training_data)} samples")
        except Exception as e:
            print(f"❌ Model training error: {e}")
        finally:
            self.is_training = False
    
    def get_training_data(self):
        """Get training data from database"""
        conn = sqlite3.connect(self.db_path)
        
        # Get biometric patterns
        patterns = pd.read_sql_query('''
            SELECT * FROM biometric_patterns 
            WHERE confidence_score > 0.7
            ORDER BY timestamp DESC
            LIMIT 1000
        ''', conn)
        
        conn.close()
        return patterns
    
    def extract_features(self, data):
        """Extract features from raw data"""
        features = []
        
        for _, row in data.iterrows():
            feature_vector = json.loads(row['feature_vector'])
            features.append(list(feature_vector.values()))
        
        return np.array(features)
    
    def generate_labels(self, data):
        """Generate labels for training"""
        # For now, use confidence scores as labels
        return data['confidence_score'].values
    
    def track_mouse_movement(self, session_id, movements):
        """Track and analyze mouse movements"""
        try:
            # Calculate mouse metrics
            speeds = []
            accelerations = []
            jerks = []
            curvatures = []
            
            for i in range(1, len(movements)):
                dx = movements[i]['x'] - movements[i-1]['x']
                dy = movements[i]['y'] - movements[i-1]['y']
                dt = movements[i]['timestamp'] - movements[i-1]['timestamp']
                
                if dt > 0:
                    speed = np.sqrt(dx**2 + dy**2) / dt
                    speeds.append(speed)
                    
                    if i > 1:
                        dv = speed - speeds[-2]
                        acceleration = dv / dt
                        accelerations.append(acceleration)
                        
                        if i > 2:
                            da = acceleration - accelerations[-2]
                            jerk = da / dt
                            jerks.append(jerk)
            
            # Calculate curvature
            for i in range(2, len(movements)):
                p1 = np.array([movements[i-2]['x'], movements[i-2]['y']])
                p2 = np.array([movements[i-1]['x'], movements[i-1]['y']])
                p3 = np.array([movements[i]['x'], movements[i]['y']])
                
                v1 = p2 - p1
                v2 = p3 - p2
                
                if np.linalg.norm(v1) > 0 and np.linalg.norm(v2) > 0:
                    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                    angle = np.arccos(np.clip(cos_angle, -1, 1))
                    curvature = angle / np.linalg.norm(v2)
                    curvatures.append(curvature)
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''
                INSERT INTO mouse_patterns 
                (session_id, movement_sequence, avg_speed, max_speed, 
                 acceleration, jerk, curvature)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                json.dumps(movements[-50:]),  # Last 50 movements
                np.mean(speeds) if speeds else 0,
                np.max(speeds) if speeds else 0,
                np.mean(accelerations) if accelerations else 0,
                np.mean(jerks) if jerks else 0,
                np.mean(curvatures) if curvatures else 0
            ))
            
            conn.commit()
            conn.close()
            
            # Check for anomalies
            self.detect_anomalies(session_id, 'mouse', {
                'avg_speed': np.mean(speeds) if speeds else 0,
                'pattern': movements[-50:]
            })
            
        except Exception as e:
            print(f"❌ Mouse tracking error: {e}")
    
    def track_keystrokes(self, session_id, keystrokes):
        """Track and analyze keystroke dynamics"""
        try:
            hold_times = []
            interkey_times = []
            errors = 0
            
            for i in range(len(keystrokes)):
                key = keystrokes[i]
                
                # Calculate hold time
                if 'press_time' in key and 'release_time' in key:
                    hold_time = key['release_time'] - key['press_time']
                    hold_times.append(hold_time)
                
                # Calculate interkey time
                if i > 0:
                    interkey_time = key['press_time'] - keystrokes[i-1]['release_time']
                    interkey_times.append(interkey_time)
                
                # Track errors (backspace/delete)
                if key.get('key') in ['Backspace', 'Delete']:
                    errors += 1
            
            # Calculate typing speed (characters per minute)
            if len(keystrokes) > 1:
                total_time = keystrokes[-1]['press_time'] - keystrokes[0]['press_time']
                typing_speed = (len(keystrokes) / total_time) * 60000 if total_time > 0 else 0
            else:
                typing_speed = 0
            
            # Error rate
            error_rate = errors / len(keystrokes) if keystrokes else 0
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''
                INSERT INTO keystroke_patterns 
                (session_id, key_sequence, hold_times, interkey_times, 
                 typing_speed, error_rate)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                json.dumps([k.get('key') for k in keystrokes[-50:]]),
                json.dumps(hold_times[-50:]),
                json.dumps(interkey_times[-50:]),
                typing_speed,
                error_rate
            ))
            
            conn.commit()
            conn.close()
            
            # Check for anomalies
            self.detect_anomalies(session_id, 'keystroke', {
                'typing_speed': typing_speed,
                'error_rate': error_rate,
                'pattern': keystrokes[-50:]
            })
            
        except Exception as e:
            print(f"❌ Keystroke tracking error: {e}")
    
    def track_decision_pattern(self, session_id, decision_data):
        """Track user decision patterns"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''
                INSERT INTO decision_patterns 
                (session_id, decision_type, response_time_ms, risk_level, 
                 hesitation_time_ms, scroll_pattern)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                decision_data.get('decision'),
                decision_data.get('response_time'),
                decision_data.get('risk_level'),
                decision_data.get('hesitation_time'),
                json.dumps(decision_data.get('scroll_pattern', []))
            ))
            
            conn.commit()
            conn.close()
            
            # Update user profile
            self.update_user_profile(session_id, decision_data)
            
        except Exception as e:
            print(f"❌ Decision tracking error: {e}")
    
    def update_user_profile(self, session_id, decision_data):
        """Update user behavioral profile"""
        if session_id not in self.user_profiles:
            self.user_profiles[session_id] = {
                'session_id': session_id,
                'first_seen': datetime.now(),
                'decisions': [],
                'avg_response_time': 0,
                'risk_tolerance': 0,
                'hesitation_pattern': [],
                'anomaly_score': 0
            }
        
        profile = self.user_profiles[session_id]
        profile['decisions'].append(decision_data)
        
        # Update average response time
        response_times = [d.get('response_time', 0) for d in profile['decisions'] if d.get('response_time')]
        if response_times:
            profile['avg_response_time'] = np.mean(response_times)
        
        # Calculate risk tolerance
        risky_decisions = sum(1 for d in profile['decisions'] 
                            if d.get('decision') == 'proceed' 
                            and d.get('risk_level') in ['WARNING', 'DANGEROUS'])
        if profile['decisions']:
            profile['risk_tolerance'] = (risky_decisions / len(profile['decisions'])) * 100
        
        # Create feature vector
        feature_vector = self.create_feature_vector(profile)
        
        # Store in database
        self.store_biometric_pattern(session_id, 'user_profile', feature_vector)
    
    def create_feature_vector(self, profile):
        """Create feature vector from profile"""
        return {
            'avg_response_time': profile['avg_response_time'],
            'risk_tolerance': profile['risk_tolerance'],
            'decision_count': len(profile['decisions']),
            'timestamp': datetime.now().timestamp()
        }
    
    def store_biometric_pattern(self, session_id, feature_type, feature_vector):
        """Store biometric pattern in database"""
        try:
            # Create hash of feature vector for quick comparison
            pattern_hash = hashlib.md5(
                json.dumps(feature_vector, sort_keys=True).encode()
            ).hexdigest()
            
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''
                INSERT INTO biometric_patterns 
                (session_id, feature_type, feature_vector, pattern_hash, confidence_score)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                session_id,
                feature_type,
                json.dumps(feature_vector),
                pattern_hash,
                0.8  # Default confidence
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"❌ Pattern storage error: {e}")
    
    def detect_anomalies(self, session_id, behavior_type, behavior_data):
        """Detect anomalous behavior"""
        try:
            # Get user's historical patterns
            conn = sqlite3.connect(self.db_path)
            
            if behavior_type == 'mouse':
                query = '''
                    SELECT avg_speed, max_speed, acceleration 
                    FROM mouse_patterns 
                    WHERE session_id = ?
                    ORDER BY timestamp DESC 
                    LIMIT 50
                '''
            elif behavior_type == 'keystroke':
                query = '''
                    SELECT typing_speed, error_rate 
                    FROM keystroke_patterns 
                    WHERE session_id = ?
                    ORDER BY timestamp DESC 
                    LIMIT 50
                '''
            else:
                conn.close()
                return
            
            patterns = pd.read_sql_query(query, conn, params=(session_id,))
            conn.close()
            
            if len(patterns) < 5:
                return  # Not enough data
            
            # Calculate statistics
            means = patterns.mean()
            stds = patterns.std()
            
            # Check for anomalies
            anomalies = []
            
            if behavior_type == 'mouse':
                if abs(behavior_data['avg_speed'] - means['avg_speed']) > 3 * stds['avg_speed']:
                    anomalies.append('Unusual mouse speed')
            
            elif behavior_type == 'keystroke':
                if abs(behavior_data['typing_speed'] - means['typing_speed']) > 3 * stds['typing_speed']:
                    anomalies.append('Unusual typing speed')
                if abs(behavior_data['error_rate'] - means['error_rate']) > 3 * stds['error_rate']:
                    anomalies.append('Unusual error rate')
            
            if anomalies:
                self.flag_anomaly(session_id, behavior_type, anomalies, behavior_data)
            
        except Exception as e:
            print(f"❌ Anomaly detection error: {e}")
    
    def flag_anomaly(self, session_id, behavior_type, anomalies, behavior_data):
        """Flag anomalous behavior"""
        print(f"⚠️ Behavioral anomaly detected for session {session_id}:")
        print(f"   Type: {behavior_type}")
        print(f"   Anomalies: {anomalies}")
        
        # Store anomaly in database
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Update biometric_patterns to mark as anomaly
        c.execute('''
            UPDATE biometric_patterns 
            SET is_anomaly = 1 
            WHERE session_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', (session_id,))
        
        conn.commit()
        conn.close()
        
        # Trigger alert for security team
        from .alert_system import alert_system
        
        alert_system.create_alert(
            title=f"Behavioral Anomaly Detected - Session {session_id[:8]}",
            message=f"Anomalies: {', '.join(anomalies)}",
            severity="WARNING",
            source="biometrics",
            metadata={
                'session_id': session_id,
                'behavior_type': behavior_type,
                'anomalies': anomalies,
                'data': behavior_data
            }
        )
    
    def verify_user(self, session_id, current_behavior):
        """Verify user based on behavioral patterns"""
        try:
            # Get user profile
            conn = sqlite3.connect(self.db_path)
            
            # Get recent patterns
            mouse_patterns = pd.read_sql_query('''
                SELECT * FROM mouse_patterns 
                WHERE session_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 10
            ''', conn, params=(session_id,))
            
            keystroke_patterns = pd.read_sql_query('''
                SELECT * FROM keystroke_patterns 
                WHERE session_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 10
            ''', conn, params=(session_id,))
            
            decision_patterns = pd.read_sql_query('''
                SELECT * FROM decision_patterns 
                WHERE session_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 10
            ''', conn, params=(session_id,))
            
            conn.close()
            
            if len(mouse_patterns) < 3 or len(keystroke_patterns) < 3:
                return {'verified': True, 'confidence': 0.5, 'reason': 'Insufficient data'}
            
            # Create feature vectors for comparison
            historical_features = self.create_verification_features(
                mouse_patterns, keystroke_patterns, decision_patterns
            )
            
            current_features = self.create_current_features(current_behavior)
            
            # Compare using model if available
            if self.model and len(historical_features) > 0:
                # Scale features
                historical_scaled = self.scaler.fit_transform(historical_features)
                current_scaled = self.scaler.transform([current_features])
                
                # Predict
                confidence = self.model.predict_proba(current_scaled)[0][1]
                verified = confidence > 0.7
                
                return {
                    'verified': verified,
                    'confidence': float(confidence),
                    'threshold': 0.7,
                    'reason': 'ML model verification' if verified else 'ML model flagged anomaly'
                }
            else:
                # Simple statistical verification
                return self.statistical_verification(historical_features, current_features)
                
        except Exception as e:
            print(f"❌ User verification error: {e}")
            return {'verified': True, 'confidence': 0.5, 'error': str(e)}
    
    def create_verification_features(self, mouse_patterns, keystroke_patterns, decision_patterns):
        """Create feature vectors for verification"""
        features = []
        
        # Mouse features
        for _, row in mouse_patterns.iterrows():
            features.append([
                row['avg_speed'],
                row['max_speed'],
                row['acceleration'],
                row['jerk'],
                row['curvature']
            ])
        
        # Keystroke features
        for _, row in keystroke_patterns.iterrows():
            features.append([
                row['typing_speed'],
                row['error_rate']
            ])
        
        return np.array(features)
    
    def create_current_features(self, current_behavior):
        """Create feature vector from current behavior"""
        features = []
        
        if 'mouse' in current_behavior:
            mouse = current_behavior['mouse']
            features.extend([
                mouse.get('avg_speed', 0),
                mouse.get('max_speed', 0),
                mouse.get('acceleration', 0),
                mouse.get('jerk', 0),
                mouse.get('curvature', 0)
            ])
        
        if 'keystroke' in current_behavior:
            keystroke = current_behavior['keystroke']
            features.extend([
                keystroke.get('typing_speed', 0),
                keystroke.get('error_rate', 0)
            ])
        
        return features
    
    def statistical_verification(self, historical_features, current_features):
        """Statistical verification when ML model is not available"""
        if len(historical_features) == 0:
            return {'verified': True, 'confidence': 0.5}
        
        # Calculate mean and std for each feature
        means = np.mean(historical_features, axis=0)
        stds = np.std(historical_features, axis=0)
        
        # Calculate z-scores
        z_scores = np.abs((current_features - means) / (stds + 1e-10))
        
        # Calculate confidence (lower z-score = higher confidence)
        avg_z = np.mean(z_scores)
        confidence = 1 / (1 + avg_z)
        
        verified = avg_z < 2.0  # Within 2 standard deviations
        
        return {
            'verified': bool(verified),
            'confidence': float(confidence),
            'z_scores': z_scores.tolist(),
            'reason': 'Statistical verification'
        }
    
    def get_user_profile(self, session_id):
        """Get user's behavioral profile"""
        if session_id in self.user_profiles:
            return self.user_profiles[session_id]
        
        # Try to load from database
        conn = sqlite3.connect(self.db_path)
        
        profile = pd.read_sql_query('''
            SELECT * FROM biometric_patterns 
            WHERE session_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', conn, params=(session_id,))
        
        conn.close()
        
        if not profile.empty:
            return json.loads(profile.iloc[0]['feature_vector'])
        
        return None

# Singleton instance
biometrics = BehavioralBiometrics()