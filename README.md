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
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                              │
│                    (React Frontend - Port 3000)                     │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐      │
│  │ Scanner │ │Analytics│ │ Biometrics│ │ Alerts │ │ Cloud DB│      │
│  └────┬────┘ └────┬────┘ └────┬─────┘ └────┬────┘ └────┬────┘      │
└───────┼───────────┼───────────┼────────────┼──────────┼────────────┘
        │           │           │            │          │
        └───────────┴───────────┴────────────┴──────────┘
                              │ HTTP/REST API
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BACKEND API SERVER                             │
│                     (Flask - Port 5001)                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    ROUTING & MIDDLEWARE                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │ URL Scanner │  │  Analytics  │  │  Biometrics │  │ Alert System│ │
│  │  Module     │  │  Module     │  │   Module    │  │   Module    │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘ │
│         │                │                │                │        │
│  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐ │
│  │ SSL Checker │  │  Database   │  │ Mouse/Key   │  │ Cloud Phish │ │
│  │ WHOIS Lookup│  │   Queries   │  │  Tracking   │  │  Database   │ │
│  │URL Analyzer │  │             │  │             │  │             │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           DATABASE                                  │
│                    (SQLite - behavior_analytics.db)                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │user_sessions│  │ url_checks  │  │   alerts    │                 │
│  └─────────────┘  └─────────────┘  └─────────────┘                 │
│  ┌─────────────┐  ┌─────────────┐                                   │
│  │behavioral_  │  │phishing_    │                                   │
│  │  metrics    │  │   urls      │                                   │
│  └─────────────┘  └─────────────┘                                   │
└─────────────────────────────────────────────────────────────────────┘

### Step-by-Step Working Process

# 1. URL Checking Flow

User enters URL (e.g., "https://www.google.com")
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│ Step 1: Frontend sends POST request to /check endpoint │
│         with URL and session ID in headers              │
└─────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│ Step 2: Backend receives request                        │
│         - Extracts URL from request body                │
│         - Gets/Creates session ID                       │
│         - Validates URL format                          │
└─────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│ Step 3: SSL Certificate Validation                      │
│         - Attempts to connect to domain on port 443     │
│         - Retrieves SSL certificate                     │
│         - Checks: validity, expiry date, issuer         │
│         - Returns: VALID/INVALID/EXPIRED                │
└─────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│ Step 4: WHOIS Domain Age Lookup                         │
│         - Queries domain registration date              │
│         - Calculates age in days/months/years           │
│         - New domains (<30 days) = higher risk          │
│         - Old domains (>1 year) = lower risk            │
└─────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│ Step 5: URL Pattern Analysis                            │
│         - Check for IP addresses (192.168.1.1)         │
│         - Detect URL shorteners (bit.ly, goo.gl)        │
│         - Identify suspicious TLDs (.tk, .xyz)          │
│         - Count hyphens and domain length               │
│         - Detect brand names in domain                  │
└─────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│ Step 6: Phishing Indicator Detection                    │
│         - Search for login/verify in URL path           │
│         - Check for @ symbol (hidden redirect)          │
│         - Count subdomains                              │
│         - Detect encoded characters                     │
└─────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│ Step 7: Cloud Database Check                            │
│         - Hash the URL for lookup                       │
│         - Check local cache first (5-minute TTL)        │
│         - Query phishing_urls table                     │
│         - Return match if found with confidence score   │
└─────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│ Step 8: Risk Score Calculation                          │
│                                                         │
│  Total Score = Suspicious_Score + Phishing_Score       │
│                                                         │
│  Factors:                                              │
│  • IP address: +5 points                               │
│  • URL shortener: +3-4 points                          │
│  • Suspicious TLD: +3 points                           │
│  • Invalid SSL: +8 points                              │
│  • Brand impersonation: +3-4 points                    │
│  • New domain: +2 points                               │
│                                                         │
│  Risk Level:                                           │
│  • 0-2 points: SAFE (10-20% phishing)                  │
│  • 3-8 points: WARNING (30-70% phishing)               │
│  • 9+ points: DANGEROUS (75-95% phishing)              │
└─────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│ Step 9: Store Results in Database                       │
│         - Insert record into url_checks table          │
│         - Link to session_id                            │
│         - Store risk level and timestamp                │
│         - Queue for background scanning                 │
└─────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│ Step 10: Return JSON Response to Frontend               │
│          - Risk level, SSL status, domain age           │
│          - Warnings and indicators                      │
│          - Recommended action                           │
│          - Session ID for tracking                      │
└─────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│ Step 11: Frontend Displays Results                      │
│          - Color-coded risk badge (SAFE/WARNING/DANGER) │
│          - SSL certificate status                       │
│          - Domain age information                       │
│          - List of warnings                             │
│          - Phishing indicators                          │
│          - Decision buttons (Proceed/Avoid)             │
└─────────────────────────────────────────────────────────┘

### 📊 Data Flow Diagram

┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  User    │───▶│ Frontend │───▶│ Backend  │───▶│Database  │
│  Input   │    │  (React) │    │ (Flask)  │    │ (SQLite) │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                     │               │                │
                     │               │                │
                     ▼               ▼                ▼
              ┌──────────┐    ┌──────────┐    ┌──────────┐
              │ Display  │◀───│ Process  │◀───│  Store   │
              │ Results  │    │ Request  │    │  Data    │
              └──────────┘    └──────────┘    └──────────┘
                     │               │                │
                     │               │                │
                     ▼               ▼                ▼
              ┌──────────┐    ┌──────────┐    ┌──────────┐
              │ User     │───▶│ Update   │───▶│ Update   │
              │ Decision │    │ Database │    │Analytics │
              └──────────┘    └──────────┘    └──────────┘

## 👨‍💻 Author

**Aakash Yadav**  
*Department of Computer Science and Engineering*  
**KPR Institute of Engineering and Technology (KPR IET)**  
*Coimbatore, Tamil Nadu, India*

**© 2026 Aakash Yadav | KPR Institute of Engineering and Technology, CSE Department**

*Built with ❤️ for a safer digital world* 🔐




