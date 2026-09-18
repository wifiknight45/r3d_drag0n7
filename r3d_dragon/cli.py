"""CLI and interactive front-end."""
from __future__ import annotations

import argparse
import traceback

from . import deps
from .chart import generate_chart
from .config import DATA_DIR, OUTPUT_DIR
from .geo import OfflineDataError
from .ephemeris import EphemerisDownloadError
from .outputs_util import ensure_dirs
from .parsing import eprint


def try_install_hint(pkgs):
    eprint("Hint: pip install " + " ".join(pkgs))


def interactive_mode():
    print("r3d_dragon Interactive Mode")
    print("Modes: Nostradamus (Swiss Ephemeris), Ptolemy (Skyfield), Paranoid (offline local-only)")
    print("  Paranoid refuses network geocode and Skyfield downloads; use US zip or lat,lon + local ephemeris.")
    mode_choice = input("Choose mode [Nostradamus/Ptolemy/Paranoid] (default Nostradamus): ").strip() or "Nostradamus"
    date_format_pref = None
    df_choice = input(
        "Select date input preference for ambiguous (1) DD/MM/YYYY or (2) MM/DD/YYYY or (3) ask each time (default ask): "
    ).strip()
    if df_choice == "1":
        date_format_pref = "DMY"
    elif df_choice == "2":
        date_format_pref = "MDY"
    date_str = input("Enter date (DD/MM/YYYY or MM/DD/YYYY or YYYY-MM-DD): ").strip()
    time_str = input("Enter time (e.g., 17:15 PDT or 5:15 PM PDT or 00:15 UTC): ").strip()
    tz_hint = input("Optional timezone hint (e.g., PDT or America/Los_Angeles) or press Enter: ").strip() or None
    location = input("Location (City, State, Country OR zipcode OR lat,lon): ").strip()
    print("Generating chart...")
    try:
        generate_chart(
            mode_choice, date_str, time_str, tz_hint, location,
            date_format_pref=date_format_pref, interactive=True,
        )
    except (OfflineDataError, EphemerisDownloadError) as e:
        eprint("Offline/Paranoid error:", e)
    except Exception as e:
        eprint("Error generating chart:", e)
        traceback.print_exc()


def cli_mode(args):
    generate_chart(
        args.mode, args.date, args.time, args.tz, args.location,
        date_format_pref=args.datefmt, interactive=False,
    )


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="r3d_dragon — astronomical/astrological chart generator"
    )
    parser.add_argument("--mode", choices=["Nostradamus", "Ptolemy", "Paranoid"], default="Nostradamus")
    parser.add_argument("--date", help="Date: DD/MM/YYYY, MM/DD/YYYY, or YYYY-MM-DD")
    parser.add_argument("--time", help="Time e.g. '17:15 PDT' or '5:15 PM'")
    parser.add_argument("--tz", help="Timezone hint (PDT or America/Los_Angeles)")
    parser.add_argument("--location", help="City / US zip / lat,lon")
    parser.add_argument("--datefmt", choices=["DMY", "MDY"], help="Ambiguous date preference")
    parser.add_argument("--interactive", action="store_true", help="Interactive prompts")
    args = parser.parse_args(argv)
    ensure_dirs(DATA_DIR, OUTPUT_DIR)
    if args.mode == "Nostradamus" and not deps.HAS_PYSWISSEPH:
        eprint("Swiss Ephemeris (pyswisseph) not detected; Nostradamus may fall back.")
        try_install_hint(["pyswisseph", "skyfield", "timezonefinder", "geopy", "requests", "fpdf2", "pillow", "plotly"])
    if args.interactive or (not args.date and not args.time and not args.location):
        interactive_mode()
    else:
        if not (args.date and args.time and args.location):
            parser.error("For CLI mode supply --date --time --location or use --interactive")
        try:
            cli_mode(args)
        except (OfflineDataError, EphemerisDownloadError) as e:
            eprint(str(e))
            raise SystemExit(2) from e
