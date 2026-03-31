# 🔐 Link Auth Checker

**An intelligent URL security scanner that analyzes threats, tracks behavior, and provides personalized security insights.**

Link Auth Checker is a full-stack security application that helps users identify malicious URLs while learning from their behavior to provide personalized security recommendations. It combines traditional security checks with modern behavioral analytics and cloud-based threat intelligence.

## 🎯 What Makes This Project Unique?

Unlike basic URL checkers, Link Auth Checker:
- **Learns from your behavior** - Tracks your decisions to calculate your security scores
- **Detects subtle patterns** - Identifies brand impersonation, URL shorteners, and suspicious TLDs
- **Provides personalized insights** - Gives you tailored security recommendations
- **Uses behavioral biometrics** - Analyzes mouse movements and keystroke patterns
- **Real-time alerting** - Notifies you immediately about security threats

## ⚡ Core Capabilities

### 🔍 URL Security Analysis
- SSL/TLS certificate validation (valid, expired, self-signed, revoked)
- WHOIS domain age lookup (new domains = higher risk)
- Suspicious pattern detection (IP addresses, hyphens, long domains)
- URL shortener detection (goo.gl, bit.ly, tinyurl, etc.)
- Brand impersonation detection (PayPal, Amazon, Apple, Microsoft, etc.)
- Phishing keyword detection (login, verify, secure, account, etc.)
- Risk scoring from 0-100% with clear explanations

### 📊 Behavioral Analytics
- Tracks user decisions (proceed/avoid) for each URL
- Measures response times and hesitation patterns
- Calculates personalized security scores:
  - **Phishing Susceptibility** - How often you proceed to risky URLs
  - **Security Compliance** - How well you avoid threats
  - **Risk Perception** - How quickly you identify risks
- Generates tailored security insights and recommendations

### 👤 Behavioral Biometrics
- Mouse movement tracking (speed, acceleration, curvature)
- Keystroke dynamics (typing speed, hold times, error rate)
- Decision pattern analysis (hesitation times, scroll behavior)
- Anomaly detection (flags unusual behavior patterns)
- User verification based on behavioral patterns

### ⚡ Background Security Scanner
- Asynchronous URL scanning (doesn't block UI)
- Queue management for multiple scans
- Resource-aware scanning (monitors CPU/memory usage)
- Persistent scan history with status tracking
- Automatic retry on failure

### 🚨 Real-time Alert System
- Multi-severity levels: CRITICAL, HIGH, MEDIUM, LOW
- Alerts from multiple sources (URL scanner, biometrics, cloud DB)
- Alert acknowledgment and resolution workflow
- Alert history tracking with timestamps
- Auto-refresh every 30 seconds

### ☁️ Cloud Phishing Database
- Integration with threat feeds (OpenPhish, PhishTank, URLhaus)
- Automatic hourly updates (keeps database current)
- Local caching for fast lookups (5-minute cache)
- Community contributions (users can add suspicious URLs)
- Statistics dashboard with real-time metrics

## 🛠 Technical Stack

| Component | Technologies |
|-----------|--------------|
| **Backend** | Python 3.9+, Flask, SQLite, Pandas, NumPy, Scikit-learn, aiohttp, whois, cryptography |
| **Frontend** | React 18, Axios, CSS3, Chart.js |
| **Security** | SSL/TLS validation, WHOIS lookup, URL parsing, regex pattern matching |
| **Database** | SQLite with optimized indexes for fast lookups |
| **ML/Analytics** | Scikit-learn for behavior classification, NumPy for calculations |

## 📊 Risk Scoring System

The risk score is calculated using a weighted algorithm:

| Factor | Impact |
|--------|--------|
| IP address usage | +5 (critical) |
| Invalid/Expired SSL | +8 (critical) |
| Brand impersonation | +3-4 (high) |
| URL shortener | +3-4 (medium) |
| Suspicious TLD (.tk, .xyz, etc.) | +3 (medium) |
| Recently registered domain | +2 (low) |
| Suspicious path terms | +1-2 (low) |

**Final Risk Levels:**
- **SAFE** (0-20%): Legitimate websites with valid SSL
- **WARNING** (30-70%): Suspicious - proceed with caution
- **DANGEROUS** (75-95%): Known malicious sites

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/link-auth-checker.git
cd link-auth-checker

## Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py

# #Frontend setup (new terminal)
cd frontend
npm install
npm start
# Then open http://localhost:3000 in your browser.
# Test URLs
# URL	                      # Expected Result
https://www.google.com	✅ SAFE (valid SSL, old domain)
http://goo.gl/abc123	⚠️ WARNING (URL shortener)
http://paypal-verify.tk	🔴 DANGEROUS (brand impersonation)
https://expired.badssl.com	🔴 DANGEROUS (expired SSL)


## Screenshots
<img width="1426" height="822" alt="screenshot2" src="https://github.com/user-attachments/assets/ba6cd5b0-0702-446c-a9ad-2042d06fc522" />
<img width="1431" height="820" alt="screenshot1" src="https://github.com/user-attachments/assets/e1257993-f6c3-446d-b131-56c33d18f34d" />

