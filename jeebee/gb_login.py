import requests
from bs4 import BeautifulSoup

import jeebee._payloads


def _get_auth_token(session: requests.Session):
    r = session.get(
        "https://accounts.majorleaguegaming.com/?return_to=https://gamebattles.majorleaguegaming.com/"
    )
    soup = BeautifulSoup(r.content, "html.parser")
    auth_token = soup.find("meta", {"name": "csrf-token"})["content"]
    return auth_token


def _login() -> requests.Session:
    sess = requests.Session()
    auth_token = _get_auth_token(sess)
    payload = jeebee._payloads.LOGIN_PAYLOAD
    payload["authenticity_token"] = auth_token

    sess.post("https://accounts.majorleaguegaming.com/session", data=payload)

    return sess


gb_session = _login()
