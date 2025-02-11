# S-IoT

Please move the collect_weather_data.py file into the collecting_data directory when you pull. It went to the wrong repo on upload.

# System Overview
This project consists of several interconnected components:

- Automated moth attraction using LED arrays
- Image capture and computer vision-based moth detection
- Environmental data collection (temperature, humidity, light)
- Solar/lunar phase tracking
- Web-based visualization dashboard

# Hardware Requirements

- Raspberry Pi 2 W Zero
- Camera module compatible with Raspberry Pi, Pi Camera Module 3 NoIR is reccomended
- NeoPixel LED rings:
-- 24-LED ring (Ring 1)
-- 16-LED ring (Ring 2)

- DHT11 Temperature & Humidity Sensor
- TCS34725 RGB & Lux Sensor
- Appropriate power supply for LED rings


# System dependencies
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    libatlas-base-dev \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7 \
    libtiff5 \
    libcamera-dev


# Installation:
https://github.com/alice-mackenzie/S-IoT
cd S-IoT

Install system dependencies

# Hardware connections:

- Connect LED rings to GPIO18
- Connect DHT11 sensor to GPIO4
- Connect TCS34725 to I2C bus
- Mount and configure camera module


# Configure location settings:

Update latitude/longitude in :
- chron_scheduler.py
- get_weather_data.py
- log_sun_moon_times.py
Set local timezone in system settings


# Data Collection
The system operates automatically based on dawn/dusk times:

Attraction Phase:

LED arrays activate before dawn/dusk
Images captured every 15 seconds
Environmental data logged continuously

Red Light Phase:

Transition to red light to observe departures
Continued image capture and analysis

# Web Dashboard

This shows: 
- Real-time environmental conditions
- Moth activity visualizations
- Historical data analysis

# Acknowledgments

Built using the Flask web framework and Plotly.js for visualizations
Computer vision components powered by OpenCV
