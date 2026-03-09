"""
VIN (Vehicle Identification Number) decoder.

Uses the NHTSA vPIC API to decode VIN information.
Reference: https://vpic.nhtsa.dot.gov/api/
"""

import logging
import re
from typing import Optional

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

VIN_PATTERN = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$", re.IGNORECASE)

CACHE_TTL = 60 * 60 * 24  # 24 hours


def validate_vin(vin: str) -> bool:
    """
    Validate a VIN string.

    Checks length (17 characters) and character set (no I, O, Q).
    Also verifies the check digit (position 9) using the standard
    transliteration and weight algorithm.
    """
    if not vin or len(vin) != 17:
        return False
    if not VIN_PATTERN.match(vin):
        return False

    # Check digit validation (position 9, zero-indexed 8)
    transliteration = {
        "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8,
        "J": 1, "K": 2, "L": 3, "M": 4, "N": 5, "P": 7, "R": 9,
        "S": 2, "T": 3, "U": 4, "V": 5, "W": 6, "X": 7, "Y": 8, "Z": 9,
    }
    weights = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]

    total = 0
    vin_upper = vin.upper()
    for i, char in enumerate(vin_upper):
        if char.isdigit():
            value = int(char)
        else:
            value = transliteration.get(char)
            if value is None:
                return False
        total += value * weights[i]

    remainder = total % 11
    check_char = vin_upper[8]

    if remainder == 10:
        return check_char == "X"
    return check_char == str(remainder)


def decode_vin(vin: str) -> Optional[dict]:
    """
    Decode a VIN using the NHTSA vPIC API.

    Returns a dictionary with decoded vehicle information or None
    if the request fails.

    Results are cached for 24 hours to reduce API calls.
    """
    vin = vin.strip().upper()

    # Check cache first
    cache_key = f"vin_decode:{vin}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    api_url = getattr(settings, "VIN_API_URL", "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues")

    try:
        response = requests.get(
            f"{api_url}/{vin}",
            params={"format": "json"},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        logger.error("VIN decode API request failed for %s: %s", vin, exc)
        return None

    results = data.get("Results", [])
    if not results:
        return None

    raw = results[0]

    # Map NHTSA response fields to our normalized structure
    decoded = {
        "vin": vin,
        "year": _safe_int(raw.get("ModelYear")),
        "make": raw.get("Make", "").strip(),
        "model": raw.get("Model", "").strip(),
        "trim": raw.get("Trim", "").strip(),
        "vehicle_type": raw.get("VehicleType", "").strip(),
        "body_class": raw.get("BodyClass", "").strip(),
        "doors": _safe_int(raw.get("Doors")),
        "fuel_type": raw.get("FuelTypePrimary", "").strip(),
        "engine_cylinders": _safe_int(raw.get("EngineCylinders")),
        "engine_displacement_l": raw.get("DisplacementL", "").strip(),
        "engine_hp": _safe_int(raw.get("EngineHP")),
        "transmission": raw.get("TransmissionStyle", "").strip(),
        "drive_type": raw.get("DriveType", "").strip(),
        "plant_city": raw.get("PlantCity", "").strip(),
        "plant_country": raw.get("PlantCountry", "").strip(),
        "manufacturer": raw.get("Manufacturer", "").strip(),
        "error_code": raw.get("ErrorCode", ""),
        "error_text": raw.get("ErrorText", "").strip(),
    }

    # Cache the result
    cache.set(cache_key, decoded, CACHE_TTL)

    return decoded


def _safe_int(value) -> Optional[int]:
    """Convert a value to int, returning None on failure."""
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None
