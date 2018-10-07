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

COUNT = 1000
LANG = "en-US"

COUNTRY = "USA"
LEAGUE = "2000000103"  # SCO prem = 2000000001

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


def soccer(func):
    def handler(*args, **kwargs):
        print("\N{SOCCER BALL}")
        ret = func(*args, **kwargs)
        print("\N{SOCCER BALL}")
        return ret

    return handler


def openCachedFile(filename):
    results = None
    with open(filename, "rb") as handle:
        resp = json.load(handle)
        results = resp["Results"]
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


@soccer
def pprintCountries(info):
    for comp in info:
        print(f"\N{SOCCER BALL}\t{comp['IdCountry']}\t{comp['Name']}")


@soccer
def pprintCompetitions(info):
    for comp in info:
        print(
            f"\N{SOCCER BALL}\t{comp['IdCompetition']}\t{comp['Name'][0]['Description']}"
        )


@soccer
def pprintSeason(info):
    for comp in info:
        print(f"\N{SOCCER BALL}\t{comp['IdSeason']}\t{comp['Name'][0]['Description']}")


@soccer
def pprintMatches(matches):
    for match in matches:
        print(
            f"\N{SOCCER BALL}\t{match['IdMatch']}\t{match['Date']}\t{match['PlaceHolderA']} {match['HomeTeamScore']} - {match['AwayTeamScore']} {match['PlaceHolderB']}"
        )


@soccer
def pprintList(info, id_tag):
    for comp in info:
        print(f"\N{SOCCER BALL}\t{comp[id_tag]}\t{comp}")


@soccer
def main():
    # confeds = listConfederations()

    countries = listCountries()
    # pprintCountries(countries)

    for country in countries:
        country_id = country["IdCountry"]
        country_name = country["Name"]
        if country_id not in ["SCO", "USA"]:
            continue

        print(f"\N{SOCCER BALL}\t{country_id}\t{country_name}")

        comps = listCompetitions(country_id)
        for comp in comps:
            comp_id = comp["IdCompetition"]
            comp_name = comp["Name"][0]["Description"]
            print(f"\N{SOCCER BALL}\t{comp_id}\t{comp_name}")

            seasons = listSeasons(country_id, comp_id)
            for season in seasons:
                season_id = season["IdSeason"]
                season_name = season["Name"][0]["Description"]
                print(f"\N{SOCCER BALL}\t{season_id}\t{season_name}")

                stages = listStages(country_id, comp_id, season_id)
                # for stage in stages:
                #     stage_id = stage["IdStage"]
                #     stage_name = stage["Name"][0]["Description"]
                #     print(f"\N{SOCCER BALL}\t{stage_id}\t{stage_name}\t{stage['StageLevel']}\t{stage['StartDate']} - {stage['EndDate']}")

                matches = listMatches(country_id, comp_id, season_id)
                pprintMatches(matches)

    # info = listCompetitions("SCO")
    # pprintCompetitions(info)

    # info = listSeasons(COUNTRY, LEAGUE)
    # pprintList(info)


if __name__ == "__main__":
    main()
