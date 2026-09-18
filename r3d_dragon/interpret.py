"""Chart interpretation with unified cusp shape support."""
from __future__ import annotations

from .knowledge import AstrologicalKnowledge, RULERS, SIGNS, PLANETS
from .houses import get_placidus_cusps, normalize_cusp_system


def sign_from_degree(deg):
    deg = deg % 360
    idx = int(deg // 30)
    return SIGNS[idx], deg - idx * 30


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
        placidus_cusps = get_placidus_cusps(cusps)
        
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
        plac = normalize_cusp_system(cusps.get("Placidus")) if cusps else None
        if plac and plac.get("cusps"):
            asc = plac["asc"] if plac.get("asc") is not None else plac["cusps"][0]
            asc_sign, asc_deg = sign_from_degree(asc)
            lines.append(f"\n*** OUTER PERSONALITY (Ascendant in {asc_sign}) ***")
            lines.append(f"Your physical appearance, first impressions, and approach to new situations are {asc_sign}.")
            lines.append(f"Others initially perceive you as embodying {asc_sign} traits, which may differ from")
            lines.append(f"your inner Sun and Moon nature. This is your social mask and life strategy.")
        
        # Look for chart ruler
        if plac and plac.get("cusps") and "ecl_lon" in sun_data:
            asc_sign, _ = sign_from_degree(plac["asc"] if plac.get("asc") is not None else plac["cusps"][0])
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


    @staticmethod
    def generate_detailed_horoscope(astro_data, cusps, name: str | None = None):
        """Detailed natal horoscope: personality, love, career, money, health, growth."""
        planets = astro_data.get("planets", {}) or {}
        who = (name or "You").strip() or "You"
        lines: list[str] = []
        lines.append("=" * 80)
        lines.append(f"DETAILED NATAL HOROSCOPE — {who}")
        lines.append("=" * 80)
        lines.append(
            "Educational astrology narrative grounded on computed placements. "
            "Not medical, legal, or financial advice."
        )

        def _p(pname: str):
            pdata = planets.get(pname) or {}
            if isinstance(pdata, dict) and "ecl_lon" in pdata:
                sign, deg = sign_from_degree(pdata["ecl_lon"])
                return sign, deg, pdata
            return None, None, None

        sun_sign, sun_deg, _ = _p("Sun")
        moon_sign, moon_deg, _ = _p("Moon")
        merc_sign, _, _ = _p("Mercury")
        venus_sign, _, _ = _p("Venus")
        mars_sign, _, _ = _p("Mars")
        jup_sign, _, _ = _p("Jupiter")
        sat_sign, _, _ = _p("Saturn")

        plac = normalize_cusp_system(cusps.get("Placidus")) if cusps else None
        asc_sign = asc_deg = None
        if plac and plac.get("cusps"):
            asc = plac["asc"] if plac.get("asc") is not None else plac["cusps"][0]
            asc_sign, asc_deg = sign_from_degree(asc)

        # —— Big three ——
        lines.append("\n" + "-" * 80)
        lines.append("1) THE BIG THREE — who you are")
        lines.append("-" * 80)
        if sun_sign:
            info = AstrologicalKnowledge.SIGN_DESCRIPTIONS.get(sun_sign, {})
            lines.append(f"\nSUN in {sun_sign} ({sun_deg:.1f}°)")
            lines.append(f"  Element / quality: {info.get('element', '?')} · {info.get('quality', '?')}")
            lines.append(f"  Keywords: {', '.join(info.get('keywords', [])[:6])}")
            lessons = info.get('life_lessons') or []
            lines.append(f"  Life lessons: {', '.join(lessons[:4]) if lessons else 'self-expression'}")
            if info.get('short_description'):
                lines.append(f"  Snapshot: {info['short_description']}")
            lines.append(AstrologicalKnowledge.get_sign_interpretation(sun_sign, "Sun"))
        if moon_sign:
            info = AstrologicalKnowledge.SIGN_DESCRIPTIONS.get(moon_sign, {})
            lines.append(f"\nMOON in {moon_sign} ({moon_deg:.1f}°)")
            lines.append(f"  Emotional climate: {', '.join(info.get('keywords', [])[:5])}")
            lines.append(AstrologicalKnowledge.get_sign_interpretation(moon_sign, "Moon"))
        if asc_sign:
            info = AstrologicalKnowledge.SIGN_DESCRIPTIONS.get(asc_sign, {})
            lines.append(f"\nRISING (Ascendant) in {asc_sign} ({asc_deg:.1f}°)")
            lines.append(f"  First impression / life approach: {', '.join(info.get('keywords', [])[:5])}")
            lines.append(AstrologicalKnowledge.get_sign_interpretation(asc_sign, "Ascendant"))

        # —— Love ——
        lines.append("\n" + "-" * 80)
        lines.append("2) LOVE & RELATIONSHIPS")
        lines.append("-" * 80)
        if venus_sign:
            lines.append(f"\nVenus in {venus_sign} — affection, attraction, aesthetics")
            lines.append(AstrologicalKnowledge.get_sign_interpretation(venus_sign, "Venus"))
            lines.append(
                f"  In romance, {who} tends to give and receive love through {venus_sign} themes: "
                f"{', '.join(AstrologicalKnowledge.SIGN_DESCRIPTIONS.get(venus_sign, {}).get('keywords', ['connection'])[:4])}."
            )
        if mars_sign:
            lines.append(f"\nMars in {mars_sign} — desire, chemistry, conflict style")
            lines.append(AstrologicalKnowledge.get_sign_interpretation(mars_sign, "Mars"))
        if moon_sign and venus_sign:
            lines.append(
                f"\nHeart note: Moon ({moon_sign}) + Venus ({venus_sign}) describe the private need vs the "
                f"social charm of relating — notice where they agree and where they tension."
            )

        # —— Career ——
        lines.append("\n" + "-" * 80)
        lines.append("3) CAREER, AMBITION & PURPOSE")
        lines.append("-" * 80)
        if sun_sign:
            careers = AstrologicalKnowledge.SIGN_DESCRIPTIONS.get(sun_sign, {}).get("career_paths") or \
                      AstrologicalKnowledge.SIGN_DESCRIPTIONS.get(sun_sign, {}).get("careers") or []
            if careers:
                lines.append(f"\nSun-path career flavors ({sun_sign}): {', '.join(careers[:8])}")
            else:
                lines.append(f"\nSun in {sun_sign} points vocation toward that sign's mastery arena.")
        if mars_sign:
            lines.append(f"Mars in {mars_sign} shows how {who} fights for goals and initiates projects.")
        if sat_sign:
            lines.append(f"Saturn in {sat_sign} — long game, responsibility, mastery curve.")
            lines.append(AstrologicalKnowledge.get_sign_interpretation(sat_sign, "Saturn"))
        if jup_sign:
            lines.append(f"Jupiter in {jup_sign} — growth, luck, teaching/expansion style.")
            lines.append(AstrologicalKnowledge.get_sign_interpretation(jup_sign, "Jupiter"))

        # —— Money ——
        lines.append("\n" + "-" * 80)
        lines.append("4) MONEY, VALUES & RESOURCES")
        lines.append("-" * 80)
        if venus_sign:
            lines.append(
                f"Venus in {venus_sign} flavors what feels valuable — spending, collecting, and "
                f"negotiating often follow this sign's taste."
            )
        # 2nd house cusp if available
        if plac and plac.get("cusps") and len(plac["cusps"]) >= 2:
            s2, d2 = sign_from_degree(plac["cusps"][1])
            lines.append(f"2nd-house cusp in {s2} ({d2:.1f}°) — money/values house tone.")
            lines.append(AstrologicalKnowledge.get_house_interpretation(2))
        if plac and plac.get("cusps") and len(plac["cusps"]) >= 8:
            s8, d8 = sign_from_degree(plac["cusps"][7])
            lines.append(f"8th-house cusp in {s8} ({d8:.1f}°) — shared resources / deeper bonds.")

        # —— Mind ——
        lines.append("\n" + "-" * 80)
        lines.append("5) MIND & COMMUNICATION")
        lines.append("-" * 80)
        if merc_sign:
            lines.append(f"Mercury in {merc_sign} — thinking, learning, talking.")
            lines.append(AstrologicalKnowledge.get_sign_interpretation(merc_sign, "Mercury"))

        # —— Wellness ——
        lines.append("\n" + "-" * 80)
        lines.append("6) BODY, NERVOUS SYSTEM & CARE (symbolic)")
        lines.append("-" * 80)
        lines.append("Symbolic only — not medical advice.")
        if sun_sign:
            body = AstrologicalKnowledge.SIGN_DESCRIPTIONS.get(sun_sign, {}).get("body_parts") or []
            if body:
                lines.append(f"Sun/{sun_sign} traditional body focus: {', '.join(body[:6])}")
        if moon_sign:
            lines.append(f"Moon in {moon_sign}: honor emotional rhythms; rest when the {moon_sign} instinct asks for safety.")
        if mars_sign:
            lines.append(f"Mars in {mars_sign}: channel heat through movement that matches this sign — avoid bottled friction.")

        # —— Growth ——
        lines.append("\n" + "-" * 80)
        lines.append("7) GROWTH EDGE & PRACTICAL GUIDANCE")
        lines.append("-" * 80)
        if sat_sign:
            lessons = AstrologicalKnowledge.SIGN_DESCRIPTIONS.get(sat_sign, {}).get("life_lessons") or []
            edge = ", ".join(lessons[:3]) if lessons else "discipline through that sign's craft"
            lines.append(f"Saturn/{sat_sign} growth edge: {edge}.")
        if sun_sign and moon_sign and sun_sign != moon_sign:
            lines.append(
                f"Integrate solar {sun_sign} will with lunar {moon_sign} needs — schedule both ambition and replenishment."
            )
        if asc_sign and sun_sign and asc_sign != sun_sign:
            lines.append(
                f"Others meet {asc_sign} first; your {sun_sign} core unfolds on a longer fuse — let trust earn depth."
            )
        lines.append(
            f"\nDaily practice idea for {who}: one act that feeds the Sun, one that soothes the Moon, "
            f"one honest Mercury conversation."
        )

        lines.append("\n" + "=" * 80)
        lines.append("END DETAILED HOROSCOPE")
        lines.append("=" * 80)
        return "\n".join(lines)

