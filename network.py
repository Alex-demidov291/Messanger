import requests
from styles import SERVER_URL


def make_server_request(endpoint, data=None, method='POST'):
    url = f"{SERVER_URL}/{endpoint}"
    if method == 'POST':
        response = requests.post(url, json=data, timeout=1)
    else:
        response = requests.get(url, timeout=1)

    if response.status_code == 200:
        return response.json()
    return None