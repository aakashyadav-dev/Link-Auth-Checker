import whois

def get_domain_age(domain):
    try:
        w = whois.whois(domain)
        return str(w.creation_date)
    except:
        return None
