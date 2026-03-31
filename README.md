[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=yellow)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![scikit‑learn](https://img.shields.io/badge/scikit--learn-1.4-orange.svg)](https://scikit-learn.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3-green.svg)](https://flask.palletsprojects.com/)

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

# (DASHBOARD OF LINK AUTH CHECKER)
<img width="1426" height="822" alt="screenshot2" src="https://github.com/user-attachments/assets/ef36ffba-41e4-41ef-9de4-7ce93dd46071" />
# (BACKGROUND SCANNER)
<img width="1431" height="820" alt="screenshot1" src="https://github.com/user-attachments/assets/a3d63e08-8288-462f-875d-f938abf04671" />

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
```
## 🧪 Test Your Security Scanner

Use these URLs to test the different risk levels and verify the scanner is working correctly.

### ✅ Safe URLs (Should show SAFE)

| URL | Expected Result | Reason |
|-----|-----------------|--------|
| https://www.google.com | SAFE | Valid SSL, old domain |
| https://www.github.com | SAFE | Valid SSL, legitimate |
| https://www.microsoft.com | SAFE | Valid SSL, legitimate |
| https://www.python.org | SAFE | Valid SSL, legitimate |

### ⚠️ Warning URLs (Should show WARNING)

| URL | Expected Result | Reason |
|-----|-----------------|--------|
| http://goo.gl/abc123 | WARNING | URL shortener |
| http://bit.ly/3xY7zK9 | WARNING | URL shortener |
| http://example.xyz | WARNING | Suspicious TLD |
| http://test-site.top | WARNING | Suspicious TLD |

### 🔴 Dangerous URLs (Should show DANGEROUS)

| URL | Expected Result | Reason |
|-----|-----------------|--------|
| http://paypal-verify.tk | DANGEROUS | Brand impersonation + suspicious TLD |
| http://apple-id-verify.ga | DANGEROUS | Brand impersonation + suspicious TLD |
| http://secure-banking-verify.xyz | DANGEROUS | Phishing keywords + suspicious TLD |
| https://expired.badssl.com | DANGEROUS | Expired SSL certificate |
| https://self-signed.badssl.com | DANGEROUS | Self-signed certificate |
| http://192.168.1.1/login | DANGEROUS | IP address usage |

###  Use Cases

1.Security Awareness Training - Help users learn to identify phishing attempts
2.Personal Security Assistant - Get personalized advice based on your behavior
3.Threat Intelligence - Contribute to community phishing database
4.Security Research - Analyze URL patterns and user behavior

## 📊 System Architecture Overview

<img width="1249" height="740" alt="Screenshot 2026-03-31 at 11 56 44 AM" src="https://github.com/user-attachments/assets/08160a29-a9cf-4c34-a756-a4c41cbfe0a4" />


### Step-by-Step Working Process

![WhatsApp Image 2026-03-31 at 11 59 32](https://github.com/user-attachments/assets/c44a982e-2d1c-44b6-9943-f3c57c0e2e1c)


### 📊 Data Flow Diagram
<img width="1312" height="703" alt="Screenshot 2026-03-31 at 11 55 53 AM" src="https://github.com/user-attachments/assets/0c9ebbf9-825f-482e-9202-59db690ca915" />


## 👨‍💻 Author

**Aakash Yadav**  
*Department of Computer Science and Engineering*  
**KPR Institute of Engineering and Technology (KPR IET)**  
*Coimbatore, Tamil Nadu, India*

**© 2026 Aakash Yadav | KPR Institute of Engineering and Technology, CSE Department**

*Built with ❤️ for a safer digital world* 🔐




