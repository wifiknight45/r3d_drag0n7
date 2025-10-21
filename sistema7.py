RULERS = {
    "Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon",
    "Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars",
    "Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"
}
SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

# ============================================================================
# CHART INTERPRETATION MODULE
# ============================================================================

class ChartInterpreter:
    """Generate detailed astrological interpretations from chart data."""
    
    @staticmethod
    def interpret_planet_in_sign(planet_name, sign_name, degree_in_sign):
        """Generate detailed interpretation of a planet in a specific sign."""
        knowledge = AstrologicalKnowledge
        
        lines = []
        lines.append(knowledge.get_sign_interpretation(sign_name, planet_name))
        
        # Add specific planet-sign combination insights
        if planet_name == "Sun":
            lines.append(f"\nWith the Sun in {sign_name}, your core identity and life purpose are colored by {sign_name}'s qualities.")
            lines.append(f"You shine brightest when expressing {sign_name}'s positive traits.")
        elif planet_name == "Moon":
            lines.append(f"\nWith the Moon in {sign_name}, your emotional nature and instinctive responses reflect {sign_name}'s characteristics.")
            lines.append(f"You feel most secure and nurtured when embodying {sign_name}'s energy.")
        elif planet_name == "Mercury":
            lines.append(f"\nWith Mercury in {sign_name}, your thinking style and communication patterns are shaped by {sign_name}'s approach.")
            lines.append(f"You learn and process information in a distinctly {sign_name} manner.")
        elif planet_name == "Venus":
            lines.append(f"\nWith Venus in {sign_name}, your approach to love, beauty, and values is filtered through {sign_name}'s lens.")
            lines.append(f"You attract and appreciate partners who embody {sign_name} qualities.")
        elif planet_name == "Mars":
            lines.append(f"\nWith Mars in {sign_name}, your drive, ambition, and assertiveness express through {sign_name}'s style.")
            lines.append(f"You pursue your desires and handle conflict in a characteristically {sign_name} way.")
        
        # Degree analysis (early, middle, late degrees have different expressions)
        if degree_in_sign < 10:
            lines.append(f"\nAt {degree_in_sign:.2f}° (early degrees), this placement is still learning {sign_name}'s lessons.")
            lines.append(f"The energy may be more impulsive, enthusiastic, or undeveloped in its expression.")
        elif degree_in_sign >= 20:
            lines.append(f"\nAt {degree_in_sign:.2f}° (late degrees), this placement has mastery of {sign_name}'s qualities.")
            lines.append(f"The energy is more mature, refined, and ready to transition to the next phase.")
        else:
            lines.append(f"\nAt {degree_in_sign:.2f}° (middle degrees), this placement is solidly embodying {sign_name}'s core expression.")
        
        return "\n".join(lines)
    
    @staticmethod
    def interpret_planets_and_aspects(astro_data):
        """Generate comprehensive interpretation of all planets and their aspects."""
        lines = []
        lines.append("\n" + "="*80)
        lines.append("COMPREHENSIVE PLANETARY INTERPRETATION")
        lines.append("="*80)
        
        planets = astro_data.get("planets", {})
        
        # Interpret each planet
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
                lines.append(f"A stellium represents a concentration of energy in one sign, making {sign}'s")
                lines.append(f"themes central to your life experience. With {len(planet_list)} planets here,")
                lines.append(f"you strongly embody {sign}'s qualities for better or worse. This is a defining")
                lines.append(f"feature of your chart and personality.")
        
        # Check for T-squares and Grand Crosses
        lines.append("\n\n*** ASPECT PATTERNS ***")
        lines.append("\nAnalyzing major aspect configurations...")
        
        # Check elements balance
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
        
        # Interpret elemental balance
        dominant_element = max(element_counts, key=element_counts.get)
        lacking_element = min(element_counts, key=element_counts.get)
        
        lines.append(f"\nDominant Element: {dominant_element}")
        if element_counts[dominant_element] >= 4:
            lines.append(f"With strong {dominant_element} emphasis, you naturally express {dominant_element}'s qualities:")
            if dominant_element == "Fire":
                lines.append("Initiative, enthusiasm, courage, and inspirational leadership.")
            elif dominant_element == "Earth":
                lines.append("Practicality, stability, material focus, and methodical building.")
            elif dominant_element == "Air":
                lines.append("Intellectual analysis, communication, social connection, and objective perspective.")
            elif dominant_element == "Water":
                lines.append("Emotional depth, intuition, empathy, and psychic sensitivity.")
        
        if element_counts[lacking_element] == 0:
            lines.append(f"\nLacking Element: {lacking_element}")
            lines.append(f"With no planets in {lacking_element} signs, you may struggle with {lacking_element}'s qualities")
            lines.append(f"or overcompensate in this area. This represents a developmental challenge.")
            if lacking_element == "Fire":
                lines.append("You may need to consciously develop initiative, courage, and spontaneous action.")
            elif lacking_element == "Earth":
                lines.append("You may need to consciously develop practical skills, patience, and material awareness.")
            elif lacking_element == "Air":
                lines.append("You may need to consciously develop objectivity, communication skills, and rational thinking.")
            elif lacking_element == "Water":
                lines.append("You may need to consciously develop emotional awareness, empathy, and intuitive connection.")
        
        return "\n".join(lines)
    
    @staticmethod
    def interpret_houses(astro_data, cusps):
        """Interpret house placements and their significance."""
        lines = []
        lines.append("\n" + "="*80)
        lines.append("HOUSE SYSTEM ANALYSIS")
        lines.append("="*80)
        
        # Determine which planets fall in which houses
        planets = astro_data.get("planets", {})
        placidus_cusps = cusps.get("Placidus", [])
        
        if not placidus_cusps or len(placidus_cusps) < 12:
            lines.append("\nHouse calculations unavailable.")
            return "\n".join(lines)
        
        house_occupants = {i: [] for i in range(1, 13)}
        
        for pname, pdata in planets.items():
            if isinstance(pdata, dict) and "ecl_lon" in pdata:
                lon = pdata["ecl_lon"]
                # Find which house this planet occupies
                for i in range(12):
                    cusp_start = placidus_cusps[i]
                    cusp_end = placidus_cusps[(i + 1) % 12]
                    
                    # Handle cusp wrap-around at 0/360 degrees
                    if cusp_start < cusp_end:
                        if cusp_start <= lon < cusp_end:
                            house_occupants[i + 1].append(pname)
                            break
                    else:  # Wraps around 0
                        if lon >= cusp_start or lon < cusp_end:
                            house_occupants[i + 1].append(pname)
                            break
        
        # Interpret each occupied house
        for house_num in range(1, 13):
            occupants = house_occupants[house_num]
            lines.append(f"\n{AstrologicalKnowledge.get_house_interpretation(house_num)}")
            
            if occupants:
                lines.append(f"\nPlanets in this house: {', '.join(occupants)}")
                lines.append(f"With {len(occupants)} planet(s) here, this life area receives significant focus and energy.")
                
                for planet in occupants:
                    if planet in planets and "ecl_lon" in planets[planet]:
                        sign, deg = sign_from_degree(planets[planet]["ecl_lon"])
                        lines.append(f"\n{planet} in House {house_num} ({sign}):")
                        lines.append(f"  {planet}'s energy expresses through {AstrologicalKnowledge.HOUSE_MEANINGS[house_num]['name']} matters,")
                        lines.append(f"  colored by {sign}'s approach.")
            else:
                lines.append(f"\nNo planets in this house.")
                lines.append(f"This life area may receive less conscious focus, operating more through the sign on the cusp.")
            
            lines.append("\n" + "-"*60)
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_synthesis(astro_data, cusps):
        """Generate a synthetic overview of the chart's main themes."""
        lines = []
        lines.append("\n" + "="*80)
        lines.append("CHART SYNTHESIS: MAJOR THEMES AND LIFE PURPOSE")
        lines.append("="*80)
        
        planets = astro_data.get("planets", {})
        
        # Sun, Moon, Ascendant form the core trinity
        sun_data = planets.get("Sun", {})
        moon_data = planets.get("Moon", {})
        
        if "ecl_lon" in sun_data:
            sun_sign, sun_deg = sign_from_degree(sun_data["ecl_lon"])
            lines.append(f"\n*** CORE IDENTITY (Sun in {sun_sign}) ***")
            lines.append(f"Your essential self, conscious will, and life purpose are fundamentally {sun_sign}.")
            lines.append(f"You shine when expressing {sun_sign}'s positive qualities and leading through")
            lines.append(f"{sun_sign}'s natural strengths. Your hero's journey involves mastering {sun_sign}'s lessons.")
        
        if "ecl_lon" in moon_data:
            moon_sign, moon_deg = sign_from_degree(moon_data["ecl_lon"])
            lines.append(f"\n*** EMOTIONAL NATURE (Moon in {moon_sign}) ***")
            lines.append(f"Your emotional needs, instinctive reactions, and inner child are colored by {moon_sign}.")
            lines.append(f"You feel safe and nurtured when you can express {moon_sign}'s emotional style.")
            lines.append(f"Your mother or primary caregiver likely embodied {moon_sign} qualities.")
        
        # Ascendant (first house cusp)
        if cusps.get("Placidus"):
            asc = cusps["Placidus"][0]
            asc_sign, asc_deg = sign_from_degree(asc)
            lines.append(f"\n*** OUTER PERSONALITY (Ascendant in {asc_sign}) ***")
            lines.append(f"Your physical appearance, first impressions, and approach to new situations are {asc_sign}.")
            lines.append(f"Others initially perceive you as embodying {asc_sign} traits, which may differ from")
            lines.append(f"your inner Sun and Moon nature. This is your social mask and life strategy.")
        
        # Look for chart ruler
        if cusps.get("Placidus") and "ecl_lon" in sun_data:
            asc_sign, _ = sign_from_degree(cusps["Placidus"][0])
            ruler_planet = RULERS.get(asc_sign)
            if ruler_planet and ruler_planet in planets and "ecl_lon" in planets[ruler_planet]:
                ruler_lon = planets[ruler_planet]["ecl_lon"]
                ruler_sign, ruler_deg = sign_from_degree(ruler_lon)
                lines.append(f"\n*** CHART RULER ({ruler_planet} rules {asc_sign} Ascendant) ***")
                lines.append(f"Your chart ruler {ruler_planet} is in {ruler_sign}, adding another layer to your personality.")
                lines.append(f"The condition and placement of {ruler_planet} significantly influences how you navigate life.")
        
        # Major life themes based on stelliums and patterns
        lines.append("\n*** INTEGRATION AND LIFE WORK ***")
        lines.append("\nYour life's work involves integrating these different facets of yourself:")
        
        if "ecl_lon" in sun_data and "ecl_lon" in moon_data:
            sun_sign, _ = sign_from_degree(sun_data["ecl_lon"])
            moon_sign, _ = sign_from_degree(moon_data["ecl_lon"])
            
            if sun_sign != moon_sign:
                lines.append(f"\n- Balancing your conscious {sun_sign} identity with your emotional {moon_sign} needs")
            
            sun_element = AstrologicalKnowledge.SIGN_DESCRIPTIONS.get(sun_sign, {}).get("element")
            moon_element = AstrologicalKnowledge.SIGN_DESCRIPTIONS.get(moon_sign, {}).get("element")
            
            if sun_element and moon_element and sun_element != moon_element:
                lines.append(f"- Harmonizing {sun_element} willpower with {moon_element} emotional nature")
        
        lines.append("\n- Expressing authentic self while honoring relationships and social responsibilities")
        lines.append("- Developing both strengths and addressing shadow aspects of each placement")
        lines.append("- Using challenging aspects as catalysts for growth rather than sources of frustration")
        
        lines.append("\n*** SPIRITUAL PATH ***")
        lines.append("\nYour spiritual evolution involves:")
        lines.append("- Transcending the limitations of your most challenging placements")
        lines.append("- Developing qualities absent or weak in your chart")
        lines.append("- Using your natural gifts in service of something greater than ego")
        lines.append("- Integrating opposites and finding your unique synthesis")
        
        return "\n".join(lines)#!/usr/bin/env python3
"""
sistema_enhanced.py

Enhanced astrological chart generator with detailed interpretations.
Modularized with comprehensive sign descriptions and astrological analysis.

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
OUT_WHEEL_PNG = os.path.join(OUTPUT_DIR, "int_chart_wheel.png")
OUT_WHEEL_HTML = os.path.join(OUTPUT_DIR, "chart_wheel.html")
OUT_PDF = os.path.join(OUTPUT_DIR, "chart_report.pdf")

# Common timezone abbreviation map to IANA (best-effort)
TZ_ABBREV_MAP = {
    "PST": "America/Los_Angeles", "PDT": "America/Los_Angeles",
    "EST": "America/New_York", "EDT": "America/New_York",
    "CST": "America/Chicago", "CDT": "America/Chicago",
    "MST": "America/Denver", "MDT": "America/Denver",
    "UTC": "UTC", "GMT": "Etc/Greenwich",
    "BST": "Europe/London", "CET": "Europe/Paris", "CEST": "Europe/Paris"
}

# Planet list mapping for Swiss Ephemeris or skyfield
PLANETS = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto"]

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
    from skyfield.api import load, Topos, Star, wgs84
    from skyfield.api import N, E, W, S
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
constantly seeking new challenges and adventures. Ruled by Mars, the planet of action and desire, Aries natives 
possess an innate courage and directness that can be both inspiring and overwhelming.

The Aries energy is pure, unfiltered enthusiasm - the kind that rushes headfirst into situations without always 
considering consequences. This sign represents the self in its most primal form, concerned primarily with personal 
identity, survival, and assertion. Aries teaches us about the importance of self-advocacy, independence, and the 
courage to start anew.

In personality, Aries manifests as boldness, competitiveness, and a pioneering spirit. These individuals are natural 
leaders who prefer to blaze their own trails rather than follow others. They possess remarkable physical energy and 
often excel in athletic pursuits or careers requiring courage and quick decision-making. However, the shadow side of 
Aries includes impatience, impulsiveness, and a tendency toward aggression when challenged.

Spiritually, Aries represents the initial spark of consciousness, the "I Am" principle that separates self from 
universe. This sign teaches lessons about healthy self-assertion, managing anger constructively, and channeling 
competitive drives toward worthwhile goals.""",
            "positive_traits": ["Courageous", "Confident", "Enthusiastic", "Passionate", "Optimistic", "Honest", "Dynamic"],
            "challenging_traits": ["Impulsive", "Impatient", "Aggressive", "Self-centered", "Tactless", "Competitive to a fault"],
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
            "full_description": """Taurus is the second sign of the zodiac, representing consolidation, material 
manifestation, and the appreciation of physical reality. Where Aries initiates, Taurus builds and maintains. 
Ruled by Venus, this sign expresses the goddess of love through earthly pleasures - fine food, beautiful art, 
comfortable surroundings, and physical affection.

The Taurus archetype is that of the builder, gardener, and sustainer. This sign understands the value of patience, 
persistence, and working with natural rhythms. Taurus natives have an innate connection to the physical world and 
often possess a "green thumb" or artistic talent. They appreciate quality over quantity and are willing to invest 
time and effort to achieve lasting results.

In personality, Taurus manifests as reliability, practicality, and a strong connection to the senses. These 
individuals are known for their loyalty, determination, and ability to create material security. They possess 
remarkable endurance and can outlast almost anyone in pursuing their goals. However, this same quality can manifest 
as stubbornness, resistance to change, and excessive attachment to material possessions.

The shadow side of Taurus includes possessiveness, laziness when comfortable, and a tendency to become stuck in ruts. 
Yet these challenges are balanced by Taurus's gifts: an unshakeable sense of self-worth, the ability to create beauty 
and abundance, and the wisdom to appreciate life's simple pleasures. Taurus teaches us to slow down, engage our senses, 
and build something lasting in the material world.""",
            "positive_traits": ["Reliable", "Patient", "Practical", "Devoted", "Stable", "Artistic", "Sensual"],
            "challenging_traits": ["Stubborn", "Possessive", "Materialistic", "Resistant to change", "Indulgent", "Lazy"],
            "body_parts": ["Neck", "Throat", "Thyroid"],
            "career_paths": ["Banking", "Agriculture", "Real Estate", "Fine Arts", "Culinary Arts", "Fashion"],
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
            "full_description": """Gemini is the third sign of the zodiac, representing communication, mental agility, 
and the exchange of information. Symbolized by the Twins, Gemini embodies duality - the ability to see multiple 
perspectives, hold paradoxical truths, and adapt rapidly to changing circumstances. Ruled by Mercury, the swift 
messenger god, this sign governs all forms of communication, learning, and social connection.

The Gemini archetype is that of the eternal student, journalist, and networker. These individuals possess an 
insatiable curiosity about the world and an ability to quickly grasp new concepts. Gemini energy is light, quick, 
and ever-moving - flitting from topic to topic, person to person, idea to idea, gathering information and making 
connections. This sign represents the human mind in its most active state, constantly processing and categorizing 
experience through language and rational thought.

In personality, Gemini manifests as wit, sociability, and intellectual versatility. These individuals are natural 
communicators who can talk to anyone about anything. They possess quick minds, sharp tongues, and an ability to 
see both sides of every situation. Gemini natives excel in careers requiring mental dexterity, such as writing, 
teaching, sales, or technology. They need constant mental stimulation and variety to feel alive.

However, this mental restlessness can also be Gemini's challenge. The shadow side includes superficiality, 
inconsistency, gossip, and scattered focus. Gemini individuals may struggle with commitment, as they're always 
aware of other possibilities and alternatives. They can become trapped in their heads, overthinking everything 
and losing touch with deeper emotions. The spiritual lesson of Gemini involves integrating the mind with the heart, 
developing depth alongside breadth, and learning that true communication requires listening as well as speaking.""",
            "positive_traits": ["Adaptable", "Intelligent", "Witty", "Curious", "Sociable", "Quick-thinking", "Expressive"],
            "challenging_traits": ["Inconsistent", "Superficial", "Nervous", "Indecisive", "Scattered", "Gossipy"],
            "body_parts": ["Arms", "Hands", "Lungs", "Nervous system"],
            "career_paths": ["Journalism", "Teaching", "Sales", "Writing", "Public Relations", "Translation"],
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
            "full_description": """Cancer is the fourth sign of the zodiac, representing emotions, nurturing, home, 
and the deep waters of the unconscious mind. Symbolized by the Crab, Cancer carries its home on its back and 
possesses both a soft interior and a hard protective shell. Ruled by the Moon, Cancer's moods wax and wane like 
lunar phases, deeply connected to emotional tides and intuitive knowing.

The Cancer archetype is that of the Great Mother, the nurturer who creates safe spaces for others to grow. This 
sign governs home, family, roots, and our deepest emotional needs. Cancer energy is deeply sensitive, empathetic, 
and protective. These individuals have remarkable emotional intelligence and can sense the unspoken feelings in 
any room. They possess strong maternal or paternal instincts, regardless of gender, and often become the emotional 
center of their families and friend groups.

In personality, Cancer manifests as caring, loyalty, and profound emotional depth. These individuals form deep 
attachments and have long memories - both for kindnesses received and hurts endured. They excel in careers involving 
care, nurturing, or creating emotional security for others. Cancer natives need a secure home base from which to 
venture into the world, and they invest tremendous energy in creating beautiful, comfortable domestic spaces.

The shadow side of Cancer includes moodiness, clinginess, and emotional manipulation. When hurt, Cancer retreats 
into its shell and can become passive-aggressive or guilt-inducing. These individuals may struggle with letting go 
of the past or allowing loved ones appropriate independence. They can become overly protective, smothering those 
they care for. The spiritual lessons of Cancer involve learning healthy emotional boundaries, releasing past hurts, 
and understanding that true nurturing sometimes means letting go.""",
            "positive_traits": ["Nurturing", "Intuitive", "Loyal", "Protective", "Empathetic", "Creative", "Devoted"],
            "challenging_traits": ["Moody", "Clingy", "Oversensitive", "Manipulative", "Pessimistic", "Insecure"],
            "body_parts": ["Chest", "Breasts", "Stomach"],
            "career_paths": ["Nursing", "Childcare", "Psychology", "Real Estate", "Hospitality", "Culinary Arts"],
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
            "full_description": """Leo is the fifth sign of the zodiac, representing creative self-expression, 
personal dignity, and the radiant warmth of confident individuality. Symbolized by the Lion, king of beasts, 
Leo embodies regal bearing, natural authority, and the courage to stand center stage. Ruled by the Sun itself, 
Leo is the zodiac's most solar sign - warm, bright, life-giving, and impossible to ignore.

The Leo archetype is that of the performer, the noble ruler, and the creative artist. This sign governs self-expression, 
play, romance, children, and all acts of personal creativity. Leo energy is generous, dramatic, and attention-seeking 
in the most positive sense - these individuals want to shine and inspire others to do the same. They possess natural 
magnetism and often become leaders simply by virtue of their confident self-assurance.

In personality, Leo manifests as warmth, generosity, and creative vitality. These individuals have big hearts and 
love to give - their time, resources, affection, and talents. They excel in careers requiring performance, leadership, 
or creative expression. Leo natives need recognition and appreciation; when they receive it, they bloom and become 
even more generous. They have a natural sense of drama and can turn even mundane situations into theatrical experiences.

However, this need for attention and admiration can also be Leo's downfall. The shadow side includes arrogance, 
vanity, stubbornness, and an excessive need for approval. When wounded, Leo's pride can be devastating, leading to 
dramatic displays or cold withdrawal. These individuals may struggle with sharing the spotlight or dealing with 
criticism. They can become tyrannical when their authority is challenged or lazy when their efforts aren't appreciated. 
The spiritual lessons of Leo involve developing genuine self-esteem independent of external validation, learning 
humility alongside pride, and understanding that true leadership serves others.""",
            "positive_traits": ["Confident", "Generous", "Warm", "Creative", "Enthusiastic", "Loyal", "Charismatic"],
            "challenging_traits": ["Arrogant", "Stubborn", "Domineering", "Vain", "Attention-seeking", "Inflexible"],
            "body_parts": ["Heart", "Upper back", "Spine"],
            "career_paths": ["Entertainment", "Management", "Politics", "Arts", "Education", "Entrepreneurship"],
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
            "full_description": """Virgo is the sixth sign of the zodiac, representing analysis, refinement, service, 
and the pursuit of perfection through practical application. Symbolized by the Virgin or Maiden, Virgo embodies 
purity of intention, discrimination, and the ability to separate wheat from chaff. Ruled by Mercury in its nocturnal, 
earth-bound expression, Virgo channels mental energy into practical improvement and skilled craftsmanship.

The Virgo archetype is that of the craftsperson, healer, and devoted servant. This sign governs health, daily work, 
skills, and the mundane routines that keep life functioning smoothly. Virgo energy is meticulous, analytical, and 
efficiency-focused. These individuals possess an exceptional eye for detail and an innate understanding of systems 
and processes. They find satisfaction in making things work better, whether that's organizing a workspace, improving 
health protocols, or editing a manuscript to perfection.

In personality, Virgo manifests as practicality, helpfulness, and high standards. These individuals are natural 
problem-solvers who can quickly identify what's wrong and how to fix it. They excel in careers requiring precision, 
analysis, or service to others - from medicine to accounting, from crafts to criticism. Virgo natives have a strong 
work ethic and often become indispensable in their workplaces due to their reliability and competence.

However, this perfectionism can also be Virgo's greatest challenge. The shadow side includes excessive criticism 
(of self and others), worry, hypochondria, and an inability to see the forest for the trees. Virgo individuals may 
become lost in details, obsessing over minor flaws while missing larger truths. They can be self-sacrificing to the 
point of martyrdom, serving others while neglecting their own needs. The judgmental quality of Virgo can make both 
the native and those around them feel perpetually inadequate. The spiritual lessons of Virgo involve accepting 
imperfection, recognizing when "good enough" is sufficient, and learning to serve from love rather than anxiety.""",
            "positive_traits": ["Analytical", "Practical", "Hardworking", "Helpful", "Reliable", "Precise", "Modest"],
            "challenging_traits": ["Critical", "Perfectionist", "Anxious", "Overly cautious", "Fussy", "Judgmental"],
            "body_parts": ["Digestive system", "Intestines", "Abdomen"],
            "career_paths": ["Healthcare", "Editing", "Accounting", "Research", "Quality Control", "Nutrition"],
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
            "full_description": """Libra is the seventh sign of the zodiac, representing balance, partnership, 
justice, and aesthetic refinement. Symbolized by the Scales, Libra is the only zodiac sign represented by an 
inanimate object, suggesting the rational, balanced approach this sign takes to life. Ruled by Venus in her 
air-sign expression, Libra seeks beauty through harmony, connection, and social grace.

The Libra archetype is that of the diplomat, judge, and artist of relationships. This sign governs marriage, 
partnerships, legal matters, and all forms of one-to-one relating. Libra energy is inherently social and relationship-
oriented - these individuals understand themselves through interaction with others. They possess natural charm, 
social grace, and an ability to see multiple perspectives. Libra seeks to create equilibrium, whether in relationships, 
art, justice systems, or interior design.

In personality, Libra manifests as charm, fairness, and aesthetic sensibility. These individuals are natural mediators 
who can find common ground between opposing viewpoints. They excel in careers requiring diplomacy, aesthetic judgment, 
or facilitating agreement between parties. Libra natives have an innate sense of style and often create beautiful 
environments. They need partnership and collaboration to feel complete, and they invest considerable energy in 
maintaining harmonious relationships.

However, this peace-seeking orientation can also be Libra's challenge. The shadow side includes indecision, people-
pleasing, superficiality, and conflict avoidance. Libra individuals may struggle to make choices, seeing merit in all 
options and fearing they might upset someone. They can lose themselves in relationships, becoming overly dependent on 
partners for identity and validation. The constant weighing of options can lead to analysis paralysis. Additionally, 
Libra's desire for surface harmony may prevent necessary confrontations. The spiritual lessons of Libra involve 
developing a strong sense of self independent of relationships, learning that true peace sometimes requires conflict, 
and understanding that not all situations can or should be balanced.""",
            "positive_traits": ["Diplomatic", "Fair", "Charming", "Cooperative", "Artistic", "Gracious", "Sociable"],
            "challenging_traits": ["Indecisive", "People-pleasing", "Superficial", "Conflict-avoidant", "Dependent", "Vain"],
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
            "full_description": """Scorpio is the eighth sign of the zodiac, representing transformation, depth, 
power, sexuality, and the mysteries of death and rebirth. Symbolized by the Scorpion, Eagle, and Phoenix, Scorpio 
embodies evolution through intensity and the courage to face life's darkest corners. Ruled by both Mars (traditional) 
and Pluto (modern), Scorpio combines martial force with profound transformation.

The Scorpio archetype is that of the shaman, detective, and transformer. This sign governs sex, death, shared 
resources, psychology, and all that is hidden beneath surface appearances. Scorpio energy is intense, penetrating, 
and uncompromising. These individuals possess x-ray vision into human nature and can sense hidden motives, unspoken 
truths, and deep emotional currents. They are drawn to life's mysteries and taboos, seeking to understand power 
dynamics, psychological depths, and transformative processes.

In personality, Scorpio manifests as intensity, loyalty, and emotional depth that can be both magnetic and overwhelming. 
These individuals form bonds that are profound and total - there is no casual relationship with Scorpio. They excel 
in careers requiring investigation, transformation, or working with power - psychology, surgery, research, finance, 
or any field dealing with life's intensities. Scorpio natives possess remarkable resilience and can survive and 
transform through experiences that would destroy others.

However, this intensity is also Scorpio's greatest challenge. The shadow side includes obsession, jealousy, 
manipulation, and destructiveness. Scorpio's fixed water nature can lead to emotional stagnation - holding grudges, 
refusing to forgive, or becoming trapped in toxic attachments. These individuals may use their penetrating insight 
manipulatively or become consumed by jealousy and possessiveness. The compulsion for control can manifest as 
domination or power games. Trust issues run deep, and Scorpio may test others endlessly or pre-emptively betray 
before being betrayed. The spiritual lessons of Scorpio involve learning healthy vulnerability, releasing the need 
for control, practicing forgiveness, and understanding that true power comes through transformation, not domination.""",
            "positive_traits": ["Passionate", "Resourceful", "Brave", "Loyal", "Determined", "Intuitive", "Deep"],
            "challenging_traits": ["Jealous", "Possessive", "Secretive", "Manipulative", "Obsessive", "Vengeful"],
            "body_parts": ["Reproductive organs", "Colon", "Bladder"],
            "career_paths": ["Psychology", "Surgery", "Research", "Detective Work", "Finance", "Occult Studies"],
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
            "full_description": """Sagittarius is the ninth sign of the zodiac, representing philosophy, higher learning, 
long-distance travel, and the quest for truth and meaning. Symbolized by the Centaur Archer, Sagittarius combines 
animal instinct with human intellect, always aiming arrows toward distant horizons and lofty ideals. Ruled by 
Jupiter, planet of expansion and abundance, this sign embodies optimism, growth, and the principle that life should 
be an adventure.

The Sagittarius archetype is that of the philosopher, priest, and adventurer. This sign governs higher education, 
religion, foreign cultures, publishing, and all activities that expand consciousness and physical boundaries. 
Sagittarius energy is enthusiastic, freedom-loving, and perpetually optimistic. These individuals are truth-seekers 
who need to understand the broader meaning and purpose behind life's experiences. They possess natural teaching 
ability and love to share their discoveries with others.

In personality, Sagittarius manifests as enthusiasm, honesty, and philosophical inclination. These individuals are 
natural explorers - whether traveling the world, diving into diverse philosophical systems, or constantly learning 
new subjects. They excel in careers involving education, travel, publishing, law, or spiritual guidance. Sagittarius 
natives possess infectious optimism and can inspire others with their vision and faith. They need freedom and variety, 
becoming restless when confined physically or intellectually.

However, this quest for freedom and truth has its shadow aspects. Sagittarius can be tactless, dogmatic, preachy, 
and irresponsible. Their blunt honesty, while refreshing, can wound others. The constant search for greener pastures 
may prevent depth or commitment - these individuals can be eternal students who never master anything or perpetual 
travelers who never build a home. Their optimism can border on recklessness, taking risks without considering 
consequences. The moral certainty of Sagittarius can manifest as judgmental preachiness or religious/philosophical 
fanaticism. The spiritual lessons of Sagittarius involve learning tact alongside honesty, developing commitment 
alongside freedom, and understanding that truth has many valid expressions.""",
            "positive_traits": ["Optimistic", "Adventurous", "Honest", "Philosophical", "Generous", "Jovial", "Open-minded"],
            "challenging_traits": ["Tactless", "Irresponsible", "Preachy", "Dogmatic", "Restless", "Commitment-phobic"],
            "body_parts": ["Hips", "Thighs", "Liver"],
            "career_paths": ["Teaching", "Travel Industry", "Publishing", "Law", "Ministry", "International Business"],
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
            "full_description": """Capricorn is the tenth sign of the zodiac, representing achievement, structure, 
authority, and mastery through discipline. Symbolized by the Mountain Goat (or Sea-Goat), Capricorn steadily climbs 
toward the peaks of worldly success, navigating difficult terrain with patience and determination. Ruled by Saturn, 
planet of time, limitation, and wisdom through experience, this sign embodies maturity, responsibility, and the 
understanding that anything worthwhile requires sustained effort.

The Capricorn archetype is that of the elder, executive, and master craftsperson. This sign governs career, public 
reputation, long-term goals, and all forms of worldly achievement. Capricorn energy is ambitious, pragmatic, and 
willing to delay gratification for future success. These individuals understand hierarchy, tradition, and the rules 
of engagement in any system. They possess natural authority and often rise to positions of responsibility through 
sheer competence and persistence.

In personality, Capricorn manifests as ambition, practicality, and serious dedication. These individuals are natural 
managers and administrators who excel at creating structures and achieving long-term goals. They thrive in careers 
requiring patience, strategic planning, and mastery - business, administration, architecture, or any field where 
expertise is earned through years of disciplined effort. Capricorn natives are often old souls who mature early and 
may grow more youthful as they age. They value tradition, quality, and lasting achievement over flash and trends.

However, this serious orientation has its costs. The shadow side of Capricorn includes coldness, excessive ambition, 
pessimism, and rigidity. These individuals may become workaholics, sacrificing personal relationships and joy for 
professional success. They can be harsh taskmasters - both to themselves and others - never feeling that they've 
achieved enough. Fear of failure or loss of control can lead to rigidity and resistance to change. The emotional 
reserve of Capricorn can manifest as coldness or inability to show vulnerability. Status-consciousness may override 
authentic values. The spiritual lessons of Capricorn involve learning to balance achievement with enjoyment, 
developing compassion alongside competence, and understanding that true authority comes from inner wisdom, not 
external position.""",
            "positive_traits": ["Ambitious", "Disciplined", "Responsible", "Patient", "Loyal", "Practical", "Wise"],
            "challenging_traits": ["Pessimistic", "Cold", "Rigid", "Workaholic", "Status-conscious", "Unforgiving"],
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
            "full_description": """Aquarius is the eleventh sign of the zodiac, representing innovation, humanitarianism, 
friendship, and collective consciousness. Symbolized by the Water Bearer pouring out knowledge for humanity's benefit, 
Aquarius brings divine wisdom down to earth for the advancement of all. Ruled by both Saturn (traditional) and 
Uranus (modern), this sign combines structural understanding with revolutionary breakthrough.

The Aquarius archetype is that of the revolutionary, scientist, and humanitarian visionary. This sign governs 
friendship, groups, technology, social causes, and utopian ideals. Aquarius energy is intellectual, progressive, 
and oriented toward the collective good rather than personal gain. These individuals are natural innovators who 
can see beyond current limitations to envision better futures. They possess strong ideals about equality, freedom, 
and human potential.

In personality, Aquarius manifests as originality, independence, and humanitarian concern. These individuals are 
often ahead of their time, championing causes before they become mainstream. They excel in careers involving 
technology, social reform, science, or any field requiring innovative thinking. Aquarius natives value friendship 
and community but maintain fierce independence. They need intellectual freedom and rebel against any attempt to 
control or conventionalize them.

However, this detached idealism has its shadow aspects. Aquarius can be emotionally cold, overly rational, and 
detached from personal feelings. Their focus on humanity in abstract may lead to neglect of individual human needs - 
they may care deeply about "the people" while being insensitive to actual people in their lives. The rebellious 
streak can become knee-jerk contrarianism, rejecting things simply because they're conventional. Fixed air makes 
Aquarius paradoxically stubborn about their progressive views. The spiritual lessons of Aquarius involve integrating 
intellect with emotion, balancing individual and collective needs, and learning that true revolution requires 
understanding human nature, not just ideals.""",
            "positive_traits": ["Original", "Humanitarian", "Intellectual", "Independent", "Progressive", "Friendly"],
            "challenging_traits": ["Detached", "Stubborn", "Aloof", "Contrary", "Impersonal", "Unpredictable"],
            "body_parts": ["Ankles", "Calves", "Circulatory system"],
            "career_paths": ["Technology", "Science", "Social Work", "Aviation", "Astrology", "Engineering"],
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
            "full_description": """Pisces is the twelfth and final sign of the zodiac, representing transcendence, 
universal love, mysticism, and the dissolution of boundaries. Symbolized by two Fish swimming in opposite directions, 
Pisces embodies the tension between spiritual and material worlds, between escape and engagement. Ruled by both 
Jupiter (traditional) and Neptune (modern), this sign combines faith and expansion with mystical dissolution and 
divine imagination.

The Pisces archetype is that of the mystic, artist, and universal lover. This sign governs spirituality, dreams, 
imagination, hidden realms, and collective unconscious. Pisces energy is empathic, intuitive, and boundaryless. 
These individuals can merge with others emotionally, channel creative inspiration from unseen realms, and sense 
the underlying unity of all existence. They possess natural healing abilities and profound compassion for suffering.

In personality, Pisces manifests as sensitivity, creativity, and spiritual inclination. These individuals are often 
artistic or musical, able to channel beauty from the collective unconscious. They excel in careers involving healing, 
art, spirituality, or service to those in need. Pisces natives are natural empaths who feel others' pain as their 
own and often sacrifice personal needs for others' welfare. They need regular retreat from harsh worldly realities 
to recharge in solitude, nature, or creative pursuits.

However, this boundaryless sensitivity creates significant challenges. The shadow side of Pisces includes escapism, 
victimhood, martyrdom, and confusion between fantasy and reality. These individuals may turn to substances, fantasy, 
or dissociation to escape painful realities. Their empathy can lead to poor boundaries - absorbing others' problems, 
enabling dysfunction, or losing themselves in relationships. Pisces may struggle with practical matters, becoming 
disorganized or impractical. The victim/savior dynamic is strong - they may attract or enable troubled people while 
neglecting self-care. Deception (of self or others) can be an issue, as Pisces sees what they wish were true rather 
than what is. The spiritual lessons of Pisces involve developing healthy boundaries, distinguishing compassion from 
enabling, grounding spiritual insights in practical reality, and learning that true transcendence includes rather 
than escapes from earthly existence.""",
            "positive_traits": ["Compassionate", "Intuitive", "Artistic", "Gentle", "Wise", "Spiritual", "Adaptable"],
            "challenging_traits": ["Escapist", "Overly trusting", "Martyr complex", "Impractical", "Victim mentality"],
            "body_parts": ["Feet", "Lymphatic system", "Immune system"],
            "career_paths": ["Arts", "Healing Professions", "Music", "Photography", "Charity Work", "Spirituality"],
            "life_lessons": ["Boundaries", "Discernment", "Practical grounding", "Self-care", "Reality testing"]
        }
    }
    
    PLANET_DESCRIPTIONS = {
        "Sun": {
            "symbol": "☉",
            "keywords": ["Identity", "Ego", "Vitality", "Purpose", "Consciousness"],
            "description": """The Sun represents core identity, conscious will, and life purpose. It symbolizes 
the central organizing principle of the personality - who you are at your essence. The Sun's sign, house, and 
aspects describe how you shine, where you seek to express yourself authentically, and what gives your life meaning 
and vitality. A well-integrated Sun manifests as confidence, creativity, and natural authority."""
        },
        "Moon": {
            "symbol": "☽",
            "keywords": ["Emotions", "Instincts", "Needs", "Memory", "Subconscious"],
            "description": """The Moon represents emotional nature, instinctive reactions, and deep psychological needs. 
It symbolizes the inner child, the mother archetype, and our relationship with nurturing and security. The Moon's 
placement describes what makes you feel safe and comfortable, how you process emotions, and your habitual responses 
to life. It governs memory, moods, and the subconscious patterns that influence behavior."""
        },
        "Mercury": {
            "symbol": "☿",
            "keywords": ["Communication", "Thinking", "Learning", "Connection", "Perception"],
            "description": """Mercury represents the rational mind, communication style, and how we process information. 
It governs learning, writing, speaking, and all forms of exchange. Mercury's placement describes mental patterns, 
communication preferences, and intellectual interests. It shows how you think, learn, and connect ideas."""
        },
        "Venus": {
            "symbol": "♀",
            "keywords": ["Love", "Beauty", "Values", "Pleasure", "Attraction"],
            "description": """Venus represents love, beauty, pleasure, and values. It governs attraction, aesthetics, 
relationships, and what we find pleasurable. Venus's placement describes how you give and receive affection, what 
you find beautiful, your artistic sensibilities, and your core values regarding relationships and resources."""
        },
        "Mars": {
            "symbol": "♂",
            "keywords": ["Action", "Desire", "Anger", "Drive", "Assertion"],
            "description": """Mars represents action, desire, and assertive energy. It governs sexuality, anger, 
competition, and how we pursue what we want. Mars's placement describes your fighting style, what motivates you 
to take action, how you express anger, and where you direct your physical and sexual energy."""
        },
        "Jupiter": {
            "symbol": "♃",
            "keywords": ["Expansion", "Growth", "Faith", "Abundance", "Wisdom"],
            "description": """Jupiter represents growth, expansion, and the principle of increase. It governs faith, 
optimism, higher learning, philosophy, and abundance. Jupiter's placement describes where you seek growth and 
meaning, your philosophical outlook, relationship with faith and luck, and areas of natural talent and opportunity."""
        },
        "Saturn": {
            "symbol": "♄",
            "keywords": ["Structure", "Discipline", "Limitation", "Maturity", "Authority"],
            "description": """Saturn represents structure, limitation, discipline, and maturity through challenge. 
It governs time, responsibility, authority, and lessons learned through experience. Saturn's placement describes 
where you face obstacles and fears, develop mastery through patience, and ultimately gain wisdom and authority."""
        },
        "Uranus": {
            "symbol": "♅",
            "keywords": ["Revolution", "Innovation", "Freedom", "Awakening", "Change"],
            "description": """Uranus represents sudden change, innovation, revolution, and awakening. It governs 
technology, progress, independence, and breakthrough experiences. Uranus's placement describes where you seek 
freedom and originality, rebel against convention, and experience sudden insights or disruptions."""
        },
        "Neptune": {
            "symbol": "♆",
            "keywords": ["Spirituality", "Illusion", "Compassion", "Transcendence", "Imagination"],
            "description": """Neptune represents spirituality, imagination, transcendence, and the dissolution of 
boundaries. It governs dreams, mysticism, compassion, and also illusion and confusion. Neptune's placement describes 
where you seek spiritual connection, may experience confusion or deception, and can access divine inspiration."""
        },
        "Pluto": {
            "symbol": "♇",
            "keywords": ["Transformation", "Power", "Regeneration", "Intensity", "Depth"],
            "description": """Pluto represents transformation, death and rebirth, and deep psychological processes. 
It governs power, intensity, sexuality, and profound change. Pluto's placement describes where you experience 
intense transformation, confront shadow material, and discover hidden sources of power and regeneration."""
        }
    }
    
    ASPECT_INTERPRETATIONS = {
        "Conjunction": {
            "angle": 0,
            "orb": 8,
            "nature": "Neutral/Intense",
            "description": """A conjunction merges the energies of two planets, creating a powerful blended influence. 
The planets function as a unit, each coloring the expression of the other. This is the most powerful aspect, 
representing new beginnings and concentrated energy. The nature depends on the planets involved - harmonious 
planets create easy conjunction, while challenging planets may create internal conflict."""
        },
        "Opposition": {
            "angle": 180,
            "orb": 8,
            "nature": "Dynamic/Challenging",
            "description": """An opposition creates tension between two planetary energies pulling in opposite 
directions. This aspect represents the need for balance and integration of polar opposite qualities. It often 
manifests as external conflicts or projection onto others until integration is achieved. The challenge is to 
honor both sides rather than swinging between extremes."""
        },
        "Trine": {
            "angle": 120,
            "orb": 7,
            "nature": "Harmonious/Flowing",
            "description": """A trine creates harmonious flow between planets in compatible elements. This aspect 
represents natural talent, ease, and support. Energy flows smoothly between the planetary principles, creating 
gifts and abilities. However, trines can also indicate laziness or taking things for granted, as the ease may 
prevent development of discipline."""
        },
        "Square": {
            "angle": 90,
            "orb": 6,
            "nature": "Dynamic/Challenging",
            "description": """A square creates friction and dynamic tension requiring action and adjustment. This 
aspect represents challenges that demand growth, effort, and problem-solving. While difficult, squares are often 
the most productive aspects, as they force development of skills and character. The key is to use the tension 
constructively rather than avoiding the challenge."""
        },
        "Sextile": {
            "angle": 60,
            "orb": 6,
            "nature": "Harmonious/Opportunistic",
            "description": """A sextile creates opportunities for cooperation between planets. Unlike trines, 
sextiles require some effort to activate. This aspect represents potential talents and opportunities that 
manifest when initiative is taken. It provides supportive connections that can be developed with conscious 
effort."""
        },
        "Quincunx": {
            "angle": 150,
            "orb": 3,
            "nature": "Adjustment/Awkward",
            "description": """A quincunx (or inconjunct) creates an awkward relationship between planets in signs 
with nothing in common. This aspect requires constant adjustment and adaptation. It often manifests as a feeling 
that two areas of life don't quite fit together, requiring creative solutions and ongoing compromise."""
        }
    }
    
    HOUSE_MEANINGS = {
        1: {
            "name": "First House (Ascendant)",
            "keywords": ["Self", "Identity", "Appearance", "First Impressions"],
            "description": """The First House represents self-image, physical appearance, and how others perceive 
you initially. It describes your approach to life, personal style, and the mask or persona you present to the 
world. Planets here significantly influence personality and life approach."""
        },
        2: {
            "name": "Second House",
            "keywords": ["Values", "Resources", "Money", "Self-Worth"],
            "description": """The Second House governs material resources, money, possessions, and personal values. 
It describes your relationship with material security, what you value, and how you earn and spend. It also relates 
to self-worth and innate talents."""
        },
        3: {
            "name": "Third House",
            "keywords": ["Communication", "Learning", "Siblings", "Short Trips"],
            "description": """The Third House rules communication, early learning, siblings, neighbors, and short 
trips. It describes your thinking style, communication patterns, relationship with siblings, and everyday interactions 
in your immediate environment."""
        },
        4: {
            "name": "Fourth House (IC)",
            "keywords": ["Home", "Family", "Roots", "Private Self"],
            "description": """The Fourth House represents home, family, roots, and emotional foundations. It describes 
your relationship with parents (especially mother/nurturing parent), your private self, sense of belonging, and 
what makes you feel secure. This is the most private sector of the chart."""
        },
        5: {
            "name": "Fifth House",
            "keywords": ["Creativity", "Romance", "Children", "Play"],
            "description": """The Fifth House governs creativity, self-expression, romance, children, and pleasure. 
It describes how you play, create, take risks, and express your unique self. It shows your approach to dating, 
hobbies, artistic pursuits, and relationship with children."""
        },
        6: {
            "name": "Sixth House",
            "keywords": ["Work", "Health", "Service", "Daily Routine"],
            "description": """The Sixth House rules daily work, health, service, and routines. It describes your 
work ethic, health habits, relationship with service and employment, and how you maintain daily life. It shows 
approaches to wellness and the mind-body connection."""
        },
        7: {
            "name": "Seventh House (Descendant)",
            "keywords": ["Partnership", "Marriage", "Others", "Projection"],
            "description": """The Seventh House represents partnerships, marriage, and one-to-one relationships. 
It describes what you seek in partners, how you relate in committed relationships, and qualities you may project 
onto others. This is the house of "the other" as mirror."""
        },
        8: {
            "name": "Eighth House",
            "keywords": ["Transformation", "Intimacy", "Shared Resources", "Death"],
            "description": """The Eighth House governs transformation, deep intimacy, shared resources, death, and 
rebirth. It describes your approach to deep bonding, sexuality, psychological work, crisis, and transformation. 
It also rules inheritances, taxes, and joint finances."""
        },
        9: {
            "name": "Ninth House",
            "keywords": ["Philosophy", "Travel", "Higher Education", "Belief"],
            "description": """The Ninth House rules higher education, philosophy, long-distance travel, and belief 
systems. It describes your quest for meaning, relationship with faith and spirituality, approach to learning, 
and connection with foreign cultures."""
        },
        10: {
            "name": "Tenth House (Midheaven)",
            "keywords": ["Career", "Reputation", "Achievement", "Public Life"],
            "description": """The Tenth House represents career, public reputation, achievement, and life direction. 
It describes your professional path, relationship with authority, public image, and major life accomplishments. 
This is the most public sector of the chart."""
        },
        11: {
            "name": "Eleventh House",
            "keywords": ["Friends", "Groups", "Aspirations", "Community"],
            "description": """The Eleventh House governs friendships, groups, social causes, and future aspirations. 
It describes your relationship with community, approach to friendship, social ideals, and hopes for the future. 
It shows where you find your tribe."""
        },
        12: {
            "name": "Twelfth House",
            "keywords": ["Spirituality", "Unconscious", "Solitude", "Transcendence"],
            "description": """The Twelfth House rules spirituality, the unconscious, hidden matters, and transcendence. 
It describes your inner spiritual life, relationship with solitude, unconscious patterns, and areas of life requiring 
surrender. It's the house of karma, mysticism, and dissolution of ego."""
        }
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
        lines.append(f"\nGoverns: {', '.join(sign_info['body_parts'])}")
        lines.append(f"\nCareer Paths: {', '.join(sign_info['career_paths'])}")
        lines.append(f"\nLife Lessons: {', '.join(sign_info['life_lessons'])}")
        
        return "\n".join(lines)
    
    @classmethod
    def get_planet_interpretation(cls, planet_name):
        """Get interpretation for a planet's general meaning."""
        if planet_name not in cls.PLANET_DESCRIPTIONS:
            return f"Interpretation for {planet_name} not available."
        
        planet_info = cls.PLANET_DESCRIPTIONS[planet_name]
        lines = []
        lines.append(f"\n{planet_name} {planet_info['symbol']}")
        lines.append(f"Keywords: {', '.join(planet_info['keywords'])}")
        lines.append(f"{planet_info['description']}")
        return "\n".join(lines)
    
    @classmethod
    def get_aspect_interpretation(cls, aspect_name, planet1, planet2):
        """Get interpretation for an aspect between two planets."""
        if aspect_name not in cls.ASPECT_INTERPRETATIONS:
            return f"Interpretation for {aspect_name} not available."
        
        aspect_info = cls.ASPECT_INTERPRETATIONS[aspect_name]
        lines = []
        lines.append(f"\n{planet1} {aspect_name} {planet2}")
        lines.append(f"Nature: {aspect_info['nature']} | Orb: {aspect_info['orb']}°")
        lines.append(f"{aspect_info['description']}")
        return "\n".join(lines)
    
    @classmethod
    def get_house_interpretation(cls, house_num):
        """Get interpretation for a house."""
        if house_num not in cls.HOUSE_MEANINGS:
            return f"Interpretation for House {house_num} not available."
        
        house_info = cls.HOUSE_MEANINGS[house_num]
        lines = []
        lines.append(f"\n{house_info['name']}")
        lines.append(f"Keywords: {', '.join(house_info['keywords'])}")
        lines.append(f"{house_info['description']}")
        return "\n".join(lines)


# Continue with original utility functions...
