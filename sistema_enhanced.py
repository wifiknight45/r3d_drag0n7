#!/usr/bin/env python3
"""
sistema_enhanced.py

Enhanced single-file astrological and astronomical chart generator with detailed interpretations.
Combined and modularized from original sistema.py and sistema7.py.

Modes:
 - Nostradamus  : High-accuracy mode using pyswisseph (Swiss Ephemeris) when available.
 - Ptolemy      : Pure-Python fallback using Skyfield and approximate house algorithms.
 - Paranoid     : Offline-only mode using local data/files.

Features:
 - Parse date inputs (DD/MM/YYYY or MM/DD/YYYY) with interactive disambiguation.
 - Parse times (24h/12h with AM/PM), timezone abbreviations or IANA tz names, and UTC.
 - Location input: city/state/country (geocoded via Nominatim), lat/lon, or zipcode (fallback to data/zipcodes.csv).
 - House systems: Placidus, Equal, Whole Sign, Porphyry, Campanus (SwissEphem exact if available; approximate fallback otherwise).
 - Output: verbose chart (text), summary, interpretation, astronomical raw JSON, PNG wheel image, interactive HTML wheel, PDF report (when libs available).
 - Historical events fetch via Wikipedia OnThisDay (online) with offline fallback events_cache.json in data/.
 - Prompts for API keys at first run (NASA optional; Nominatim uses unauthenticated endpoints).
 - Saves outputs to outputs/ directory.
 - Interactive + CLI modes supported.
 - Comprehensive astrological interpretations including planet placements, aspects, patterns, houses, and synthesis.

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

# Rulers and Signs
RULERS = {
    "Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon",
    "Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars",
    "Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"
}
SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

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
# ASTROLOGICAL KNOWLEDGE BASE
# ============================================================================

class AstrologicalKnowledge:
    """Comprehensive astrological knowledge base for interpretations."""
    
    SIGN_DESCRIPTIONS = {
        "Aries": {
            "symbol": "♈",
            "element": "Fire",
            "quality": "Cardinal",
            "ruling_planet": "Mars",
            "keywords": ["Initiative", "Courage", "Leadership", "Independence", "Action"],
            "short_description": "The pioneering warrior who initiates new beginnings with bold enthusiasm.",
            "full_description": """Aries, the first sign of the zodiac, represents pure life force and the spark of 
individuality. Symbolized by the Ram, Aries embodies raw energy, pioneering spirit, and the drive to assert one's 
existence in the world. As a Cardinal Fire sign ruled by Mars, it combines initiatory power with passionate intensity 
to charge forward into new territory without hesitation.

The Aries archetype is that of the warrior, pioneer, and entrepreneur. This sign governs self-assertion, independence, 
courage, and the instinct to compete and conquer. Aries energy is direct, honest, and unapologetically self-focused. 
These individuals excel at starting projects, leading charges, and facing challenges head-on. They possess natural 
leadership abilities and thrive on competition, adventure, and physical activity.

In personality, Aries manifests as boldness, enthusiasm, and quick action. These individuals are often charismatic 
leaders who inspire others with their confidence and willingness to take risks. They excel in careers requiring 
initiative, such as entrepreneurship, athletics, or emergency response. Aries natives are straightforward 
communicators who value honesty and directness in relationships.

However, this pioneering energy creates challenges. The shadow side of Aries includes impulsiveness, impatience, 
self-centeredness, and difficulty completing what they've started. These individuals may rush into situations 
without considering consequences, leading to unnecessary conflicts or abandoned projects. Their competitive nature 
can become aggressive or domineering if unchecked. Aries may struggle with collaboration, preferring to go it alone 
rather than compromise. The spiritual lessons of Aries involve channeling raw energy constructively, learning 
patience and consideration for others, and understanding that true courage includes vulnerability and cooperation.""",
            "positive_traits": ["Courageous", "Energetic", "Honest", "Passionate", "Optimistic", "Adventurous"],
            "challenging_traits": ["Impulsive", "Impatient", "Self-centered", "Aggressive", "Reckless"],
            "body_parts": ["Head", "Face", "Eyes"],
            "career_paths": ["Entrepreneurship", "Sports", "Military", "Sales", "Leadership Roles"],
            "life_lessons": ["Patience", "Cooperation", "Follow-through", "Diplomacy", "Self-awareness"]
        },
        "Taurus": {
            "symbol": "♉",
            "element": "Earth",
            "quality": "Fixed",
            "ruling_planet": "Venus",
            "keywords": ["Stability", "Sensuality", "Persistence", "Security", "Practicality"],
            "short_description": "The steadfast builder who creates lasting value through patient determination.",
            "full_description": """Taurus, the second sign, represents the stabilization of individual existence through 
material security and sensory appreciation. Symbolized by the Bull, Taurus embodies earthly strength, persistence, 
and the drive to build and maintain resources. As a Fixed Earth sign ruled by Venus, it combines grounded stability 
with aesthetic appreciation to create lasting beauty and security.

The Taurus archetype is that of the builder, gardener, and sensualist. This sign governs material resources, values, 
physical pleasures, and the instinct to possess and preserve. Taurus energy is patient, reliable, and deeply connected 
to the physical world. These individuals excel at creating financial security, cultivating beauty, and enjoying life's 
sensual pleasures. They possess natural talents in finance, arts, or any field requiring persistence and practical skills.

In personality, Taurus manifests as reliability, sensuality, and determined focus. These individuals are often calm 
and composed, with a strong appreciation for comfort, good food, and beautiful surroundings. They excel in careers 
involving finance, real estate, arts, or agriculture. Taurus natives are loyal partners who value stability and 
physical affection in relationships.

However, this stabilizing energy creates challenges. The shadow side of Taurus includes stubbornness, possessiveness, 
materialism, and resistance to change. These individuals may cling to comfort zones, relationships, or possessions 
long after they've outlived their usefulness. Their love of security can become fear of loss, leading to hoarding 
or jealousy. Taurus may struggle with flexibility, preferring routine over innovation. The spiritual lessons of 
Taurus involve learning to release attachments, embracing change as part of growth, and understanding that true 
security comes from within rather than external possessions.""",
            "positive_traits": ["Reliable", "Patient", "Sensual", "Practical", "Loyal", "Determined"],
            "challenging_traits": ["Stubborn", "Possessive", "Materialistic", "Inflexible", "Indulgent"],
            "body_parts": ["Neck", "Throat", "Thyroid"],
            "career_paths": ["Finance", "Arts", "Agriculture", "Real Estate", "Culinary"],
            "life_lessons": ["Flexibility", "Non-attachment", "Sharing", "Adaptability", "Spiritual values"]
        },
        "Gemini": {
            "symbol": "♊",
            "element": "Air",
            "quality": "Mutable",
            "ruling_planet": "Mercury",
            "keywords": ["Communication", "Adaptability", "Curiosity", "Versatility", "Intellect"],
            "short_description": "The clever communicator who connects ideas and people with quick wit.",
            "full_description": """Gemini, the third sign, represents the development of perception and communication. 
Symbolized by the Twins, Gemini embodies duality, versatility, and the drive to connect and exchange information. As a 
Mutable Air sign ruled by Mercury, it combines intellectual flexibility with rapid mental processing to navigate the 
world through curiosity and adaptation.

The Gemini archetype is that of the messenger, networker, and eternal student. This sign governs communication, 
learning, short trips, siblings, and immediate environment. Gemini energy is quick-witted, adaptable, and socially 
agile. These individuals excel at multitasking, learning new skills, and connecting people and ideas. They possess 
natural talents in writing, speaking, teaching, or any field requiring mental agility and social interaction.

In personality, Gemini manifests as curiosity, wit, and social charm. These individuals are often engaging 
conversationalists with broad knowledge across many subjects. They excel in careers involving media, education, 
sales, or technology. Gemini natives are playful partners who value mental stimulation and variety in relationships.

However, this versatile energy creates challenges. The shadow side of Gemini includes superficiality, inconsistency, 
nervousness, and difficulty with depth or commitment. These individuals may scatter their energy across too many 
interests, leading to unfinished projects or shallow relationships. Their adaptability can become duplicity or 
manipulation. Gemini may struggle with focus, becoming restless or bored easily. The spiritual lessons of Gemini 
involve developing depth alongside breadth, learning to commit without losing freedom, and using communication for 
truth rather than evasion.""",
            "positive_traits": ["Adaptable", "Witty", "Curious", "Versatile", "Sociable", "Intelligent"],
            "challenging_traits": ["Superficial", "Inconsistent", "Nervous", "Gossipy", "Restless"],
            "body_parts": ["Arms", "Hands", "Lungs", "Nervous System"],
            "career_paths": ["Writing", "Teaching", "Journalism", "Sales", "Technology"],
            "life_lessons": ["Depth", "Commitment", "Focus", "Authenticity", "Emotional integration"]
        },
        "Cancer": {
            "symbol": "♋",
            "element": "Water",
            "quality": "Cardinal",
            "ruling_planet": "Moon",
            "keywords": ["Nurturing", "Emotional", "Protective", "Intuitive", "Home-loving"],
            "short_description": "The nurturing protector who creates emotional security through caring bonds.",
            "full_description": """Cancer, the fourth sign, represents the foundation of emotional security and belonging. 
Symbolized by the Crab, Cancer embodies protective instinct, emotional depth, and the drive to nurture and be nurtured. 
As a Cardinal Water sign ruled by the Moon, it combines initiatory energy with fluid emotional sensitivity to create 
safe havens and family bonds.

The Cancer archetype is that of the mother, nurturer, and guardian. This sign governs home, family, emotional needs, 
and ancestral roots. Cancer energy is intuitive, empathetic, and deeply protective of loved ones. These individuals 
excel at creating comfortable environments, providing emotional support, and preserving traditions. They possess 
natural talents in caregiving, real estate, food service, or any field involving nurturing or protection.

In personality, Cancer manifests as sensitivity, intuition, and strong family orientation. These individuals are often 
empathetic listeners with strong emotional intelligence. They excel in careers involving care, history, or home-related 
fields. Cancer natives are devoted partners who value emotional connection and security in relationships.

However, this protective energy creates challenges. The shadow side of Cancer includes moodiness, clinginess, 
indirectness, and difficulty letting go. These individuals may retreat into their shell when hurt, or use emotional 
manipulation to maintain security. Their sensitivity can become oversensitivity or paranoia. Cancer may struggle with 
boundaries, becoming overly dependent or controlling in relationships. The spiritual lessons of Cancer involve 
developing emotional independence, learning to release the past, and extending nurturing beyond immediate family to 
the larger world.""",
            "positive_traits": ["Nurturing", "Intuitive", "Loyal", "Protective", "Imaginative", "Empathetic"],
            "challenging_traits": ["Moody", "Clingy", "Indirect", "Oversensitive", "Manipulative"],
            "body_parts": ["Chest", "Breasts", "Stomach"],
            "career_paths": ["Nursing", "Teaching", "Real Estate", "Food Service", "Counseling"],
            "life_lessons": ["Independence", "Release", "Boundaries", "Objectivity", "Global care"]
        },
        "Leo": {
            "symbol": "♌",
            "element": "Fire",
            "quality": "Fixed",
            "ruling_planet": "Sun",
            "keywords": ["Creative", "Generous", "Dramatic", "Proud", "Leadership"],
            "short_description": "The radiant performer who inspires through creative self-expression and warmth.",
            "full_description": """Leo, the fifth sign, represents the development of creative self-expression and 
individual radiance. Symbolized by the Lion, Leo embodies regal presence, generosity, and the drive to shine and be 
appreciated. As a Fixed Fire sign ruled by the Sun, it combines sustained passion with vital life force to create 
and lead with heart-centered authority.

The Leo archetype is that of the king/queen, performer, and creative artist. This sign governs creativity, romance, 
children, and self-expression. Leo energy is warm, charismatic, and naturally authoritative. These individuals excel 
at inspiring others, creative pursuits, and leadership roles that allow them to shine. They possess natural talents 
in performing arts, teaching, or any field requiring charisma and creativity.

In personality, Leo manifests as confidence, generosity, and dramatic flair. These individuals are often natural 
leaders with a strong presence and warm heart. They excel in careers involving entertainment, education, or management. 
Leo natives are passionate partners who value romance, loyalty, and admiration in relationships.

However, this radiant energy creates challenges. The shadow side of Leo includes arrogance, attention-seeking, 
drama-queening, and difficulty sharing the spotlight. These individuals may become tyrannical or overly dramatic 
when insecure. Their pride can prevent them from admitting mistakes or accepting help. Leo may struggle with 
humility, becoming vain or self-centered. The spiritual lessons of Leo involve learning that true leadership serves 
others, developing humility alongside confidence, and recognizing that everyone's light deserves to shine.""",
            "positive_traits": ["Generous", "Creative", "Warm-hearted", "Confident", "Loyal", "Enthusiastic"],
            "challenging_traits": ["Arrogant", "Attention-seeking", "Dramatic", "Stubborn", "Bossy"],
            "body_parts": ["Heart", "Spine", "Upper Back"],
            "career_paths": ["Acting", "Teaching", "Politics", "Design", "Entertainment"],
            "life_lessons": ["Humility", "Service", "Sharing spotlight", "Authenticity", "Inner validation"]
        },
        "Virgo": {
            "symbol": "♍",
            "element": "Earth",
            "quality": "Mutable",
            "ruling_planet": "Mercury",
            "keywords": ["Analytical", "Practical", "Service-oriented", "Detail-focused", "Efficient"],
            "short_description": "The meticulous analyst who perfects through dedicated service and discernment.",
            "full_description": """Virgo, the sixth sign, represents the organization and refinement of daily life. 
Symbolized by the Virgin, Virgo embodies purity, service, and the drive to analyze and improve. As a Mutable Earth 
sign ruled by Mercury, it combines practical adaptability with analytical intelligence to perfect systems and serve 
others effectively.

The Virgo archetype is that of the craftsman, healer, and analyst. This sign governs work, health, service, and daily 
routines. Virgo energy is detail-oriented, efficient, and dedicated to improvement. These individuals excel at 
organization, problem-solving, and helping others through practical means. They possess natural talents in healthcare, 
editing, research, or any field requiring precision and analysis.

In personality, Virgo manifests as modesty, diligence, and helpfulness. These individuals are often intelligent 
problem-solvers with strong work ethic. They excel in careers involving service, health, or technical skills. Virgo 
natives are reliable partners who show love through practical acts of service.

However, this refining energy creates challenges. The shadow side of Virgo includes criticism, perfectionism, 
worry, and over-analysis. These individuals may become hyper-critical of self and others, leading to anxiety or 
dissatisfaction. Their helpfulness can become meddling or controlling. Virgo may struggle with self-acceptance, 
focusing on flaws rather than wholeness. The spiritual lessons of Virgo involve learning that perfection is an 
illusion, developing compassion alongside discernment, and understanding that true service includes self-care.""",
            "positive_traits": ["Analytical", "Helpful", "Precise", "Reliable", "Intelligent", "Modest"],
            "challenging_traits": ["Critical", "Perfectionist", "Worrying", "Fussy", "Overly cautious"],
            "body_parts": ["Intestines", "Digestive System", "Nervous System"],
            "career_paths": ["Healthcare", "Editing", "Research", "Accounting", "Teaching"],
            "life_lessons": ["Acceptance", "Compassion", "Wholeness", "Self-care", "Flexibility"]
        },
        "Libra": {
            "symbol": "♎",
            "element": "Air",
            "quality": "Cardinal",
            "ruling_planet": "Venus",
            "keywords": ["Harmonious", "Diplomatic", "Social", "Artistic", "Balanced"],
            "short_description": "The gracious diplomat who creates harmony through partnership and aesthetics.",
            "full_description": """Libra, the seventh sign, represents the awareness of others and the drive for balance. 
Symbolized by the Scales, Libra embodies harmony, partnership, and the pursuit of justice and beauty. As a Cardinal 
Air sign ruled by Venus, it combines initiatory social energy with aesthetic refinement to create balanced relationships 
and environments.

The Libra archetype is that of the diplomat, artist, and peacemaker. This sign governs partnerships, marriage, 
social harmony, and aesthetics. Libra energy is gracious, fair-minded, and relationship-oriented. These individuals 
excel at mediation, design, and creating social connections. They possess natural talents in law, arts, diplomacy, 
or any field requiring balance and aesthetics.

In personality, Libra manifests as charm, diplomacy, and artistic sensibility. These individuals are often elegant 
social butterflies with strong sense of fairness. They excel in careers involving law, design, or public relations. 
Libra natives are romantic partners who value equality and harmony in relationships.

However, this harmonizing energy creates challenges. The shadow side of Libra includes indecisiveness, people-pleasing, 
superficiality, and conflict avoidance. These individuals may compromise too much, losing themselves in relationships 
or becoming manipulative to maintain peace. Their love of beauty can become vanity or materialism. Libra may struggle 
with confrontation, preferring indirect approaches. The spiritual lessons of Libra involve developing inner balance 
independent of others, learning decisive action, and understanding that true harmony sometimes requires addressing 
conflict.""",
            "positive_traits": ["Diplomatic", "Charming", "Artistic", "Fair-minded", "Sociable", "Romantic"],
            "challenging_traits": ["Indecisive", "People-pleasing", "Superficial", "Avoidant", "Vain"],
            "body_parts": ["Kidneys", "Lower Back", "Skin"],
            "career_paths": ["Law", "Design", "Diplomacy", "Counseling", "Arts"],
            "life_lessons": ["Decisiveness", "Self-reliance", "Authenticity", "Confrontation", "Inner peace"]
        },
        "Scorpio": {
            "symbol": "♏",
            "element": "Water",
            "quality": "Fixed",
            "ruling_planet": "Pluto (modern), Mars (traditional)",
            "keywords": ["Intense", "Transformative", "Passionate", "Secretive", "Powerful"],
            "short_description": "The profound investigator who transforms through depth and intensity.",
            "full_description": """Scorpio, the eighth sign, represents the deepening of emotional bonds through 
transformation and shared resources. Symbolized by the Scorpion, Eagle, and Phoenix, Scorpio embodies intensity, 
regeneration, and the drive to penetrate life's mysteries. As a Fixed Water sign ruled by Pluto (modern) and Mars 
(traditional), it combines sustained emotional depth with penetrating power to catalyze profound change.

The Scorpio archetype is that of the detective, psychologist, and alchemist. This sign governs transformation, 
sexuality, shared resources, death, and rebirth. Scorpio energy is intense, perceptive, and magnetically powerful. 
These individuals excel at research, crisis management, and psychological insight. They possess natural talents in 
investigation, therapy, finance, or any field requiring depth and strategy.

In personality, Scorpio manifests as intensity, loyalty, and emotional depth. These individuals are often magnetic 
personalities with strong willpower and perceptive minds. They excel in careers involving research, psychology, 
or resource management. Scorpio natives are passionate partners who seek deep, transformative connections in 
relationships.

However, this transformative energy creates challenges. The shadow side of Scorpio includes jealousy, possessiveness, 
secretiveness, and power struggles. These individuals may become manipulative or vengeful when hurt, or obsess over 
control. Their intensity can become destructive or self-destructive. Scorpio may struggle with trust, leading to 
paranoia or isolation. The spiritual lessons of Scorpio involve learning to release control, forgive and let go, 
and use power for healing rather than domination.""",
            "positive_traits": ["Passionate", "Resourceful", "Loyal", "Perceptive", "Determined", "Transformative"],
            "challenging_traits": ["Jealous", "Secretive", "Manipulative", "Vengeful", "Obsessive"],
            "body_parts": ["Reproductive System", "Elimination Organs"],
            "career_paths": ["Psychology", "Investigation", "Finance", "Research", "Surgery"],
            "life_lessons": ["Trust", "Release", "Forgiveness", "Empowerment", "Healing"]
        },
        "Sagittarius": {
            "symbol": "♐",
            "element": "Fire",
            "quality": "Mutable",
            "ruling_planet": "Jupiter",
            "keywords": ["Optimistic", "Adventurous", "Philosophical", "Freedom-loving", "Expansive"],
            "short_description": "The wise explorer who seeks meaning through adventure and philosophy.",
            "full_description": """Sagittarius, the ninth sign, represents the expansion of consciousness through 
exploration and philosophy. Symbolized by the Centaur Archer, Sagittarius embodies the quest for truth, freedom, 
and higher meaning. As a Mutable Fire sign ruled by Jupiter, it combines adaptable enthusiasm with expansive optimism 
to pursue wisdom and growth.

The Sagittarius archetype is that of the philosopher, traveler, and teacher. This sign governs higher education, 
philosophy, long-distance travel, and belief systems. Sagittarius energy is optimistic, adventurous, and truth-seeking. 
These individuals excel at teaching, publishing, or any field involving exploration or big-picture thinking. They 
possess natural talents in sports, academia, or international relations.

In personality, Sagittarius manifests as enthusiasm, honesty, and philosophical bent. These individuals are often 
jovial adventurers with broad perspectives and love of freedom. They excel in careers involving travel, education, 
or law. Sagittarius natives are fun-loving partners who value independence and intellectual stimulation in relationships.

However, this expansive energy creates challenges. The shadow side of Sagittarius includes tactlessness, exaggeration, 
restlessness, and dogmatism. These individuals may become preachy or judgmental about beliefs, or avoid commitment 
through constant movement. Their optimism can become unrealistic or irresponsible. Sagittarius may struggle with 
details and routine. The spiritual lessons of Sagittarius involve developing tact alongside honesty, committing to 
depth in addition to breadth, and recognizing that truth is multifaceted.""",
            "positive_traits": ["Optimistic", "Honest", "Adventurous", "Generous", "Philosophical", "Enthusiastic"],
            "challenging_traits": ["Tactless", "Restless", "Irresponsible", "Dogmatic", "Exaggerating"],
            "body_parts": ["Hips", "Thighs", "Liver"],
            "career_paths": ["Teaching", "Travel", "Publishing", "Law", "Philosophy"],
            "life_lessons": ["Tact", "Commitment", "Realism", "Depth", "Tolerance"]
        },
        "Capricorn": {
            "symbol": "♑",
            "element": "Earth",
            "quality": "Cardinal",
            "ruling_planet": "Saturn",
            "keywords": ["Ambitious", "Disciplined", "Practical", "Responsible", "Patient"],
            "short_description": "The determined achiever who builds lasting structures through discipline.",
            "full_description": """Capricorn, the tenth sign, represents the structuring of society through achievement 
and responsibility. Symbolized by the Sea-Goat, Capricorn embodies ambition, discipline, and the drive to climb to 
the top through persistent effort. As a Cardinal Earth sign ruled by Saturn, it combines initiatory practicality with 
structured determination to build lasting legacies.

The Capricorn archetype is that of the executive, elder, and master builder. This sign governs career, public 
reputation, authority, and long-term goals. Capricorn energy is responsible, strategic, and achievement-oriented. 
These individuals excel at management, planning, and building organizations. They possess natural talents in business, 
politics, or any field requiring discipline and structure.

In personality, Capricorn manifests as ambition, reliability, and dry humor. These individuals are often mature 
beyond their years with strong sense of duty. They excel in careers involving management, finance, or government. 
Capricorn natives are committed partners who value stability and shared goals in relationships.

However, this structuring energy creates challenges. The shadow side of Capricorn includes pessimism, rigidity, 
workaholism, and emotional repression. These individuals may become overly controlling or status-conscious, sacrificing 
personal life for achievement. Their caution can become fear of failure. Capricorn may struggle with expressing 
emotions or enjoying the present moment. The spiritual lessons of Capricorn involve balancing ambition with emotional 
life, learning that vulnerability is strength, and understanding that true success includes inner fulfillment.""",
            "positive_traits": ["Ambitious", "Disciplined", "Responsible", "Patient", "Practical", "Loyal"],
            "challenging_traits": ["Pessimistic", "Rigid", "Workaholic", "Cold", "Controlling"],
            "body_parts": ["Bones", "Knees", "Skin"],
            "career_paths": ["Business", "Politics", "Engineering", "Management", "Finance"],
            "life_lessons": ["Emotional expression", "Joy", "Flexibility", "Inner worth", "Balance"]
        },
        "Aquarius": {
            "symbol": "♒",
            "element": "Air",
            "quality": "Fixed",
            "ruling_planet": "Uranus (modern), Saturn (traditional)",
            "keywords": ["Innovative", "Humanitarian", "Independent", "Intellectual", "Unconventional"],
            "short_description": "The visionary reformer who innovates for collective progress and freedom.",
            "full_description": """Aquarius, the eleventh sign, represents the innovation of society through progressive 
ideals and group consciousness. Symbolized by the Water Bearer, Aquarius embodies humanitarian vision, originality, 
and the drive to reform for the greater good. As a Fixed Air sign ruled by Uranus (modern) and Saturn (traditional), 
it combines sustained intellectual focus with revolutionary energy to create future-oriented change.

The Aquarius archetype is that of the inventor, rebel, and visionary. This sign governs innovation, groups, 
humanitarianism, and future visions. Aquarius energy is independent, progressive, and intellectually detached. 
These individuals excel at networking, invention, and social reform. They possess natural talents in technology, 
science, activism, or any field requiring innovative thinking.

In personality, Aquarius manifests as originality, humanitarianism, and intellectual independence. These individuals 
are often eccentric thinkers with strong social ideals. They excel in careers involving technology, science, or 
social causes. Aquarius natives are freedom-loving partners who value friendship and intellectual equality in 
relationships.

However, this innovative energy creates challenges. The shadow side of Aquarius includes detachment, rebellion for 
its own sake, unpredictability, and intellectual arrogance. These individuals may become emotionally aloof or rigidly 
attached to ideas. Their independence can become isolation or contrariness. Aquarius may struggle with intimacy and 
emotional expression. The spiritual lessons of Aquarius involve balancing group focus with personal relationships, 
integrating heart with mind, and using innovation in service of genuine human needs.""",
            "positive_traits": ["Innovative", "Humanitarian", "Independent", "Intelligent", "Progressive", "Friendly"],
            "challenging_traits": ["Detached", "Unpredictable", "Stubborn", "Aloof", "Rebellious"],
            "body_parts": ["Ankles", "Circulatory System", "Nervous System"],
            "career_paths": ["Technology", "Science", "Activism", "Invention", "Aviation"],
            "life_lessons": ["Emotional connection", "Flexibility", "Intimacy", "Grounding", "Compassion"]
        },
        "Pisces": {
            "symbol": "♓",
            "element": "Water",
            "quality": "Mutable",
            "ruling_planet": "Neptune (modern), Jupiter (traditional)",
            "keywords": ["Compassionate", "Intuitive", "Artistic", "Spiritual", "Imaginative"],
            "short_description": "The mystical dreamer who connects through universal compassion and imagination.",
            "full_description": """Pisces, the twelfth and final sign, represents the dissolution of individual ego into 
universal consciousness. Symbolized by two Fish swimming in opposite directions, 
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
        
        return "\n".join(lines)

# ---------------------------
# Utility functions
# ---------------------------
def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def eprint(*a, **k): print(*a, file=sys.stderr, **k)

def try_install_hint(pkg_list):
    eprint("Some optional functionality needs additional packages.")
    eprint("You can run the following session-only pip install (example):")
    eprint("python3 -m pip install " + " ".join(pkg_list))

# ---------------------------
# Input parsing helpers
# ---------------------------
def parse_date_input(raw_date, preferred_format=None):
    """
    Accepts DD/MM/YYYY or MM/DD/YYYY.
    If ambiguous and preferred_format provided ('DMY' or 'MDY'), obey it.
    Otherwise ask interactively to confirm (interactive mode).
    Returns datetime.date.
    """
    raw = raw_date.strip()
    parts = raw.split("/")
    if len(parts) != 3:
        raise ValueError("Date must be in DD/MM/YYYY or MM/DD/YYYY format")
    a,b,c = parts
    if len(a)==4: # ISO style
        return datetime.fromisoformat(raw).date()
    # numeric parse
    try:
        d1 = int(a); d2 = int(b); y = int(c)
    except Exception:
        raise ValueError("Invalid numeric date parts")
    ambiguous = (d1 <= 12 and d2 <= 12)
    if not ambiguous:
        # decide by which looks like day>12
        if d1 > 12:
            return datetime(y, d1, d2).date()
        else:
            return datetime(y, d2, d1).date()
    if preferred_format == 'DMY':
        return datetime(y, d1, d2).date()
    if preferred_format == 'MDY':
        return datetime(y, d2, d1).date()
    # interactive confirmation
    print(f"Ambiguous date {raw}. Interpret as:")
    print(f"  1) DD/MM/YYYY -> {d1}/{d2}/{y}  (day={d1})")
    print(f"  2) MM/DD/YYYY -> {d2}/{d1}/{y}  (month={d1})")
    choice = input("Choose 1 or 2 (default 1): ").strip() or "1"
    if choice.startswith("2"):
        return datetime(y, d2, d1).date()
    return datetime(y, d1, d2).date()

def parse_time_input(raw_time, tz_hint=None):
    """
    Accepts:
     - 24-hour with optional timezone (17:15 PDT)
     - 12-hour with am/pm (5:15 PM PDT)
     - UTC (00:15)
    Returns aware datetime.time and tzinfo.
    """
    s = raw_time.strip()
    parts = s.split()
    time_part = parts[0]
    tz_part = None
    if len(parts) > 1:
        tz_part = parts[-1]
    # try hh:mm
    # handle am/pm by dateutil if available, else basic parse
    if HAS_DATEUTIL:
        # dateutil can parse time with AM/PM; create a dummy date
        dt = du_parser.parse(time_part + ((" " + tz_part) if tz_part else ""))
        tzinfo = None
        if tz_part:
            tzinfo = resolve_tz(tz_part)
        return dt.time(), tzinfo
    else:
        # basic parse
        if ":" not in time_part:
            raise ValueError("Time must include ':' between hour and minute")
        hh,mm = time_part.split(":")
        hh = int(hh); mm = int(mm)
        tzinfo = resolve_tz(tz_part) if tz_part else None
        return datetime(2000,1,1,hh,mm).time(), tzinfo

def resolve_tz(tz_input):
    """
    Map common abbreviations to IANA via TZ_ABBREV_MAP.
    If given an IANA string, return ZoneInfo.
    If given UTC offset like UTC+2, parse it.
    """
    if not tz_input:
        return None
    s = tz_input.strip()
    if s.upper() in TZ_ABBREV_MAP:
        try:
            return ZoneInfo(TZ_ABBREV_MAP[s.upper()])
        except Exception:
            return ZoneInfo("UTC")
    if s.upper().startswith("UTC"):
        # UTC, UTC+/-HH[:MM]
        rest = s[3:]
        if not rest:
            return timezone.utc
        sign = 1
        if rest[0] in "+-":
            sign = 1 if rest[0]=="+" else -1
            rest = rest[1:]
        parts = rest.split(":")
        hh = int(parts[0]) if parts[0] else 0
        mm = int(parts[1]) if len(parts)>1 else 0
        return timezone(timedelta(hours=sign*hh, minutes=sign*mm))
    # assume it's an IANA name
    try:
        return ZoneInfo(s)
    except Exception:
        # unknown; return UTC as safe default but warn
        print(f"Warning: unknown timezone '{s}', defaulting to UTC")
        return timezone.utc

# ---------------------------
# Geocoding helpers
# ---------------------------
def geocode_location(input_loc, prefer_online=True, max_retries=5):
    """
    Accepts:
     - "City, State, Country"
     - "latitude N longitude W" e.g. "37.7749 N -122.4194 W" or "36.97 N, -122.03 W"
     - Zipcode (e.g., "94108")
    Returns (lat, lon, display_name, tzinfo_str)
    """
    s = str(input_loc).strip()
    # detect lat/lon numeric patterns
    if any(ch.isdigit() for ch in s) and ("," in s or " " in s) and ("N" in s or "S" in s or "E" in s or "W" in s or "-" in s):
        # try to parse numeric lat lon
        # accept forms: "36.9741 N and -122.0308 W" or "36.9741 N, -122.0308 W" or "36.9741 -122.0308"
        toks = s.replace("and", ",").replace("°","").replace("º","").replace("  "," ").replace(" , ",",").replace(" ,",",").replace(", ",",").split(",")
        flat=None; flon=None
        # find two float numbers
        nums = []
        for t in s.replace("N"," ").replace("S"," ").replace("E"," ").replace("W"," ").replace("°"," ").replace("º"," ").replace(","," ").split():
            try:
                nums.append(float(t))
            except:
                pass
        if len(nums)>=2:
            flat=nums[0]; flon=nums[1]
            # handle negative longitude if indicated by W earlier
            if "W" in s.upper() and flon>0:
                flon = -abs(flon)
            if "S" in s.upper() and flat>0:
                flat = -abs(flat)
            # try tzfinder if available
            tzname = None
            if HAS_TFINDER:
                try:
                    tf = TimezoneFinder()
                    tzname = tf.timezone_at(lng=flon, lat=flat)
                except Exception:
                    tzname = None
            return flat, flon, f"Coords {flat},{flon}", tzname
    # detect zipcode numeric
    if s.isdigit() and os.path.exists(ZIPFILE):
        # local lookup in zipcodes.csv: format expected "zipcode,lat,lon,city,state,country"
        with open(ZIPFILE, "r", encoding="utf-8") as fh:
            for line in fh:
                parts = line.strip().split(",")
                if parts and parts[0]==s:
                    try:
                        lat = float(parts[1]); lon = float(parts[2])
                        city = parts[3] if len(parts)>3 else ""
                        state = parts[4] if len(parts)>4 else ""
                        country = parts[5] if len(parts)>5 else ""
                        tzname = None
                        if HAS_TFINDER:
                            try:
                                tf = TimezoneFinder()
                                tzname = tf.timezone_at(lng=lon, lat=lat)
                            except Exception:
                                tzname = None
                        return lat, lon, f"{city},{state},{country}", tzname
                    except:
                        continue
    # attempt Nominatim geocode (online preferred)
    if prefer_online and HAS_REQUESTS:
        url = "https://nominatim.openstreetmap.org/search"
        headers = {"User-Agent":"astrocharts/1.0 (email@example.com)"}
        params = {"q": s, "format":"json", "limit":1}
        backoff = 1
        for attempt in range(max_retries):
            try:
                r = requests.get(url, params=params, headers=headers, timeout=10)
                if r.status_code==200:
                    data = r.json()
                    if data:
                        lat = float(data[0]["lat"]); lon = float(data[0]["lon"])
                        display = data[0].get("display_name","")
                        # timezone via TimezoneFinder or fallback to tz API if available
                        tzname = None
                        if HAS_TFINDER:
                            try:
                                tf = TimezoneFinder()
                                tzname = tf.timezone_at(lng=lon, lat=lat)
                            except Exception:
                                tzname = None
                        return lat, lon, display, tzname
                    else:
                        break
                elif r.status_code in (429, 503):
                    time.sleep(backoff); backoff *= 2; continue
                else:
                    break
            except Exception:
                time.sleep(backoff); backoff *= 2; continue
    # fallback to local zip file search by token (best effort)
    if os.path.exists(ZIPFILE):
        q = s.lower()
        with open(ZIPFILE, "r", encoding="utf-8") as fh:
            for line in fh:
                if q in line.lower():
                    parts = line.strip().split(",")
                    try:
                        lat=float(parts[1]); lon=float(parts[2]); city=parts[3]
                        return lat, lon, f"{parts[3]},{parts[4]},{parts[5]}", None
                    except:
                        continue
    raise ValueError("Could not geocode location; provide lat,lon or ensure data/zipcodes.csv exists or network available for Nominatim")

# ---------------------------
# Astronomical / Ephemeris
# ---------------------------
def load_ephemeris_preference():
    """
    Determine ephemeris backend. Preference:
     - Swiss Ephemeris (pyswisseph) -> Nostradamus
     - Skyfield (JPL) -> Ptolemy fallback (lower precision for some houses)
    """
    if HAS_PYSWISSEPH:
        return "swisseph"
    if HAS_SKYFIELD:
        return "skyfield"
    return "builtin"

def jd_from_datetime(dt_utc):
    """
    Convert Python datetime (UTC-aware) to Julian Day (UTC) for swisseph and other uses.
    Uses algorithm for Julian Day (proleptic Gregorian).
    """
    # dt_utc must be timezone-aware in UTC
    if dt_utc.tzinfo is None:
        raise ValueError("datetime must be timezone-aware UTC")
    # Convert to UTC naive
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
    """
    Uses swisseph to compute planetary geocentric ecliptic longitudes and latitudes,
    distances, moon phases, heliocentric coordinates, house cusps for various systems.
    Returns structured dict.
    """
    res = {}
    if eph_path:
        swe.set_ephe_path(eph_path)
    # ensure ephemeris loaded
    try:
        swe.set_topo(lon, lat, 0) # set earth surface if needed
    except Exception:
        pass
    # planets: swisseph constants
    planet_map = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY, "Venus": swe.VENUS,
        "Mars": swe.MARS, "Jupiter": swe.JUPITER, "Saturn": swe.SATURN,
        "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE, "Pluto": swe.PLUTO
    }
    res["planets"] = {}
    for pname, pid in planet_map.items():
        ret = swe.calc_ut(jd_ut, pid)
        if ret:
            res["planets"][pname] = {"ecl_lon": ret[0][0], "ecl_lat": ret[0][1], "distance_au": ret[0][2]}
    # houses (example Placidus)
    res["houses"] = {}
    house_systems = {'Placidus': 'P', 'Equal': 'E', 'Whole Sign': 'W', 'Porphyry': 'O', 'Campanus': 'C'}
    for hname, hcode in house_systems.items():
        hcusps, ascmc = swe.houses_ex(jd_ut, lat, lon, ord(hcode))
        res["houses"][hname] = {"cusps": hcusps, "ascendant": ascmc[0], "mc": ascmc[3]}
    return res

def compute_planet_positions_skyfield(dt_utc, lat, lon):
    """
    Uses skyfield to compute planetary positions.
    Returns dict with ecliptic longitudes, etc.
    Note: houses approximate.
    """
    res = {}
    ts = load.timescale()
    t = ts.from_datetime(dt_utc)
    planets = load('de421.bsp')
    earth = planets['earth']
    observer = wgs84.latlon(lat * N if lat>0 else -lat * S, lon * E if lon>0 else -lon * W)
    top = earth + observer
    res["planets"] = {}
    sf_planet_map = {
        "Sun": "sun", "Moon": "moon", "Mercury": "mercury barycenter", "Venus": "venus barycenter",
        "Mars": "mars barycenter", "Jupiter": "jupiter barycenter", "Saturn": "saturn barycenter",
        "Uranus": "uranus barycenter", "Neptune": "neptune barycenter", "Pluto": "pluto barycenter"
    }
    for pname, sfname in sf_planet_map.items():
        target = planets[sfname]
        astrometric = top.at(t).observe(target)
        ra, dec, dist = astrometric.radec()
        # convert to ecliptic
        eclip = astrometric.ecliptic_latlon()
        res["planets"][pname] = {"ecl_lon": eclip[1].degrees, "ecl_lat": eclip[0].degrees, "distance_au": dist.au}
    # approximate houses (skyfield doesn't have direct house calc; use approx)
    res["houses"] = {}
    # approx ascendant, etc.
    return res

def equal_house_cusps(asc):
    return [ (asc + i*30) % 360 for i in range(12) ]

def whole_sign_cusps(asc):
    sign_start = (math.floor(asc / 30) * 30) % 360
    return [ (sign_start + i*30) % 360 for i in range(12) ]

def porphyry_cusps(asc, mc):
    # approximate
    return equal_house_cusps(asc)  # placeholder

def campanus_cusps(asc, lat, lon, jd_ut):
    # approximate
    return equal_house_cusps(asc)  # placeholder

def sign_from_degree(deg):
    deg = deg % 360
    idx = int(deg//30)
    sign = SIGNS[idx]
    deg_in_sign = deg - idx*30
    return sign, deg_in_sign

def aspects_between(a_deg, b_deg):
    # return list of aspects with small orb rules
    dif = abs((a_deg - b_deg + 180) % 360 - 180)
    aspects = []
    # aspect table: angle: (name, orb)
    table = {0:("Conjunction",8), 180:("Opposition",8), 120:("Trine",7), 60:("Sextile",6), 90:("Square",6), 150:("Quincunx",3)}
    for ang,(name,orb) in table.items():
        if abs(dif - ang) <= orb:
            aspects.append((name, ang, dif))
    return aspects

# ---------------------------
# Historical events (Wikipedia OnThisDay)
# ---------------------------
def fetch_events_on_date(dt, prefer_online=True):
    """
    dt: datetime.date
    If online and requests available, fetch from Wikipedia API OnThisDay endpoints.
    Else fallback to events_cache.json
    """
    events = []
    if prefer_online and HAS_REQUESTS:
        url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/all/{dt.month}/{dt.day}"
        try:
            r = requests.get(url, timeout=10, headers={"User-Agent":"astrocharts/1.0"})
            if r.status_code == 200:
                data = r.json()
                # pick births, events, deaths condensed
                for cat in ("births","events","deaths"):
                    for item in data.get(cat, [])[:5]:
                        year = item.get("year")
                        text = item.get("text") or item.get("pages",[{}])[0].get("extract")
                        events.append({"category":cat, "year":year, "text": text})
                return events
        except Exception:
            pass
    # fallback
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
# Output formatting and visualization
# ---------------------------
def write_text_file(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)

def create_simple_wheel_png(planet_positions, cusps, outpath):
    """
    Create a simple PNG wheel with planet glyphs as text markers.
    Requires PIL. If not available, skip.
    """
    if not HAS_PIL:
        return False
    size = 1200
    img = Image.new("RGBA", (size,size), "white")
    draw = ImageDraw.Draw(img)
    center = (size//2, size//2)
    radius = int(size*0.4)
    # draw circle
    draw.ellipse((center[0]-radius,center[1]-radius,center[0]+radius,center[1]+radius), outline="black", width=3)
    # draw cusp lines
    for c in cusps:
        ang = math.radians((90 - c) % 360)
        x = center[0] + radius*math.cos(ang)
        y = center[1] - radius*math.sin(ang)
        draw.line([center,(x,y)], fill="black", width=2)
    # place planet markers
    for pname, pdata in planet_positions.items():
        lon = pdata.get("ecl_lon")
        if lon is None:
            continue
        ang = math.radians((90 - lon) % 360)
        pr = radius*0.85
        x = center[0] + pr*math.cos(ang)
        y = center[1] - pr*math.sin(ang)
        draw.text((x-10,y-10), pname[0], fill="red")
    img.save(outpath)
    return True

def create_plotly_wheel(planet_positions, cusps, outpath_html):
    if not HAS_PLOTLY:
        return False
    # create simple polar plot
    labels = []
    angles = []
    radii = []
    for pname, pdata in planet_positions.items():
        lon = pdata.get("ecl_lon")
        if lon is None: continue
        labels.append(pname)
        angles.append((lon/360.0)*2*math.pi)
        radii.append(1)
    fig = go.Figure()
    theta = [math.degrees(a) for a in angles]
    fig.add_trace(go.Barpolar(theta=theta, r=[1]*len(theta), text=labels, marker_color="indianred"))
    fig.update_layout(template=None, title="Planet positions (ecliptic longitudes)")
    fig.write_html(outpath_html)
    return True

# ---------------------------
# Main calculation pipeline
# ---------------------------
def generate_chart(mode, date_str, time_str, tz_input, location_input, date_format_pref=None, interactive=True):
    """
    mode: 'Nostradamus', 'Ptolemy', or 'Paranoid'
    """
    ensure_dirs()
    # parse date
    dt_date = parse_date_input(date_str, preferred_format = 'DMY' if date_format_pref=='DMY' else ('MDY' if date_format_pref=='MDY' else None))
    # parse time
    ttime, tzinfo = parse_time_input(time_str, tz_hint=tz_input)
    tzinfo = tzinfo or resolve_tz(tz_input)
    # assemble datetime with timezone
    if isinstance(tzinfo, ZoneInfo):
        local_dt = datetime.combine(dt_date, ttime).replace(tzinfo=tzinfo)
    elif isinstance(tzinfo, timezone):
        local_dt = datetime.combine(dt_date, ttime).replace(tzinfo=tzinfo)
    else:
        # fallback: assume local is UTC
        local_dt = datetime.combine(dt_date, ttime).replace(tzinfo=timezone.utc)
    # convert to UTC
    dt_utc = local_dt.astimezone(timezone.utc)
    # geocode
    geo_lat, geo_lon, geo_display, tzname = geocode_location(location_input, prefer_online=(mode!="Paranoid"))
    # if tzname exists and tzinfo was None, set tzinfo
    if tzname and (not tzinfo):
        try:
            tzinfo = ZoneInfo(tzname)
            local_dt = local_dt.astimezone(tzinfo)
            dt_utc = local_dt.astimezone(timezone.utc)
        except Exception:
            pass
    # choose ephemeris backend
    backend = load_ephemeris_preference()
    jd_ut = jd_from_datetime(dt_utc)
    astro = {}
    if backend == "swisseph" and mode!="Paranoid":
        # use swisseph (Nostradamus)
        try:
            astro = compute_planet_positions_swisseph(jd_ut, geo_lat, geo_lon)
        except Exception as e:
            eprint("Swiss Ephemeris error:", e)
            astro = {"error":"swisseph failed, fallback to skyfield if available"}
            if HAS_SKYFIELD:
                astro = compute_planet_positions_skyfield(dt_utc, geo_lat, geo_lon)
    elif HAS_SKYFIELD:
        astro = compute_planet_positions_skyfield(dt_utc, geo_lat, geo_lon)
    else:
        astro = {"error":"No ephemeris backend available. Install pyswisseph or skyfield."}
    # Houses: try to extract asc/MC from astro if available; else compute approximate ascendant via sidereal math
    # For fallback, compute ascendant approximate:
    if "houses" in astro and "Placidus" in astro["houses"]:
        asc = astro["houses"]["Placidus"]["ascendant"]
        mc = astro["houses"]["Placidus"]["mc"]
        cusps_pl = astro["houses"]["Placidus"]["cusps"]
    else:
        # approximate ascendant calculation using local sidereal time and obliquity:
        # approximate GST -> LST -> ascendant
        # This is a simplification; accurate ascendant needs full ephemeris.
        # Use skyfield for LST/asc if available
        asc = 0.0; mc = 0.0; cusps_pl = equal_house_cusps(0.0)
    # compute cusps for each requested system using either swisseph results or approximate functions
    cusps = {}
    if "houses" in astro and astro["houses"].get("Placidus"):
        cusps['Placidus'] = astro["houses"]["Placidus"]["cusps"]
    else:
        cusps['Placidus'] = equal_house_cusps(asc)
    cusps['Equal'] = equal_house_cusps(asc)
    cusps['Whole'] = whole_sign_cusps(asc)
    cusps['Porphyry'] = porphyry_cusps(asc, mc)
    cusps['Campanus'] = campanus_cusps(asc, geo_lat, geo_lon, jd_ut)

    # Compose verbose textual report
    verbose_lines = []
    verbose_lines.append(f"Input (interpreted): date={dt_date.isoformat()}, local_time={local_dt.isoformat()}, UTC={dt_utc.isoformat()}")
    verbose_lines.append(f"Location: {geo_display} (lat={geo_lat}, lon={geo_lon})")
    verbose_lines.append(f"Backend: {backend}; Mode: {mode}")
    verbose_lines.append("")
    verbose_lines.append("Planetary positions (ecliptic longitude degrees) and signs:")
    for pname, pdata in astro.get("planets", {}).items():
        if isinstance(pdata, dict) and "ecl_lon" in pdata:
            sign, deg_in = sign_from_degree(pdata["ecl_lon"])
            verbose_lines.append(f" - {pname}: {pdata['ecl_lon']:.4f}° (sign {sign} {deg_in:.2f}°), lat {pdata.get('ecl_lat')}, dist {pdata.get('distance_au') or pdata.get('distance_km')}")
        else:
            verbose_lines.append(f" - {pname}: {pdata}")
    verbose_lines.append("")
    verbose_lines.append("Houses (cusps) by system (degrees):")
    for sysname, cvals in cusps.items():
        verbose_lines.append(f" - {sysname}: " + ", ".join([f"{round(c,4)}" for c in cvals]))
    verbose_lines.append("")
    # aspects summary
    verbose_lines.append("Significant aspects (sample pairwise check among classical planets):")
    planet_list = [p for p in astro.get("planets", {}).keys()]
    for i in range(len(planet_list)):
        for j in range(i+1, len(planet_list)):
            pa = astro["planets"].get(planet_list[i], {})
            pb = astro["planets"].get(planet_list[j], {})
            if not pa or not pb or "ecl_lon" not in pa or "ecl_lon" not in pb:
                continue
            asp = aspects_between(pa["ecl_lon"], pb["ecl_lon"])
            if asp:
                for a in asp:
                    verbose_lines.append(f"  * {planet_list[i]} - {planet_list[j]}: {a[0]} (angle={a[1]}°, diff={a[2]:.2f}°)")

    # summarization
    summary_lines = []
    summary_lines.append("Chart summary:")
    for pname, pdata in astro.get("planets", {}).items():
        if isinstance(pdata, dict) and "ecl_lon" in pdata:
            sign, deg_in = sign_from_degree(pdata["ecl_lon"])
            ruler = RULERS.get(sign, "Unknown")
            summary_lines.append(f"{pname} in {sign} {deg_in:.1f}° (ruler: {ruler})")
    # historical events
    events = fetch_events_on_date(dt_date, prefer_online=(mode!="Paranoid"))
    event_lines = ["Historical events on this date (sample):"]
    if events:
        for ev in events[:8]:
            event_lines.append(f" - [{ev.get('category')}] {ev.get('year')}: {ev.get('text')}")
    else:
        event_lines.append(" - No online events found; check data/events_cache.json for offline entries.")

    # Generate interpretations
    interpreter = ChartInterpreter()
    planets_interp = interpreter.interpret_planets_and_aspects(astro)
    patterns_interp = interpreter.interpret_chart_patterns(astro)
    houses_interp = interpreter.interpret_houses(astro, cusps)
    synthesis = interpreter.generate_synthesis(astro, cusps)
    full_interp = "\n".join([planets_interp, patterns_interp, houses_interp, synthesis])

    # write outputs
    write_text_file(OUT_VERBOSE, "\n".join(verbose_lines))
    write_text_file(OUT_SUMMARY, "\n".join(summary_lines + [""] + event_lines))
    write_text_file(OUT_INTERPRETATION, full_interp)
    with open(OUT_ASTRO_RAW, "w", encoding="utf-8") as fh:
        json.dump({"input": {"date": dt_date.isoformat(), "local_time": local_dt.isoformat(), "utc": dt_utc.isoformat(), "location": {"lat":geo_lat,"lon":geo_lon,"display":geo_display}}, "astro": astro, "cusps": cusps, "events": events}, fh, indent=2)
    # images
    create_simple_wheel_png(astro.get("planets", {}), cusps.get("Placidus", []), OUT_WHEEL_PNG)
    create_plotly_wheel(astro.get("planets", {}), cusps.get("Placidus", []), OUT_WHEEL_HTML)
    # PDF report if fpdf installed
    if HAS_FPDF:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0,6, "\n".join(verbose_lines))
        if os.path.exists(OUT_WHEEL_PNG):
            pdf.image(OUT_WHEEL_PNG, x=10, w=180)
        pdf.output(OUT_PDF)
    # results summary printed to console
    print("Outputs written to 'outputs/' directory:")
    print(" - Verbose chart:", OUT_VERBOSE)
    print(" - Summary:", OUT_SUMMARY)
    print(" - Interpretation:", OUT_INTERPRETATION)
    print(" - Raw astro JSON:", OUT_ASTRO_RAW)
    print(" - Wheel PNG (if PIL available):", OUT_WHEEL_PNG)
    print(" - Wheel interactive HTML (if Plotly available):", OUT_WHEEL_HTML)
    if HAS_FPDF:
        print(" - PDF report:", OUT_PDF)
    print("\nNOTE: For Nostradamus mode exact Swiss Ephemeris calculations, install pyswisseph and ephemeris files.")
    return True

# ---------------------------
# CLI / interactive front end
# ---------------------------
def interactive_mode():
    print("AstroCharts Interactive Mode")
    print("Modes: Nostradamus (swisseph), Ptolemy (skyfield/fallback), Paranoid (offline)")
    mode_choice = input("Choose mode [Nostradamus/Ptolemy/Paranoid] (default Nostradamus): ").strip() or "Nostradamus"
    date_format_pref = None
    df_choice = input("Select date input preference for ambiguous (1) DD/MM/YYYY or (2) MM/DD/YYYY or (3) ask each time (default ask): ").strip()
    if df_choice == "1": date_format_pref = "DMY"
    elif df_choice == "2": date_format_pref = "MDY"
    else: date_format_pref = None
    date_str = input("Enter date (DD/MM/YYYY or MM/DD/YYYY): ").strip()
    time_str = input("Enter time (e.g., 17:15 PDT or 5:15 PM PDT or 00:15 UTC): ").strip()
    tz_hint = input("Optional timezone hint (e.g., PDT or America/Los_Angeles) or press Enter: ").strip() or None
    location = input("Location (City, State, Country OR zipcode OR lat lon): ").strip()
    print("Generating chart... this may take a few seconds.")
    try:
        generate_chart(mode_choice, date_str, time_str, tz_hint, location, date_format_pref=date_format_pref, interactive=True)
    except Exception as e:
        eprint("Error generating chart:", e)
        traceback.print_exc()

def cli_mode(args):
    # args: mode, date, time, tz, location, datefmt
    generate_chart(args.mode, args.date, args.time, args.tz, args.location, date_format_pref=args.datefmt, interactive=False)

def main():
    parser = argparse.ArgumentParser(description="AstroCharts CLI and Interactive tool")
    parser.add_argument("--mode", choices=["Nostradamus","Ptolemy","Paranoid"], default="Nostradamus", help="Computation mode")
    parser.add_argument("--date", help="Date input DD/MM/YYYY or MM/DD/YYYY")
    parser.add_argument("--time", help="Time input e.g. '17:15 PDT' or '5:15 PM PDT' or '00:15 UTC'")
    parser.add_argument("--tz", help="Optional timezone hint (PDT or America/Los_Angeles)")
    parser.add_argument("--location", help="Location: 'City, State, Country' or 'latitude,longitude' or zipcode")
    parser.add_argument("--datefmt", choices=["DMY","MDY"], help="Preferred interpretation for ambiguous dates")
    parser.add_argument("--interactive", action="store_true", help="Interactive prompts")
    args = parser.parse_args()
    ensure_dirs()
    # auto-install hint when critical packages missing for Nostradamus mode
    if args.mode=="Nostradamus" and not HAS_PYSWISSEPH:
        eprint("Swiss Ephemeris (pyswisseph) not detected. Nostradamus mode will fallback to Ptolemy calculations.")
        try_install_hint(["pyswisseph","matplotlib","plotly","pillow","skyfield","timezonefinder","geopy","requests","fpdf"])
    if args.interactive or (not args.date and not args.time and not args.location):
        interactive_mode()
    else:
        if not (args.date and args.time and args.location):
            parser.error("For CLI mode supply --date --time --location or use --interactive")
        cli_mode(args)

if __name__ == "__main__":
    main()
