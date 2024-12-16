import os
import ephem
from astral import LocationInfo
from astral.sun import sun
import datetime

# Location coordinates for London
LATITUDE = 51.5074
LONGITUDE = -0.1278

def get_solar_times(lat, lon, date=None):
    """Calculate dawn, dusk, sunrise, and sunset."""
    if date is None:
        date = datetime.datetime.now()

    location = LocationInfo(latitude=lat, longitude=lon)
    solar_data = sun(location.observer, date=date)
    return {
        "dawn": solar_data["dawn"],
        "dusk": solar_data["dusk"],
        "sunrise": solar_data["sunrise"],
        "sunset": solar_data["sunset"],
    }

def get_lunar_data(lat, lon, date=None):
    """Calculate moonrise, moonset, and moon phase."""
    if date is None:
        date = datetime.datetime.now()

    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.lon = str(lon)
    observer.date = date

    moon = ephem.Moon(observer)
    return {
        "moonrise": ephem.localtime(observer.next_rising(ephem.Moon())),
        "moonset": ephem.localtime(observer.next_setting(ephem.Moon())),
        "moon_phase": moon.phase,  # 0 = New Moon, 50 = Full Moon
    }

def log_day_moon_light():
    """Log daily solar and lunar data to CSV."""
    date = datetime.datetime.now()
    solar_times = get_solar_times(LATITUDE, LONGITUDE, date)
    lunar_data = get_lunar_data(LATITUDE, LONGITUDE, date)

    # Prepare the log entry
    log_entry = {
        "Date": date.strftime("%Y-%m-%d"),
        "Dawn": solar_times["dawn"].strftime("%Y-%m-%d %H:%M:%S"),
        "Dusk": solar_times["dusk"].strftime("%Y-%m-%d %H:%M:%S"),
        "Moonrise": lunar_data["moonrise"].strftime("%Y-%m-%d %H:%M:%S"),
        "Moonset": lunar_data["moonset"].strftime("%Y-%m-%d %H:%M:%S"),
        "Moon Phase (%)": round(lunar_data["moon_phase"], 1),
    }

    # Log to CSV file
    log_file = os.path.expanduser("~/Documents/app/data/day-moon-light.csv")
    try:
        # Create the file with headers if it doesn't exist
        with open(log_file, "x") as file:
            file.write("Date,Dawn,Dusk,Moonrise,Moonset,Moon Phase (%)\n")
    except FileExistsError:
        pass  # File already exists

    # Append the log entry
    with open(log_file, "a") as file:
        file.write(",".join(str(log_entry[col]) for col in log_entry) + "\n")

    print("Day and moonlight data logged.")

if __name__ == "__main__":
    log_day_moon_light()

