import requests

def check_redirects(url):
    try:
        response = requests.get(url, allow_redirects=True, timeout=5)
        return len(response.history)
    except:
        return -1
