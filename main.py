"""
Flames of Shiva — Backend API
Serves real chart calculations using validated Swiss Ephemeris pipeline.

Run:
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000

All math here is validated against real provider data and cross-checked
against AstroSage (see project notes) — this is not mock data.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

from ephemeris import get_all_planets, get_moon_longitude
from mahadasha import calculate_full_dasha_timeline, current_dasha
from kp import kp_details, sign_of
from divisional_charts import all_vargas_for_chart, all_vargas_with_houses, VARGA_SIGNIFICANCE
from doshas_yogas import full_dosha_yoga_report
from remedies import full_remedy_report

app = FastAPI(title="Flames of Shiva API")

# Allow the frontend (localhost:5173 in dev, your real domain in prod) to call this
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your real domain before launch
    allow_methods=["*"],
    allow_headers=["*"],
)

RASHIS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
          "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
WEEKDAY_LORDS = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]


class BirthDetails(BaseModel):
    name: str | None = None
    date: str          # "YYYY-MM-DD"
    time: str           # "HH:MM" 24hr
    utc_offset_hours: float = 5.5
    lat: float
    lon: float


class MatchRequest(BaseModel):
    person_a: BirthDetails
    person_b: BirthDetails


def _parse_birth(b: BirthDetails) -> datetime:
    try:
        return datetime.strptime(f"{b.date} {b.time}", "%Y-%m-%d %H:%M")
    except ValueError:
        raise HTTPException(400, "date must be YYYY-MM-DD and time HH:MM")


def _house_of(rashi: str, lagna_rashi: str) -> int:
    return ((RASHIS.index(rashi) - RASHIS.index(lagna_rashi) + 12) % 12) + 1


@app.get("/")
def root():
    return {"status": "ok", "service": "Flames of Shiva API"}


@app.post("/kundali/compute")
def compute_kundali(birth: BirthDetails):
    """Full D1 chart: all planets, houses, nakshatras, and Mahadasha timeline."""
    dt = _parse_birth(birth)
    planets_raw = get_all_planets(dt, birth.utc_offset_hours, birth.lat, birth.lon)

    lagna_lon = planets_raw.pop("Lagna")
    lagna_rashi = sign_of(lagna_lon)

    planets = {}
    for name, lon in planets_raw.items():
        d = kp_details(lon)
        planets[name] = {
            "longitude": round(lon, 4),
            "rashi": d["sign"],
            "rashi_lord": d["sign_lord"],
            "nakshatra": d["star"],
            "nakshatra_lord": d["star_lord"],
            "house": _house_of(d["sign"], lagna_rashi),
        }

    dasha = calculate_full_dasha_timeline(planets_raw["Moon"], dt)
    active = current_dasha(dasha["mahadasha_timeline"])

    return {
        "birth_details": birth.model_dump(),
        "lagna": {
            "longitude": round(lagna_lon, 4),
            "rashi": lagna_rashi,
            "rashi_lord": kp_details(lagna_lon)["sign_lord"],
        },
        "planets": planets,
        "dasha": {
            "nakshatra": dasha["nakshatra"],
            "nakshatra_lord": dasha["nakshatra_lord"],
            "timeline": dasha["mahadasha_timeline"],
            "current_mahadasha": active["mahadasha"] if active else None,
            "current_antardasha": active.get("antardasha") if active else None,
        },
    }


@app.post("/kundali/kp")
def compute_kp(birth: BirthDetails):
    """KP Ruling Planets, Cusps (Placidus), and Planets tables."""
    import swisseph as swe

    dt = _parse_birth(birth)
    utc_hour = dt.hour + dt.minute / 60 - birth.utc_offset_hours
    jd_ut = swe.julday(dt.year, dt.month, dt.day, utc_hour)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    cusps, ascmc = swe.houses_ex(jd_ut, birth.lat, birth.lon, b'P', flags=flags)
    asc_lon = ascmc[0]

    bodies = {"Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
              "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE}
    positions = {}
    for name, bid in bodies.items():
        pos, _ = swe.calc_ut(jd_ut, bid, flags)
        positions[name] = pos[0]
    positions["Ketu"] = (positions["Rahu"] + 180) % 360

    def which_house(lon_val):
        for i in range(12):
            c1, c2 = cusps[i], cusps[(i + 1) % 12]
            if c2 < c1:
                if lon_val >= c1 or lon_val < c2:
                    return i + 1
            elif c1 <= lon_val < c2:
                return i + 1
        return None

    d_asc = kp_details(asc_lon)
    d_moon = kp_details(positions["Moon"])
    day_lord = WEEKDAY_LORDS[dt.weekday()]

    ruling_planets = {
        "asc_sign_lord": d_asc["sign_lord"],
        "asc_star_lord": d_asc["star_lord"],
        "asc_sub_lord": d_asc["sub_lord"],
        "moon_sign_lord": d_moon["sign_lord"],
        "moon_star_lord": d_moon["star_lord"],
        "moon_sub_lord": d_moon["sub_lord"],
        "day_lord": day_lord,
    }

    kp_cusps = []
    for i, c_lon in enumerate(cusps[:12], start=1):
        d = kp_details(c_lon)
        kp_cusps.append({"cusp": i, **d})

    kp_planets = []
    for name, lon_val in positions.items():
        d = kp_details(lon_val)
        kp_planets.append({"planet": name, "cusp": which_house(lon_val), **d})

    return {
        "ruling_planets": ruling_planets,
        "cusps": kp_cusps,
        "planets": kp_planets,
    }


@app.post("/kundali/divisional-charts")
def compute_divisional_charts(birth: BirthDetails):
    """All 16 Shodashvarga divisional charts, each with its own Lagna and
    whole-sign houses (not just D1's houses) — validated against real
    provider D60 data (all 9 planets matched exactly — see divisional_charts.py)."""
    dt = _parse_birth(birth)
    planets_raw = get_all_planets(dt, birth.utc_offset_hours, birth.lat, birth.lon)
    lagna_lon = planets_raw.pop("Lagna")

    vargas = all_vargas_with_houses(planets_raw, lagna_lon)

    return {
        "birth_details": birth.model_dump(),
        "vargas": vargas,
        "significance": VARGA_SIGNIFICANCE,
    }


@app.post("/kundali/doshas-yogas")
def compute_doshas_yogas(birth: BirthDetails):
    """Mangal Dosha (checked from Lagna, Moon, and Venus) plus a comprehensive
    yoga set: Gaja Kesari, Chandra-Mangal, Budhaditya, Kemadruma, all five
    Pancha Mahapurusha yogas, Neechabhanga, Dhana Yogas, and Raja Yogas."""
    dt = _parse_birth(birth)
    planets_raw = get_all_planets(dt, birth.utc_offset_hours, birth.lat, birth.lon)
    lagna_lon = planets_raw.pop("Lagna")
    lagna_rashi = sign_of(lagna_lon)

    planet_rashis = {name: sign_of(lon) for name, lon in planets_raw.items()}

    report = full_dosha_yoga_report(planet_rashis, lagna_rashi)

    return {
        "birth_details": birth.model_dump(),
        "lagna_rashi": lagna_rashi,
        **report,
    }


@app.post("/kundali/summary")
def compute_summary(birth: BirthDetails):
    """
    One call, all 7 sections: General, Remedies, Dosha, Ascendant, Planetary,
    Vimshottari, Yoga. Combines every module built in this project so the
    frontend doesn't need 5 separate requests for one summary view.
    """
    import swisseph as swe

    dt = _parse_birth(birth)
    planets_raw = get_all_planets(dt, birth.utc_offset_hours, birth.lat, birth.lon)
    lagna_lon = planets_raw.pop("Lagna")
    lagna_rashi = sign_of(lagna_lon)
    lagna_d = kp_details(lagna_lon)

    planet_rashis = {name: sign_of(lon) for name, lon in planets_raw.items()}

    # Planetary (full detail per planet)
    planetary = {}
    for name, lon in planets_raw.items():
        d = kp_details(lon)
        planetary[name] = {
            "longitude": round(lon, 4), "rashi": d["sign"], "rashi_lord": d["sign_lord"],
            "nakshatra": d["star"], "nakshatra_lord": d["star_lord"],
            "house": _house_of(d["sign"], lagna_rashi),
        }

    # Ascendant
    ascendant = {
        "longitude": round(lagna_lon, 4), "rashi": lagna_d["sign"], "rashi_lord": lagna_d["sign_lord"],
        "nakshatra": lagna_d["star"], "nakshatra_lord": lagna_d["star_lord"],
    }

    # Vimshottari
    dasha = calculate_full_dasha_timeline(planets_raw["Moon"], dt)
    active = current_dasha(dasha["mahadasha_timeline"])
    vimshottari = {
        "nakshatra": dasha["nakshatra"], "nakshatra_lord": dasha["nakshatra_lord"],
        "current_mahadasha": active["mahadasha"] if active else None,
        "current_antardasha": active.get("antardasha") if active else None,
        "full_timeline": dasha["mahadasha_timeline"],
    }

    # Dosha & Yoga
    dosha_yoga = full_dosha_yoga_report(planet_rashis, lagna_rashi)

    # Remedies (uses Mangal Dosha result from above)
    remedies = full_remedy_report(planet_rashis, lagna_rashi, dosha_yoga["mangal_dosha"]["is_manglik"])

    # General (a compact overview combining the headline facts)
    general = {
        "lagna": lagna_rashi,
        "moon_sign": planetary["Moon"]["rashi"],
        "moon_nakshatra": planetary["Moon"]["nakshatra"],
        "sun_sign": planetary["Sun"]["rashi"],
        "current_mahadasha": vimshottari["current_mahadasha"]["lord"] if vimshottari["current_mahadasha"] else None,
        "is_manglik": dosha_yoga["mangal_dosha"]["is_manglik"],
        "yogas_count": len(dosha_yoga["yogas_present"]),
    }

    return {
        "birth_details": birth.model_dump(),
        "general": general,
        "remedies": remedies,
        "dosha": dosha_yoga["mangal_dosha"],
        "ascendant": ascendant,
        "planetary": planetary,
        "vimshottari": vimshottari,
        "yoga": dosha_yoga["yogas"],
        "yogas_present": dosha_yoga["yogas_present"],
    }


@app.post("/matching/ashtakoot")
def compute_matching(req: MatchRequest):
    """Ashtakoot (Guna Milan) matching between two people."""
    dt_a = _parse_birth(req.person_a)
    dt_b = _parse_birth(req.person_b)

    moon_a = get_moon_longitude(dt_a, req.person_a.utc_offset_hours)
    moon_b = get_moon_longitude(dt_b, req.person_b.utc_offset_hours)

    # NOTE: full Ashtakoot (8-koota) scoring with real lookup tables is a
    # larger build than the validated dasha/KP pieces above — this endpoint
    # currently returns the two Moon nakshatras/rashis as a foundation.
    # Wire in complete koota tables here before using this for real matching.
    d_a = kp_details(moon_a)
    d_b = kp_details(moon_b)

    return {
        "person_a": {"nakshatra": d_a["star"], "rashi": d_a["sign"]},
        "person_b": {"nakshatra": d_b["star"], "rashi": d_b["sign"]},
        "note": "Full 8-koota scoring not yet implemented — see backend/main.py",
    }
