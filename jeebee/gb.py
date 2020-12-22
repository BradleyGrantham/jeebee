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

    if not all_match_pages:
        return matches

    for page_number in range(2, r.json()["body"]["totalPages"]):
        r = requests.get(
            jeebee.constants.GB_MATCHES_URL.format(
                team_id=GB_TEAM_ID, page_number=page_number
            )
        )
        matches += r.json()["body"]["records"]
    return matches


def get_win_percentage(n: Optional[int] = None):
    """Get the win percentage over the last n games (all games if n is None)."""
    matches = get_matches_from_gb()
    print(len(matches))
    if n is not None:
        matches = matches[:n]

    wins = 0
    for match in matches:
        if match.get("winningTeamId", 0) == GB_TEAM_ID:
            wins += 1

    return (wins / len(matches)) * 100


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
            "value": "\n".join(f"[{p[0]}](http://profile.majorleaguegaming.com/{p[2]})" for p in match_info["opposition_team_roster"]),
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

    home_or_visitor = (
        "home" if match["match"]["homeTeamId"] != GB_TEAM_ID else "visitor"
    )
    d["oppostion_team_id"] = match["match"][f"{home_or_visitor}TeamId"]
    d["oppostion_team_name"] = match[f"{home_or_visitor}TeamCard"]["name"]

    match_details = get_match_details(d["match_id"])
    d["opposition_team_roster"] = [
        (p["guid"], f"{p['rank']['rank']:,}", p["matchPlayer"]["username"])
        for p in match_details["visitorTeamDetails"]["roster"]
    ]
    d["maps"] = "\n".join([map["map"]["title"] for map in match_details["mapModes"]])
    d["opposition_rank"] = match_details["visitorTeamDetails"]["teamStanding"]["rank"]
    d["opposition_streak"] = match_details["visitorTeamDetails"]["teamStanding"][
        "streak"
    ]["current"]

    d["won"] = match_details.get("results", dict()).get("winningTeamId") == GB_TEAM_ID

    return d
