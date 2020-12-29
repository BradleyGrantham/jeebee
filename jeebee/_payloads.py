from jeebee.constants import GB_TEAM_ID, USERNAME, PASSWORD

_TESTING_CHALLENGE_PAYLOAD_ONE_MAN = {
    "challengerTeamId": GB_TEAM_ID,
    "scheduleType": "AVAILABLE_NOW",
    "games": 5,
    "players": 1,
    "fields": [
        {"id": 62765, "value": ["Use Standard Gameplay"]},
        {"id": 62771, "value": ["Allowed"]},
        {"id": 62772, "value": ["Mouse & Keyboard Only"]},
        {"id": 62774, "value": ["Use GB Variant Restrictions"]},
    ],
    "premiumOnly": False,
    "roster": [],
    "maps": [],
    "mapsetId": 2305,
}

CHALLENGE_PAYLOAD = {
    "challengerTeamId": GB_TEAM_ID,
    "scheduleType": "AVAILABLE_NOW",
    "games": 3,
    # "players": 4,
    "fields": [
        {"id": 62744, "value": ["Use GB Variant Gameplay"]},
        {"id": 62749, "value": ["Allowed"]},
        {"id": 62750, "value": ["Controller Only"]},
    ],
    "premiumOnly": False,
    "roster": [],
    "maps": [],
    "mapsetId": 2318,
}

ACCEPT_CHALLENGE_PAYLOAD = {"acceptingTeamId": GB_TEAM_ID, "maps": [], "roster": []}


LOGIN_PAYLOAD = payload = {
    "utf8": True,
    "login": USERNAME,
    "return_to": "",
    "is_popup": "",
    "view_type": "full",
    "password": PASSWORD,
    "remember_me": "yes",
    "login_button": "Log+in",
}
