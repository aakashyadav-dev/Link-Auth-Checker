from urllib.parse import urlparse
import re
import asyncio
from datetime import datetime
from .ssl_checker import ssl_checker
from .whois_checker import get_domain_age

# Comprehensive list of suspicious TLDs
SUSPICIOUS_TLDS = [
    '.tk', '.ml', '.ga', '.cf', '.xyz', '.top', '.club', '.work', '.date',
    '.men', '.loan', '.download', '.review', '.party', '.racing', '.online',
    '.site', '.website', '.space', '.tech', '.store', '.shop', '.click',
    '.link', '.info', '.biz', '.tv', '.cc', '.ws', '.pw'
]

# Legitimate TLDs (safe)
LEGITIMATE_TLDS = [
    '.com', '.org', '.net', '.edu', '.gov', '.mil', '.io', '.co', '.uk',
    '.de', '.jp', '.fr', '.au', '.ca', '.ch', '.in', '.eu', '.us'
]

# URL shorteners (often used to hide malicious URLs)
URL_SHORTENERS = [
    'bit.ly', 'tinyurl.com', 'goo.gl', 'ow.ly', 'tiny.cc', 'is.gd',
    'buff.ly', 'adf.ly', 'short.link', 'shorturl.com', 'shorturl.at',
    't.co', 'bitly.com', 'rebrand.ly', 'cutt.ly', 'tiny.one', 'shorte.st',
    'bc.vc', 't2m.io', 'clck.ru', 'gg.gg', 'qps.ru'
]

# Known phishing keywords (only suspicious when combined with other factors)
PHISHING_KEYWORDS = [
    'login', 'signin', 'verify', 'secure', 'account', 'banking', 'paypal',
    'update', 'confirm', 'validation', 'authenticate', 'credential',
    'password', 'username', 'wallet', 'payment', 'shipping', 'invoice',
    'bill', 'refund', 'support'
]

# Legitimate domains that should NEVER be flagged as dangerous
LEGITIMATE_DOMAINS = [
    'google.com', 'www.google.com', 'mail.google.com', 'drive.google.com',
    'microsoft.com', 'www.microsoft.com', 'office.microsoft.com', 'support.microsoft.com',
    'apple.com', 'www.apple.com', 'icloud.com', 'www.icloud.com',
    'amazon.com', 'www.amazon.com', 'aws.amazon.com',
    'facebook.com', 'www.facebook.com', 'instagram.com', 'www.instagram.com',
    'twitter.com', 'www.twitter.com', 'x.com', 'www.x.com',
    'linkedin.com', 'www.linkedin.com',
    'github.com', 'www.github.com',
    'stackoverflow.com', 'www.stackoverflow.com',
    'python.org', 'www.python.org',
    'netflix.com', 'www.netflix.com',
    'spotify.com', 'www.spotify.com',
    'dropbox.com', 'www.dropbox.com',
    'slack.com', 'www.slack.com',
    'zoom.us', 'www.zoom.us',
    'whatsapp.com', 'www.whatsapp.com',
    'telegram.org', 'www.telegram.org',
    'wikipedia.org', 'www.wikipedia.org',
    'youtube.com', 'www.youtube.com',
    'bing.com', 'www.bing.com',
    'yahoo.com', 'www.yahoo.com',
    'reddit.com', 'www.reddit.com',
    'wordpress.com', 'www.wordpress.com',
    'medium.com', 'www.medium.com',
    'quora.com', 'www.quora.com',
    'pinterest.com', 'www.pinterest.com',
    'tumblr.com', 'www.tumblr.com',
    'twitch.tv', 'www.twitch.tv',
    'discord.com', 'www.discord.com',
    'paypal.com', 'www.paypal.com',
    'ebay.com', 'www.ebay.com',
    'walmart.com', 'www.walmart.com',
    'target.com', 'www.target.com',
    'bestbuy.com', 'www.bestbuy.com',
    'nike.com', 'www.nike.com',
    'adidas.com', 'www.adidas.com',
    'zara.com', 'www.zara.com',
    'hm.com', 'www.hm.com'
]

def extract_domain_parts(url):
    """Extract domain parts using simple parsing"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        if not domain:
            domain = url.split('/')[0].lower()
        
        # Remove www prefix for analysis
        domain_without_www = domain.replace('www.', '')
        
        # Split into parts
        parts = domain_without_www.split('.')
        
        if len(parts) >= 2:
            return {
                'subdomain': '.'.join(parts[:-2]) if len(parts) > 2 else '',
                'domain': parts[-2] if len(parts) >= 2 else parts[0],
                'suffix': parts[-1] if len(parts) >= 1 else '',
                'full_domain': domain,
                'full_domain_without_www': domain_without_www
            }
        else:
            return {
                'subdomain': '',
                'domain': parts[0] if parts else '',
                'suffix': '',
                'full_domain': domain,
                'full_domain_without_www': domain_without_www
            }
    except:
        return None

def is_legitimate_domain(domain):
    """Check if domain is in legitimate domains list"""
    domain_lower = domain.lower()
    domain_without_www = domain_lower.replace('www.', '')
    
    for legit in LEGITIMATE_DOMAINS:
        if legit == domain_lower or legit == domain_without_www:
            return True, legit
        # Check for subdomains of legitimate domains
        if domain_without_www.endswith(f'.{legit}') or domain_without_www.endswith(f'.{legit.replace("www.", "")}'):
            return True, legit
    return False, None

def is_url_shortener(domain):
    """Check if domain is a known URL shortener"""
    domain_lower = domain.lower()
    domain_without_www = domain_lower.replace('www.', '')
    
    for shortener in URL_SHORTENERS:
        if shortener == domain_without_www or shortener in domain_without_www:
            return True, shortener
    return False, None

def analyze_url_security(url):
    """Comprehensive URL security analysis"""
    suspicious_score = 0
    warnings = []
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        if not domain:
            domain = url.split('/')[0].lower()
            parsed = urlparse(f"http://{url}")
            domain = parsed.netloc.lower()
        
        # Check if domain is legitimate (bypass all checks for known good domains)
        is_legit, legit_domain = is_legitimate_domain(domain)
        if is_legit:
            return 0, [f"✅ Known legitimate domain: {legit_domain}"]
        
        domain_without_www = domain.replace('www.', '')
        
        # Check for IP address usage
        ip_pattern = r'^\d+\.\d+\.\d+\.\d+$'
        if re.match(ip_pattern, domain_without_www):
            suspicious_score += 5
            warnings.append("🚨 Uses IP address instead of domain name (highly suspicious)")
        
        # Check for URL shorteners
        is_shortener, shortener_name = is_url_shortener(domain)
        if is_shortener:
            suspicious_score += 3
            warnings.append(f"⚠️ URL shortener detected: {shortener_name} - destination hidden")
        
        # Check for suspicious TLDs
        domain_parts = extract_domain_parts(url)
        if domain_parts and domain_parts['suffix']:
            tld = f".{domain_parts['suffix']}"
            if tld in SUSPICIOUS_TLDS:
                suspicious_score += 3
                warnings.append(f"⚠️ Suspicious TLD detected: {tld} (often used for phishing)")
        
        # Check for excessive hyphens
        hyphen_count = domain_without_www.count('-')
        if hyphen_count > 3:
            suspicious_score += min(hyphen_count, 3)
            warnings.append(f"⚠️ Multiple hyphens in domain ({hyphen_count}) - often indicates deceptive domains")
        elif hyphen_count > 0:
            suspicious_score += 1
            warnings.append("⚠️ Hyphen in domain name")
        
        # Check for long domain
        if len(domain_without_www) > 40:
            suspicious_score += 2
            warnings.append("⚠️ Unusually long domain name")
        elif len(domain_without_www) > 30:
            suspicious_score += 1
            warnings.append("⚠️ Long domain name")
        
        # Check for numeric domain
        if re.search(r'\d{4,}', domain_without_www):
            suspicious_score += 2
            warnings.append("⚠️ Domain contains multiple numbers - often automated/phishing")
        
        # Check for mixed letters and numbers
        if re.search(r'[a-z]+\d+[a-z]+', domain_without_www):
            suspicious_score += 1
            warnings.append("⚠️ Mixed letters and numbers in unusual pattern")
        
    except Exception as e:
        print(f"URL analysis error: {e}")
    
    return suspicious_score, warnings

def check_phishing_indicators(url, domain):
    """Check for phishing indicators"""
    phishing_score = 0
    indicators = []
    
    try:
        domain_lower = domain.lower()
        domain_without_www = domain_lower.replace('www.', '')
        parsed = urlparse(url)
        path = parsed.path.lower()
        query = parsed.query.lower()
        
        # First check if it's a legitimate domain - if so, return 0
        is_legit, legit_domain = is_legitimate_domain(domain)
        if is_legit:
            return 0, [f"✅ Known legitimate domain: {legit_domain}"]
        
        # Brands to check for impersonation
        brands = ['paypal', 'amazon', 'apple', 'microsoft', 'google', 'facebook', 
                  'instagram', 'netflix', 'spotify', 'dropbox', 'linkedin', 'twitter',
                  'chase', 'wellsfargo', 'bankofamerica', 'americanexpress', 
                  'mastercard', 'visa', 'ebay', 'walmart', 'target', 'bestbuy',
                  'nike', 'adidas', 'zara', 'hm']
        
        # Check for brand impersonation
        for brand in brands:
            if brand in domain_without_www:
                # Check if it's actually the legitimate domain
                legitimate_patterns = [
                    f"{brand}.com", f"www.{brand}.com", f"{brand}.org", 
                    f"{brand}.net", f"{brand}.co.uk", f"{brand}.de",
                    f"{brand}.fr", f"{brand}.jp", f"{brand}.au"
                ]
                
                is_legitimate_brand = False
                for legit in legitimate_patterns:
                    if legit == domain_without_www or domain_without_www.endswith(f'.{legit}'):
                        is_legitimate_brand = True
                        break
                
                # Special case for microsoft.com - it's legitimate
                if brand == 'microsoft' and (domain_without_www == 'microsoft.com' or 
                                             domain_without_www.endswith('.microsoft.com')):
                    is_legitimate_brand = True
                
                if not is_legitimate_brand:
                    phishing_score += 4
                    indicators.append(f"🚨 Possible {brand} impersonation detected")
                    # Only count the first brand match
                    break
        
        # Check for login/verify in path (only adds points if domain is suspicious)
        suspicious_path_terms = ['login', 'signin', 'verify', 'secure', 'account', 
                                 'update', 'confirm', 'validation', 'auth', 'authenticate',
                                 'password', 'credential', 'wallet', 'payment']
        
        path_terms_found = []
        for term in suspicious_path_terms:
            if term in path:
                path_terms_found.append(term)
        
        # Only add phishing score for path terms if domain already has some suspicion
        if path_terms_found and phishing_score > 0:
            phishing_score += min(len(path_terms_found), 2)
            indicators.append(f"⚠️ Suspicious path terms: {', '.join(path_terms_found[:2])}")
        
        # Check for @ symbol in URL
        if '@' in url:
            phishing_score += 4
            indicators.append("🚨 '@' symbol in URL - can hide real destination")
        
        # Check for multiple subdomains
        subdomain_count = domain.count('.') - 1
        if subdomain_count > 3 and phishing_score > 0:
            phishing_score += min(subdomain_count, 2)
            indicators.append(f"⚠️ Multiple subdomains ({subdomain_count})")
        
        # Check for encoded characters
        if '%' in url and phishing_score > 0:
            phishing_score += 1
            indicators.append("⚠️ Encoded characters in URL")
        
    except Exception as e:
        print(f"Phishing check error: {e}")
    
    return phishing_score, indicators

async def calculate_risk_level_async(url):
    """Calculate risk level based on comprehensive checks"""
    try:
        # Parse URL
        parsed = urlparse(url)
        domain = parsed.netloc
        
        if not domain:
            try:
                parsed = urlparse(f"http://{url}")
                domain = parsed.netloc
            except:
                return "WARNING", 50, {'error': 'Invalid URL format'}
        
        clean_domain = domain.replace('www.', '')
        
        print(f"🔍 Analyzing: {url} (domain: {clean_domain})")
        
        # First check if it's a legitimate domain
        is_legit, legit_domain = is_legitimate_domain(domain)
        if is_legit:
            print(f"✅ Recognized legitimate domain: {legit_domain}")
            return "SAFE", 10, {
                'ssl_status': 'VALID',
                'domain_age': get_domain_age(clean_domain),
                'warnings': [f"✅ Known legitimate domain"],
                'suspicious_score': 0,
                'phishing_score': 0,
                'total_score': 0,
                'is_url_shortener': False,
                'shortener_name': None
            }
        
        # Get SSL status
        ssl_status = 'Unknown'
        ssl_error = None
        try:
            ssl_result = await ssl_checker.check_ssl_async(clean_domain)
            ssl_status = ssl_result.get('status', 'Unknown')
            ssl_error = ssl_result.get('error')
        except Exception as e:
            print(f"SSL check error: {e}")
            ssl_status = 'ERROR'
            ssl_error = str(e)
        
        # Get domain age
        domain_age = get_domain_age(clean_domain)
        
        # Analyze URL security
        suspicious_score, warnings = analyze_url_security(url)
        
        # Check phishing indicators
        phishing_score, indicators = check_phishing_indicators(url, clean_domain)
        
        # Calculate total score
        total_score = suspicious_score + phishing_score
        
        # SSL status has a MAJOR impact on risk
        if ssl_status == "INVALID" or ssl_status == "EXPIRED":
            total_score += 8  # Major increase for invalid SSL
            warnings.append(f"❌ Invalid SSL certificate: {ssl_error if ssl_error else 'Certificate is not valid'}")
        elif ssl_status == "EXPIRING_SOON":
            total_score += 2
            warnings.append("⚠️ SSL certificate expiring soon")
        elif ssl_status == "VALID":
            # Valid SSL reduces risk slightly
            if total_score > 2:
                total_score -= 1
        elif ssl_status == "ERROR" or ssl_status == "Unknown":
            total_score += 3
            warnings.append("⚠️ Could not verify SSL certificate")
        
        # Adjust based on domain age
        if "year" in domain_age:
            try:
                years = int(domain_age.split()[0])
                if years > 5:
                    total_score = max(0, total_score - 2)
                elif years > 1:
                    total_score = max(0, total_score - 1)
            except:
                pass
        elif "month" in domain_age:
            # New domain - increase risk
            total_score += 2
            warnings.append("⚠️ Recently registered domain")
        
        # Check for URL shorteners
        is_shortener, shortener_name = is_url_shortener(clean_domain)
        if is_shortener:
            total_score += 3
            indicators.append(f"⚠️ URL shortener ({shortener_name}) - destination unknown")
        
        # Determine risk level based on total score AND SSL status
        if ssl_status == "INVALID" or ssl_status == "EXPIRED":
            # Invalid SSL automatically makes it at least WARNING, usually DANGEROUS
            if total_score >= 5:
                risk = "DANGEROUS"
                phishing_percent = 85
            else:
                risk = "WARNING"
                phishing_percent = 60
        elif total_score <= 2:
            risk = "SAFE"
            phishing_percent = 10
        elif total_score <= 5:
            risk = "WARNING"
            phishing_percent = 30 + (total_score - 2) * 10
        elif total_score <= 8:
            risk = "WARNING"
            phishing_percent = 60 + (total_score - 5) * 5
        else:
            risk = "DANGEROUS"
            phishing_percent = 75 + (total_score - 8) * 5
        
        # Cap phishing percentage
        phishing_percent = min(95, max(10, phishing_percent))
        
        # Combine warnings and indicators
        all_warnings = warnings + indicators
        
        # Remove duplicates
        unique_warnings = []
        for w in all_warnings:
            if w not in unique_warnings:
                unique_warnings.append(w)
        
        result = {
            'ssl_status': ssl_status,
            'domain_age': domain_age,
            'warnings': unique_warnings,
            'suspicious_score': suspicious_score,
            'phishing_score': phishing_score,
            'total_score': total_score,
            'is_url_shortener': is_shortener,
            'shortener_name': shortener_name if is_shortener else None,
            'ssl_error': ssl_error
        }
        
        print(f"✅ Risk calculation: {risk} (Score: {total_score}, Phishing: {phishing_percent}%, SSL: {ssl_status})")
        return risk, int(phishing_percent), result
        
    except Exception as e:
        print(f"❌ Risk calculation error: {e}")
        return "WARNING", 50, {'error': str(e)}

def calculate_risk_level(url):
    """Synchronous wrapper for calculate_risk_level_async"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(calculate_risk_level_async(url))
        return result
    finally:
        loop.close()