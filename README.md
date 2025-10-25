![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows-lightgrey)
![Astrology](https://img.shields.io/badge/astrology-charts-purple)
![Ephemeris](https://img.shields.io/badge/ephemeris-swiss%20%7C%20nasa-orange)
![Outputs](https://img.shields.io/badge/output-txt%20%7C%20json%20%7C%20png%20%7C%20html%20%7C%20pdf-informational)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)

# r3d_drag0n7 is under dev, check back for updates etc. 

a script of astral systems

r3d_drag0n7 (sistema.py) is a comprehensive astronomical and astrological chart generation tool that combines professional-grade ephemeris calculations with flexible input parsing and rich visualization capabilities. Designed as a single-file solution, it offers three distinct computation modes to balance accuracy, dependency requirements, and offline capability.
Whether you're an astrology enthusiast, researcher, or developer building astrological applications, r3d_drag0n7 provides the tools you need with intelligent fallbacks and extensive customization options.


## Overview

This system generates complete astrological birth charts with detailed interpretations based on planetary positions, house systems, and chart patterns. It supports multiple calculation backends, offline operation modes, and produces comprehensive reports suitable for both technical analysis and readable interpretations.

## Features

### Core Functionality

- **Multiple Calculation Modes**: Nostradamus (high-accuracy Swiss Ephemeris), Ptolemy (Skyfield fallback), and Paranoid (offline-only)
- **Flexible Date/Time Input**: Supports DD/MM/YYYY and MM/DD/YYYY formats with intelligent disambiguation, 12-hour and 24-hour time formats with AM/PM
- **Smart Timezone Handling**: Common abbreviations (PST, EST, etc.), IANA timezone names, UTC offsets
- **Location Geocoding**: City/state/country lookup via Nominatim, US zipcode support, direct latitude/longitude coordinates
- **Multiple House Systems**: Placidus, Equal House, Whole Sign, Porphyry, Campanus

### Astrological Content

- **Planetary Positions**: All traditional planets (Sun through Pluto) with ecliptic longitude, latitude, and distance
- **Comprehensive Sign Descriptions**: Element, quality, ruling planet, keywords, traits, body correspondences, career paths, life lessons
- **Detailed Interpretations**: Planet-in-sign meanings, degree analysis (early/middle/late), chart synthesis
- **Chart Pattern Detection**: Stelliums (3+ planets in same sign), elemental balance analysis, dominant element identification
- **Historical Context**: Wikipedia OnThisDay events for birth dates with offline fallback cache

### Output Formats

- **Verbose Chart**: Complete technical data including all planetary positions and house cusps
- **Summary Report**: Concise planet placements with rulerships and historical events
- **Detailed Interpretation**: Comprehensive astrological analysis with sign descriptions and chart patterns
- **JSON Data**: Machine-readable astronomical data for further processing
- **Visual Charts**: PNG chart wheel (PIL) and interactive HTML wheel (Plotly)
- **PDF Report**: Complete formatted report with chart wheel image

## Installation

### Prerequisites

Python 3.7 or higher with `zoneinfo` support (Python 3.9+ recommended)

### Basic Installation

```bash
git clone https://github.com/wifiknight45/r3d_drag0n7.git
cd astrological-chart-generator OR r3d_drag0n7
```

### Dependencies

Install required dependencies based on desired functionality:

**Core Dependencies** (recommended for full functionality):
```bash
pip install pyswisseph skyfield matplotlib plotly pillow fpdf timezonefinder geopy requests python-dateutil
```

**Minimal Installation** (basic functionality only):
```bash
pip install skyfield
```

**Optional Dependencies by Feature**:
- High-accuracy calculations: `pyswisseph`
- Skyfield calculations: `skyfield`
- PNG charts: `pillow`
- Interactive HTML charts: `plotly`
- PDF reports: `fpdf`
- Timezone detection: `timezonefinder`
- Location geocoding: `geopy`
- Online features: `requests`
- Enhanced date parsing: `python-dateutil`

## Usage

### Interactive Mode

The easiest way to use the system:

```bash
python sistema_completa.py --interactive
```

Follow the prompts to enter birth date, time, location, and preferences.

### Command Line Interface

For automated or scripted usage:

```bash
python sistema_completa.py --date "15/08/1990" --time "14:30 PST" --location "San Francisco, CA"
```

### CLI Arguments

```
--mode {Nostradamus,Ptolemy,Paranoid}
    Computation mode (default: Nostradamus)

--date DATE
    Birth date in DD/MM/YYYY or MM/DD/YYYY format

--time TIME
    Birth time: '14:30' or '2:30 PM' (with optional timezone)

--tz TIMEZONE
    Timezone: 'PST', 'America/Los_Angeles', 'UTC+5:30', etc.

--location LOCATION
    Location: 'City, State, Country', zipcode, or 'lat,lon'

--datefmt {DMY,MDY}
    Date format preference for ambiguous dates

--interactive, -i
    Run in interactive mode with prompts
```

## Computation Modes

### Nostradamus Mode (Default)

Uses Swiss Ephemeris (pyswisseph) for highest accuracy. Requires ephemeris data files.

**Accuracy**: Sub-arcsecond precision for most calculations  
**Requirements**: `pyswisseph` package, optional ephemeris files in `data/` directory  
**Use Cases**: Professional astrology, research, precision calculations

### Ptolemy Mode

Fallback mode using Skyfield with NASA JPL ephemeris data.

**Accuracy**: High precision for most purposes  
**Requirements**: `skyfield` package, internet access for ephemeris download (cached after first use)  
**Use Cases**: General use when Swiss Ephemeris unavailable

### Paranoid Mode

Offline-only mode using cached data, no internet connections.

**Accuracy**: Depends on available cached data  
**Requirements**: Pre-populated cache files in `data/` directory  
**Use Cases**: Privacy-sensitive applications, air-gapped systems

## Input Formats

### Date Formats

- **DD/MM/YYYY**: European format (e.g., `15/08/1990`)
- **MM/DD/YYYY**: US format (e.g., `08/15/1990`)
- **Ambiguous dates**: System will prompt for confirmation or use `--datefmt` preference

### Time Formats

- **24-hour**: `14:30`, `09:15`
- **12-hour with AM/PM**: `2:30 PM`, `9:15 AM`
- **With timezone**: `14:30 PST`, `2:30 PM EST`

### Timezone Formats

- **Abbreviations**: PST, PDT, EST, EDT, CST, CDT, MST, MDT, UTC, GMT, BST, CET, CEST
- **IANA names**: `America/Los_Angeles`, `Europe/London`, `Asia/Tokyo`
- **UTC offsets**: `UTC`, `UTC+5:30`, `UTC-8`

### Location Formats

- **City/State/Country**: `San Francisco, CA, USA` or `London, UK`
- **US Zipcode**: `94102` (requires zipcodes.csv)
- **Coordinates**: `37.7749,-122.4194` or `37.7749 N, 122.4194 W`

## Output Files

All output files are saved to the `outputs/` directory:

### Text Reports

- **chart_verbose.txt**: Complete technical chart data with all positions and house cusps
- **chart_summary.txt**: Concise summary with planet placements and historical events
- **chart_interpretation.txt**: Detailed astrological interpretation with sign descriptions and chart patterns

### Data Files

- **astro_data_raw.json**: Machine-readable JSON containing all astronomical data, input parameters, and historical events

### Visual Charts

- **chart_wheel.png**: Traditional circular chart wheel (requires PIL/Pillow)
- **chart_wheel.html**: Interactive chart wheel with zoom and pan (requires Plotly)

### Reports

- **chart_report.pdf**: Complete formatted PDF report with chart wheel (requires FPDF)

## Dependencies

### Required

- Python 3.7+ with `zoneinfo` support

### Optional (Recommended)

| Package | Purpose | Installation |
|---------|---------|--------------|
| pyswisseph | High-accuracy Swiss Ephemeris calculations | `pip install pyswisseph` |
| skyfield | NASA JPL ephemeris calculations (fallback) | `pip install skyfield` |
| matplotlib | Chart plotting (optional) | `pip install matplotlib` |
| plotly | Interactive HTML charts | `pip install plotly` |
| pillow | PNG chart wheel generation | `pip install pillow` |
| fpdf | PDF report generation | `pip install fpdf` |
| timezonefinder | Automatic timezone detection from coordinates | `pip install timezonefinder` |
| geopy | Location geocoding via Nominatim | `pip install geopy` |
| requests | Online features (Wikipedia events, geocoding) | `pip install requests` |
| python-dateutil | Enhanced date/time parsing | `pip install python-dateutil` |

## Project Structure

### Recommended Directory Structure

```
astrological-chart-generator/
├── sistema_complete.py          # Main application script
├── README.md                     # This file
├── LICENSE                       # License file
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore rules
│
├── data/                         # Data files (not tracked in git)
│   ├── keys.json                 # API keys (if needed)
│   ├── zipcodes.csv              # US zipcode database
│   ├── tz_cache.csv              # Timezone cache
│   ├── ephem_snapshot.json       # Offline ephemeris snapshot
│   ├── events_cache.json         # Historical events cache
│   └── ephe/                     # Swiss Ephemeris data files
│       ├── seas_18.se1
│       ├── semo_18.se1
│       └── sepl_18.se1
│
├── outputs/                      # Generated output files (not tracked)
│   ├── chart_verbose.txt
│   ├── chart_summary.txt
│   ├── chart_interpretation.txt
│   ├── astro_data_raw.json
│   ├── chart_wheel.png
│   ├── chart_wheel.html
│   └── chart_report.pdf
│
├── tests/                        # Unit tests
│   ├── __init__.py
│   ├── test_parsing.py
│   ├── test_calculations.py
│   ├── test_interpretations.py
│   └── test_outputs.py
│
├── docs/                         # Documentation
│   ├── API.md                    # API documentation
│   ├── ASTROLOGICAL_REFERENCE.md # Astrological interpretation guide
│   └── EXAMPLES.md               # Usage examples
│
└── scripts/                      # Utility scripts
    ├── download_ephemeris.py     # Download Swiss Ephemeris files
    ├── build_zipcode_db.py       # Build zipcode database
    └── cache_events.py           # Pre-cache historical events
```

### .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Data files
data/keys.json
data/zipcodes.csv
data/tz_cache.csv
data/ephem_snapshot.json
data/events_cache.json
data/ephe/

# Outputs
outputs/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
```

## Configuration

### Environment Variables

Optional environment variables for configuration:

```bash
export ASTRO_DATA_DIR="/path/to/data"       # Override data directory
export ASTRO_OUTPUT_DIR="/path/to/outputs" # Override output directory
export ASTRO_EPHE_PATH="/path/to/ephe"     # Swiss Ephemeris files
```

### Data Files

#### zipcodes.csv Format

```csv
zipcode,latitude,longitude,city,state
94102,37.7749,-122.4194,San Francisco,CA
10001,40.7506,-73.9971,New York,NY
```

#### events_cache.json Format

```json
{
  "08-15": [
    {
      "category": "births",
      "year": 1769,
      "text": "Napoleon Bonaparte, French military leader"
    }
  ]
}
```

## Examples

### Example 1: Basic Usage

```bash
python sistema_complete.py \
  --date "15/08/1990" \
  --time "14:30" \
  --tz "America/Los_Angeles" \
  --location "San Francisco, CA"
```

### Example 2: With Coordinates

```bash
python sistema_complete.py \
  --mode Ptolemy \
  --date "08/15/1990" \
  --time "2:30 PM PST" \
  --location "37.7749,-122.4194"
```

### Example 3: Offline Mode

```bash
python sistema_complete.py \
  --mode Paranoid \
  --date "15/08/1990" \
  --time "14:30 UTC" \
  --location "37.7749,-122.4194"
```

### Example 4: Interactive Mode

```bash
python sistema_complete.py --interactive
```

## Troubleshooting

### Swiss Ephemeris Not Found

**Problem**: "WARNING: Swiss Ephemeris (pyswisseph) not detected"

**Solution**: 
```bash
pip install pyswisseph
```

If installation fails, ensure you have build tools:
- **Linux**: `sudo apt-get install python3-dev`
- **macOS**: `xcode-select --install`
- **Windows**: Install Visual Studio Build Tools

### Ephemeris Data Missing

**Problem**: Calculations fail with ephemeris errors

**Solution**: Download Swiss Ephemeris files from https://www.astro.com/ftp/swisseph/ephe/ and place in `data/ephe/` directory. Required files:
- `seas_18.se1` (main planets)
- `semo_18.se1` (Moon)
- `sepl_18.se1` (outer planets)

### Geocoding Fails

**Problem**: Location cannot be resolved

**Solution**:
1. Check internet connection (required for Nominatim)
2. Use more specific location string (include country)
3. Try direct coordinates: `latitude,longitude`
4. Use zipcode if in US (requires zipcodes.csv)

### Timezone Detection Issues

**Problem**: Incorrect timezone for location

**Solution**:
1. Explicitly specify timezone with `--tz` argument
2. Install timezonefinder: `pip install timezonefinder`
3. Use IANA timezone name: `--tz "America/Los_Angeles"`

### PDF Generation Fails

**Problem**: PDF output not created

**Solution**:
```bash
pip install fpdf
```

Note: FPDF has limited font support. For production use, consider migrating to ReportLab.

## Future Enhancements

### High Priority

- **Aspect Calculations**: Implement comprehensive aspect analysis (conjunctions, trines, squares, oppositions, sextiles, quincunxes)
- **Aspect Interpretations**: Add detailed interpretations for all major and minor aspects
- **Arabic Parts**: Calculate and interpret Lot of Fortune, Lot of Spirit, and other Arabic Parts
- **Midpoints**: Implement midpoint calculations and interpretations
- **Transits**: Add current transit calculations and interpretations
- **Progressions**: Secondary progressions and solar arc calculations

### Medium Priority

- **Additional Bodies**: Calculate positions for Chiron, asteroids (Ceres, Pallas, Juno, Vesta), lunar nodes, Black Moon Lilith
- **Fixed Stars**: Prominent fixed star conjunctions and interpretations
- **Declination**: Calculate and interpret declination, parallel, and contraparallel aspects
- **Dignities**: Essential dignities (domicile, exaltation, detriment, fall) and accidental dignities
- **Retrograde Analysis**: Detect retrograde planets and provide interpretations
- **House Ruler Analysis**: Track house rulers through signs and houses
- **Synastry Mode**: Chart comparison for relationship analysis
- **Composite Charts**: Generate and interpret composite charts
- **Davison Charts**: Calculate and interpret Davison relationship charts

### Visualization Improvements

- **Enhanced Chart Wheels**: Color-coded planets by element, aspect lines, degree markers
- **Multiple Chart Display**: Side-by-side comparison charts for synastry
- **Aspect Grid**: Visual matrix of aspects between planets
- **Chart Animations**: Animated transit movements over natal chart
- **3D Solar System View**: Interactive 3D visualization of planetary positions

### Data and Interpretation

- **Sabian Symbols**: Add Sabian Symbol interpretations for each degree
- **Fixed Star Database**: Comprehensive fixed star positions and meanings
- **Asteroid Ephemeris**: Extended asteroid calculations
- **Additional House Systems**: Koch, Regiomontanus, Topocentric, Morinus
- **Configurable Orbs**: User-definable aspect orbs
- **Interpretation Customization**: Selectable interpretation styles (modern, traditional, psychological)

### Technical Improvements

- **Web Interface**: Flask/FastAPI web application with responsive design
- **Database Storage**: Store charts in SQLite/PostgreSQL for chart library
- **Batch Processing**: Process multiple charts from CSV input
- **API Endpoints**: RESTful API for chart generation
- **Configuration File**: YAML/JSON configuration for default settings
- **Localization**: Multi-language support for interpretations
- **Chart Templates**: Customizable report templates
- **Export Formats**: Additional export options (DOCX, LaTeX, Markdown)

### Testing and Quality

- **Unit Tests**: Comprehensive test coverage for all modules
- **Integration Tests**: End-to-end testing of chart generation
- **Validation Tests**: Verify calculations against known reference charts
- **Performance Optimization**: Caching, parallel processing for batch operations
- **Error Recovery**: Graceful degradation when optional features unavailable
- **Logging System**: Structured logging for debugging and monitoring

### User Experience

- **Chart Library**: Save and manage multiple charts
- **Search and Filter**: Find charts by criteria (date range, location, planet positions)
- **Comparison Tools**: Visual and textual chart comparisons
- **Print Layouts**: Optimized layouts for different paper sizes
- **Mobile App**: React Native mobile application
- **Chart Sharing**: Generate shareable links or embed codes

### Advanced Features

- **Electional Astrology**: Find optimal times for events
- **Horary Astrology**: Question-specific chart analysis
- **Mundane Astrology**: Political and world event charts
- **Relocation Charts**: Relocated angles for different locations
- **Harmonic Charts**: 5th, 7th, 9th harmonic calculations
- **Solar Returns**: Annual solar return charts
- **Lunar Returns**: Monthly lunar return charts
- **Progressed Moon Phase**: Calculate progressed lunation cycle

## License

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---
### Please note this is one of many side projects, dev is ongoing, testing is needed and will occur as time allows etc. 

Objective: to teach + aid in learning python scripting, API dev, GUI integration, zodiac systems and promote questions 

Acknowlegements: Anthropic Sonnet 4.5, Microsoft Copilot Think Deeper, Google Colab, Python

For questions, issues, or contributions fork it, submit a PR or email: wifiknight45@proton.me

Made with ✨ for the stars • Calculated with precision • Interpreted with wisdom

"As above, so below; as within, so without."
