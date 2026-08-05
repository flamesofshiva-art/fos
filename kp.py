"""
KP (Krishnamurti Paddhati) sub-lord calculation.

Each of the 27 nakshatras (13°20' = 800') is divided into 9 unequal parts,
proportional to the Vimshottari dasha years of the 9 lords, always starting
from the nakshatra's OWN lord and cycling through the standard 9-lord order.

Sub-lord segment length (in minutes of arc) = (dasha_years / 120) * 800'
"""

DASHA_SEQUENCE = [
    ("Ketu", 7), ("Venus", 20), ("Sun", 6), ("Moon", 10), ("Mars", 7),
    ("Rahu", 18), ("Jupiter", 16), ("Saturn", 19), ("Mercury", 17),
]
LORD_ORDER = [name for name, _ in DASHA_SEQUENCE]
DASHA_YEARS = dict(DASHA_SEQUENCE)

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

RASHIS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio",
          "Sagittarius","Capricorn","Aquarius","Pisces"]
RASHI_LORDS = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun",
               "Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter",
               "Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}

NAKSHATRA_SPAN = 360.0 / 27.0  # 13.3333... degrees = 800 arcminutes


def nakshatra_index(longitude: float) -> int:
    return int((longitude % 360) / NAKSHATRA_SPAN)


def star_lord(longitude: float) -> str:
    return LORD_ORDER[nakshatra_index(longitude) % 9]


def sub_lord(longitude: float) -> str:
    """
    The KP sub-lord: which of the 9 lords' proportional sub-segment
    the exact longitude falls into, within its nakshatra.
    """
    nak_idx = nakshatra_index(longitude)
    starting_lord_idx = nak_idx % 9  # nakshatra's own lord starts the sub-cycle
    position_in_nak = (longitude % 360) % NAKSHATRA_SPAN  # degrees into this nakshatra

    cumulative = 0.0
    for i in range(9):
        lord = LORD_ORDER[(starting_lord_idx + i) % 9]
        segment_span = (DASHA_YEARS[lord] / 120.0) * NAKSHATRA_SPAN
        cumulative += segment_span
        if position_in_nak < cumulative:
            return lord
    return LORD_ORDER[(starting_lord_idx + 8) % 9]  # fallback, floating point edge


def sign_lord(longitude: float) -> str:
    rashi = RASHIS[int((longitude % 360) // 30)]
    return RASHI_LORDS[rashi]


def sign_of(longitude: float) -> str:
    return RASHIS[int((longitude % 360) // 30)]


def kp_details(longitude: float) -> dict:
    nak_idx = nakshatra_index(longitude)
    return {
        "longitude": round(longitude, 4),
        "sign": sign_of(longitude),
        "sign_lord": sign_lord(longitude),
        "star": NAKSHATRAS[nak_idx],
        "star_lord": star_lord(longitude),
        "sub_lord": sub_lord(longitude),
    }


if __name__ == "__main__":
    # Sanity check: sub-lord segments within one nakshatra should sum to exactly 13.3333...
    total = sum((DASHA_YEARS[l] / 120.0) * NAKSHATRA_SPAN for l in LORD_ORDER)
    print(f"Sub-lord segments sum check: {total:.4f} (should equal {NAKSHATRA_SPAN:.4f})")
    assert abs(total - NAKSHATRA_SPAN) < 1e-9

    # ggg's Lagna: 23.9168 (Aries)
    print()
    print("Ascendant (Lagna) KP details:")
    print(kp_details(23.9168))

    # ggg's Moon: 200.8740 (Libra)
    print()
    print("Moon KP details:")
    print(kp_details(200.8740))
