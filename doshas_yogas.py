"""
Mangal Dosha (Manglik) and Yoga detection.

Uses whole-sign houses computed from the same validated ephemeris pipeline
as everything else in this project.
"""

RASHIS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
          "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

KENDRAS = {1, 4, 7, 10}      # angular houses
TRIKONAS = {1, 5, 9}         # trinal houses
MANGLIK_HOUSES = {1, 2, 4, 7, 8, 12}

EXALTATION = {"Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn", "Mercury": "Virgo",
              "Jupiter": "Cancer", "Venus": "Pisces", "Saturn": "Libra"}
DEBILITATION = {"Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer", "Mercury": "Pisces",
                "Jupiter": "Capricorn", "Venus": "Virgo", "Saturn": "Aries"}
OWN_SIGNS = {"Sun": ["Leo"], "Moon": ["Cancer"], "Mars": ["Aries", "Scorpio"],
             "Mercury": ["Gemini", "Virgo"], "Jupiter": ["Sagittarius", "Pisces"],
             "Venus": ["Taurus", "Libra"], "Saturn": ["Capricorn", "Aquarius"]}

RASHI_LORDS = {"Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
               "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
               "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"}


def house_of(rashi, lagna_rashi):
    return ((RASHIS.index(rashi) - RASHIS.index(lagna_rashi) + 12) % 12) + 1


def rashi_of(longitude):
    return RASHIS[int((longitude % 360) // 30)]


def lord_of_house(house_num, lagna_rashi):
    """Which planet rules the sign that falls in this house (whole-sign)."""
    sign_idx = (RASHIS.index(lagna_rashi) + house_num - 1) % 12
    return RASHI_LORDS[RASHIS[sign_idx]]


# ---------------- Mangal Dosha ----------------

def check_mangal_dosha(planet_rashis: dict, lagna_rashi: str):
    """
    Checks Mars's house from Lagna, Moon, and Venus -- classical texts
    differ on which reference point(s) matter, so all three are reported.
    """
    mars_rashi = planet_rashis["Mars"]
    mars_house_from_lagna = house_of(mars_rashi, lagna_rashi)
    mars_house_from_moon = house_of(mars_rashi, planet_rashis["Moon"])
    mars_house_from_venus = house_of(mars_rashi, planet_rashis["Venus"])

    from_lagna = mars_house_from_lagna in MANGLIK_HOUSES
    from_moon = mars_house_from_moon in MANGLIK_HOUSES
    from_venus = mars_house_from_venus in MANGLIK_HOUSES

    # Classical cancellation: Mars in own sign or exaltation sign reduces/cancels the dosha
    mars_dignity = None
    if mars_rashi in OWN_SIGNS["Mars"]:
        mars_dignity = "own sign"
    elif mars_rashi == EXALTATION["Mars"]:
        mars_dignity = "exalted"

    return {
        "mars_rashi": mars_rashi,
        "house_from_lagna": mars_house_from_lagna,
        "house_from_moon": mars_house_from_moon,
        "house_from_venus": mars_house_from_venus,
        "manglik_from_lagna": from_lagna,
        "manglik_from_moon": from_moon,
        "manglik_from_venus": from_venus,
        "is_manglik": from_lagna or from_moon or from_venus,
        "mars_dignity": mars_dignity,
        "cancellation_note": (
            f"Mars is {mars_dignity} in this chart, which classically reduces or "
            f"cancels the dosha's severity." if mars_dignity else None
        ),
    }


# ---------------- Yogas ----------------

def check_gaja_kesari(planet_rashis, lagna_rashi):
    """Jupiter in a kendra (1,4,7,10) from Moon."""
    jup_house_from_moon = house_of(planet_rashis["Jupiter"], planet_rashis["Moon"])
    present = jup_house_from_moon in KENDRAS
    return {"name": "Gaja Kesari Yoga", "present": present,
            "description": "Jupiter in a kendra from the Moon — fame, wisdom, respect.",
            "detail": f"Jupiter is house {jup_house_from_moon} from Moon."}


def check_chandra_mangal(planet_rashis):
    """Moon and Mars conjunct (same sign)."""
    present = planet_rashis["Moon"] == planet_rashis["Mars"]
    return {"name": "Chandra-Mangal Yoga", "present": present,
            "description": "Moon and Mars conjunct — wealth-generating drive and ambition.",
            "detail": f"Moon in {planet_rashis['Moon']}, Mars in {planet_rashis['Mars']}."}


def check_budhaditya(planet_rashis):
    """Sun and Mercury conjunct."""
    present = planet_rashis["Sun"] == planet_rashis["Mercury"]
    return {"name": "Budhaditya Yoga", "present": present,
            "description": "Sun and Mercury conjunct — sharp intellect, communication skill.",
            "detail": f"Sun in {planet_rashis['Sun']}, Mercury in {planet_rashis['Mercury']}."}


def check_kemadruma(planet_rashis, lagna_rashi):
    """Moon with no planets in the houses immediately before/after it (2nd/12th from Moon), and no kendra planets -- a dosha, not a yoga."""
    moon_house = house_of(planet_rashis["Moon"], lagna_rashi)
    adjacent_houses = {((moon_house - 2) % 12) + 1, (moon_house % 12) + 1}  # 12th and 2nd from Moon
    other_planets = {k: v for k, v in planet_rashis.items() if k != "Moon"}
    occupied_houses = {house_of(rashi, lagna_rashi) for rashi in other_planets.values()}
    isolated = len(adjacent_houses & occupied_houses) == 0
    return {"name": "Kemadruma Yoga (dosha)", "present": isolated,
            "description": "Moon isolated with no planets adjacent — can indicate emotional struggle; cancelled if any planet is in a kendra from Moon or Lagna.",
            "detail": f"Moon in house {moon_house}; adjacent houses {sorted(adjacent_houses)} occupied: {not isolated}."}


def check_pancha_mahapurusha(planet_rashis, lagna_rashi):
    """
    Five great-person yogas: Mars(Ruchaka), Mercury(Bhadra), Jupiter(Hamsa),
    Venus(Malavya), Saturn(Sasa) -- each in own sign or exaltation, in a kendra.
    """
    yoga_names = {"Mars": "Ruchaka Yoga", "Mercury": "Bhadra Yoga", "Jupiter": "Hamsa Yoga",
                  "Venus": "Malavya Yoga", "Saturn": "Sasa Yoga"}
    results = []
    for planet, yoga_name in yoga_names.items():
        rashi = planet_rashis[planet]
        house = house_of(rashi, lagna_rashi)
        in_kendra = house in KENDRAS
        in_dignity = rashi in OWN_SIGNS.get(planet, []) or rashi == EXALTATION.get(planet)
        present = in_kendra and in_dignity
        results.append({
            "name": yoga_name, "present": present,
            "description": f"{planet} in own/exaltation sign in a kendra house — a Pancha Mahapurusha yoga.",
            "detail": f"{planet} in {rashi} (house {house}); dignity: {'yes' if in_dignity else 'no'}, kendra: {'yes' if in_kendra else 'no'}.",
        })
    return results


def check_neechabhanga(planet_rashis, lagna_rashi):
    """
    Simplified Neechabhanga (debilitation cancellation) check: a planet is
    debilitated, but the lord of its debilitation sign is in a kendra from
    Lagna or Moon -- one of several classical cancellation rules.
    """
    results = []
    for planet, deb_sign in DEBILITATION.items():
        if planet_rashis.get(planet) != deb_sign:
            continue
        deb_lord = RASHI_LORDS[deb_sign]
        if deb_lord not in planet_rashis:
            continue
        deb_lord_house_lagna = house_of(planet_rashis[deb_lord], lagna_rashi)
        deb_lord_house_moon = house_of(planet_rashis[deb_lord], planet_rashis["Moon"])
        cancelled = deb_lord_house_lagna in KENDRAS or deb_lord_house_moon in KENDRAS
        results.append({
            "name": f"Neechabhanga Raja Yoga ({planet})", "present": cancelled,
            "description": f"{planet} is debilitated in {deb_sign}, but its dispositor {deb_lord}'s kendra placement cancels the debilitation, converting it to a Raja Yoga.",
            "detail": f"{deb_lord} (lord of {deb_sign}) is house {deb_lord_house_lagna} from Lagna, house {deb_lord_house_moon} from Moon.",
        })
    return results


def check_dhana_yoga(planet_rashis, lagna_rashi):
    """
    Simplified Dhana Yoga: 2nd lord and 11th lord (both wealth houses)
    conjunct, or mutually aspecting by conjunction (same sign) with each other
    or with the 9th lord (fortune).
    """
    lord_2 = lord_of_house(2, lagna_rashi)
    lord_11 = lord_of_house(11, lagna_rashi)
    lord_9 = lord_of_house(9, lagna_rashi)

    results = []
    pairs = [("2nd & 11th lords", lord_2, lord_11), ("2nd & 9th lords", lord_2, lord_9), ("9th & 11th lords", lord_9, lord_11)]
    for label, p1, p2 in pairs:
        if p1 in planet_rashis and p2 in planet_rashis:
            conjunct = planet_rashis[p1] == planet_rashis[p2]
            results.append({
                "name": f"Dhana Yoga ({label})", "present": conjunct,
                "description": "Wealth-house lords conjunct — indicates financial gain.",
                "detail": f"{p1} in {planet_rashis.get(p1)}, {p2} in {planet_rashis.get(p2)}.",
            })
    return results


def check_raja_yoga(planet_rashis, lagna_rashi):
    """
    Simplified Raja Yoga: a kendra lord (1,4,7,10) conjunct a trikona lord
    (1,5,9) -- one of the most classic power/status combinations.
    """
    kendra_lords = {lord_of_house(h, lagna_rashi) for h in KENDRAS}
    trikona_lords = {lord_of_house(h, lagna_rashi) for h in TRIKONAS}

    results = []
    checked_pairs = set()
    for kl in kendra_lords:
        for tl in trikona_lords:
            if kl == tl or (kl, tl) in checked_pairs or (tl, kl) in checked_pairs:
                continue
            checked_pairs.add((kl, tl))
            if kl in planet_rashis and tl in planet_rashis:
                conjunct = planet_rashis[kl] == planet_rashis[tl]
                if conjunct:
                    results.append({
                        "name": f"Raja Yoga ({kl} + {tl})", "present": True,
                        "description": "Kendra lord conjunct trikona lord — a classic power/status yoga.",
                        "detail": f"{kl} and {tl} both in {planet_rashis[kl]}.",
                    })
    return results


def full_dosha_yoga_report(planet_rashis: dict, lagna_rashi: str):
    """
    planet_rashis: {"Sun": "Cancer", "Moon": "Libra", ...} -- D1 rashis only.
    Returns Mangal Dosha + all yoga checks.
    """
    yogas = []
    yogas.append(check_gaja_kesari(planet_rashis, lagna_rashi))
    yogas.append(check_chandra_mangal(planet_rashis))
    yogas.append(check_budhaditya(planet_rashis))
    yogas.append(check_kemadruma(planet_rashis, lagna_rashi))
    yogas.extend(check_pancha_mahapurusha(planet_rashis, lagna_rashi))
    yogas.extend(check_neechabhanga(planet_rashis, lagna_rashi))
    yogas.extend(check_dhana_yoga(planet_rashis, lagna_rashi))
    yogas.extend(check_raja_yoga(planet_rashis, lagna_rashi))

    return {
        "mangal_dosha": check_mangal_dosha(planet_rashis, lagna_rashi),
        "yogas": yogas,
        "yogas_present": [y for y in yogas if y["present"]],
    }


if __name__ == "__main__":
    from datetime import datetime
    import sys
    sys.path.insert(0, '.')
    from ephemeris import get_all_planets
    from divisional_charts import RASHIS as R2

    birth = datetime(1996, 7, 25, 0, 0)
    planets = get_all_planets(birth, utc_offset_hours=5.5, lat=23.5158, lon=87.308)
    lagna_lon = planets.pop("Lagna")
    lagna_rashi = R2[int(lagna_lon // 30)]

    planet_rashis = {name: R2[int(lon // 30)] for name, lon in planets.items()}

    print(f"Lagna: {lagna_rashi}")
    print(f"Planets: {planet_rashis}")
    print()

    report = full_dosha_yoga_report(planet_rashis, lagna_rashi)
    print("=== Mangal Dosha ===")
    for k, v in report["mangal_dosha"].items():
        print(f"  {k}: {v}")

    print()
    print("=== Yogas present ===")
    for y in report["yogas_present"]:
        print(f"  {y['name']}: {y['detail']}")

    print()
    print(f"Total yogas checked: {len(report['yogas'])}, present: {len(report['yogas_present'])}")
