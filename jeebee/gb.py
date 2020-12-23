import datetime
import os
from typing import Optional

import dotenv
import requests

import jeebee.constants

dotenv.load_dotenv()
GB_TEAM_ID = int(os.getenv("GB_TEAM_ID"))


def get_matches_from_gb(all_match_pages: Optional[bool] = True):
    """Get matches for the GameBattles team with id GB_TEAM_ID."""
    r = requests.get(
        jeebee.constants.GB_MATCHES_URL.format(team_id=GB_TEAM_ID, page_number=1)
    )
    matches = r.json()["body"]["records"]

    if all_match_pages:
        for page_number in range(2, r.json()["body"]["totalPages"]):
            r = requests.get(
                jeebee.constants.GB_MATCHES_URL.format(
                    team_id=GB_TEAM_ID, page_number=page_number
                )
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

    wins_and_rosters = []
    for match in matches:
        try:
            details = (
                "homeTeamDetails"
                if match["match"]["homeTeamId"] == GB_TEAM_ID
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
            if match.get("winningTeamId", 0) == GB_TEAM_ID:
                wins += 1
        else:
            roster = [x[-1] for x in get_match_info(match)["we_rush_a_roster"]]
            if player in roster:
                match_num += 1
                if match.get("winningTeamId", 0) == GB_TEAM_ID:
                    wins += 1

    return (wins / match_num) * 100


def get_match_details(match_id: int):
    """Get the raw JSON match details from GameBattles."""
    match_details = requests.get(
        jeebee.constants.GB_MATCH_DETAILS_URL.format(match_id=match_id)
    )
    return match_details.json()["body"]


def get_current_active_match():
    """Get the current active match from GameBattles."""
    current_match = get_matches_from_gb(all_match_pages=False)[0]

    if current_match["match"]["status"] == "COMPLETED":
        return [
            {
                "name": "**Next match** :video_game:",
                "value": "[No pending matches.](https://gamebattles.majorleaguegaming.com/x-play/black-ops-cold-war/ladder/squads-eu/match-finder)",
            }
        ]

    if current_match["match"]["status"] == "ACTIVE":
        match_info = get_match_info(current_match)

        fields = [
            {
                "name": "**Next match** :video_game:",
                "value": f"[**{match_info['match_time']}**](https://gamebattles.majorleaguegaming.com/x-play/black-ops-cold-war/team/{GB_TEAM_ID}/match/{match_info['match_id']})",
            },
            {
                "name": "**Opposition** :right_facing_fist:",
                "value": f"[**{match_info['oppostion_team_name']}**](https://gamebattles.majorleaguegaming.com/x-play/black-ops-cold-war/team/{match_info['oppostion_team_id']})\nRank: {match_info['opposition_rank']:,}\nCurrent streak: {match_info['opposition_streak']} :fire:",
            },
            {"name": "**Maps** :map:", "value": f"{match_info['maps']}"},
            {
                "name": "**Roster**",
                "value": "\n".join(p[0] for p in match_info["opposition_team_roster"]),
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
            "value": f"[**{match_info['match_time']}**](https://gamebattles.majorleaguegaming.com/x-play/black-ops-cold-war/team/{GB_TEAM_ID}/match/{match_info['match_id']})",
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
        "home" if match["match"]["homeTeamId"] != GB_TEAM_ID else "visitor"
    )
    we_rush_a_home_or_visitor = (
        "home" if match["match"]["homeTeamId"] == GB_TEAM_ID else "visitor"
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

    d["won"] = match_details.get("results", dict()).get("winningTeamId") == GB_TEAM_ID

    return d


def find_matches(all_matches=False, kbm_only=True):
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
            "name": "**Available matches** :palm_tree:",
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
