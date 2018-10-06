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
GET_COUNTRY = "api/v1/countries/{countryCode}"  # ?language={language}"
GET_COMPETITIONS = (
    "api/v1/competitions?countryId={countryId}&count={count}&language={language}"
)
GET_SEASONS = (
    "api/v1/seasons?idCompetition={idCompetition}&count={count}&language={language}"
)


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

    resp = requests.get(url, headers=HEADERS, stream=True)
    resp.raise_for_status()

    with open(filename, "wb") as handle:
        for block in resp.iter_content(1024):
            handle.write(block)

    return openCachedFile(filename)


def listCountries():
    url = f"{BASE_URL}{GET_COUNTRIES}".format(count=COUNT, language=LANG)
    filename = "countries/list"
    return fetchList(url, filename)


def listCompetitions(country_id):
    url = f"{BASE_URL}{GET_COMPETITIONS}".format(
        count=COUNT, language=LANG, countryId=country_id
    )
    filename = f"competitions/{country_id}"
    return fetchList(url, filename)


def listSeasons(country_id, competition_id):
    url = f"{BASE_URL}{GET_SEASONS}".format(
        count=COUNT, language=LANG, idCompetition=competition_id
    )
    filename = f"competitions/{country_id}/{competition_id}"
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
def main():
    # info = listCountries()
    # pprintCountries(info)

    info = listCompetitions(COUNTRY)
    pprintCompetitions(info)

    # info = listCompetitions("SCO")
    # pprintCompetitions(info)

    info = listSeasons(COUNTRY, LEAGUE)
    pprintCompetitions(info)


if __name__ == "__main__":
    main()
