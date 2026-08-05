"""
Remedies — gemstones, mantras, and simple practices tied to the actual chart:
weak/afflicted planets, the Lagna lord's condition, and any Mangal Dosha found.

This is presented as traditional guidance, not medical/financial advice.
"""

RASHIS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
          "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

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

GEMSTONES = {
    "Sun": {"stone": "Ruby", "metal": "Gold", "finger": "Ring finger", "day": "Sunday"},
    "Moon": {"stone": "Pearl", "metal": "Silver", "finger": "Little finger", "day": "Monday"},
    "Mars": {"stone": "Red Coral", "metal": "Gold/Copper", "finger": "Ring finger", "day": "Tuesday"},
    "Mercury": {"stone": "Emerald", "metal": "Gold", "finger": "Little finger", "day": "Wednesday"},
    "Jupiter": {"stone": "Yellow Sapphire", "metal": "Gold", "finger": "Index finger", "day": "Thursday"},
    "Venus": {"stone": "Diamond/White Sapphire", "metal": "Silver/Platinum", "finger": "Middle finger", "day": "Friday"},
    "Saturn": {"stone": "Blue Sapphire", "metal": "Silver/Iron", "finger": "Middle finger", "day": "Saturday"},
    "Rahu": {"stone": "Hessonite (Gomed)", "metal": "Silver", "finger": "Middle finger", "day": "Saturday"},
    "Ketu": {"stone": "Cat's Eye", "metal": "Silver", "finger": "Ring finger", "day": "Tuesday"},
}

MANTRAS = {
    "Sun": "Om Suryaya Namaha", "Moon": "Om Chandraya Namaha", "Mars": "Om Angarakaya Namaha",
    "Mercury": "Om Budhaya Namaha", "Jupiter": "Om Gurave Namaha", "Venus": "Om Shukraya Namaha",
    "Saturn": "Om Shanicharaya Namaha", "Rahu": "Om Rahave Namaha", "Ketu": "Om Ketave Namaha",
}

DEITIES = {
    "Sun": "Surya", "Moon": "Shiva / Chandra", "Mars": "Hanuman", "Mercury": "Vishnu",
    "Jupiter": "Vishnu / Brihaspati", "Venus": "Lakshmi", "Saturn": "Shani / Hanuman",
    "Rahu": "Durga / Bhairava", "Ketu": "Ganesha",
}

CHARITY = {
    "Sun": "Donate wheat, jaggery, or copper items on Sundays",
    "Moon": "Donate rice, milk, or white cloth on Mondays",
    "Mars": "Donate red lentils (masoor dal) or red cloth on Tuesdays",
    "Mercury": "Donate green vegetables or green cloth on Wednesdays",
    "Jupiter": "Donate turmeric, yellow cloth, or books on Thursdays",
    "Venus": "Donate white sweets, perfume, or white cloth on Fridays",
    "Saturn": "Donate black sesame, iron items, or mustard oil on Saturdays",
    "Rahu": "Donate blankets or dark-colored grains on Saturdays",
    "Ketu": "Donate multi-colored blankets or feed dogs on Saturdays",
}


def planet_dignity(planet, rashi):
    if rashi == EXALTATION.get(planet):
        return "exalted"
    if rashi == DEBILITATION.get(planet):
        return "debilitated"
    if rashi in OWN_SIGNS.get(planet, []):
        return "own sign"
    return "neutral"


def find_weak_planets(planet_rashis: dict):
    """Planets that are debilitated -- the classical trigger for remedy suggestions."""
    weak = []
    for planet, rashi in planet_rashis.items():
        dignity = planet_dignity(planet, rashi)
        if dignity == "debilitated":
            weak.append({"planet": planet, "rashi": rashi, "dignity": dignity})
    return weak


def remedy_for_planet(planet, reason):
    gem = GEMSTONES.get(planet, {})
    return {
        "planet": planet,
        "reason": reason,
        "gemstone": gem.get("stone"),
        "metal": gem.get("metal"),
        "finger": gem.get("finger"),
        "wear_day": gem.get("day"),
        "mantra": MANTRAS.get(planet),
        "deity": DEITIES.get(planet),
        "charity": CHARITY.get(planet),
        "gemstone_note": (
            "Gemstone recommendations are traditional guidance. A qualified "
            "astrologer should confirm suitability before wearing any stone, "
            "since an incompatible gem is classically considered counterproductive."
        ),
    }


def full_remedy_report(planet_rashis: dict, lagna_rashi: str, mangal_dosha_present: bool = False):
    """
    planet_rashis: {"Sun": "Cancer", ...} -- D1 rashis.
    lagna_rashi: the Ascendant's rashi.
    mangal_dosha_present: pass through from the doshas_yogas module if available.
    """
    remedies = []

    # 1. Debilitated planets
    weak = find_weak_planets(planet_rashis)
    for w in weak:
        remedies.append(remedy_for_planet(
            w["planet"],
            f"{w['planet']} is debilitated in {w['rashi']} — classical texts recommend strengthening it."
        ))

    # 2. Lagna lord's condition (a weak Lagna lord affects overall vitality/confidence)
    lagna_lord = RASHI_LORDS[lagna_rashi]
    if lagna_lord in planet_rashis:
        lagna_lord_dignity = planet_dignity(lagna_lord, planet_rashis[lagna_lord])
        if lagna_lord_dignity == "debilitated":
            already_included = any(r["planet"] == lagna_lord for r in remedies)
            if not already_included:
                remedies.append(remedy_for_planet(
                    lagna_lord,
                    f"{lagna_lord} rules your Ascendant ({lagna_rashi}) and is currently debilitated — "
                    f"traditionally linked to lower vitality or confidence."
                ))

    # 3. Mangal Dosha remedy (independent of planet strength -- a placement-based dosha)
    if mangal_dosha_present:
        remedies.append({
            "planet": "Mars",
            "reason": "Mangal Dosha (Manglik) detected in this chart.",
            "gemstone": GEMSTONES["Mars"]["stone"],
            "metal": GEMSTONES["Mars"]["metal"],
            "finger": GEMSTONES["Mars"]["finger"],
            "wear_day": GEMSTONES["Mars"]["day"],
            "mantra": "Om Angarakaya Namaha, or the Hanuman Chalisa",
            "deity": "Hanuman",
            "charity": CHARITY["Mars"],
            "specific_practice": "Kumbh Vivah or Mangal Dosha Nivaran Puja are traditional "
                                  "remedies specifically for this dosha, distinct from general "
                                  "planetary strengthening.",
            "gemstone_note": remedy_for_planet("Mars", "")["gemstone_note"],
        })

    return {
        "weak_planets_found": weak,
        "remedies": remedies,
        "general_note": (
            "These are traditional remedial suggestions based on classical Vedic "
            "principles, not medical, legal, or financial advice. Consult a "
            "qualified astrologer before undertaking gemstone or ritual remedies."
        ),
    }


if __name__ == "__main__":
    from datetime import datetime
    import sys
    sys.path.insert(0, '.')
    from ephemeris import get_all_planets
    from doshas_yogas import check_mangal_dosha

    birth = datetime(1996, 7, 25, 0, 0)
    planets = get_all_planets(birth, utc_offset_hours=5.5, lat=23.5158, lon=87.308)
    lagna_lon = planets.pop("Lagna")
    lagna_rashi = RASHIS[int(lagna_lon // 30)]
    planet_rashis = {name: RASHIS[int(lon // 30)] for name, lon in planets.items()}

    mangal = check_mangal_dosha(planet_rashis, lagna_rashi)
    report = full_remedy_report(planet_rashis, lagna_rashi, mangal["is_manglik"])

    print(f"Lagna: {lagna_rashi} (lord: {RASHI_LORDS[lagna_rashi]})")
    print(f"Weak planets: {report['weak_planets_found']}")
    print()
    for r in report["remedies"]:
        print(f"--- {r['planet']} ---")
        print(f"  Reason: {r['reason']}")
        print(f"  Gemstone: {r['gemstone']} ({r['metal']}, {r['finger']}, wear on {r['wear_day']})")
        print(f"  Mantra: {r['mantra']}")
        print(f"  Deity: {r['deity']}")
        print(f"  Charity: {r['charity']}")
        print()
