#!/usr/bin/env python3
"""
sistema_complete.py

Complete astrological and astronomical chart generator with detailed interpretations.

Modes:
 - Nostradamus  : High-accuracy mode using pyswisseph (Swiss Ephemeris) when available.
 - Ptolemy      : Pure-Python fallback using Skyfield and approximate house algorithms.
 - Paranoid     : Offline-only mode using local data/ files.

Features:
 - Parse date inputs (DD/MM/YYYY or MM/DD/YYYY) with interactive disambiguation.
 - Parse times (24h/12h with AM/PM), timezone abbreviations or IANA tz names, and UTC.
 - Location input: city/state/country (geocoded via Nominatim), lat/lon, or zipcode.
 - House systems: Placidus, Equal, Whole Sign, Porphyry, Campanus.
 - Comprehensive astrological interpretations with sign descriptions and chart patterns.
 - Output: verbose chart, summary, detailed interpretation, astronomical JSON, PNG/HTML wheels, PDF.
 - Historical events fetch via Wikipedia OnThisDay with offline fallback.

MIT License
Copyright 2025
"""

import sys, os, math, json, time, traceback
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import argparse
import shutil

# ---------------------------
# Configuration / constants
# ---------------------------
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
KEYS_FILE = os.path.join(DATA_DIR, "keys.json")
ZIPFILE = os.path.join(DATA_DIR, "zipcodes.csv")
TZ_CACHE = os.path.join(DATA_DIR, "tz_cache.csv")
EPHEM_SNAPSHOT = os.path.join(DATA_DIR, "ephem_snapshot.json")
EVENTS_CACHE = os.path.join(DATA_DIR, "events_cache.json")

# Default output filenames
OUT_VERBOSE = os.path.join(OUTPUT_DIR, "chart_verbose.txt")
OUT_SUMMARY = os.path.join(OUTPUT_DIR, "chart_summary.txt")
OUT_INTERPRETATION = os.path.join(OUTPUT_DIR, "chart_interpretation.txt")
OUT_ASTRO_RAW = os.path.join(OUTPUT_DIR, "astro_data_raw.json")
OUT_WHEEL_PNG = os.path.join(OUTPUT_DIR, "chart_wheel.png")
OUT_WHEEL_HTML = os.path.join(OUTPUT_DIR, "chart_wheel.html")
OUT_PDF = os.path.join(OUTPUT_DIR, "chart_report.pdf")

# Common timezone abbreviation map to IANA
TZ_ABBREV_MAP = {
    "PST": "America/Los_Angeles", "PDT": "America/Los_Angeles",
    "EST": "America/New_York", "EDT": "America/New_York",
    "CST": "America/Chicago", "CDT": "America/Chicago",
    "MST": "America/Denver", "MDT": "America/Denver",
    "UTC": "UTC", "GMT": "Etc/Greenwich",
    "BST": "Europe/London", "CET": "Europe/Paris", "CEST": "Europe/Paris"
}

# Planet list
PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]

# Rulerships
RULERS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# ---------------------------
# Dependency detection
# ---------------------------
HAS_PYSWISSEPH = False
HAS_SKYFIELD = False
HAS_MATPLOTLIB = False
HAS_PLOTLY = False
HAS_PIL = False
HAS_FPDF = False
HAS_GEOPY = False
HAS_TFINDER = False
HAS_REQUESTS = False
HAS_DATEUTIL = False

try:
    import swisseph as swe
    HAS_PYSWISSEPH = True
except Exception:
    HAS_PYSWISSEPH = False

try:
    from skyfield.api import load, wgs84
    HAS_SKYFIELD = True
except Exception:
    HAS_SKYFIELD = False

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except Exception:
    HAS_MATPLOTLIB = False

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except Exception:
    HAS_PLOTLY = False

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except Exception:
    HAS_PIL = False

try:
    from fpdf import FPDF
    HAS_FPDF = True
except Exception:
    HAS_FPDF = False

try:
    from geopy.geocoders import Nominatim
    HAS_GEOPY = True
except Exception:
    HAS_GEOPY = False

try:
    from timezonefinder import TimezoneFinder
    HAS_TFINDER = True
except Exception:
    HAS_TFINDER = False

try:
    import requests
    HAS_REQUESTS = True
except Exception:
    HAS_REQUESTS = False

try:
    from dateutil import parser as du_parser
    HAS_DATEUTIL = True
except Exception:
    HAS_DATEUTIL = False

# ============================================================================
# ASTROLOGICAL KNOWLEDGE BASE MODULE
# ============================================================================

class AstrologicalKnowledge:
    """Comprehensive astrological interpretations and descriptions."""
    
    SIGN_DESCRIPTIONS = {
        "Aries": {
            "symbol": "♈",
            "element": "Fire",
            "quality": "Cardinal",
            "ruling_planet": "Mars",
            "polarity": "Masculine/Yang",
            "keywords": ["Initiative", "Courage", "Leadership", "Impulsiveness", "Independence"],
            "short_description": "The pioneering warrior and fearless leader of the zodiac.",
            "full_description": """Aries is the first sign of the zodiac, representing new beginnings, raw energy, 
and the spark of life itself. Those with strong Aries placements embody the archetype of the warrior and pioneer, 
constantly seeking new challenges and adventures. Ruled by Mars, Aries natives possess innate courage and directness 
that can be both inspiring and overwhelming. This sign represents the self in its most primal form, concerned primarily 
with personal identity, survival, and assertion.""",
            "positive_traits": ["Courageous", "Confident", "Enthusiastic", "Passionate", "Optimistic", "Honest", "Dynamic"],
            "challenging_traits": ["Impulsive", "Impatient", "Aggressive", "Self-centered", "Tactless"],
            "body_parts": ["Head", "Face", "Brain"],
            "career_paths": ["Military", "Sports", "Entrepreneurship", "Emergency Services", "Surgery"],
            "life_lessons": ["Patience", "Consideration of others", "Strategic thinking", "Anger management"]
        },
        "Taurus": {
            "symbol": "♉",
            "element": "Earth",
            "quality": "Fixed",
            "ruling_planet": "Venus",
            "polarity": "Feminine/Yin",
            "keywords": ["Stability", "Sensuality", "Persistence", "Materialism", "Loyalty"],
            "short_description": "The steadfast builder who values security, beauty, and earthly pleasures.",
            "full_description": """Taurus is the second sign, representing consolidation, material manifestation, 
and appreciation of physical reality. Ruled by Venus, this sign expresses love through earthly pleasures - fine food, 
beautiful art, comfortable surroundings, and physical affection. Taurus natives have innate connection to the physical 
world and appreciate quality over quantity.""",
            "positive_traits": ["Reliable", "Patient", "Practical", "Devoted", "Stable", "Artistic", "Sensual"],
            "challenging_traits": ["Stubborn", "Possessive", "Materialistic", "Resistant to change", "Indulgent"],
            "body_parts": ["Neck", "Throat", "Thyroid"],
            "career_paths": ["Banking", "Agriculture", "Real Estate", "Fine Arts", "Culinary Arts"],
            "life_lessons": ["Flexibility", "Non-attachment", "Accepting change", "Balancing material and spiritual"]
        },
        "Gemini": {
            "symbol": "♊",
            "element": "Air",
            "quality": "Mutable",
            "ruling_planet": "Mercury",
            "polarity": "Masculine/Yang",
            "keywords": ["Communication", "Versatility", "Curiosity", "Duality", "Intellect"],
            "short_description": "The curious messenger who connects ideas, people, and perspectives.",
            "full_description": """Gemini represents communication, mental agility, and exchange of information. 
Symbolized by the Twins, Gemini embodies duality and the ability to see multiple perspectives. Ruled by Mercury, 
this sign governs all forms of communication, learning, and social connection. Gemini energy is light, quick, 
and ever-moving.""",
            "positive_traits": ["Adaptable", "Intelligent", "Witty", "Curious", "Sociable", "Quick-thinking"],
            "challenging_traits": ["Inconsistent", "Superficial", "Nervous", "Indecisive", "Scattered"],
            "body_parts": ["Arms", "Hands", "Lungs", "Nervous system"],
            "career_paths": ["Journalism", "Teaching", "Sales", "Writing", "Public Relations"],
            "life_lessons": ["Depth over breadth", "Follow-through", "Emotional awareness", "Active listening"]
        },
        "Cancer": {
            "symbol": "♋",
            "element": "Water",
            "quality": "Cardinal",
            "ruling_planet": "Moon",
            "polarity": "Feminine/Yin",
            "keywords": ["Nurturing", "Emotion", "Home", "Security", "Intuition"],
            "short_description": "The protective caregiver who creates emotional sanctuary and deep bonds.",
            "full_description": """Cancer represents emotions, nurturing, home, and the deep waters of the unconscious. 
Symbolized by the Crab, Cancer carries its home on its back and possesses both soft interior and hard protective shell. 
Ruled by the Moon, Cancer's moods wax and wane like lunar phases, deeply connected to emotional tides.""",
            "positive_traits": ["Nurturing", "Intuitive", "Loyal", "Protective", "Empathetic", "Creative"],
            "challenging_traits": ["Moody", "Clingy", "Oversensitive", "Manipulative", "Pessimistic"],
            "body_parts": ["Chest", "Breasts", "Stomach"],
            "career_paths": ["Nursing", "Childcare", "Psychology", "Real Estate", "Hospitality"],
            "life_lessons": ["Emotional boundaries", "Letting go", "Independence", "Trusting others"]
        },
        "Leo": {
            "symbol": "♌",
            "element": "Fire",
            "quality": "Fixed",
            "ruling_planet": "Sun",
            "polarity": "Masculine/Yang",
            "keywords": ["Creativity", "Drama", "Generosity", "Pride", "Leadership"],
            "short_description": "The radiant performer who expresses authentic self with confidence and flair.",
            "full_description": """Leo represents creative self-expression, personal dignity, and radiant warmth. 
Symbolized by the Lion, Leo embodies regal bearing and natural authority. Ruled by the Sun, Leo is warm, bright, 
life-giving, and impossible to ignore. Leo energy is generous, dramatic, and naturally magnetic.""",
            "positive_traits": ["Confident", "Generous", "Warm", "Creative", "Enthusiastic", "Loyal"],
            "challenging_traits": ["Arrogant", "Stubborn", "Domineering", "Vain", "Attention-seeking"],
            "body_parts": ["Heart", "Upper back", "Spine"],
            "career_paths": ["Entertainment", "Management", "Politics", "Arts", "Education"],
            "life_lessons": ["Humility", "Sharing spotlight", "Inner validation", "Service leadership"]
        },
        "Virgo": {
            "symbol": "♍",
            "element": "Earth",
            "quality": "Mutable",
            "ruling_planet": "Mercury",
            "polarity": "Feminine/Yin",
            "keywords": ["Analysis", "Service", "Perfection", "Health", "Practicality"],
            "short_description": "The discerning analyst who serves through skill, precision, and improvement.",
            "full_description": """Virgo represents analysis, refinement, service, and pursuit of perfection. 
Symbolized by the Virgin, Virgo embodies purity of intention and discrimination. Ruled by Mercury in earth-bound 
expression, Virgo channels mental energy into practical improvement and skilled craftsmanship.""",
            "positive_traits": ["Analytical", "Practical", "Hardworking", "Helpful", "Reliable", "Precise"],
            "challenging_traits": ["Critical", "Perfectionist", "Anxious", "Overly cautious", "Fussy"],
            "body_parts": ["Digestive system", "Intestines", "Abdomen"],
            "career_paths": ["Healthcare", "Editing", "Accounting", "Research", "Quality Control"],
            "life_lessons": ["Accepting imperfection", "Self-compassion", "Seeing big picture", "Receiving help"]
        },
        "Libra": {
            "symbol": "♎",
            "element": "Air",
            "quality": "Cardinal",
            "ruling_planet": "Venus",
            "polarity": "Masculine/Yang",
            "keywords": ["Balance", "Harmony", "Justice", "Partnership", "Diplomacy"],
            "short_description": "The gracious diplomat who seeks beauty, balance, and harmonious relationships.",
            "full_description": """Libra represents balance, partnership, justice, and aesthetic refinement. 
Symbolized by the Scales, Libra suggests rational, balanced approach to life. Ruled by Venus in air-sign expression, 
Libra seeks beauty through harmony, connection, and social grace.""",
            "positive_traits": ["Diplomatic", "Fair", "Charming", "Cooperative", "Artistic", "Gracious"],
            "challenging_traits": ["Indecisive", "People-pleasing", "Superficial", "Conflict-avoidant"],
            "body_parts": ["Kidneys", "Lower back", "Adrenal glands"],
            "career_paths": ["Law", "Diplomacy", "Design", "Counseling", "Fashion", "Art Curation"],
            "life_lessons": ["Making decisions", "Healthy confrontation", "Independence", "Authenticity over harmony"]
        },
        "Scorpio": {
            "symbol": "♏",
            "element": "Water",
            "quality": "Fixed",
            "ruling_planet": "Mars/Pluto",
            "polarity": "Feminine/Yin",
            "keywords": ["Transformation", "Intensity", "Power", "Sexuality", "Depth"],
            "short_description": "The transformative investigator who plumbs emotional depths and embraces power.",
            "full_description": """Scorpio represents transformation, depth, power, sexuality, and mysteries of death 
and rebirth. Symbolized by Scorpion, Eagle, and Phoenix, Scorpio embodies evolution through intensity. Ruled by Mars 
and Pluto, Scorpio combines martial force with profound transformation.""",
            "positive_traits": ["Passionate", "Resourceful", "Brave", "Loyal", "Determined", "Intuitive"],
            "challenging_traits": ["Jealous", "Possessive", "Secretive", "Manipulative", "Obsessive"],
            "body_parts": ["Reproductive organs", "Colon", "Bladder"],
            "career_paths": ["Psychology", "Surgery", "Research", "Detective Work", "Finance"],
            "life_lessons": ["Trust", "Forgiveness", "Letting go", "Healthy vulnerability", "Non-attachment"]
        },
        "Sagittarius": {
            "symbol": "♐",
            "element": "Fire",
            "quality": "Mutable",
            "ruling_planet": "Jupiter",
            "polarity": "Masculine/Yang",
            "keywords": ["Philosophy", "Adventure", "Truth", "Expansion", "Freedom"],
            "short_description": "The philosophical adventurer who seeks truth, meaning, and endless horizons.",
            "full_description": """Sagittarius represents philosophy, higher learning, travel, and quest for truth. 
Symbolized by Centaur Archer, Sagittarius combines animal instinct with human intellect. Ruled by Jupiter, this sign 
embodies optimism, growth, and the principle that life should be an adventure.""",
            "positive_traits": ["Optimistic", "Adventurous", "Honest", "Philosophical", "Generous", "Jovial"],
            "challenging_traits": ["Tactless", "Irresponsible", "Preachy", "Dogmatic", "Restless"],
            "body_parts": ["Hips", "Thighs", "Liver"],
            "career_paths": ["Teaching", "Travel Industry", "Publishing", "Law", "Ministry"],
            "life_lessons": ["Tact", "Commitment", "Follow-through", "Listening", "Respecting different truths"]
        },
        "Capricorn": {
            "symbol": "♑",
            "element": "Earth",
            "quality": "Cardinal",
            "ruling_planet": "Saturn",
            "polarity": "Feminine/Yin",
            "keywords": ["Ambition", "Discipline", "Achievement", "Structure", "Authority"],
            "short_description": "The determined achiever who climbs mountains through discipline and mastery.",
            "full_description": """Capricorn represents achievement, structure, authority, and mastery through discipline. 
Symbolized by Mountain Goat, Capricorn steadily climbs toward peaks of worldly success. Ruled by Saturn, this sign 
embodies maturity, responsibility, and understanding that anything worthwhile requires sustained effort.""",
            "positive_traits": ["Ambitious", "Disciplined", "Responsible", "Patient", "Loyal", "Practical"],
            "challenging_traits": ["Pessimistic", "Cold", "Rigid", "Workaholic", "Status-conscious"],
            "body_parts": ["Bones", "Knees", "Teeth", "Skin"],
            "career_paths": ["Business Management", "Government", "Architecture", "Finance", "Administration"],
            "life_lessons": ["Work-life balance", "Emotional expression", "Flexibility", "Self-compassion"]
        },
        "Aquarius": {
            "symbol": "♒",
            "element": "Air",
            "quality": "Fixed",
            "ruling_planet": "Saturn/Uranus",
            "polarity": "Masculine/Yang",
            "keywords": ["Innovation", "Independence", "Humanity", "Rebellion", "Progress"],
            "short_description": "The visionary humanitarian who champions progress and collective evolution.",
            "full_description": """Aquarius represents innovation, humanitarianism, friendship, and collective consciousness. 
Symbolized by Water Bearer pouring knowledge for humanity's benefit, Aquarius brings divine wisdom to earth. Ruled by 
Saturn and Uranus, combines structural understanding with revolutionary breakthrough.""",
            "positive_traits": ["Original", "Humanitarian", "Intellectual", "Independent", "Progressive"],
            "challenging_traits": ["Detached", "Stubborn", "Aloof", "Contrary", "Impersonal"],
            "body_parts": ["Ankles", "Calves", "Circulatory system"],
            "career_paths": ["Technology", "Science", "Social Work", "Aviation", "Astrology"],
            "life_lessons": ["Emotional connection", "Personal intimacy", "Practical application", "Compromise"]
        },
        "Pisces": {
            "symbol": "♓",
            "element": "Water",
            "quality": "Mutable",
            "ruling_planet": "Jupiter/Neptune",
            "polarity": "Feminine/Yin",
            "keywords": ["Compassion", "Mysticism", "Imagination", "Transcendence", "Sacrifice"],
            "short_description": "The mystical dreamer who dissolves boundaries and channels divine compassion.",
            "full_description": """Pisces represents transcendence, universal love, mysticism, and dissolution of boundaries. 
Symbolized by two Fish swimming in opposite directions, Pisces embodies tension between spiritual and material worlds. 
Ruled by Jupiter and Neptune, combines faith and expansion with mystical dissolution.""",
            "positive_traits": ["Compassionate", "Intuitive", "Artistic", "Gentle", "Wise", "Spiritual"],
            "challenging_traits": ["Escapist", "Overly trusting", "Martyr complex", "Impractical"],
            "body_parts": ["Feet", "Lymphatic system", "Immune system"],
            "career_paths": ["Arts", "Healing Professions", "Music", "Photography", "Charity Work"],
            "life_lessons": ["Boundaries", "Discernment", "Practical grounding", "Self-care", "Reality testing"]
        }
    }
    
    HOUSE_MEANINGS = {
        1: {"name": "First House (Ascendant)", "keywords": ["Self", "Identity", "Appearance"]},
        2: {"name": "Second House", "keywords": ["Values", "Resources", "Money"]},
        3: {"name": "Third House", "keywords": ["Communication", "Learning", "Siblings"]},
        4: {"name": "Fourth House (IC)", "keywords": ["Home", "Family", "Roots"]},
        5: {"name": "Fifth House", "keywords": ["Creativity", "Romance", "Children"]},
        6: {"name": "Sixth House", "keywords": ["Work", "Health", "Service"]},
        7: {"name": "Seventh House (Descendant)", "keywords": ["Partnership", "Marriage"]},
        8: {"name": "Eighth House", "keywords": ["Transformation", "Intimacy", "Shared Resources"]},
        9: {"name": "Ninth House", "keywords": ["Philosophy", "Travel", "Higher Education"]},
        10: {"name": "Tenth House (Midheaven)", "keywords": ["Career", "Reputation", "Achievement"]},
        11: {"name": "Eleventh House", "keywords": ["Friends", "Groups", "Aspirations"]},
        12: {"name": "Twelfth House", "keywords": ["Spirituality", "Unconscious", "Solitude"]}
    }
    
    @classmethod
    def get_sign_interpretation(cls, sign_name, planet_name=None):
        """Get comprehensive interpretation for a planet in a sign."""
        if sign_name not in cls.SIGN_DESCRIPTIONS:
            return f"Interpretation for {sign_name} not available."
        
        sign_info = cls.SIGN_DESCRIPTIONS[sign_name]
        lines = []
        lines.append(f"\n{'='*80}")
        if planet_name:
            lines.append(f"{planet_name} in {sign_name} {sign_info['symbol']}")
        else:
            lines.append(f"{sign_name} {sign_info['symbol']}")
        lines.append(f"{'='*80}")
        lines.append(f"Element: {sign_info['element']} | Quality: {sign_info['quality']} | Ruler: {sign_info['ruling_planet']}")
        lines.append(f"Keywords: {', '.join(sign_info['keywords'])}")
        lines.append(f"\n{sign_info['short_description']}")
        lines.append(f"\n{sign_info['full_description']}")
        lines.append(f"\nPositive Traits: {', '.join(sign_info['positive_traits'])}")
        lines.append(f"\nChallenging Traits: {', '.join(sign_info['challenging_traits'])}")
        return "\n".join(lines)
    
    @classmethod
    def get_house_interpretation(cls, house_num):
        """Get interpretation for a house."""
        if house_num not in cls.HOUSE_MEANINGS:
            return f"Interpretation for House {house_num} not available."
        
        house_info = cls.HOUSE_MEANINGS[house_num]
        return f"\n{house_info['name']} - Keywords: {', '.join(house_info['keywords'])}"

# ============================================================================
# CHART INTERPRETATION MODULE
# ============================================================================

class ChartInterpreter:
    """Generate detailed astrological interpretations from chart data."""
    
    @staticmethod
    def interpret_planet_in_sign(planet_name, sign_name, degree_in_sign):
        """Generate detailed interpretation of a planet in a specific sign."""
        lines = []
        lines.append(AstrologicalKnowledge.get_sign_interpretation(sign_name, planet_name))
        
        # Add specific planet-sign insights
        if planet_name == "Sun":
            lines.append(f"\nWith the Sun in {sign_name}, your core identity and life purpose are colored by {sign_name}'s qualities.")
        elif planet_name == "Moon":
            lines.append(f"\nWith the Moon in {sign_name}, your emotional nature and instinctive responses reflect {sign_name}'s characteristics.")
        elif planet_name == "Mercury":
            lines.append(f"\nWith Mercury in {sign_name}, your thinking style and communication patterns are shaped by {sign_name}'s approach.")
        elif planet_name == "Venus":
            lines.append(f"\nWith Venus in {sign_name}, your approach to love, beauty, and values is filtered through {sign_name}'s lens.")
        elif planet_name == "Mars":
            lines.append(f"\nWith Mars in {sign_name}, your drive, ambition, and assertiveness express through {sign_name}'s style.")
        
        # Degree analysis
        if degree_in_sign < 10:
            lines.append(f"\nAt {degree_in_sign:.2f}° (early degrees), this placement is learning {sign_name}'s lessons with fresh enthusiasm.")
        elif degree_in_sign >= 20:
            lines.append(f"\nAt {degree_in_sign:.2f}° (late degrees), this placement has mastery of {sign_name}'s qualities.")
        else:
            lines.append(f"\nAt {degree_in_sign:.2f}° (middle degrees), this placement solidly embodies {sign_name}'s core expression.")
        
        return "\n".join(lines)
    
    @staticmethod
    def interpret_planets_and_aspects(astro_data):
        """Generate comprehensive interpretation of all planets."""
        lines = []
        lines.append("\n" + "="*80)
        lines.append("COMPREHENSIVE PLANETARY INTERPRETATION")
        lines.append("="*80)
        
        planets = astro_data.get("planets", {})
        
        for pname in PLANETS:
            pdata = planets.get(pname, {})
            if isinstance(pdata, dict) and "ecl_lon" in pdata:
                sign, deg_in = sign_from_degree(pdata["ecl_lon"])
                interpretation = ChartInterpreter.interpret_planet_in_sign(pname, sign, deg_in)
                lines.append(interpretation)
                lines.append("\n" + "-"*80 + "\n")
        
        return "\n".join(lines)
    
    @staticmethod
    def interpret_chart_patterns(astro_data):
        """Identify and interpret significant chart patterns."""
        lines = []
        lines.append("\n" + "="*80)
        lines.append("CHART PATTERNS AND CONFIGURATIONS")
        lines.append("="*80)
        
        planets = astro_data.get("planets", {})
        planet_positions = {}
        
        for pname, pdata in planets.items():
            if isinstance(pdata, dict) and "ecl_lon" in pdata:
                planet_positions[pname] = pdata["ecl_lon"]
        
        # Check for stelliums (3+ planets in same sign)
        sign_counts = {}
        for pname, lon in planet_positions.items():
            sign, _ = sign_from_degree(lon)
            if sign not in sign_counts:
                sign_counts[sign] = []
            sign_counts[sign].append(pname)
        
        stelliums = {sign: planets for sign, planets in sign_counts.items() if len(planets) >= 3}
        
        if stelliums:
            lines.append("\n*** STELLIUMS DETECTED ***")
            for sign, planet_list in stelliums.items():
                lines.append(f"\nStellium in {sign}: {', '.join(planet_list)}")
                lines.append(f"A stellium represents concentration of energy in one sign, making {sign}'s themes central to life experience.")
        
        # Element balance
        element_counts = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
        for pname, lon in planet_positions.items():
            sign, _ = sign_from_degree(lon)
            sign_info = AstrologicalKnowledge.SIGN_DESCRIPTIONS.get(sign, {})
            element = sign_info.get("element")
            if element:
                element_counts[element] += 1
        
        lines.append("\n\n*** ELEMENTAL BALANCE ***")
        total = sum(element_counts.values())
        for element, count in element_counts.items():
            percentage = (count / total * 100) if total > 0 else 0
            lines.append(f"{element}: {count} planets ({percentage:.1f}%)")
        
        dominant_element = max(element_counts, key=element_counts.get)
        if element_counts[dominant_element] >= 4:
            lines.append(f"\nDominant Element: {dominant_element} - You naturally express {dominant_element}'s qualities.")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_synthesis(astro_data, cusps):
        """Generate synthetic overview of the chart's main themes."""
        lines = []
        lines.append("\n" + "="*80)
        lines.append("CHART SYNTHESIS: MAJOR THEMES AND LIFE PURPOSE")
        lines.append("="*80)
        
        planets = astro_data.get("planets", {})
        sun_data = planets.get("Sun", {})
        moon_data = planets.get("Moon", {})
        
        if "ecl_lon" in sun_data:
            sun_sign, sun_deg = sign_from_degree(sun_data["ecl_lon"])
            lines.append(f"\n*** CORE IDENTITY (Sun in {sun_sign}) ***")
            lines.append(f"Your essential self and life purpose are fundamentally {sun_sign}.")
        
        if "ecl_lon" in moon_data:
            moon_sign, moon_deg = sign_from_degree(moon_data["ecl_lon"])
            lines.append(f"\n*** EMOTIONAL NATURE (Moon in {moon_sign}) ***")
            lines.append(f"Your emotional needs and instinctive reactions are colored by {moon_sign}.")
        
        # Ascendant
        if cusps.get("Placidus"):
            asc = cusps["Placidus"][0]
            asc_sign, asc_deg = sign_from_degree(asc)
            lines.append(f"\n*** OUTER PERSONALITY (Ascendant in {asc_sign}) ***")
            lines.append(f"Your physical appearance and first impressions are {asc_sign}.")
            lines.append(f"This is your social mask and life strategy.")
        
        return "\n".join(lines)

# ---------------------------
# Utility functions
# ---------------------------
def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def eprint(*a, **k): 
    print(*a, file=sys.stderr, **k)

def try_install_hint(pkg_list):
    eprint("Some optional functionality needs additional packages.")
    eprint("You can run: python3 -m pip install " + " ".join(pkg_list))

def sign_from_degree(deg):
    deg = deg % 360
    idx = int(deg//30)
    sign = SIGNS[idx]
    deg_in_sign = deg - idx*30
    return sign, deg_in_sign

def aspects_between(a_deg, b_deg):
    dif = abs((a_deg - b_deg + 180) % 360 - 180)
    aspects = []
    table = {0:("Conjunction",8), 180:("Opposition",8), 120:("Trine",7), 
             60:("Sextile",6), 90:("Square",6), 150:("Quincunx",3)}
    for ang,(name,orb) in table.items():
        if abs(dif - ang) <= orb:
            aspects.append((name, ang, dif))
    return aspects

# ---------------------------
# Input parsing helpers
# ---------------------------
def parse_date_input(raw_date, preferred_format=None):
    """Parse DD/MM/YYYY or MM/DD/YYYY with disambiguation."""
    raw = raw_date.strip()
    parts = raw.split("/")
    if len(parts) != 3:
        raise ValueError("Date must be in DD/MM/YYYY or MM/DD/YYYY format")
    a, b, c = parts
    if len(c) == 4 and len(a) <= 2:  # Normal format
        try:
            d1 = int(a); d2 = int(b); y = int(c)
        except Exception:
            raise ValueError("Invalid numeric date parts")
        
        ambiguous = (d1 <= 12 and d2 <= 12)
        if not ambiguous:
            if d1 > 12:
                return datetime(y, d2, d1).date()
            else:
                return datetime(y, d1, d2).date()
        
        if preferred_format == 'DMY':
            return datetime(y, d2, d1).date()
        if preferred_format == 'MDY':
            return datetime(y, d1, d2).date()
        
        # Interactive confirmation
        print(f"Ambiguous date {raw}. Interpret as:")
        print(f"  1) DD/MM/YYYY -> {d1}/{d2}/{y}")
        print(f"  2) MM/DD/YYYY -> {d2}/{d1}/{y}")
        choice = input("Choose 1 or 2 (default 1): ").strip() or "1"
        if choice.startswith("2"):
            return datetime(y, d1, d2).date()
        return datetime(y, d2, d1).date()
    else:
        return datetime.fromisoformat(raw).date()

def parse_time_input(raw_time, tz_hint=None):
    """Parse time with AM/PM support."""
    s = raw_time.strip()
    parts = s.split()
    time_part = parts[0]
    tz_part = None
    if len(parts) > 1:
        tz_part = parts[-1]
    
    if HAS_DATEUTIL:
        dt = du_parser.parse(time_part + ((" " + tz_part) if tz_part else ""))
        tzinfo = None
        if tz_part:
            tzinfo = resolve_tz(tz_part)
        return dt.time(), tzinfo
    else:
        # Basic parse
        if ":" not in time_part:
            raise ValueError("Time must include ':'")
        hh, mm = time_part.split(":")
        hh = int(hh); mm = int(mm)
        tzinfo = resolve_tz(tz_part) if tz_part else None
        return datetime(2000, 1, 1, hh, mm).time(), tzinfo

def resolve_tz(tz_input):
    """Map timezone abbreviations to IANA."""
    if not tz_input:
        return None
    s = tz_input.strip()
    if s.upper() in TZ_ABBREV_MAP:
        try:
            return ZoneInfo(TZ_ABBREV_MAP[s.upper()])
        except Exception:
            return ZoneInfo("UTC")
    if s.upper().startswith("UTC"):
        rest = s[3:]
        if not rest:
            return timezone.utc
        sign = 1
        if rest[0] in "+-":
            sign = 1 if rest[0] == "+" else -1
            rest = rest[1:]
        parts = rest.split(":")
        hh = int(parts[0]) if parts[0] else 0
        mm = int(parts[1]) if len(parts) > 1 else 0
        return timezone(timedelta(hours=sign*hh, minutes=sign*mm))
    try:
        return ZoneInfo(s)
    except Exception:
        print(f"Warning: unknown timezone '{s}', defaulting to UTC")
        return timezone.utc

# ---------------------------
# Geocoding helpers
# ---------------------------
def geocode_location(input_loc, prefer_online=True, max_retries=5):
    """Geocode location from various inputs."""
    s = str(input_loc).strip()
    
    # Detect lat/lon patterns
    if any(ch.isdigit() for ch in s) and ("N" in s or "S" in s or "E" in s or "W" in s or "-" in s):
        nums = []
        for t in s.replace("N", " ").replace("S", " ").replace("E", " ").replace("W", " ").replace(",", " ").split():
            try:
                nums.append(float(t))
            except:
                pass
        if len(nums) >= 2:
            flat = nums[0]; flon = nums[1]
            if "W" in s.upper() and flon > 0:
                flon = -abs(flon)
            if "S" in s.upper() and flat > 0:
                flat = -abs(flat)
            tzname = None
            if HAS_TFINDER:
                try:
                    tf = TimezoneFinder()
                    tzname = tf.timezone_at(lng=flon, lat=flat)
                except Exception:
                    tzname = None
            return flat, flon, f"Coords {flat},{flon}", tzname
    
    # Zipcode lookup
    if s.isdigit() and os.path.exists(ZIPFILE):
        with open(ZIPFILE, "r", encoding="utf-8") as fh:
            for line in fh:
                parts = line.strip().split(",")
                if parts and parts[0] == s:
                    try:
                        lat = float(parts[1]); lon = float(parts[2])
                        city = parts[3] if len(parts) > 3 else ""
                        state = parts[4] if len(parts) > 4 else ""
                        tzname = None
                        if HAS_TFINDER:
                            try:
                                tf = TimezoneFinder()
                                tzname = tf.timezone_at(lng=lon, lat=lat)
                            except Exception:
                                pass
                        return lat, lon, f"{city},{state}", tzname
                    except:
                        continue
    
    # Nominatim online geocoding
    if prefer_online and HAS_REQUESTS and HAS_GEOPY:
        try:
            geolocator = Nominatim(user_agent="astrocharts/1.0")
            location = geolocator.geocode(s, timeout=10)
            if location:
                lat = location.latitude
                lon = location.longitude
                display = location.address
                tzname = None
                if HAS_TFINDER:
                    try:
                        tf = TimezoneFinder()
                        tzname = tf.timezone_at(lng=lon, lat=lat)
                    except Exception:
                        pass
                return lat, lon, display, tzname
        except Exception:
            pass
    
    raise ValueError("Could not geocode location")

# ---------------------------
# Astronomical / Ephemeris
# ---------------------------
def jd_from_datetime(dt_utc):
    """Convert datetime to Julian Day."""
    if dt_utc.tzinfo is None:
        raise ValueError("datetime must be timezone-aware UTC")
    t = dt_utc.astimezone(timezone.utc)
    year = t.year; month = t.month; day = t.day
    hour = t.hour + t.minute/60 + t.second/3600 + t.microsecond/3.6e9
    if month <= 2:
        year -= 1; month += 12
    A = year // 100
    B = 2 - A + A//4
    jd = int(365.25*(year+4716)) + int(30.6001*(month+1)) + day + B - 1524.5 + hour/24.0
    return jd

def compute_planet_positions_swisseph(jd_ut, lat, lon, eph_path=None):
    """Use swisseph for planet positions."""
    res = {}
    if eph_path:
        swe.set_ephe_path(eph_path)
    try:
        swe.set_topo(lon, lat, 0)
    except Exception:
        pass
    
    sw_planets = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY, "Venus": swe.VENUS,
        "Mars": swe.MARS, "Jupiter": swe.JUPITER, "Saturn": swe.SATURN,
        "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE, "Pluto": swe.PLUTO
    }
    res["planets"] = {}
    for name, pconst in sw_planets.items():
        try:
            lonlat_dist = swe.calc_ut(jd_ut, pconst)
            res["planets"][name] = {
                "ecl_lon": lonlat_dist[0],
                "ecl_lat": lonlat_dist[1],
                "distance_au": lonlat_dist[2] if len(lonlat_dist) > 2 else None
            }
        except Exception as e:
            res["planets"][name] = {"error": str(e)}
    
    # Houses
    houses = {}
    try:
        asc_mc, cusp = swe.houses(jd_ut, lat, lon, b'P')
        houses['Placidus'] = {"ascendant": asc_mc[0], "mc": asc_mc[1], "cusps": list(cusp)}
        
        asc_mc_e, cusp_e = swe.houses(jd_ut, lat, lon, b'E')
        houses['Equal'] = {"ascendant": asc_mc_e[0], "mc": asc_mc_e[1], "cusps": list(cusp_e)}
        
        asc = asc_mc[0]
        asc_sign = int(asc//30)
        whole_cusps = [((asc_sign + i)*30) % 360 for i in range(12)]
        houses['Whole'] = {"ascendant": asc, "mc": asc_mc[1], "cusps": whole_cusps}
        
        try:
            asc_mc_c, cusp_c = swe.houses(jd_ut, lat, lon, b'C')
            houses['Campanus'] = {"ascendant": asc_mc_c[0], "mc": asc_mc_c[1], "cusps": list(cusp_c)}
        except Exception:
            houses['Campanus'] = {"method_note": "approximate"}
    except Exception as e:
        houses['error'] = str(e)
    
    res["houses"] = houses
    return res

def compute_planet_positions_skyfield(dt_utc, lat, lon):
    """Skyfield fallback for planet positions."""
    ts = load.timescale()
    t = ts.utc(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour, dt_utc.minute, dt_utc.second)
    eph = load('de421.bsp')
    earth = eph['earth']
    
    res = {"planets": {}}
    for name in PLANETS:
        try:
            if name.lower() in ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune']:
                body = eph[name.lower()]
                astrometric = earth.at(t).observe(body)
                ra, dec, dist = astrometric.radec()
                # Approximate ecliptic conversion
                lon_ecl = math.degrees(math.atan2(dec.radians, ra.radians)) % 360
                res["planets"][name] = {"ecl_lon": lon_ecl, "ecl_lat": 0, "distance_km": dist.km}
            else:
                res["planets"][name] = {"error": "not in ephemeris"}
        except Exception as e:
            res["planets"][name] = {"error": str(e)}
    
    return res

# ---------------------------
# House approximations
# ---------------------------
def equal_house_cusps(asc):
    asc = asc % 360
    return [(asc + i*30) % 360 for i in range(12)]

def whole_sign_cusps(asc):
    asc = asc % 360
    sign_start = (asc//30)*30
    return [(sign_start + i*30) % 360 for i in range(12)]

def porphyry_cusps(asc, mc):
    asc = asc % 360; mc = mc % 360
    ic = (mc + 180) % 360
    dsc = (asc + 180) % 360
    cusps = []
    pts = {"asc": asc, "mc": mc, "dsc": dsc, "ic": ic}
    for (a, b) in [("asc", "mc"), ("mc", "dsc"), ("dsc", "ic"), ("ic", "asc")]:
        start = pts[a]; end = pts[b]
        span = (end - start) % 360
        for i in range(3):
            cusps.append((start + span*(i/3)) % 360)
    return [round(c, 6) for c in cusps[:12]]

# ---------------------------
# Historical events
# ---------------------------
def fetch_events_on_date(dt, prefer_online=True):
    """Fetch historical events for date."""
    events = []
    if prefer_online and HAS_REQUESTS:
        url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/all/{dt.month}/{dt.day}"
        try:
            r = requests.get(url, timeout=10, headers={"User-Agent": "astrocharts/1.0"})
            if r.status_code == 200:
                data = r.json()
                for cat in ("births", "events", "deaths"):
                    for item in data.get(cat, [])[:5]:
                        year = item.get("year")
                        text = item.get("text") or item.get("pages", [{}])[0].get("extract")
                        events.append({"category": cat, "year": year, "text": text})
                return events
        except Exception:
            pass
    
    # Fallback to cache
    if os.path.exists(EVENTS_CACHE):
        try:
            with open(EVENTS_CACHE, "r", encoding="utf-8") as fh:
                cache = json.load(fh)
                key = f"{dt.month:02d}-{dt.day:02d}"
                return cache.get(key, [])
        except Exception:
            return []
    return []

# ---------------------------
# Output formatting
# ---------------------------
def write_text_file(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)

def create_simple_wheel_png(planet_positions, cusps, outpath):
    """Create PNG wheel with PIL."""
    if not HAS_PIL:
        return False
    size = 1200
    img = Image.new("RGBA", (size, size), "white")
    draw = ImageDraw.Draw(img)
    center = (size//2, size//2)
    radius = int(size*0.4)
    
    draw.ellipse((center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius), 
                 outline="black", width=3)
    
    for c in cusps:
        ang = math.radians((90 - c) % 360)
        x = center[0] + radius*math.cos(ang)
        y = center[1] - radius*math.sin(ang)
        draw.line([center, (x, y)], fill="black", width=2)
    
    for pname, pdata in planet_positions.items():
        lon = pdata.get("ecl_lon")
        if lon is None:
            continue
        ang = math.radians((90 - lon) % 360)
        pr = radius*0.85
        x = center[0] + pr*math.cos(ang)
        y = center[1] - pr*math.sin(ang)
        draw.text((x-10, y-10), pname[0], fill="red")
    
    img.save(outpath)
    return True

def create_plotly_wheel(planet_positions, cusps, outpath_html):
    """Create interactive HTML wheel with Plotly."""
    if not HAS_PLOTLY:
        return False
    
    labels = []
    angles = []
    for pname, pdata in planet_positions.items():
        lon = pdata.get("ecl_lon")
        if lon is None: 
            continue
        labels.append(pname)
        angles.append(lon)
    
    fig = go.Figure()
    fig.add_trace(go.Barpolar(
        theta=angles, 
        r=[1]*len(angles), 
        text=labels, 
        marker_color="indianred"
    ))
    fig.update_layout(
        template=None, 
        title="Astrological Chart - Planet Positions"
    )
    fig.write_html(outpath_html)
    return True

# ---------------------------
# Main calculation pipeline
# ---------------------------
def generate_chart(mode, date_str, time_str, tz_input, location_input, 
                   date_format_pref=None, interactive=True):
    """Main chart generation function."""
    ensure_dirs()
    
    # Parse inputs
    dt_date = parse_date_input(date_str, preferred_format=date_format_pref)
    ttime, tzinfo = parse_time_input(time_str, tz_hint=tz_input)
    tzinfo = tzinfo or resolve_tz(tz_input)
    
    # Create datetime
    if tzinfo:
        local_dt = datetime.combine(dt_date, ttime).replace(tzinfo=tzinfo)
    else:
        local_dt = datetime.combine(dt_date, ttime).replace(tzinfo=timezone.utc)
    
    dt_utc = local_dt.astimezone(timezone.utc)
    
    # Geocode
    geo_lat, geo_lon, geo_display, tzname = geocode_location(location_input, prefer_online=(mode != "Paranoid"))
    
    if tzname and not tzinfo:
        try:
            tzinfo = ZoneInfo(tzname)
            local_dt = datetime.combine(dt_date, ttime).replace(tzinfo=tzinfo)
            dt_utc = local_dt.astimezone(timezone.utc)
        except Exception:
            pass
    
    # Compute ephemeris
    jd_ut = jd_from_datetime(dt_utc)
    astro = {}
    
    if HAS_PYSWISSEPH and mode != "Paranoid":
        try:
            swe.set_ephe_path(DATA_DIR)
            astro = compute_planet_positions_swisseph(jd_ut, geo_lat, geo_lon)
        except Exception as e:
            eprint("Swiss Ephemeris error:", e)
            if HAS_SKYFIELD:
                astro = compute_planet_positions_skyfield(dt_utc, geo_lat, geo_lon)
    elif HAS_SKYFIELD:
        astro = compute_planet_positions_skyfield(dt_utc, geo_lat, geo_lon)
    else:
        astro = {"error": "No ephemeris backend available"}
    
    # Extract houses
    if "houses" in astro and "Placidus" in astro["houses"]:
        asc = astro["houses"]["Placidus"]["ascendant"]
        mc = astro["houses"]["Placidus"]["mc"]
    else:
        asc = 0.0; mc = 0.0
    
    # Compute all house systems
    cusps = {}
    if "houses" in astro:
        cusps = astro["houses"]
    else:
        cusps['Placidus'] = {"cusps": equal_house_cusps(asc)}
    
    cusps['Equal'] = {"cusps": equal_house_cusps(asc)}
    cusps['Whole'] = {"cusps": whole_sign_cusps(asc)}
    cusps['Porphyry'] = {"cusps": porphyry_cusps(asc, mc)}
    
    # Generate verbose output
    verbose_lines = []
    verbose_lines.append(f"Chart Generated: {datetime.now().isoformat()}")
    verbose_lines.append(f"Input Date: {dt_date.isoformat()}")
    verbose_lines.append(f"Local Time: {local_dt.isoformat()}")
    verbose_lines.append(f"UTC Time: {dt_utc.isoformat()}")
    verbose_lines.append(f"Location: {geo_display}")
    verbose_lines.append(f"Coordinates: {geo_lat:.4f}, {geo_lon:.4f}")
    verbose_lines.append(f"Mode: {mode}")
    verbose_lines.append("")
    verbose_lines.append("="*80)
    verbose_lines.append("PLANETARY POSITIONS")
    verbose_lines.append("="*80)
    
    for pname, pdata in astro.get("planets", {}).items():
        if isinstance(pdata, dict) and "ecl_lon" in pdata:
            sign, deg_in = sign_from_degree(pdata["ecl_lon"])
            verbose_lines.append(f"{pname:10s}: {pdata['ecl_lon']:7.3f}° - {sign} {deg_in:.2f}°")
    
    verbose_lines.append("")
    verbose_lines.append("="*80)
    verbose_lines.append("HOUSE CUSPS")
    verbose_lines.append("="*80)
    for sysname, sysdata in cusps.items():
        if "cusps" in sysdata:
            verbose_lines.append(f"\n{sysname}:")
            for i, c in enumerate(sysdata["cusps"][:12], 1):
                sign, deg = sign_from_degree(c)
                verbose_lines.append(f"  House {i:2d}: {c:7.3f}° ({sign} {deg:.2f}°)")
    
    # Summary output
    summary_lines = []
    summary_lines.append("ASTROLOGICAL CHART SUMMARY")
    summary_lines.append("="*80)
    for pname, pdata in astro.get("planets", {}).items():
        if isinstance(pdata, dict) and "ecl_lon" in pdata:
            sign, deg_in = sign_from_degree(pdata["ecl_lon"])
            ruler = RULERS.get(sign, "Unknown")
            summary_lines.append(f"{pname} in {sign} {deg_in:.1f}° (ruler: {ruler})")
    
    # Historical events
    events = fetch_events_on_date(dt_date, prefer_online=(mode != "Paranoid"))
    event_lines = ["\n" + "="*80, "HISTORICAL EVENTS ON THIS DATE", "="*80]
    if events:
        for ev in events[:8]:
            event_lines.append(f"[{ev.get('category')}] {ev.get('year')}: {ev.get('text', '')[:100]}")
    else:
        event_lines.append("No events found.")
    
    # Generate interpretations
    interpretation_lines = []
    interpretation_lines.append("DETAILED ASTROLOGICAL INTERPRETATION")
    interpretation_lines.append("="*80)
    interpretation_lines.append(ChartInterpreter.interpret_planets_and_aspects(astro))
    interpretation_lines.append(ChartInterpreter.interpret_chart_patterns(astro))
    interpretation_lines.append(ChartInterpreter.generate_synthesis(astro, cusps))
    
    # Write outputs
    write_text_file(OUT_VERBOSE, "\n".join(verbose_lines))
    write_text_file(OUT_SUMMARY, "\n".join(summary_lines + event_lines))
    write_text_file(OUT_INTERPRETATION, "\n".join(interpretation_lines))
    
    with open(OUT_ASTRO_RAW, "w", encoding="utf-8") as fh:
        json.dump({
            "input": {
                "date": dt_date.isoformat(),
                "local_time": local_dt.isoformat(),
                "utc": dt_utc.isoformat(),
                "location": {"lat": geo_lat, "lon": geo_lon, "display": geo_display}
            },
            "astro": astro,
            "cusps": {k: v.get("cusps", []) for k, v in cusps.items()},
            "events": events
        }, fh, indent=2)
    
    # Generate visualizations
    planet_pos = astro.get("planets", {})
    placidus_cusps = cusps.get("Placidus", {}).get("cusps", [])
    
    create_simple_wheel_png(planet_pos, placidus_cusps, OUT_WHEEL_PNG)
    create_plotly_wheel(planet_pos, placidus_cusps, OUT_WHEEL_HTML)
    
    # PDF report
    if HAS_FPDF:
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)
            pdf.multi_cell(0, 5, "\n".join(verbose_lines[:50]))
            if os.path.exists(OUT_WHEEL_PNG):
                pdf.add_page()
                pdf.image(OUT_WHEEL_PNG, x=10, w=190)
            pdf.output(OUT_PDF)
        except Exception as e:
            eprint(f"PDF generation failed: {e}")
    
    # Print results
    print("\n" + "="*80)
    print("CHART GENERATION COMPLETE")
    print("="*80)
    print(f"Outputs written to '{OUTPUT_DIR}' directory:")
    print(f"  - Verbose chart:     {OUT_VERBOSE}")
    print(f"  - Summary:           {OUT_SUMMARY}")
    print(f"  - Interpretation:    {OUT_INTERPRETATION}")
    print(f"  - Raw JSON:          {OUT_ASTRO_RAW}")
    print(f"  - Wheel PNG:         {OUT_WHEEL_PNG}" if HAS_PIL else "  - Wheel PNG: (PIL not available)")
    print(f"  - Wheel HTML:        {OUT_WHEEL_HTML}" if HAS_PLOTLY else "  - Wheel HTML: (Plotly not available)")
    print(f"  - PDF Report:        {OUT_PDF}" if HAS_FPDF else "  - PDF Report: (FPDF not available)")
    print("="*80)
    
    return True

# ---------------------------
# CLI / Interactive interface
# ---------------------------
def interactive_mode():
    """Interactive prompts for chart generation."""
    print("\n" + "="*80)
    print("ASTROLOGICAL CHART GENERATOR - Interactive Mode")
    print("="*80)
    print("\nModes:")
    print("  - Nostradamus: High-accuracy (requires pyswisseph)")
    print("  - Ptolemy: Fallback mode (Skyfield)")
    print("  - Paranoid: Offline-only mode")
    
    mode_choice = input("\nChoose mode [Nostradamus/Ptolemy/Paranoid] (default: Nostradamus): ").strip() or "Nostradamus"
    
    date_format_pref = None
    df_choice = input("\nDate format: (1) DD/MM/YYYY or (2) MM/DD/YYYY or (3) ask each time [default: 3]: ").strip()
    if df_choice == "1": 
        date_format_pref = "DMY"
    elif df_choice == "2": 
        date_format_pref = "MDY"
    
    date_str = input("\nEnter birth date (DD/MM/YYYY or MM/DD/YYYY): ").strip()
    time_str = input("Enter birth time (e.g., 14:30 or 2:30 PM): ").strip()
    tz_hint = input("Timezone (e.g., PST, America/New_York, or press Enter): ").strip() or None
    location = input("Location (City, State, Country OR zipcode OR lat,lon): ").strip()
    
    print("\nGenerating chart...")
    try:
        generate_chart(mode_choice, date_str, time_str, tz_hint, location, 
                      date_format_pref=date_format_pref, interactive=True)
    except Exception as e:
        eprint(f"\nError generating chart: {e}")
        traceback.print_exc()

def cli_mode(args):
    """CLI mode for non-interactive usage."""
    generate_chart(args.mode, args.date, args.time, args.tz, args.location, 
                  date_format_pref=args.datefmt, interactive=False)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Complete Astrological Chart Generator with Detailed Interpretations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive mode:
    python sistema_complete.py --interactive
  
  CLI mode:
    python sistema_complete.py --date "15/08/1990" --time "14:30 PST" --location "San Francisco, CA"
    python sistema_complete.py --mode Ptolemy --date "08/15/1990" --time "2:30 PM" --tz "America/Los_Angeles" --location "37.7749,-122.4194"
    
Modes:
  - Nostradamus: High-accuracy using Swiss Ephemeris (requires pyswisseph)
  - Ptolemy: Fallback mode using Skyfield
  - Paranoid: Offline-only mode using cached data
  
Output files (saved to outputs/ directory):
  - chart_verbose.txt: Detailed technical chart data
  - chart_summary.txt: Concise planet placements and historical events
  - chart_interpretation.txt: Complete astrological interpretation
  - astro_data_raw.json: Machine-readable astronomical data
  - chart_wheel.png: Visual chart wheel (requires PIL)
  - chart_wheel.html: Interactive chart wheel (requires Plotly)
  - chart_report.pdf: Complete PDF report (requires fpdf)
        """
    )
    
    parser.add_argument("--mode", 
                       choices=["Nostradamus", "Ptolemy", "Paranoid"], 
                       default="Nostradamus", 
                       help="Computation mode (default: Nostradamus)")
    parser.add_argument("--date", 
                       help="Birth date: DD/MM/YYYY or MM/DD/YYYY")
    parser.add_argument("--time", 
                       help="Birth time: '14:30' or '2:30 PM' (optionally with timezone)")
    parser.add_argument("--tz", 
                       help="Timezone: 'PST', 'America/Los_Angeles', 'UTC', etc.")
    parser.add_argument("--location", 
                       help="Location: 'City, State, Country', 'zipcode', or 'lat,lon'")
    parser.add_argument("--datefmt", 
                       choices=["DMY", "MDY"], 
                       help="Date format preference for ambiguous dates")
    parser.add_argument("--interactive", "-i",
                       action="store_true", 
                       help="Run in interactive mode with prompts")
    
    args = parser.parse_args()
    
    ensure_dirs()
    
    # Check dependencies and provide hints
    if args.mode == "Nostradamus" and not HAS_PYSWISSEPH:
        eprint("\nWARNING: Swiss Ephemeris (pyswisseph) not detected.")
        eprint("Nostradamus mode will fallback to Ptolemy calculations.")
        eprint("\nRecommended packages for full functionality:")
        try_install_hint([
            "pyswisseph", "skyfield", "matplotlib", "plotly", 
            "pillow", "fpdf", "timezonefinder", "geopy", "requests", "python-dateutil"
        ])
        print()
    
    # Dependency status
    if args.interactive or (not args.date and not args.time and not args.location):
        print("\nDependency Status:")
        print(f"  Swiss Ephemeris (pyswisseph): {'✓' if HAS_PYSWISSEPH else '✗'}")
        print(f"  Skyfield:                     {'✓' if HAS_SKYFIELD else '✗'}")
        print(f"  PIL (Pillow):                 {'✓' if HAS_PIL else '✗'}")
        print(f"  Plotly:                       {'✓' if HAS_PLOTLY else '✗'}")
        print(f"  FPDF:                         {'✓' if HAS_FPDF else '✗'}")
        print(f"  TimezoneFinder:               {'✓' if HAS_TFINDER else '✗'}")
        print(f"  Geopy:                        {'✓' if HAS_GEOPY else '✗'}")
        print(f"  Requests:                     {'✓' if HAS_REQUESTS else '✗'}")
        print(f"  python-dateutil:              {'✓' if HAS_DATEUTIL else '✗'}")
        print()
        interactive_mode()
    else:
        if not (args.date and args.time and args.location):
            parser.error("For CLI mode, provide --date, --time, and --location (or use --interactive)")
        cli_mode(args)

if __name__ == "__main__":
    main()
