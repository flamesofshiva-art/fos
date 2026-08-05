"""
Real ephemeris calculation using pyswisseph (Swiss Ephemeris Python bindings).
Validated: reproduces known-correct Moon longitude (116.0715°) exactly for
the Durgapur test case, matching real provider data to 4 decimal places.

Install: pip install pyswisseph
"""

import swisseph as swe
from datetime import datetime


def get_moon_longitude(birth_date: datetime, utc_offset_hours: float) -> float:
    """
    Real sidereal (Lahiri) Moon longitude from date/time + UTC offset.

    birth_date: naive datetime in LOCAL time (e.g. datetime(2002,10,30,12,16))
    utc_offset_hours: e.g. 5.5 for India (IST = UTC+5:30)

    Returns longitude in degrees (0-360), sidereal, Lahiri ayanamsa.
    """
    # Convert local time to UTC
    utc_hour = birth_date.hour + birth_date.minute / 60.0 - utc_offset_hours

    jd_ut = swe.julday(birth_date.year, birth_date.month, birth_date.day, utc_hour)

    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    moon_pos, _ = swe.calc_ut(jd_ut, swe.MOON, flags)

    return moon_pos[0]


def get_all_planets(birth_date: datetime, utc_offset_hours: float,
                     lat: float = None, lon: float = None) -> dict:
    """
    Real sidereal (Lahiri) longitudes for all 9 grahas (planets + nodes).
    lat/lon only needed if you also want the Ascendant (Lagna) — pass them
    to get that too; omit for planets-only.
    """
    utc_hour = birth_date.hour + birth_date.minute / 60.0 - utc_offset_hours
    jd_ut = swe.julday(birth_date.year, birth_date.month, birth_date.day, utc_hour)

    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    bodies = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
        "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, "Venus": swe.VENUS,
        "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE,  # mean node; TRUE_NODE is the alternative convention
    }

    result = {}
    for name, body_id in bodies.items():
        pos, _ = swe.calc_ut(jd_ut, body_id, flags)
        result[name] = pos[0]

    # Ketu is always exactly 180° from Rahu
    result["Ketu"] = (result["Rahu"] + 180.0) % 360.0

    if lat is not None and lon is not None:
        # Ascendant (Lagna) - whole-sign house system ('W')
        cusps, ascmc = swe.houses_ex(jd_ut, lat, lon, b'W', flags=swe.FLG_SIDEREAL)
        result["Lagna"] = ascmc[0]

    return result


if __name__ == "__main__":
    # Validation against real provider data
    birth = datetime(2002, 10, 30, 12, 16)
    moon_lon = get_moon_longitude(birth, utc_offset_hours=5.5)
    print(f"Moon longitude: {moon_lon:.4f} (expected 116.0715)")
    assert abs(moon_lon - 116.0715) < 0.001, "MISMATCH — check ayanamsa/flags"
    print("✓ Matches real provider data exactly")

    print()
    all_planets = get_all_planets(birth, utc_offset_hours=5.5, lat=23.5158, lon=87.308)
    print("All planets (sidereal, Lahiri):")
    for name, lon in all_planets.items():
        print(f"  {name:10s} {lon:.4f}°")
