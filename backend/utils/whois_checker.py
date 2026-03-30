import whois
from datetime import datetime
import socket
import re

# Known domain ages for common services
KNOWN_DOMAINS = {
    # Major websites
    'google.com': 28,
    'www.google.com': 28,
    'facebook.com': 21,
    'www.facebook.com': 21,
    'youtube.com': 20,
    'www.youtube.com': 20,
    'amazon.com': 29,
    'www.amazon.com': 29,
    'wikipedia.org': 24,
    'www.wikipedia.org': 24,
    'twitter.com': 19,
    'www.twitter.com': 19,
    'instagram.com': 15,
    'www.instagram.com': 15,
    'linkedin.com': 22,
    'www.linkedin.com': 22,
    'microsoft.com': 34,
    'www.microsoft.com': 34,
    'apple.com': 38,
    'www.apple.com': 38,
    'github.com': 17,
    'www.github.com': 17,
    'stackoverflow.com': 17,
    'www.stackoverflow.com': 17,
    'python.org': 24,
    'www.python.org': 24,
    'netflix.com': 27,
    'www.netflix.com': 27,
    'paypal.com': 25,
    'www.paypal.com': 25,
    
    # URL shorteners
    'goo.gl': 15,
    'bit.ly': 15,
    'tinyurl.com': 22,
    'ow.ly': 12,
    'tiny.cc': 15,
    'is.gd': 15,
    'buff.ly': 12,
    'adf.ly': 14,
    't.co': 13,
    'cutt.ly': 8,
    'rebrand.ly': 7,
    'short.link': 6,
}

def get_domain_age(domain):
    """Get domain registration age with comprehensive fallback"""
    try:
        # Clean the domain
        clean_domain = domain.replace('www.', '').replace('http://', '').replace('https://', '').split('/')[0].split('?')[0]
        
        # Check known domains first
        if clean_domain in KNOWN_DOMAINS:
            years = KNOWN_DOMAINS[clean_domain]
            if years < 1:
                return "Less than 1 year"
            elif years == 1:
                return "1 year"
            else:
                return f"{years} years"
        
        # Check if it's a subdomain of a known domain
        for known_domain, years in KNOWN_DOMAINS.items():
            if known_domain in clean_domain:
                if years < 1:
                    return "Less than 1 year"
                elif years == 1:
                    return "1 year"
                else:
                    return f"{years} years (based on main domain)"
        
        # Try WHOIS lookup
        try:
            domain_info = whois.whois(clean_domain)
            
            if domain_info and domain_info.creation_date:
                creation_date = domain_info.creation_date
                
                # Handle list of dates
                if isinstance(creation_date, list):
                    creation_date = creation_date[0]
                
                # Handle different date formats
                if isinstance(creation_date, datetime):
                    age_days = (datetime.now() - creation_date).days
                elif isinstance(creation_date, str):
                    try:
                        creation_date = datetime.strptime(creation_date.split()[0], '%Y-%m-%d')
                        age_days = (datetime.now() - creation_date).days
                    except:
                        # Try to extract year
                        year_match = re.search(r'(\d{4})', creation_date)
                        if year_match:
                            year = int(year_match.group(1))
                            age_days = (datetime.now().year - year) * 365
                        else:
                            return "Unknown"
                else:
                    return "Unknown"
                
                # Format the age
                if age_days < 0:
                    return "Future date (invalid)"
                elif age_days < 30:
                    return "Less than 1 month"
                elif age_days < 365:
                    months = age_days // 30
                    return f"{months} months"
                else:
                    years = age_days // 365
                    return f"{years} years"
                    
        except whois.parser.PywhoisError as e:
            if "No match for" in str(e):
                return "Domain not found (possibly new/unregistered)"
            print(f"WHOIS parser error: {e}")
        except Exception as e:
            print(f"WHOIS lookup error: {e}")
        
        # Try DNS lookup as fallback
        try:
            socket.gethostbyname(clean_domain)
            # Domain exists but WHOIS failed
            return "Unknown (domain exists)"
        except:
            pass
        
        # Check for patterns in domain
        if any(tld in clean_domain for tld in ['.tk', '.ml', '.ga', '.cf', '.xyz']):
            return "Recently registered (suspicious TLD)"
        
        return "Unknown"
        
    except Exception as e:
        print(f"Domain age error for {domain}: {e}")
        return "Unknown"

def check_domain_exists(domain):
    """Check if domain exists via DNS lookup"""
    try:
        socket.gethostbyname(domain)
        return True
    except:
        return False