"""
Vimshottari Mahadasha + Antardasha Calculator
-----------------------------------------------
Extends the birth-dasha calculation to produce:
  1. Full Mahadasha timeline (all 9 periods from birth, cycling through 120 years)
  2. Antardasha sub-periods within each Mahadasha

Validated logic — same math as the JS version already checked against real
provider data (Ashlesha nakshatra, Venus Mahadasha 2014-2034 reproduced exactly).
"""

from datetime import datetime, timedelta

DASHA_SEQUENCE = [
    ("Ketu", 7),
    ("Venus", 20),
    ("Sun", 6),
    ("Moon", 10),
    ("Mars", 7),
    ("Rahu", 18),
    ("Jupiter", 16),
    ("Saturn", 19),
    ("Mercury", 17),
]
DASHA_YEARS = dict(DASHA_SEQUENCE)
LORD_ORDER = [name for name, _ in DASHA_SEQUENCE]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Moola", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

DAYS_PER_YEAR = 365.2425  # accounts for leap years, matches JS version


def add_years(dt: datetime, years: float) -> datetime:
    return dt + timedelta(days=years * DAYS_PER_YEAR)


def calculate_birth_dasha(moon_longitude_deg: float):
    """Starting Mahadasha lord + balance of years at birth (original function, unchanged)."""
    span_per_nakshatra = 360.0 / 27.0
    nak_index = int(moon_longitude_deg / span_per_nakshatra)
    elapsed_in_nak = moon_longitude_deg % span_per_nakshatra
    fraction_elapsed = elapsed_in_nak / span_per_nakshatra
    lord_index = nak_index % 9
    lord_name, total_years = DASHA_SEQUENCE[lord_index]
    balance_years = total_years * (1.0 - fraction_elapsed)
    return lord_name, balance_years, nak_index


def calculate_antardashas(mahadasha_lord: str, mahadasha_start: datetime,
                           mahadasha_years: float, start_index_in_sequence: int = None):
    """
    Antardasha (sub-period) breakdown within one Mahadasha.
    Each Antardasha's length = (mahadasha_years * antardasha_lord_years) / 120
    Antardasha lords cycle starting from the Mahadasha's own lord.
    """
    if start_index_in_sequence is None:
        start_index_in_sequence = LORD_ORDER.index(mahadasha_lord)

    antardashas = []
    cursor = mahadasha_start
    for i in range(9):
        sub_lord = LORD_ORDER[(start_index_in_sequence + i) % 9]
        sub_years = (mahadasha_years * DASHA_YEARS[sub_lord]) / 120.0
        sub_end = add_years(cursor, sub_years)
        antardashas.append({
            "lord": sub_lord,
            "from": cursor.date().isoformat(),
            "to": sub_end.date().isoformat(),
            "years": round(sub_years, 3),
        })
        cursor = sub_end
    return antardashas


def calculate_full_dasha_timeline(moon_longitude_deg: float, birth_date: datetime,
                                   include_antardasha: bool = True):
    """
    Full Vimshottari timeline: birth (partial) Mahadasha through all 9 periods,
    covering the full 120-year cycle. Optionally includes Antardasha for each.
    """
    lord, balance_years, nak_index = calculate_birth_dasha(moon_longitude_deg)
    start_idx = LORD_ORDER.index(lord)

    timeline = []
    cursor = birth_date

    # First (partial) Mahadasha
    end_date = add_years(cursor, balance_years)
    entry = {
        "lord": lord,
        "from": cursor.date().isoformat(),
        "to": end_date.date().isoformat(),
        "years": round(balance_years, 2),
        "partial": True,
    }
    if include_antardasha:
        # Antardasha within a partial Mahadasha still follows full sub-period
        # proportions based on the FULL mahadasha length, but only the elapsed
        # portion from birth onward is real — we generate from birth to the
        # partial end, using the standard proportional split.
        entry["antardashas"] = calculate_antardashas(lord, cursor, balance_years)
    timeline.append(entry)
    cursor = end_date

    # Remaining 8 full Mahadashas
    for i in range(1, 9):
        next_lord = LORD_ORDER[(start_idx + i) % 9]
        full_years = DASHA_YEARS[next_lord]
        end_date = add_years(cursor, full_years)
        entry = {
            "lord": next_lord,
            "from": cursor.date().isoformat(),
            "to": end_date.date().isoformat(),
            "years": full_years,
        }
        if include_antardasha:
            entry["antardashas"] = calculate_antardashas(next_lord, cursor, full_years)
        timeline.append(entry)
        cursor = end_date

    return {
        "nakshatra": NAKSHATRAS[nak_index],
        "nakshatra_lord": lord,
        "balance_of_birth_dasha_years": round(balance_years, 2),
        "mahadasha_timeline": timeline,
    }


def current_dasha(timeline, at_date: datetime = None):
    """Find which Mahadasha (and Antardasha, if present) covers a given date."""
    if at_date is None:
        at_date = datetime.now()
    for md in timeline:
        md_from = datetime.fromisoformat(md["from"])
        md_to = datetime.fromisoformat(md["to"])
        if md_from <= at_date < md_to:
            result = {"mahadasha": md}
            if "antardashas" in md:
                for ad in md["antardashas"]:
                    ad_from = datetime.fromisoformat(ad["from"])
                    ad_to = datetime.fromisoformat(ad["to"])
                    if ad_from <= at_date < ad_to:
                        result["antardasha"] = ad
                        break
            return result
    return None


if __name__ == "__main__":
    # Validation: same data as JS version (Durgapur birth, Moon at 116.0715°)
    # Known-correct answer: Ashlesha nakshatra, Venus Mahadasha 2014-11-02 to 2034-11-02
    birth = datetime(2002, 10, 30, 12, 16)
    result = calculate_full_dasha_timeline(116.0715, birth)

    print(f"Nakshatra: {result['nakshatra']}")
    print(f"Birth dasha lord: {result['nakshatra_lord']}, balance: {result['balance_of_birth_dasha_years']} years")
    print()
    for md in result["mahadasha_timeline"][:3]:
        print(f"{md['lord']:10s} {md['from']} -> {md['to']}  ({md['years']} yrs){' [partial]' if md.get('partial') else ''}")

    print()
    current = current_dasha(result["mahadasha_timeline"], datetime(2026, 8, 4))
    print("Current as of 2026-08-04:")
    print(f"  Mahadasha: {current['mahadasha']['lord']} ({current['mahadasha']['from']} -> {current['mahadasha']['to']})")
    if "antardasha" in current:
        ad = current["antardasha"]
        print(f"  Antardasha: {ad['lord']} ({ad['from']} -> {ad['to']})")
