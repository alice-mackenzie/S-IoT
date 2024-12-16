import os
import time
import requests
import board
import busio
import Adafruit_DHT
import adafruit_tcs34725
from datetime import datetime

# Weather API Configuration
API_KEY = "REMOVED FOR PRIVACY"  # Replace with your API key
LATITUDE = 51.5074 
LONGITUDE = -0.1278 

# DHT Sensor Configuration
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4  # GPIO pin for the DHT sensor

# RGB Lux Sensor Initialization
i2c = busio.I2C(board.SCL, board.SDA)
rgb_sensor = adafruit_tcs34725.TCS34725(i2c)

# Log file path
LOG_FILE = os.path.expanduser("~/Documents/app/data/weather_data_log.csv")

def get_weather_data(api_key, lat, lon):
    """Fetch weather data from OpenWeatherMap API."""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric",
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        rainfall = data.get("rain", {}).get("1h", 0)
        cloud_cover = data.get("clouds", {}).get("all", 0)
        description = data.get("weather", [{}])[0].get("description", "No description")

        return {
            "rainfall": rainfall,
            "cloud_cover": cloud_cover,
            "description": description,
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

def read_temp_humid():
    """Read temperature and humidity from the DHT sensor."""
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    
    # Check if readings are valid
    if humidity is None or temperature is None:
        print("Failed to get DHT reading.")
        return None
        
    # Check physical limits
    if temperature < -40 or temperature > 80:
        print(f"Error: Temperature reading {temperature}°C is outside physical limits (-40°C to 80°C)")
        return None
        
    if humidity < 0 or humidity > 100:
        print(f"Error: Humidity reading {humidity}% is outside physical limits (0% to 100%)")
        return None
        
    return {"temperature": temperature, "humidity": humidity}

def read_rgb_lux():
    """Read RGB and lux data from the TCS34725 sensor with basic physical limits validation."""
    try:
        r, g, b = rgb_sensor.color_rgb_bytes
        color_temp = rgb_sensor.color_temperature
        lux = rgb_sensor.lux
        
        # Check RGB values (0-255)
        for color, value in [('Red', r), ('Green', g), ('Blue', b)]:
            if value < 0 or value > 255:
                print(f"Error: {color} value {value} is outside valid range (0-255)")
                return None
        
        # Check color temperature (typical range 1500K-15000K)
        if color_temp < 1500 or color_temp > 15000:
            print(f"Error: Color temperature {color_temp}K is outside typical range (1500K-15000K)")
            return None
            
        # Check lux (0-65535 for 16-bit sensor)
        if lux < 0 or lux > 65535:
            print(f"Error: Lux value {lux} is outside valid range (0-65535)")
            return None
            
        return {
            "red": r,
            "green": g,
            "blue": b,
            "color_temperature": color_temp,
            "lux": lux,
        }
    except Exception as e:
        print(f"Error reading RGB/Lux sensor: {e}")
        return None

def log_data():
    """Fetch and log weather, DHT, and RGB/Lux data."""
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Fetch data
    weather_data = get_weather_data(API_KEY, LATITUDE, LONGITUDE)
    dht_data = read_temp_humid()
    rgb_data = read_rgb_lux()

    # Prepare log entry
    log_entry = [timestamp]
    if weather_data:
        log_entry += [weather_data["rainfall"], weather_data["cloud_cover"], weather_data["description"]]
    else:
        log_entry += ["N/A", "N/A", "N/A"]

    if dht_data:
        log_entry += [dht_data["temperature"], dht_data["humidity"]]
    else:
        log_entry += ["N/A", "N/A"]

    if rgb_data:
        log_entry += [
            rgb_data["red"], rgb_data["green"], rgb_data["blue"],
            rgb_data["color_temperature"], rgb_data["lux"]
        ]
    else:
        log_entry += ["N/A", "N/A", "N/A", "N/A", "N/A"]
    
    # Write log entry to file
    with open(LOG_FILE, "a") as f:
        f.write(",".join(map(str, log_entry)) + "\n")

    print(f"Data logged at {timestamp}")

def main():
    """Main function to log data every hour."""
    # Initialize log file with headers if not exists
    try:
        with open(LOG_FILE, "x") as f:
            f.write("Timestamp,Rainfall (mm),Cloud Cover (%),Weather Description,Temperature (C),"
                    "Humidity (%),Red,Green,Blue,Color Temperature (K),Lux\n")
    except FileExistsError:
        pass  # File already exists

    # Log data
    log_data()


if __name__ == "__main__":
    main()


