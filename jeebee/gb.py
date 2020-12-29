import datetime
from typing import Optional, Iterable
from pprint import pformat, pprint

import requests

import jeebee.constants
import jeebee._payloads
from jeebee.utils import logger
from jeebee.gb_login import gb_session


def get_matches_from_gb(all_match_pages: Optional[bool] = True):
    """Get matches for the GameBattles team with id GB_TEAM_ID."""
    r = requests.get(jeebee.constants.GB_MATCHES_URL.format(page_number=1))
    matches = r.json()["body"]["records"]

    if all_match_pages:
        for page_number in range(2, r.json()["body"]["totalPages"]):
            r = requests.get(
                jeebee.constants.GB_MATCHES_URL.format(page_number=page_number)
            )
            matches += r.json()["body"]["records"]

    matches = sorted(matches, key=lambda x: x["match"]["playTime"], reverse=True)
    return matches


def get_wins_and_rosters(matches):

    match_details_url = (
        "https://gb-api.majorleaguegaming.com/api/web/v1/match-screen/{match_id}"
    )
    new_matches = []
    for match in matches:
        match_details = requests.get(
            match_details_url.format(match_id=match["match"]["id"])
        ).json()
        new_matches.append({**match, **match_details["body"]})

    for match in matches:
        try:
            details = (
                "homeTeamDetails"
                if match["match"]["homeTeamId"] == jeebee.constants.GB_TEAM_ID
                else "visitorTeamDetails"
            )
            roster = [
                match_player["matchPlayer"]["username"]
                for match_player in match[details]["roster"]
            ]
            match["roster"] = roster
        except KeyError:
            pass
    return matches


def get_win_percentage(n: Optional[int] = None, player: Optional[str] = None):
    """Get the win percentage over the last n games (all games if n is None)."""
    matches = get_matches_from_gb()

    if n is not None:
        matches = matches[:n]

    wins = 0
    match_num = 0
    for match in matches:
        if player is None:
            match_num += 1
            if match.get("winningTeamId", 0) == jeebee.constants.GB_TEAM_ID:
                wins += 1
        else:
            roster = [x[-1] for x in get_match_info(match)["we_rush_a_roster"]]
            if player in roster:
                match_num += 1
                if match.get("winningTeamId", 0) == jeebee.constants.GB_TEAM_ID:
                    wins += 1

    return (wins / match_num) * 100


def get_match_details(match_id: int):
    """Get the raw JSON match details from GameBattles."""
    match_details = requests.get(
        jeebee.constants.GB_MATCH_DETAILS_URL.format(match_id=match_id)
    )
    return match_details.json()["body"]


def get_current_active_match(return_status=False):
    """Get the current active match from GameBattles."""
    current_match = get_matches_from_gb(all_match_pages=False)[0]
    logger.info(f"Match status: {current_match['match']['status']}")
    if return_status:
        return current_match["match"]["status"]

    if current_match["match"]["status"] in ("COMPLETED", "DISPUTED"):
        return [
            {
                "name": "**Next match** :video_game:",
                "value": "[No pending matches.](https://gamebattles.majorleaguegaming.com/x-play/black-ops-cold-war/ladder/squads-eu/match-finder)",
            }
        ]

    if current_match["match"]["status"] in ("ACTIVE", "PENDING", "SCHEDULED"):

        match_info = get_match_info(current_match)

        fields = [
            {
                "name": "**Next match** :video_game:",
                "value": f"[**{match_info['match_time']}**](https://gamebattles.majorleaguegaming.com/x-play/black-ops-cold-war/team/{jeebee.constants.GB_TEAM_ID}/match/{match_info['match_id']})",
            },
            {
                "name": "**Opposition** :right_facing_fist:",
                "value": f"[**{match_info['oppostion_team_name']}**](https://gamebattles.majorleaguegaming.com/x-play/black-ops-cold-war/team/{match_info['oppostion_team_id']})\nRank: {match_info['opposition_rank']:,}\nCurrent streak: {match_info['opposition_streak']} :fire:",
            },
            {"name": "**Maps** :map:", "value": f"{match_info['maps']}"},
            {
                "name": "**Roster**",
                "value": "\n".join(
                    f"[{p[0]}](http://profile.majorleaguegaming.com/{p[2]})"
                    for p in match_info["opposition_team_roster"]
                ),
                "inline": True,
            },
            {
                "name": "**Ranks**",
                "value": "\n".join(p[1] for p in match_info["opposition_team_roster"]),
                "inline": True,
            },
        ]
        return fields


def get_last_completed_match():
    completed_status = "NOT-COMPLETED"
    i = 0
    while completed_status != "COMPLETED":
        current_match = get_matches_from_gb(all_match_pages=False)[i]
        completed_status = current_match["match"]["status"]
        i += 1

    match_info = get_match_info(current_match)

    fields = [
        {
            "name": "**Last match** :video_game:",
            "value": f"[**{match_info['match_time']}**](https://gamebattles.majorleaguegaming.com/x-play/black-ops-cold-war/team/{jeebee.constants.GB_TEAM_ID}/match/{match_info['match_id']})",
        },
        {
            "name": "**Result**",
            "value": f"{':poo: Loss!' if not match_info['won'] else ':trophy: Win!'}",
        },
        {
            "name": "**Opposition** :right_facing_fist:",
            "value": f"[**{match_info['oppostion_team_name']}**](https://gamebattles.majorleaguegaming.com/x-play/black-ops-cold-war/team/{match_info['oppostion_team_id']})\nRank: {match_info['opposition_rank']:,}\nCurrent streak: {match_info['opposition_streak']} :fire:",
        },
        {"name": "**Maps** :map:", "value": f"{match_info['maps']}"},
        {
            "name": "**Roster**",
            "value": "\n".join(
                f"[{p[0]}](http://profile.majorleaguegaming.com/{p[2]})"
                for p in match_info["opposition_team_roster"]
            ),
            "inline": True,
        },
        {
            "name": "**Ranks**",
            "value": "\n".join(p[1] for p in match_info["opposition_team_roster"]),
            "inline": True,
        },
    ]
    return fields


def get_match_info(match):
    d = dict()
    d["match_id"] = match["match"]["id"]

    d["match_time"] = datetime.datetime.fromtimestamp(
        match["match"]["playTime"]
    ).strftime("%Y-%m-%d %H:%M")

    opposition_home_or_visitor = (
        "home"
        if match["match"]["homeTeamId"] != jeebee.constants.GB_TEAM_ID
        else "visitor"
    )
    we_rush_a_home_or_visitor = (
        "home"
        if match["match"]["homeTeamId"] == jeebee.constants.GB_TEAM_ID
        else "visitor"
    )
    d["oppostion_team_id"] = match["match"][f"{opposition_home_or_visitor}TeamId"]
    d["oppostion_team_name"] = match[f"{opposition_home_or_visitor}TeamCard"]["name"]

    match_details = get_match_details(d["match_id"])
    d["opposition_team_roster"] = [
        (p.get("guid", ""), f"{p['rank']['rank']:,}", p["matchPlayer"]["username"])
        for p in match_details[f"{opposition_home_or_visitor}TeamDetails"]["roster"]
    ]
    d["we_rush_a_roster"] = [
        (p.get("guid", ""), f"{p['rank']['rank']:,}", p["matchPlayer"]["username"])
        for p in match_details[f"{we_rush_a_home_or_visitor}TeamDetails"]["roster"]
    ]
    d["maps"] = "\n".join([map["map"]["title"] for map in match_details["mapModes"]])
    d["opposition_rank"] = match_details[f"{opposition_home_or_visitor}TeamDetails"][
        "teamStanding"
    ]["rank"]
    d["opposition_streak"] = match_details[f"{opposition_home_or_visitor}TeamDetails"][
        "teamStanding"
    ]["streak"]["current"]

    d["won"] = (
        match_details.get("results", dict()).get("winningTeamId")
        == jeebee.constants.GB_TEAM_ID
    )

    return d


def find_matches(all_matches=False, kbm_only=True, return_fields=True):
    r = requests.get(jeebee.constants.GB_MATCH_FINDER_URL)
    available_matches = r.json()["body"]["records"]
    available_matches_with_details = []
    for i, match in enumerate(available_matches):
        match_details = requests.get(
            jeebee.constants.GB_MATCH_FINDER_DETAILS_URL.format(match_id=match["id"])
        ).json()["body"]
        match_details = {x["name"]: x["value"][0] for x in match_details}
        match_details["record_num"] = i
        available_matches_with_details.append({**match, **match_details})

    del available_matches

    if not all_matches:
        # filter games that are scheduled for later
        available_matches_with_details = [
            match
            for match in available_matches_with_details
            if match.get("scheduleType") == "AVAILABLE_NOW"
        ]

        # filter games that are premium
        available_matches_with_details = [
            match
            for match in available_matches_with_details
            if not match.get("isPremiumOnly")
        ]

        # filter any games that aren't GB Variant: Search & Destroy
        available_matches_with_details = [
            match
            for match in available_matches_with_details
            if "GB Variant: Search & Destroy" in match.get("mapset").get("title", "")
        ]

        # filter any games that arent best of 3
        available_matches_with_details = [
            match for match in available_matches_with_details if match["games"] == 3
        ]

        # filter only PC Players Allowed
        available_matches_with_details = [
            match
            for match in available_matches_with_details
            if match.get("PC Players") == "Allowed"
        ]

        if kbm_only:
            available_matches_with_details = [
                match
                for match in available_matches_with_details
                if match.get("Input Type") == "Any"
            ]

    if not return_fields:
        return available_matches_with_details

    if not available_matches_with_details:
        return [
            {
                "name": "**Available matches** :palm_tree:",
                "value": "[No suitable matches.](https://gamebattles.majorleaguegaming.com/x-play/black-ops-cold-war/ladder/squads-eu/match-finder)",
            }
        ]

    pc_players_allowed = [
        ":white_check_mark:" if match["PC Players"] == "Allowed" else ":no_entry:"
        for match in available_matches_with_details
    ]
    kbm_allowed = [
        ":white_check_mark:"
        if match["Input Type"] != "Controller Only"
        else ":no_entry:"
        for match in available_matches_with_details
    ]

    fields = [
        {
            "name": ":palm_tree:",
            "value": "\n".join(
                str(match["record_num"]) for match in available_matches_with_details
            ),
            "inline": True,
        },
        {
            "name": "**Game Type**",
            "value": "\n".join(
                match["mapset"]["title"]
                .replace("Search & Destroy", "S&D")
                .replace(" Variant", "")
                .replace("(3v3+)", "({p}v{p})".format(p=match["players"]))
                for match in available_matches_with_details
            ),
            "inline": True,
        },
        {
            "name": "**PC** :desktop: / **KBM** :mouse:",
            "value": "\n".join(
                [x + "   /   " + y for x, y in zip(pc_players_allowed, kbm_allowed)]
            ),
            "inline": True,
        },
        {
            "name": "Left number shows the position of the match on the match finder",
            "value": "[GameBattles match finder](https://gamebattles.majorleaguegaming.com/x-play/black-ops-cold-war/ladder/squads-eu/match-finder)",
        },
        # {
        #     "name": "**Dispute Percentage** :",
        #     "value": "\n".join(f"{match['disputePercentage']:.2f}%" for match in available_matches_with_details),
        #     "inline": True,
        # },
    ]

    return fields


def get_team_members():
    r = requests.get(jeebee.constants.GB_TEAM_MEMBERS_URL)
    team_members = r.json()["body"]
    team_members = {player["username"].lower(): player["id"] for player in team_members}
    return team_members


def convert_usernames_to_ids(roster):
    team_member_ids = get_team_members()
    roster = [player.lower() for player in roster]
    roster_ids = [team_member_ids[player] for player in roster]
    assert len(roster) == len(roster_ids)
    return roster_ids


def post_match(roster: Iterable, kbm_only=False):
    try:
        roster = convert_usernames_to_ids(roster)
    except KeyError:
        return None, [
            {
                "name": "**I can't find all of the usernames you entered** :cry:",
                "value": "[Match finder.](https://gamebattles.majorleaguegaming.com/x-play/black-ops-cold-war/ladder/squads-eu/match-finder)",
            }
        ]
    data = jeebee._payloads._TESTING_CHALLENGE_PAYLOAD_ONE_MAN
    data["players"] = len(roster)
    data["roster"] = roster

    if kbm_only:
        data["fields"] = [
            {"id": 62744, "value": ["Use GB Variant Gameplay"]},
            {"id": 62749, "value": ["Allowed"]},
            {"id": 62750, "value": ["Any"]},
        ]

    r = gb_session.post(
        "https://gb-api.majorleaguegaming.com/api/v1/challenges", json=data
    )
    logger.info(r.content)
    pprint(r.json())
    if r.status_code != 200:
        return None, [
            {
                "name": "**There has been an issue** :cry:",
                "value": "[Match finder.](https://gamebattles.majorleaguegaming.com/x-play/black-ops-cold-war/ladder/squads-eu/match-finder)",
            }
        ]

    return r.json()["body"]["id"], [
        {
            "name": "**Match posted** :clock230:",
            "value": "[Waiting to be accepted.](https://gamebattles.majorleaguegaming.com/x-play/black-ops-cold-war/ladder/squads-eu/match-finder)",
        }
    ]


def accept_match(roster, kbm_only=False):
    try:
        roster = convert_usernames_to_ids(roster)
    except KeyError:
        return [
            {
                "name": "**I can't find all of the usernames you entered** :cry:",
                "value": "[Match finder.](https://gamebattles.majorleaguegaming.com/x-play/black-ops-cold-war/ladder/squads-eu/match-finder)",
            }
        ]

    matches = find_matches(kbm_only=kbm_only, return_fields=False)
    matches = [match for match in matches if match["players"] == len(roster)]
    matches = sorted(matches, key=lambda x: x["disputePercentage"])
    if not matches:
        return [
            {
                "name": "**There aren't any suitable matches** :interrobang:",
                "value": "Type jeebee post <usernames> to put a match up",
            }
        ]
    match_id = matches[0]["id"]
    data = jeebee._payloads.ACCEPT_CHALLENGE_PAYLOAD
    data["roster"] = roster

    r = gb_session.put(
        f"https://gb-api.majorleaguegaming.com/api/v1/challenges/{match_id}/accept",
        json=data,
    )
    logger.info(r.content)
    if r.status_code != 200:
        pprint(f"Status code: {r.status_code}")
        pprint(r.content)
        return [
            {
                "name": "**There has been an issue** :cry:",
                "value": "[Match finder.](https://gamebattles.majorleaguegaming.com/x-play/black-ops-cold-war/ladder/squads-eu/match-finder)",
            }
        ]

    return [
        {
            "name": "**Match accepted** :mechanical_arm:",
            "value": "Type jeebee match to see match details",
        }
    ]


def report_last_match(win: bool):
    match = get_matches_from_gb(all_match_pages=False)[0]
    match_id = match["match"]["id"]
    r = gb_session.post(
        f"https://gb-api.majorleaguegaming.com/api/v1/matches/{match_id}/report",
        json={"reportTeamStatus": "WON" if win else "LOST"},
    )
    logger.info(f"Report status code: {r.status_code}")
    logger.info(pformat(r.content))
    return True if r.status_code == 200 else False


def cancel_match(match_id):
    r = gb_session.delete(
        f"https://gb-api.majorleaguegaming.com/api/v1/challenges/{match_id}"
    )
    logger.info(f"Report status code: {r.status_code}")
    return True if r.status_code == 204 else False


if __name__ == "__main__":
    post_match(["ntsfbrad"])
