"""Chart interpretation with unified cusp shape support."""
from __future__ import annotations

from .knowledge import AstrologicalKnowledge, RULERS, SIGNS
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

