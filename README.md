# Flames of Shiva — Backend API

Real Swiss Ephemeris calculation engine. Validated against known-correct
provider data and cross-checked against AstroSage (independent third party).

## Run it

```
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API docs auto-generate at http://localhost:8000/docs

## Endpoints

- POST /kundali/compute — full D1 chart: planets, houses, nakshatras, Mahadasha
- POST /kundali/kp — KP Ruling Planets, Cusps (Placidus), Planets
- POST /kundali/divisional-charts — all 16 Shodashvarga charts (D1-D60)
- POST /kundali/doshas-yogas — Mangal Dosha + comprehensive yoga detection
- POST /kundali/summary — all 7 sections in one call (General, Remedies,
  Dosha, Ascendant, Planetary, Vimshottari, Yoga)
- POST /matching/ashtakoot — Moon nakshatra/rashi for two people
  (full 8-koota scoring NOT yet implemented — see note in main.py)

## Request format

```json
{
  "date": "2002-10-30",
  "time": "12:16",
  "utc_offset_hours": 5.5,
  "lat": 23.5158,
  "lon": 87.308
}
```

## Validation

This engine's output has been checked against:
- Original real provider API response (exact match, all planets)
- AstroSage's KP calculator (exact match, all 7 Ruling Planets fields,
  tested on a real birth chart)

## Before production

- Set CORS allow_origins to your real domain (currently "*")
- Add rate limiting
- Complete Ashtakoot 8-koota lookup tables in /matching/ashtakoot
- Consider caching: same birth details always produce the same chart
