#!/usr/bin/env python3
# Photo Metadata Inspector
# Developed by Curlgit

import json
import os
import sys
import time
import threading
from pathlib import Path
from datetime import datetime

GREEN = "\033[92m"
BRIGHT_GREEN = "\033[1;92m"
DIM_GREEN = "\033[2;32m"
WHITE = "\033[97m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
CLEAR = "\033[2J\033[H"

BOLD = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
    "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭"
    "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇"
    "𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵"
)

APP_DIR = Path.home() / ".photo_metadata_inspector"
REPORT_FILE = APP_DIR / "last_report.json"

def styled(text):
    return str(text).translate(BOLD)

def clear():
    print(CLEAR, end="")

def line(char="━", width=54):
    print(BRIGHT_GREEN + char * width + RESET)

def header():
    clear()
    line()
    print(BRIGHT_GREEN + styled("PHOTO METADATA INSPECTOR").center(54) + RESET)
    print(GREEN + styled("DEVELOPED BY CURLGIT").center(54) + RESET)
    print(DIM_GREEN + styled("EXIF  •  GPS  •  CAMERA INFO").center(54) + RESET)
    line()

def pause():
    input(f"\n{DIM_GREEN}Press Enter to continue...{RESET}")

def spinner_task(message, duration=1.8):
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end = time.time() + duration
    i = 0
    while time.time() < end:
        print(f"\r{BRIGHT_GREEN}{frames[i % len(frames)]} {message}{RESET}", end="", flush=True)
        time.sleep(0.09)
        i += 1
    print(f"\r{BRIGHT_GREEN}✓ {message} - DONE{' ' * 12}{RESET}")

def readable_size(size):
    amount = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if amount < 1024 or unit == "TB":
            return f"{amount:.2f} {unit}"
        amount /= 1024
    return f"{size} B"

def safe_value(value):
    if value is None:
        return "Not available"
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8", errors="replace")
        except Exception:
            return repr(value)
    if isinstance(value, (tuple, list)):
        return ", ".join(safe_value(x) for x in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, default=str)
    return str(value)

def rational_to_float(value):
    try:
        if hasattr(value, "numerator") and hasattr(value, "denominator"):
            return float(value.numerator) / float(value.denominator)
        if isinstance(value, tuple) and len(value) == 2:
            return float(value[0]) / float(value[1])
        return float(value)
    except Exception:
        return None

def dms_to_decimal(dms, ref):
    try:
        degrees = rational_to_float(dms[0])
        minutes = rational_to_float(dms[1])
        seconds = rational_to_float(dms[2])
        if None in (degrees, minutes, seconds):
            return None
        decimal = degrees + minutes / 60 + seconds / 3600
        if str(ref).upper() in ("S", "W"):
            decimal = -decimal
        return decimal
    except Exception:
        return None

def get_exif(path):
    try:
        from PIL import Image, ExifTags
    except ImportError:
        return None, None, "Pillow is not installed."

    try:
        with Image.open(path) as image:
            raw = image.getexif()
            if not raw:
                return {}, {}, None

            tags = {ExifTags.TAGS.get(k, str(k)): v for k, v in raw.items()}
            gps = {}
            try:
                gps_raw = raw.get_ifd(ExifTags.IFD.GPSInfo)
                gps = {
                    ExifTags.GPSTAGS.get(k, str(k)): v
                    for k, v in gps_raw.items()
                }
            except Exception:
                pass

            return tags, gps, None
    except Exception as exc:
        return None, None, str(exc)

def get_gps(gps):
    if not gps:
        return None
    lat_ref = gps.get("GPSLatitudeRef")
    lat = gps.get("GPSLatitude")
    lon_ref = gps.get("GPSLongitudeRef")
    lon = gps.get("GPSLongitude")
    if lat is None or lon is None or lat_ref is None or lon_ref is None:
        return None
    latitude = dms_to_decimal(lat, lat_ref)
    longitude = dms_to_decimal(lon, lon_ref)
    if latitude is None or longitude is None:
        return None
    return {
        "latitude": round(latitude, 7),
        "longitude": round(longitude, 7),
        "altitude": safe_value(gps.get("GPSAltitude")),
        "timestamp": safe_value(gps.get("GPSTimeStamp")),
        "datestamp": safe_value(gps.get("GPSDateStamp")),
        "map_url": f"https://www.openstreetmap.org/?mlat={latitude}&mlon={longitude}#map=16/{latitude}/{longitude}"
    }

def format_datetime(value):
    if value is None:
        return "Not available"
    try:
        return datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "Not available"

def analyze_photo(raw_path):
    # All validation and processing live inside one try/finally.
    # This prevents instant menu-return on bad paths or metadata errors.
    try:
        cleaned_path = raw_path.strip().strip('"').strip("'")
        if not cleaned_path:
            print(f"\n{YELLOW}No path entered.{RESET}")
            return

        cleaned_path = os.path.expandvars(os.path.expanduser(cleaned_path))
        path = Path(cleaned_path)

        if not path.exists():
            print(f"\n{RED}✗ File not found. Check the path and try again.{RESET}")
            print(f"{YELLOW}Path received: {cleaned_path}{RESET}")
            print(f"{DIM_GREEN}Example: /storage/emulated/0/DCIM/Camera/photo.jpg{RESET}")
            return

        if not path.is_file():
            print(f"\n{RED}✗ The path is not a file.{RESET}")
            return

        spinner_task("Reading photo file")

        stat = path.stat()
        with path.open("rb") as f:
            signature = f.read(16)

        tags, gps_tags, exif_error = get_exif(path)

        image_width = image_height = None
        image_format = path.suffix.lstrip(".").upper() or "Unknown"
        try:
            from PIL import Image
            with Image.open(path) as im:
                image_width, image_height = im.size
                image_format = im.format or image_format
        except ImportError:
            pass
        except Exception as image_error:
            if not exif_error:
                exif_error = str(image_error)

        gps = get_gps(gps_tags or {})
        report = {
            "file": {
                "name": path.name,
                "path": str(path.resolve()),
                "format": image_format,
                "size": readable_size(stat.st_size),
                "size_bytes": stat.st_size,
                "resolution": f"{image_width} x {image_height}" if image_width else "Not available",
                "modified": format_datetime(stat.st_mtime),
                "header_bytes_hex": signature.hex()
            },
            "camera": {},
            "gps": gps,
            "metadata": {},
            "note": "GPS and camera information are shown only if present in the file."
        }

        if tags:
            camera_keys = [
                "Make", "Model", "LensModel", "LensMake", "Software",
                "DateTime", "DateTimeOriginal", "DateTimeDigitized",
                "ExposureTime", "FNumber", "ISOSpeedRatings", "PhotographicSensitivity",
                "FocalLength", "Flash", "WhiteBalance", "Orientation",
                "ExposureProgram", "MeteringMode"
            ]
            for key in camera_keys:
                if key in tags:
                    report["camera"][key] = safe_value(tags[key])
            report["metadata"] = {str(k): safe_value(v) for k, v in tags.items()}
            if gps_tags:
                report["metadata"]["GPSInfo"] = {
                    str(k): safe_value(v) for k, v in gps_tags.items()
                }

        APP_DIR.mkdir(parents=True, exist_ok=True)
        REPORT_FILE.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        header()
        print(f"{BRIGHT_GREEN}{styled('PHOTO ANALYSIS REPORT')}{RESET}")
        line("─")
        show_section("FILE INFORMATION", [
            ("Filename", report["file"]["name"]),
            ("Format", report["file"]["format"]),
            ("File size", report["file"]["size"]),
            ("Resolution", report["file"]["resolution"]),
            ("Modified", report["file"]["modified"]),
            ("Path", report["file"]["path"]),
        ])
        show_section("CAMERA INFORMATION", [
            ("Make", report["camera"].get("Make", "Not available")),
            ("Model", report["camera"].get("Model", "Not available")),
            ("Lens", report["camera"].get("LensModel", "Not available")),
            ("Software", report["camera"].get("Software", "Not available")),
            ("Date taken", report["camera"].get("DateTimeOriginal", report["camera"].get("DateTime", "Not available"))),
            ("ISO", report["camera"].get("ISOSpeedRatings", report["camera"].get("PhotographicSensitivity", "Not available"))),
            ("Aperture", report["camera"].get("FNumber", "Not available")),
            ("Shutter speed", report["camera"].get("ExposureTime", "Not available")),
            ("Focal length", report["camera"].get("FocalLength", "Not available")),
            ("Flash", report["camera"].get("Flash", "Not available")),
        ])

        if gps:
            show_section("GPS LOCATION", [
                ("Latitude", gps["latitude"]),
                ("Longitude", gps["longitude"]),
                ("Altitude", gps["altitude"]),
                ("GPS date", gps["datestamp"]),
                ("GPS time", gps["timestamp"]),
                ("Map URL", gps["map_url"]),
            ])
            print(f"{GREEN}GPS data found in the photo metadata.{RESET}")
        else:
            show_section("GPS LOCATION", [("Status", "GPS DATA NOT FOUND")])
            print(f"{YELLOW}No complete GPS coordinates were found in this photo's metadata.{RESET}")

        show_section("METADATA SUMMARY", [
            ("EXIF tags found", len(report["metadata"])),
            ("Saved report", str(REPORT_FILE)),
            ("Photo modified", "No"),
        ])
        if exif_error:
            print(f"{YELLOW}Metadata reader note: {exif_error}{RESET}")
        print(f"\\n{DIM_GREEN}Original photo was not modified.{RESET}")

    except PermissionError:
        print(f"\\n{RED}✗ Permission denied. Check Termux storage access.{RESET}")
        print(f"{YELLOW}Try: termux-setup-storage{RESET}")
    except Exception as exc:
        print(f"\\n{RED}✗ Analysis failed: {type(exc).__name__}: {exc}{RESET}")
    finally:
        # Always pause after option 1, even for missing paths/errors.
        try:
            input(f"\\n{DIM_GREEN}Press Enter to return to the main menu...{RESET}")
        except (EOFError, KeyboardInterrupt):
            print()

def show_section(title, rows):
    print(f"\n{BRIGHT_GREEN}{styled(title)}{RESET}")
    line("·", 54)
    for key, value in rows:
        value = safe_value(value)
        print(f"{GREEN}{key:<17}{RESET} {WHITE}{value}{RESET}")

def view_last_report():
    header()
    if not REPORT_FILE.exists():
        print(f"{YELLOW}No saved report yet. Analyze a photo first.{RESET}")
        return
    try:
        data = json.loads(REPORT_FILE.read_text(encoding="utf-8"))
        print(f"{BRIGHT_GREEN}{styled('LAST REPORT')}{RESET}")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as exc:
        print(f"{RED}Could not read report: {exc}{RESET}")

def about():
    header()
    print(f"{BRIGHT_GREEN}{styled('ABOUT THIS TOOL')}{RESET}")
    print(f"{GREEN}Reads available photo metadata locally on your device.")
    print("No photo upload. Original photo is not modified.")
    print("GPS is displayed only when coordinates are embedded.")
    print("Metadata can be missing, edited, or inaccurate.")
    print(f"\nReports folder: {APP_DIR}{RESET}")

def main():
    while True:
        header()
        print(f"{BRIGHT_GREEN}[1] {styled('ANALYZE PHOTO METADATA')}{RESET}")
        print(f"{GREEN}[2] {styled('VIEW LAST REPORT')}{RESET}")
        print(f"{GREEN}[3] {styled('ABOUT')}{RESET}")
        print(f"{GREEN}[4] {styled('EXIT')}{RESET}")
        line("─")
        choice = input(f"{BRIGHT_GREEN}{styled('SELECT AN OPTION')}: {RESET}").strip()

        if choice == "1":
            print(f"\n{GREEN}{styled('ENTER PHOTO FILE PATH')}{RESET}")
            print(f"{DIM_GREEN}Example: /sdcard/DCIM/Camera/IMG_1234.jpg{RESET}")
            # Re-prompt if the terminal/keyboard submits an empty line.
            # Do not call analyze_photo with an empty string.
            while True:
                path = input(f"{BRIGHT_GREEN}Path: {RESET}")
                path = path.strip().strip('"').strip("'")
                if path:
                    break
                print(f"{YELLOW}Path was empty. Paste the full path and press Enter again.{RESET}")

            analyze_photo(path)
        elif choice == "2":
            view_last_report()
            pause()
        elif choice == "3":
            about()
            pause()
        elif choice == "4":
            print(f"{BRIGHT_GREEN}Goodbye! Thanks for using Curlgit tools.{RESET}")
            break
        else:
            print(f"{RED}Invalid option. Choose 1-4.{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{GREEN}Exiting safely.{RESET}")
        sys.exit(0)
