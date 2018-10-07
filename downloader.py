#!/usr/bin/env python
import logging
import errno
import json
import os
import sys
import requests

# import json


logging.basicConfig(
    stream=sys.stdout,
    format="%(asctime)s:%(levelname)s: %(message)s",
    level=os.environ.get("DEBUG_LEVEL") or logging.INFO,
)

log = logging.getLogger(__name__)  # pylint: disable=C0103

BALL = "\N{SOCCER BALL}"
SUB_IN = "\N{Up-Pointing Small Red Triangle}"
SUB_OUT = "\N{Down-Pointing Small Red Triangle}"

COUNT = 1000
LANG = "en-US"

COUNTRIES = ["SCO", "USA"]
ABERDEEN_ID = "31068"
SOUNDERS_ID = "2000000975"

HEADERS = {"Accept": "application/json"}

BASE_URL = "https://api.fifa.com/"

GET_COUNTRIES = "api/v1/countries?count={count}&language={language}"
GET_COUNTRY = "api/v1/countries/{countryCode}?language={language}"
GET_CONFEDERATIONS = "api/v1/confederations?language={language}"
GET_COMPETITIONS = (
    "api/v1/competitions?countryId={countryId}&count={count}&language={language}"
)
GET_SEASONS = (
    "api/v1/seasons?idCompetition={idCompetition}&count={count}&language={language}"
)
GET_STAGES = "api/v1/stages?idCompetition={idCompetition}&idSeason={idSeason}&count={count}&language={language}"
# GET_MATCHES = "api/v1/calendar/matches?idSeason={idSeason}&idCompetition={idCompetition}&idStage={idStage}&language={language}&count={count}"
# &idGroup={idGroup}&idTeam={idTeam}
GET_MATCHES = "api/v1/calendar/matches?idSeason={idSeason}&idCompetition={idCompetition}&language={language}&count={count}"

# GET_TIMELINE = "api/v1/timelines/{idCompetition}/{idSeason}/{idStage}/{idMatch}/{idGroup}?language={language}&scope={scope}"
GET_TIMELINE = "api/v1/timelines/{idCompetition}/{idSeason}/{idStage}/{idMatch}/?language={language}"

GET_PLAYER = "api/v1/players/{idPlayer}?language={language}"

GET_TEAM = "api/v1/teams/{idTeam}?language={language}"

EVENT_PERIODS = {
    0: "Unknown",  # Unknown event period.
    1: "Scheduled",  # Scheduled event period.
    2: "PreMatch",  # PreMatch event period.
    3: "First_Half",  # First half event period.
    4: "Half_Time",  # Half time event period.
    5: "Second_Half",  # Second half event period.
    6: "Extra_Time",  # Extra time event period.
    7: "Extra_First_Half",  # Extra first half event period.
    8: "Extra_Half_Time",  # Extra half time event period.
    9: "Extra_Second_Half",  # Extra second half event period.
    10: "Full_Time",  # Full time event period.
    11: "Penalty_Shootout",  # Penalty shootout event period.
    12: "PostMatch",  # Post match event period.
    13: "Abandoned",  # Abandoned event period.
    14: "Third_Half",  # Third Half event period (beach soccer).
}
EVENT_PERIODS_MAP = {v: k for k, v in EVENT_PERIODS.items()}

EVENT_TYPES = {
    0: "Goal",  # Goal type.
    1: "Assist",  # Assist type.
    2: "YellowCard",  # Yellow card type.
    3: "RedCard",  # Red card type.
    4: "Red2Yellow",  # Red to yellow card type.
    5: "Substitution",  # Substitution type.
    6: "Penalty",  # Penalty type.
    7: "StartTime",  # Start time type.
    8: "EndTime",  # End time type.
    9: "PauseTime",  # Pause time type.
    10: "ResumeTime",  # Resume time type.
    11: "Suspension",  # Suspension type.
    12: "Shot",  # Shot type.
    13: "BigChance",  # Big chance type.
    14: "FreeKick",  # Free kick type.
    15: "Offside",  # Offside type.
    16: "Corner",  # Corner type.
    17: "Save",  # Save type.
    18: "Foul",  # Foul type.
    19: "TossCoin",  # Toss coin type.
    20: "Dribbling",  # Dribbling type.
    21: "Skill",  # Skill type.
    22: "Tackle",  # Tackle type.
    23: "DroppedBall",  # Dropped ball type.
    24: "ThrowIn",  # Throw in type.
    25: "Clearance",  # Clearance type.
    26: "EndMatch",  # End match type.
    27: "AerialDuel",  # Aerial duel type.
    28: "BallOut",  # Ball out type.
    29: "Punch",  # Punch type.
    30: "Claim",  # Claim type.
    31: "TimeOut",  # Time out type.
    32: "HitBar",  # Hit bar type.
    33: "HitPost",  # Hit post type.
    34: "OwnGoal",  # Own goal type.
    35: "PenaltyShootOut",  # Penalty shoot out type.
    36: "SecondPenalty",  # Second penalty type.
    37: "HandBall",  # HandBall
    71: "VarNotification",  # VarNotification
    72: "FoulCausingPenalty",  # FoulCausingPenalty
    9999: "Unknown",  # Unknown type.
    38: "Simulation",  # Foul Simulation
    39: "GoalFromFreeKick",  # GoalFromFreeKick
    40: "GoalFromIndirectKick",  # GoalFromIndirectKick
    41: "GoalFromPenalty",  # GoalFromPenalty
    42: "GoalFromSecondPenalty",  # GoalFromSecondPenalty
    43: "GoalOverhead",  # GoalOverhead
    44: "HitBarFromFreeKick",  # HitBarFromFreeKick
    45: "HitBarFromIndirectKick",  # HitBarFromIndirectKick
    46: "HitBarFromPenalty",  # HitBarFromPenalty
    47: "HitBarFromSecondPenalty",  # HitBarFromSecondPenalty
    48: "HitBarOverhead",  # HitBarOverhead
    49: "HitPostFromFreeKick",  # HitPostFromFreeKick
    50: "HitPostFromIndirectKick",  # HitPostFromIndirectKick
    51: "HitPostFromPenalty",  # HitPostFromPenalty
    52: "HitPostFromSecondPenalty",  # HitPostFromSecondPenalty
    53: "HitPostOverhead",  # HitPostOverhead
    54: "ShotFromIndirectKick",  # ShotFromIndirectKick
    55: "ShotFromPenalty",  # ShotFromPenalty
    56: "ShotOverhead",  # ShotOverhead
    57: "SaveByGoalKeeper",  # SaveByGoalKeeper
    58: "SaveFromFreeKick",  # SaveFromFreeKick
    59: "SaveFromIndirectKick",  # SaveFromIndirectKick
    60: "SaveFromPenalty",  # SaveFromPenalty
    61: "SaveFromSecondPenalty",  # SaveFromSecondPenalty
    62: "SaveOverhead",  # SaveOverhead
    63: "BallOutFromFreeKick",  # BallOutFromFreeKick
    64: "BallOutFromIndirectKick",  # BallOutFromIndirectKick
    65: "BallOutFromPenalty",  # BallOutFromPenalty
    66: "BallOutFromSecondPenalty",  # BallOutFromSecondPenalty
    67: "BallOutOverhead",  # BallOutOverhead
    68: "EndTimeWithExtra",  # EndTimeWithExtra
    69: "EndTimeWithPSO",  # EndTimeWithPSO
    70: "StartMatch",  # StartMatch
}
EVENT_TYPES_MAP = {v: k for k, v in EVENT_TYPES.items()}


def soccer(func):
    def handler(*args, **kwargs):
        print(BALL)
        ret = func(*args, **kwargs)
        print(BALL)
        return ret

    return handler


def openCachedFile(filename):
    results = None
    with open(filename, "rb") as handle:
        resp = json.load(handle)
        results = resp["Results"] if "Results" in resp else resp
    return results


def fetchList(url, filename):

    filename = f"data/{filename}.json"
    dirname = os.path.dirname(filename)
    if os.path.exists(filename):
        return openCachedFile(filename)

    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    logging.info("GET %s", url)
    resp = requests.get(url, headers=HEADERS, stream=True)
    resp.raise_for_status()

    with open(filename, "wb") as handle:
        for block in resp.iter_content(1024):
            handle.write(block)

    return openCachedFile(filename)


def listConfederations():
    url = f"{BASE_URL}{GET_CONFEDERATIONS}".format(language=LANG)
    filename = "confederations"
    return fetchList(url, filename)


def listCountries():
    url = f"{BASE_URL}{GET_COUNTRIES}".format(count=COUNT, language=LANG)
    filename = "countries"
    return fetchList(url, filename)


def listCompetitions(country_id):
    url = f"{BASE_URL}{GET_COMPETITIONS}".format(
        count=COUNT, language=LANG, countryId=country_id
    )
    filename = f"countries/{country_id}/competitions"
    return fetchList(url, filename)


def listSeasons(country_id, competition_id):
    url = f"{BASE_URL}{GET_SEASONS}".format(
        count=COUNT, language=LANG, idCompetition=competition_id
    )
    filename = f"countries/{country_id}/competitions/{competition_id}"
    return fetchList(url, filename)


def listStages(country_id, competition_id, season_id):
    url = f"{BASE_URL}{GET_STAGES}".format(
        count=COUNT, language=LANG, idCompetition=competition_id, idSeason=season_id
    )
    filename = f"countries/{country_id}/competitions/{competition_id}/seasons/{season_id}/stages"
    return fetchList(url, filename)


def listStageMatches(country_id, competition_id, season_id, stage_id):
    url = f"{BASE_URL}{GET_MATCHES}".format(
        count=COUNT, language=LANG, idCompetition=competition_id, idSeason=season_id
    )
    filename = f"countries/{country_id}/competitions/{competition_id}/seasons/{season_id}/stages/{stage_id}/matches"
    return fetchList(url, filename)


def listMatches(country_id, competition_id, season_id):
    url = f"{BASE_URL}{GET_MATCHES}".format(
        count=COUNT, language=LANG, idCompetition=competition_id, idSeason=season_id
    )
    filename = f"countries/{country_id}/competitions/{competition_id}/seasons/{season_id}/matches"
    return fetchList(url, filename)


def getTimeline(country_id, competition_id, season_id, stage_id, match_id):
    url = f"{BASE_URL}{GET_TIMELINE}".format(
        count=COUNT,
        language=LANG,
        idCompetition=competition_id,
        idSeason=season_id,
        idStage=stage_id,
        idMatch=match_id,
    )
    filename = f"countries/{country_id}/competitions/{competition_id}/seasons/{season_id}/matches/{match_id}"
    return fetchList(url, filename)


def getPlayer(player_id):
    url = f"{BASE_URL}{GET_PLAYER}".format(language=LANG, idPlayer=player_id)
    filename = f"players/{player_id}"
    return fetchList(url, filename)


def getTeam(team_id):
    url = f"{BASE_URL}{GET_TEAM}".format(language=LANG, idTeam=team_id)
    filename = f"teams/{team_id}"
    return fetchList(url, filename)


@soccer
def pprintCountries(info):
    for comp in info:
        print(f"{BALL}\t{comp['IdCountry']}\t{comp['Name']}")


@soccer
def pprintCompetitions(info):
    for comp in info:
        print(f"{BALL}\t{comp['IdCompetition']}\t{comp['Name'][0]['Description']}")


@soccer
def pprintSeason(info):
    for comp in info:
        print(f"{BALL}\t{comp['IdSeason']}\t{comp['Name'][0]['Description']}")


@soccer
def pprintMatches(matches):
    for match in matches:
        print(
            f"{BALL}\t{match['IdMatch']}\t{match['Date']}\t{match['PlaceHolderA']} {match['HomeTeamScore']} - {match['AwayTeamScore']} {match['PlaceHolderB']}"
        )


@soccer
def pprintTimeline(timeline):
    for event in timeline["Event"]:
        if event["Type"] == EVENT_TYPES_MAP["Goal"]:
            player = getPlayer(event["IdPlayer"])
            team = getTeam(event["IdTeam"])
            print(
                f"{event['MatchMinute']}: {BALL} - {player['Name'][0]['Description']} [{team['Name'][0]['Description']}]"
            )
        elif event["Type"] == EVENT_TYPES_MAP["GoalFromPenalty"]:
            player = getPlayer(event["IdPlayer"])
            team = getTeam(event["IdTeam"])
            print(
                f"{event['MatchMinute']}: \N{GOAL NET}{BALL} - {player['Name'][0]['Description']} [{team['Name'][0]['Description']}]"
            )
        elif event["Type"] == EVENT_TYPES_MAP["OwnGoal"]:
            player = getPlayer(event["IdPlayer"])
            team = getTeam(event["IdTeam"])
            print(
                f"{event['MatchMinute']}: \N{Face Palm} - {player['Name'][0]['Description']} [{team['Name'][0]['Description']}]"
            )
        elif event["Type"] == EVENT_TYPES_MAP["YellowCard"]:
            player = getPlayer(event["IdPlayer"])
            team = getTeam(event["IdTeam"])
            print(
                f"{event['MatchMinute']}: \N{LEDGER} - {player['Name'][0]['Description']} [{team['Name'][0]['Description']}]"
            )
        elif event["Type"] == EVENT_TYPES_MAP["RedCard"]:
            player = getPlayer(event["IdPlayer"])
            team = getTeam(event["IdTeam"])
            print(
                f"{event['MatchMinute']}: \N{LARGE RED CIRCLE} - {player['Name'][0]['Description']} [{team['Name'][0]['Description']}]"
            )
        elif event["Type"] == EVENT_TYPES_MAP["Red2Yellow"]:
            player = getPlayer(event["IdPlayer"])
            team = getTeam(event["IdTeam"])
            print(
                f"{event['MatchMinute']}: \N{LEDGER}\N{LEDGER}\N{LARGE RED CIRCLE} - {player['Name'][0]['Description']} [{team['Name'][0]['Description']}]"
            )
        elif event["Type"] == EVENT_TYPES_MAP["Substitution"]:
            player = getPlayer(event["IdPlayer"])
            team = getTeam(event["IdTeam"])
            subPlayer = (
                getPlayer(event["IdSubPlayer"])
                if event["IdSubPlayer"]
                else {"Name": [{"Description": "???"}]}
            )
            print(
                f"{event['MatchMinute']}: Sub - {SUB_IN} {player['Name'][0]['Description']} \N{Left Right Arrow} {SUB_OUT} {subPlayer['Name'][0]['Description']} [{team['Name'][0]['Description']}]"
            )
        elif event["Type"] != EVENT_TYPES_MAP["Unknown"]:
            print(
                f"{event['MatchMinute']} - \N{STOPWATCH} {EVENT_TYPES[event['Type']]}"
            )


@soccer
def pprintList(info, id_tag):
    for comp in info:
        print(f"{BALL}\t{comp[id_tag]}\t{comp}")


@soccer
def main():
    # confeds = listConfederations()

    countries = listCountries()
    # pprintCountries(countries)

    for country in countries:
        country_id = country["IdCountry"]
        country_name = country["Name"]
        if country_id not in COUNTRIES:
            continue

        print(f"{BALL}\t{country_id}\t{country_name}")

        comps = listCompetitions(country_id)
        for comp in comps:
            comp_id = comp["IdCompetition"]
            comp_name = comp["Name"][0]["Description"]
            print(f"{BALL}\t{comp_id}\t{comp_name}")

            seasons = listSeasons(country_id, comp_id)
            for season in seasons:
                season_id = season["IdSeason"]
                season_name = season["Name"][0]["Description"]
                print(f"{BALL}\t{season_id}\t{season_name}")

                _ = listStages(country_id, comp_id, season_id)
                # for stage in stages:
                #     stage_id = stage["IdStage"]
                #     stage_name = stage["Name"][0]["Description"]
                #     print(f"{BALL}\t{stage_id}\t{stage_name}\t{stage['StageLevel']}\t{stage['StartDate']} - {stage['EndDate']}")

                matches = listMatches(country_id, comp_id, season_id)
                # pprintMatches(matches)

                for match in matches:
                    if match["HomeTeamScore"] is None:
                        continue
                    if match["Home"]["IdTeam"] not in [
                        ABERDEEN_ID,
                        SOUNDERS_ID,
                    ] and match["Away"]["IdTeam"] not in [ABERDEEN_ID, SOUNDERS_ID]:
                        continue

                    print(
                        f"{match['IdMatch']}\t{match['Date']}\t{match['PlaceHolderA'] or match['Home']['TeamName'][0]['Description']} {BALL * match['HomeTeamScore'] or 0} - {BALL * match['AwayTeamScore'] or 0} {match['PlaceHolderB'] or match['Away']['TeamName'][0]['Description']}"
                    )
                    match_id = match["IdMatch"]
                    stage_id = match["IdStage"]
                    timeline = getTimeline(
                        country_id, comp_id, season_id, stage_id, match_id
                    )
                    pprintTimeline(timeline)

    # info = listCompetitions("SCO")
    # pprintCompetitions(info)

    # info = listSeasons(COUNTRY, LEAGUE)
    # pprintList(info)


if __name__ == "__main__":
    main()
