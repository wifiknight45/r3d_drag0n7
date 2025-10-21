# r3d_drag0n7
a script of astral systems

r3d_drag0n7 (sistema.py) is a comprehensive astronomical and astrological chart generation tool that combines professional-grade ephemeris calculations with flexible input parsing and rich visualization capabilities. Designed as a single-file solution, it offers three distinct computation modes to balance accuracy, dependency requirements, and offline capability.
Whether you're an astrology enthusiast, researcher, or developer building astrological applications, r3d_drag0n7 provides the tools you need with intelligent fallbacks and extensive customization options.

✨ Key Features
🎯 Core Capabilities

Multi-Mode Computation: Choose between Swiss Ephemeris precision, Skyfield accuracy, or pure-Python fallback
Intelligent Date Parsing: Handles DD/MM/YYYY and MM/DD/YYYY formats with interactive disambiguation
Flexible Time Input: Supports 24-hour, 12-hour (AM/PM), timezone abbreviations, IANA timezone names, and UTC offsets
Smart Location Resolution:

City/State/Country via Nominatim geocoding
Direct latitude/longitude coordinates
US ZIP code lookup (with local fallback database)
Automatic timezone detection via TimezoneFinder



📊 Astronomical Calculations

Planetary Positions: Geocentric ecliptic longitude/latitude for all classical planets plus Uranus, Neptune, and Pluto
Multiple House Systems: Placidus, Equal, Whole Sign, Porphyry, and Campanus
Lunar Data: Moon phase calculations and illumination fraction
Aspect Detection: Automatic detection of major aspects (conjunction, opposition, trine, square, sextile, quincunx) with configurable orbs
Dignities & Rulers: Sign rulers and planetary dignities analysis

🎨 Visualization & Output

Text Reports: Verbose charts, summary reports, and interpretative text
Visual Wheels: PNG chart wheels (via PIL) and interactive HTML charts (via Plotly)
PDF Reports: Professional PDF output with embedded images (when fpdf available)
Raw Data Export: JSON format for integration with other tools
Historical Context: Wikipedia OnThisDay events for birth dates (with offline cache fallback)

🔒 Privacy & Offline Support

Paranoid Mode: Fully offline operation using local data files
Cached Data: Local ephemeris snapshots, timezone databases, and historical events
No Tracking: Direct API calls to public services (Nominatim, Wikipedia) with no intermediaries


🎭 Computation Modes
🧙 Nostradamus Mode (Recommended)
High-precision calculations using Swiss Ephemeris

Utilizes pyswisseph for professional-grade accuracy
Exact house cusp calculations for all supported systems
Preferred by professional astrologers
Requires: pyswisseph package and optional ephemeris files

bashpython sistema.py --mode Nostradamus --interactive
🔭 Ptolemy Mode
Reliable fallback using NASA JPL ephemeris

Uses skyfield with DE421 ephemeris data
Good accuracy for planetary positions
Approximate house calculations when Swiss Ephemeris unavailable
Auto-downloads ephemeris data (requires internet on first run)

bashpython sistema.py --mode Ptolemy --interactive
🔐 Paranoid Mode
Complete offline operation

No network requests whatsoever
Uses local data files from data/ directory
Requires pre-populated cache files:

zipcodes.csv for location lookup
tz_cache.csv for timezone resolution
events_cache.json for historical events


Lower precision but complete privacy

bashpython sistema.py --mode Paranoid --interactive

🚀 Installation
Prerequisites

Python 3.8 or higher
pip package manager

Basic Installation

Clone the repository:

bashgit clone https://github.com/wifiknight45/r3d_drag0n7.git
cd r3d_drag0n7

Create data and output directories:

bashmkdir -p data outputs

Run with minimal dependencies:

bashpython sistema.py --interactive
Recommended Installation (Full Features)
For the best experience with all features enabled:
bashpip install pyswisseph skyfield matplotlib plotly pillow fpdf timezonefinder geopy requests python-dateutil
Package breakdown:

pyswisseph: Swiss Ephemeris for Nostradamus mode
skyfield: NASA JPL ephemeris for Ptolemy mode
matplotlib: Chart generation support
plotly: Interactive HTML wheel charts
pillow: PNG wheel image generation
fpdf: PDF report generation
timezonefinder: Automatic timezone detection from coordinates
geopy: Nominatim geocoding for location search
requests: API access for online features
python-dateutil: Enhanced date/time parsing

Minimal Installation (Core Features Only)
For basic functionality without visualization:
bashpip install skyfield requests geopy timezonefinder

⚡ Quick Start
Interactive Mode (Easiest)
bashpython sistema.py --interactive
Follow the prompts to enter:

Computation mode (Nostradamus/Ptolemy/Paranoid)
Date format preference (DD/MM/YYYY or MM/DD/YYYY)
Birth date
Birth time with timezone
Location

Command-Line Mode
bashpython sistema.py \
  --mode Nostradamus \
  --date "15/08/1995" \
  --time "14:30 PDT" \
  --location "San Francisco, CA, USA" \
  --datefmt DMY
Example: Using Coordinates
bashpython sistema.py \
  --mode Ptolemy \
  --date "08/15/1995" \
  --time "2:30 PM America/Los_Angeles" \
  --location "37.7749 N, -122.4194 W" \
  --datefmt MDY
Example: Using ZIP Code
bashpython sistema.py \
  --mode Nostradamus \
  --date "15/08/1995" \
  --time "14:30" \
  --tz "America/Los_Angeles" \
  --location "94102"

📖 Usage Guide
Date Input Formats
The script accepts multiple date formats with intelligent disambiguation:
Supported Formats:

DD/MM/YYYY (European format): 15/08/1995
MM/DD/YYYY (US format): 08/15/1995
YYYY-MM-DD (ISO format): 1995-08-15

Ambiguous Date Handling:
When a date like 05/06/2000 could be interpreted as either May 6th or June 5th:

With --datefmt flag:

bash   --datefmt DMY  # Interprets as DD/MM/YYYY
   --datefmt MDY  # Interprets as MM/DD/YYYY

Without flag (interactive):

Script will prompt you to choose interpretation
Default is DD/MM/YYYY if you press Enter



Time Input Formats
24-Hour Format:
bash--time "17:30"
--time "17:30 PDT"
--time "17:30 America/Los_Angeles"
12-Hour Format (AM/PM):
bash--time "5:30 PM"
--time "5:30 PM PDT"
--time "5:30 PM America/Los_Angeles"
UTC Time:
bash--time "00:30 UTC"
--time "14:30 UTC+0"
UTC Offset:
bash--time "14:30 UTC-7"
--time "14:30 UTC+5:30"  # Supports fractional offsets
Timezone Specifications
Common Abbreviations (Mapped to IANA):

PST, PDT → America/Los_Angeles
EST, EDT → America/New_York
CST, CDT → America/Chicago
MST, MDT → America/Denver
GMT → Etc/Greenwich
BST → Europe/London
CET, CEST → Europe/Paris

IANA Timezone Names (Recommended):
bash--tz "America/Los_Angeles"
--tz "Europe/London"
--tz "Asia/Tokyo"
--tz "Australia/Sydney"
Note: Using IANA names ensures accurate historical DST handling.
Location Input Methods
1. City/State/Country
bash--location "San Francisco, CA, USA"
--location "London, UK"
--location "Mumbai, Maharashtra, India"
2. Latitude/Longitude (Multiple Formats)
bash--location "37.7749 N, -122.4194 W"
--location "37.7749, -122.4194"
--location "37.7749 N and 122.4194 W"
Direction Indicators:

Use N for North latitude (positive)
Use S for South latitude (negative)
Use E for East longitude (positive)
Use W for West longitude (negative)

3. ZIP Code (US Only)
bash--location "94102"
--location "10001"
```

**Requirements:**
- Must have `data/zipcodes.csv` populated with format:
```
  zipcode,lat,lon,city,state,country
  94102,37.7749,-122.4194,San Francisco,CA,USA
```

---

## 🏛️ House Systems

r3d_drag0n7 supports five major house systems, each with different division philosophies:

### 1. **Placidus** (Most Popular)
- Time-based division system
- Unequal houses based on time it takes for degree to rise
- Most commonly used in Western astrology
- Exact calculation requires ephemeris (SwissEph preferred)

### 2. **Equal House**
- Each house is exactly 30° from Ascendant
- Simple and elegant system
- Popular in modern astrology
- Easy to calculate (no ephemeris required)

### 3. **Whole Sign**
- Each house corresponds to one complete zodiac sign
- Ancient system used in Hellenistic astrology
- First house begins at 0° of Ascendant sign
- Independent of birth time precision

### 4. **Porphyry**
- Divides quadrants (ASC→MC, MC→DSC, DSC→IC, IC→ASC) into three equal parts
- Compromise between equal and quadrant systems
- Approximate calculation in Ptolemy mode
- Exact calculation in Nostradamus mode

### 5. **Campanus**
- Based on prime vertical division
- Spatially-oriented system
- Complex calculation (approximate in fallback mode)
- Preferred by some horary astrologers

**House System Output:**
All systems are calculated and output simultaneously, allowing comparison and analysis based on preference.

---

## 📁 Output Files

All outputs are saved to the `outputs/` directory:

### 1. **chart_verbose.txt**
Detailed textual report including:
- Input parameters (interpreted dates, times, locations)
- Complete planetary positions with ecliptic coordinates
- All house cusps for all systems
- Aspect grid with orbs
- Calculation backend information

**Example snippet:**
```
Sun: 142.3456° (sign Leo 22.35°), lat 0.0001, dist 1.0156 AU
Moon: 78.9123° (sign Gemini 18.91°), lat 5.1234, dist 0.0026 AU

Houses (cusps) by system (degrees):
 - Placidus: 15.234, 45.123, 75.456, ...
 - Equal: 15.000, 45.000, 75.000, ...
```

### 2. **chart_summary.txt**
Concise interpretative summary:
- Planet placements in signs with degrees
- Ruling planets for each placement
- Historical events on the birth date
- Quick reference format

**Example:**
```
Sun in Leo 22.3° (ruler: Sun)
Moon in Gemini 18.9° (ruler: Mercury)
Mercury in Virgo 5.2° (ruler: Mercury)

Historical events on this date:
 - [births] 1769: Napoleon Bonaparte born
 - [events] 1945: V-J Day declared
3. astro_data_raw.json
Complete structured data for programmatic use:
json{
  "input": {
    "date": "1995-08-15",
    "local_time": "1995-08-15T14:30:00-07:00",
    "utc": "1995-08-15T21:30:00+00:00",
    "location": {
      "lat": 37.7749,
      "lon": -122.4194,
      "display": "San Francisco, California, USA"
    }
  },
  "astro": {
    "planets": {
      "Sun": {
        "ecl_lon": 142.3456,
        "ecl_lat": 0.0001,
        "distance_au": 1.0156
      }
    },
    "houses": {
      "Placidus": {
        "ascendant": 15.234,
        "mc": 185.678,
        "cusps": [15.234, 45.123, ...]
      }
    }
  }
}
```

### 4. **int_chart_wheel.png**
Visual representation of the chart:
- Circular wheel with house divisions
- Planet symbols placed at ecliptic positions
- House cusps marked with radial lines
- Requires PIL (Pillow) package

### 5. **chart_wheel.html**
Interactive HTML chart:
- Polar plot showing planetary positions
- Hover tooltips with exact degrees
- Zoom and pan capabilities
- Requires Plotly package
- Can be opened directly in web browser

### 6. **chart_report.pdf**
Professional PDF report combining:
- Complete verbose text
- Embedded PNG wheel image
- Print-ready format
- Requires fpdf package

---

## 📦 Dependencies

### Core Dependencies (Included in Python)
- `sys`, `os`, `math`, `json`, `time`, `traceback`
- `datetime`, `zoneinfo`, `argparse`, `shutil`

### Optional Dependencies

| Package | Purpose | Mode Benefits | Install Command |
|---------|---------|---------------|-----------------|
| `pyswisseph` | Swiss Ephemeris calculations | **Essential** for Nostradamus mode | `pip install pyswisseph` |
| `skyfield` | NASA JPL ephemeris | **Essential** for Ptolemy mode | `pip install skyfield` |
| `matplotlib` | Chart generation support | Enhanced visualizations | `pip install matplotlib` |
| `plotly` | Interactive HTML charts | Interactive wheel charts | `pip install plotly` |
| `pillow` (PIL) | PNG image generation | Chart wheel images | `pip install pillow` |
| `fpdf` | PDF report generation | PDF output | `pip install fpdf` |
| `geopy` | Location geocoding | Online location search | `pip install geopy` |
| `timezonefinder` | Timezone from coordinates | Automatic TZ detection | `pip install timezonefinder` |
| `requests` | HTTP requests | Online features | `pip install requests` |
| `python-dateutil` | Enhanced date parsing | Better time input parsing | `pip install python-dateutil` |

### Dependency Detection

The script automatically detects available packages and gracefully degrades:
- Missing visualization packages → Text-only output
- Missing ephemeris → Falls back to lower precision mode
- Missing geocoding → Requires manual lat/lon input
- All missing → Core calculations still work with manual inputs

---

## 🏗️ Architecture

### Modular Design
```
sistema.py
├── Configuration (DATA_DIR, OUTPUT_DIR, constants)
├── Dependency Detection (HAS_PYSWISSEPH, HAS_SKYFIELD, etc.)
├── Utility Functions
│   ├── ensure_dirs()
│   ├── eprint()
│   └── try_install_hint()
├── Input Parsing
│   ├── parse_date_input()
│   ├── parse_time_input()
│   └── resolve_tz()
├── Geocoding
│   └── geocode_location()
├── Astronomical Calculations
│   ├── jd_from_datetime()
│   ├── compute_planet_positions_swisseph()
│   └── compute_planet_positions_skyfield()
├── House System Calculations
│   ├── equal_house_cusps()
│   ├── whole_sign_cusps()
│   ├── porphyry_cusps()
│   └── campanus_cusps()
├── Astrological Interpretation
│   ├── sign_from_degree()
│   └── aspects_between()
├── Historical Data
│   └── fetch_events_on_date()
├── Output Generation
│   ├── write_text_file()
│   ├── create_simple_wheel_png()
│   └── create_plotly_wheel()
├── Main Pipeline
│   └── generate_chart()
└── User Interface
    ├── interactive_mode()
    ├── cli_mode()
    └── main()
```

### Data Flow

1. **Input Stage**: Parse command-line arguments or interactive prompts
2. **Normalization**: Convert dates/times to UTC-aware datetime objects
3. **Location Resolution**: Geocode to lat/lon coordinates with timezone
4. **Ephemeris Selection**: Choose backend (swisseph → skyfield → fallback)
5. **Calculation**: Compute planetary positions and house cusps
6. **Interpretation**: Calculate aspects, dignities, and historical context
7. **Output Generation**: Create all requested output formats
8. **File Writing**: Save to `outputs/` directory

---

## 🔬 Advanced Features

### Aspect Detection

The script automatically detects major aspects with configurable orbs:

| Aspect | Angle | Default Orb | Interpretation |
|--------|-------|-------------|----------------|
| Conjunction | 0° | ±8° | Unity, blending of energies |
| Opposition | 180° | ±8° | Tension, awareness, polarity |
| Trine | 120° | ±7° | Harmony, ease, flow |
| Square | 90° | ±6° | Challenge, dynamic tension |
| Sextile | 60° | ±6° | Opportunity, cooperation |
| Quincunx | 150° | ±3° | Adjustment, inconjunct |

**Output Format:**
```
Sun - Moon: Trine (angle=120°, diff=118.45°)
Moon - Mars: Square (angle=90°, diff=92.13°)
Venus - Jupiter: Conjunction (angle=0°, diff=3.21°)
Dignity System
Automatic planetary ruler identification:
SignRulerSignRulerAriesMarsLibraVenusTaurusVenusScorpioMarsGeminiMercurySagittariusJupiterCancerMoonCapricornSaturnLeoSunAquariusSaturnVirgoMercuryPiscesJupiter
Note: Modern rulers (Uranus for Aquarius, Neptune for Pisces, Pluto for Scorpio) can be added by modifying the RULERS dictionary.
Historical Events Integration
Wikipedia OnThisDay API provides context:

Notable births on the date
Historical events
Deaths of notable figures
Online mode fetches real-time data
Paranoid mode uses local cache

Cache Format (data/events_cache.json):
json{
  "08-15": [
    {"category": "births", "year": 1769, "text": "Napoleon Bonaparte"},
    {"category": "events", "year": 1945, "text": "V-J Day"},
    {"category": "deaths", "year": 1935, "text": "Will Rogers"}
  ]
}
Lunar Calculations
Beyond basic Moon position:

Phase Angle: Elongation from Sun (0° = New, 180° = Full)
Illumination Fraction: Percentage of visible disc illuminated
Distance: Earth-Moon distance in AU


🔧 Troubleshooting
Common Issues
"Swiss Ephemeris not detected"
Solution: Install pyswisseph or use Ptolemy mode:
bashpip install pyswisseph
# OR
python sistema.py --mode Ptolemy
"Could not geocode location"
Symptoms: Location lookup fails
Solutions:

Check internet connection (for online modes)
Use direct coordinates: --location "37.7749, -122.4194"
Populate data/zipcodes.csv for ZIP lookups
Try alternate location format (add country)

"Ambiguous date" prompts every time
Solution: Set date format preference:
bash--datefmt DMY  # For DD/MM/YYYY preference
--datefmt MDY  # For MM/DD/YYYY preference
"No ephemeris backend available"
Solution: Install at least one ephemeris package:
bashpip install skyfield  # Easier installation
# OR
pip install pyswisseph  # Higher precision
PNG/HTML output missing
Symptoms: Only text files generated
Solution: Install visualization packages:
bashpip install pillow plotly matplotlib
TimezoneFinder warnings
Symptoms: Timezone detection fails
Solution:
bashpip install timezonefinder
# If still issues, manually specify timezone:
--tz "America/Los_Angeles"
Debug Mode
For verbose error tracking, run with Python debug:
bashpython -u sistema.py --interactive 2>&1 | tee debug.log
Checking Installed Packages
bashpython -c "import sistema; print('PySwisseph:', sistema.HAS_PYSWISSEPH); print('Skyfield:', sistema.HAS_SKYFIELD); print('PIL:', sistema.HAS_PIL)"
```

---

## 🗂️ Directory Structure
```
r3d_drag0n7/
├── sistema.py              # Main script (all-in-one)
├── README.md               # This file
├── LICENSE                 # MIT License
├── data/                   # Local data files (optional)
│   ├── zipcodes.csv       # ZIP code database (format: zip,lat,lon,city,state,country)
│   ├── tz_cache.csv       # Timezone cache
│   ├── events_cache.json  # Historical events offline cache
│   ├── ephem_snapshot.json # Ephemeris data snapshot (future use)
│   └── keys.json          # API keys (currently unused, reserved)
└── outputs/               # Generated output files
    ├── chart_verbose.txt
    ├── chart_summary.txt
    ├── astro_data_raw.json
    ├── int_chart_wheel.png
    ├── chart_wheel.html
    └── chart_report.pdf

🎯 Use Cases
Personal Birth Chart Analysis
bashpython sistema.py --interactive
Generate comprehensive natal chart with interpretations.
Research & Data Collection
bashfor date in {01..31}; do
  python sistema.py --mode Nostradamus \
    --date "01/${date}/2000" --time "12:00 UTC" \
    --location "0,0" --datefmt MDY
done
Batch generation for statistical analysis.
Educational Tool
Use Ptolemy mode for teaching astronomy/astrology concepts without complex dependencies.
Historical Event Correlation
Combine astronomical data with Wikipedia events to explore historical patterns.
Application Integration
Use astro_data_raw.json as input for web applications, mobile apps, or other tools.

🛠️ Development & Extension
Adding New House Systems
Edit the house calculation section:
pythondef custom_house_cusps(asc, mc, lat, lon):
    # Your calculation logic
    cusps = [...]  # 12-element list
    return cusps

# In generate_chart():
cusps['Custom'] = custom_house_cusps(asc, mc, geo_lat, geo_lon)
Adding Asteroids/Fixed Stars
For Swiss Ephemeris mode:
python# Add to sw_planets dict:
sw_planets["Chiron"] = swe.CHIRON
sw_planets["Ceres"] = swe.CERES

# For fixed stars, use swe.fixstar()
Custom Aspect Orbs
Modify the aspects_between() function:
pythontable = {
    0: ("Conjunction", 10),    # Wider orb
    180: ("Opposition", 10),
    120: ("Trine", 8),
    # Add new aspects:
    45: ("Semi-square", 2),
    135: ("Sesquiquadrate", 2)
}
Output Formatters
Add new output functions:
pythondef create_svg_wheel(planet_positions, cusps, outpath):
    # SVG generation logic
    pass

# Call in generate_chart()
create_svg_wheel(astro["planets"], cusps["Placidus"], OUT_WHEEL_SVG)
```

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

### High Priority
- [ ] Arabic Parts calculation (Part of Fortune, etc.)
- [ ] Midpoint analysis
- [ ] Progressed chart calculations
- [ ] Solar return chart generation
- [ ] Aspect patterns detection (T-Square, Grand Trine, etc.)

### Medium Priority
- [ ] More house systems (Koch, Regiomontanus, Morinus)
- [ ] Fixed stars integration
- [ ] Asteroid ephemeris (Chiron, Ceres, Pallas, Juno, Vesta)
- [ ] Lunar nodes (True/Mean)
- [ ] Enhanced dignity system (exaltation, detriment, fall)

### Nice to Have
- [ ] SVG wheel generation
- [ ] LaTeX report generation
- [ ] Database storage for multiple charts
- [ ] Chart comparison (synastry, composite)
- [ ] Transit calculation
- [ ] Harmonic charts

### Contribution Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Maintain single-file architecture (unless splitting is clearly justified)
4. Test with all three modes (Nostradamus, Ptolemy, Paranoid)
5. Update README if adding new features
6. Commit with clear messages (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License:
```
MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

- **Swiss Ephemeris**: Astrodienst AG for the high-precision ephemeris library
- **NASA JPL**: For DE421 and other ephemeris datasets
- **Skyfield**: Brandon Rhodes for the excellent Python astronomy library
- **OpenStreetMap**: Nominatim geocoding service
- **Wikipedia**: OnThisDay API for historical context
- **Astrology Community**: For house system algorithms and traditional wisdom

---

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/wifiknight45/r3d_drag0n7/issues)
- **Discussions**: [GitHub Discussions](https://github.com/wifiknight45/r3d_drag0n7/discussions)
- **Repository**: [https://github.com/wifiknight45/r3d_drag0n7](https://github.com/wifiknight45/r3d_drag0n7)

---

## 🌠 Example Session
```
$ python sistema.py --interactive

AstroCharts Interactive Mode
Modes: Nostradamus (swisseph), Ptolemy (skyfield/fallback), Paranoid (offline)
Choose mode [Nostradamus/Ptolemy/Paranoid] (default Nostradamus): Nostradamus

Select date input preference for ambiguous (1) DD/MM/YYYY or (2) MM/DD/YYYY or (3) ask each time (default ask): 1

Enter date (DD/MM/YYYY or MM/DD/YYYY): 15/08/1995

Enter time (e.g., 17:15 PDT or 5:15 PM PDT or 00:15 UTC): 2:30 PM PDT

Optional timezone hint (e.g., PDT or America/Los_Angeles) or press Enter: 

Location (City, State, Country OR zipcode OR lat lon): San Francisco, CA, USA

Generating chart... this may take a few seconds.

Outputs written to 'outputs/' directory:
 - Verbose chart: outputs/chart_verbose.txt
 - Summary: outputs/chart_summary.txt
 - Raw astro JSON: outputs/astro_data_raw.json
 - Wheel PNG (if PIL available): outputs/int_chart_wheel.png
 - Wheel interactive HTML (if Plotly available): outputs/chart_wheel.html
 - PDF report: outputs/chart_report.pdf

NOTE: For Nostradamus mode exact Swiss Ephemeris calculations, install pyswisseph and ephemeris files.

Made with ✨ for the stars • Calculated with precision • Interpreted with wisdom

"As above, so below; as within, so without."
