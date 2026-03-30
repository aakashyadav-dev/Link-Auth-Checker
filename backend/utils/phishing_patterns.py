def detect_phishing_patterns(url):
    patterns = ["secure-", "verify", "update", "@", "login", "free", "bonus"]
    return any(p in url.lower() for p in patterns)
