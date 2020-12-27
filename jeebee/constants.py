import os

import dotenv

dotenv.load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

USERNAME = os.getenv("MLG_USERNAME")
PASSWORD = os.getenv("MLG_PASSWORD")

if os.getenv("ENV") == "production":
    GB_TEAM_ID = 35017683
elif os.getenv("ENV") == "development":
    GB_TEAM_ID = 35286312

# GB_CONSTANTS
GB_MATCHES_URL = "https://gb-api.majorleaguegaming.com/api/web/v1/team-matches-screen/team/{team_id}?pageSize=10&pageNumber={{page_number}}".format(
    team_id=GB_TEAM_ID
)
GB_MATCH_DETAILS_URL = (
    "https://gb-api.majorleaguegaming.com/api/web/v1/match-screen/{match_id}"
)
GB_MATCH_FINDER_URL = "https://gb-api.majorleaguegaming.com/api/v2/challenges/ladder/2492?pageSize=25&page=1"
GB_MATCH_FINDER_DETAILS_URL = (
    "https://gb-api.majorleaguegaming.com/api/v1/challenges/{match_id}/fields/public"
)
GB_TEAM_MEMBERS_URL = (
    "https://gb-api.majorleaguegaming.com/api/v1/teams/{team_id}/members".format(
        team_id=GB_TEAM_ID
    )
)
