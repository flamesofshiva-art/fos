"""
Shodashvarga — the 16 classical divisional (Varga) charts.

Each function takes a planet's sidereal longitude (0-360°) and returns
the rashi (0-11, Aries=0) it falls into for that division.

Standard, widely-accepted calculation methods used throughout (Parashari
system) — the same conventions used by most professional software.
"""

RASHIS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
          "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

ODD_SIGNS = {0, 2, 4, 6, 8, 10}   # Aries, Gemini, Leo, Libra, Sagittarius, Aquarius (0-indexed)
MOVABLE = {0, 3, 6, 9}    # Aries, Cancer, Libra, Capricorn
FIXED = {1, 4, 7, 10}     # Taurus, Leo, Scorpio, Aquarius
DUAL = {2, 5, 8, 11}      # Gemini, Virgo, Sagittarius, Pisces


def _sign_index(longitude):
    return int((longitude % 360) // 30)


def _deg_in_sign(longitude):
    return (longitude % 360) % 30


def d1(longitude):
    """Rashi chart — the birth chart itself."""
    return _sign_index(longitude)


def d2_hora(longitude):
    """Hora — wealth. Two divisions of 15° each."""
    sign = _sign_index(longitude)
    deg = _deg_in_sign(longitude)
    half = int(deg // 15)  # 0 or 1
    if sign in ODD_SIGNS:
        return 4 if half == 0 else 3  # Leo (4) first half, Cancer (3) second half
    else:
        return 3 if half == 0 else 4  # Cancer first half, Leo second half


def d3_drekkana(longitude):
    """Drekkana — siblings, courage. Three divisions of 10°."""
    sign = _sign_index(longitude)
    deg = _deg_in_sign(longitude)
    part = int(deg // 10)  # 0, 1, 2
    return (sign + part * 4) % 12


def d4_chaturthamsa(longitude):
    """Chaturthamsa — fortune, property. Four divisions of 7°30'."""
    sign = _sign_index(longitude)
    deg = _deg_in_sign(longitude)
    part = int(deg // 7.5)  # 0-3
    return (sign + part * 3) % 12


def d7_saptamsa(longitude):
    """Saptamsa — children, progeny. Seven divisions of ~4°17'."""
    sign = _sign_index(longitude)
    deg = _deg_in_sign(longitude)
    part = int(deg // (30 / 7))  # 0-6
    if sign in ODD_SIGNS:
        return (sign + part) % 12
    else:
        return (sign + 6 + part) % 12  # starts from the 7th sign for even signs


def d9_navamsa(longitude):
    """Navamsa — marriage, dharma. Nine divisions of 3°20'. Most-used varga after D1."""
    sign = _sign_index(longitude)
    deg = _deg_in_sign(longitude)
    part = int(deg // (30 / 9))  # 0-8
    if sign in MOVABLE:
        start = sign
    elif sign in FIXED:
        start = (sign + 8) % 12
    else:  # DUAL
        start = (sign + 4) % 12
    return (start + part) % 12


def d10_dasamsa(longitude):
    """Dasamsa — career, profession. Ten divisions of 3°."""
    sign = _sign_index(longitude)
    deg = _deg_in_sign(longitude)
    part = int(deg // 3)  # 0-9
    if sign in ODD_SIGNS:
        return (sign + part) % 12
    else:
        return (sign + 8 + part) % 12


def d12_dwadasamsa(longitude):
    """Dwadasamsa — parents, ancestry. Twelve divisions of 2°30'."""
    sign = _sign_index(longitude)
    deg = _deg_in_sign(longitude)
    part = int(deg // 2.5)  # 0-11
    return (sign + part) % 12


def d16_shodasamsa(longitude):
    """Shodasamsa — vehicles, general happiness. Sixteen divisions of 1°52'30"."""
    sign = _sign_index(longitude)
    deg = _deg_in_sign(longitude)
    part = int(deg // (30 / 16))  # 0-15
    if sign in MOVABLE:
        start = 0  # Aries
    elif sign in FIXED:
        start = 4  # Leo
    else:
        start = 8  # Sagittarius
    return (start + part) % 12


def d20_vimsamsa(longitude):
    """Vimsamsa — spiritual life, worship. Twenty divisions of 1°30'."""
    sign = _sign_index(longitude)
    deg = _deg_in_sign(longitude)
    part = int(deg // 1.5)  # 0-19
    if sign in MOVABLE:
        start = 0  # Aries
    elif sign in FIXED:
        start = 8  # Sagittarius
    else:
        start = 4  # Leo
    return (start + part) % 12


def d24_chaturvimsamsa(longitude):
    """Chaturvimsamsa — education, learning. Twenty-four divisions of 1°15'."""
    sign = _sign_index(longitude)
    deg = _deg_in_sign(longitude)
    part = int(deg // 1.25)  # 0-23
    start = 4 if sign in ODD_SIGNS else 3  # Leo for odd, Cancer for even
    return (start + part) % 12


def d27_bhamsa(longitude):
    """Bhamsa (Saptavimsamsa) — strengths and weaknesses. 27 divisions of 1°6'40"."""
    sign = _sign_index(longitude)
    deg = _deg_in_sign(longitude)
    part = int(deg // (30 / 27))  # 0-26
    element_start = {0: 0, 1: 3, 2: 6, 3: 9}  # fire->Aries, earth->Cancer, air->Libra, water->Capricorn
    group = sign % 4  # 0=fire,1=earth,2=air,3=water (Aries,Taurus,Gemini,Cancer pattern)
    start = element_start[group]
    return (start + part) % 12


def d30_trimsamsa(longitude):
    """Trimsamsa — misfortunes, difficulties. Uneven divisions per classical rule."""
    sign = _sign_index(longitude)
    deg = _deg_in_sign(longitude)
    # Classical uneven split, differs for odd/even signs
    if sign in ODD_SIGNS:
        bounds = [(0, 5, 0), (5, 10, 10), (10, 18, 8), (18, 25, 2), (25, 30, 6)]
    else:
        bounds = [(0, 5, 1), (5, 12, 5), (12, 20, 11), (20, 25, 9), (25, 30, 7)]
    for lo, hi, target_sign in bounds:
        if lo <= deg < hi:
            return target_sign
    return bounds[-1][2]


def d40_khavedamsa(longitude):
    """Khavedamsa — auspicious/inauspicious effects, maternal lineage. 40 divisions of 45'."""
    sign = _sign_index(longitude)
    deg = _deg_in_sign(longitude)
    part = int(deg // 0.75)  # 0-39
    start = 0 if sign in ODD_SIGNS else 6  # Aries for odd, Libra for even
    return (start + part) % 12


def d45_akshavedamsa(longitude):
    """Akshavedamsa — general indications, character. 45 divisions of 40'."""
    sign = _sign_index(longitude)
    deg = _deg_in_sign(longitude)
    part = int(deg // (2 / 3))  # 0-44
    if sign in MOVABLE:
        start = 0  # Aries
    elif sign in FIXED:
        start = 4  # Leo
    else:
        start = 8  # Sagittarius
    return (start + part) % 12


def d60_shashtiamsa(longitude):
    """Shashtiamsa — past-life karma, most subtle/important varga. 60 divisions of 30'."""
    sign = _sign_index(longitude)
    deg = _deg_in_sign(longitude)
    part = int(deg // 0.5)  # 0-59
    return (sign + part) % 12


VARGA_FUNCTIONS = {
    "D1": d1, "D2": d2_hora, "D3": d3_drekkana, "D4": d4_chaturthamsa,
    "D7": d7_saptamsa, "D9": d9_navamsa, "D10": d10_dasamsa, "D12": d12_dwadasamsa,
    "D16": d16_shodasamsa, "D20": d20_vimsamsa, "D24": d24_chaturvimsamsa,
    "D27": d27_bhamsa, "D30": d30_trimsamsa, "D40": d40_khavedamsa,
    "D45": d45_akshavedamsa, "D60": d60_shashtiamsa,
}

VARGA_SIGNIFICANCE = {
    "D1": "Physical body, general life", "D2": "Wealth, family resources",
    "D3": "Siblings, courage, initiative", "D4": "Fortune, property, home",
    "D7": "Children, progeny", "D9": "Marriage, dharma, spouse",
    "D10": "Career, profession, status", "D12": "Parents, ancestry",
    "D16": "Vehicles, general happiness", "D20": "Spiritual life, worship",
    "D24": "Education, learning", "D27": "Strengths and weaknesses",
    "D30": "Misfortunes, difficulties", "D40": "Auspicious/inauspicious effects, maternal lineage",
    "D45": "General indications, character", "D60": "Past-life karma (most subtle varga)",
}


def all_vargas_for_longitude(longitude):
    """Returns {varga_name: rashi_name} for all 16 divisional charts, for one planet."""
    return {name: RASHIS[fn(longitude)] for name, fn in VARGA_FUNCTIONS.items()}


def all_vargas_for_chart(planet_longitudes: dict, lagna_longitude: float = None):
    """
    planet_longitudes: {"Sun": 192.77, "Moon": 116.07, ...}
    lagna_longitude: the D1 Ascendant's longitude (optional). If given, each
        varga also gets its own Lagna position, computed the same way as any
        planet -- this is what lets house numbers be derived per-varga,
        since whole-sign houses depend on THAT chart's own ascendant, not D1's.
    Returns: {"D1": {"Sun": "Libra", ..., "Lagna": "Capricorn"}, "D2": {...}, ...}
    """
    result = {varga: {} for varga in VARGA_FUNCTIONS}
    for planet, lon in planet_longitudes.items():
        vargas = all_vargas_for_longitude(lon)
        for varga, rashi in vargas.items():
            result[varga][planet] = rashi

    if lagna_longitude is not None:
        lagna_vargas = all_vargas_for_longitude(lagna_longitude)
        for varga, rashi in lagna_vargas.items():
            result[varga]["Lagna"] = rashi

    return result


def house_of(planet_rashi: str, lagna_rashi: str) -> int:
    """Whole-sign house number of a planet, given that chart's own Lagna rashi."""
    return ((RASHIS.index(planet_rashi) - RASHIS.index(lagna_rashi) + 12) % 12) + 1


def all_vargas_with_houses(planet_longitudes: dict, lagna_longitude: float):
    """
    Same as all_vargas_for_chart, but each planet entry becomes
    {"rashi": ..., "house": N} instead of a bare rashi string --
    ready for square-chart rendering.
    """
    raw = all_vargas_for_chart(planet_longitudes, lagna_longitude)
    result = {}
    for varga, planets in raw.items():
        lagna_rashi = planets["Lagna"]
        result[varga] = {
            name: {"rashi": rashi, "house": house_of(rashi, lagna_rashi)}
            for name, rashi in planets.items()
            if name != "Lagna"
        }
        result[varga]["Lagna"] = {"rashi": lagna_rashi, "house": 1}
    return result


if __name__ == "__main__":
    # Validation: D9 for known chart (Durgapur, Moon at 116.0715 -> Cancer in D1)
    # Cancer is FIXED-group start... wait Cancer is index 3, which is MOVABLE.
    # Let's just print and sanity check manually against expectations.
    from datetime import datetime
    import sys
    sys.path.insert(0, '.')
    from ephemeris import get_all_planets

    birth = datetime(2002, 10, 30, 12, 16)
    planets = get_all_planets(birth, utc_offset_hours=5.5, lat=23.5158, lon=87.308)
    planets.pop("Lagna", None)

    print("D1 (should match real provider data exactly):")
    for name, lon in planets.items():
        print(f"  {name:10s} {RASHIS[d1(lon)]}")

    print("\nD9 Navamsa:")
    for name, lon in planets.items():
        print(f"  {name:10s} {RASHIS[d9_navamsa(lon)]}")

    print("\nAll 16 vargas for Moon (116.0715, Cancer):")
    for varga, rashi in all_vargas_for_longitude(116.0715).items():
        print(f"  {varga:5s} {rashi:12s} ({VARGA_SIGNIFICANCE[varga]})")
