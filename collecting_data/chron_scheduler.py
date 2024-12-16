import os
from datetime import datetime, timedelta
from astral import LocationInfo
from astral.sun import sun
from crontab import CronTab

def schedule_dawn_dusk():
    """Schedule moth collection for next dawn and dusk using cron"""
    # Initialize location
    location = LocationInfo(latitude=51.5074, longitude=0.1278)  # Update with your coordinates
    
    # Get next dawn and dusk times
    today = datetime.now()
    s = sun(location.observer, date=today)
    dawn = s["dawn"]
    dusk = s["dusk"]
    
    # Convert to timezone-naive for comparison
    current_time = datetime.now()
    naive_dusk = dusk.replace(tzinfo=None)
    
    # If we're past today's dusk, get tomorrow's times
    if current_time > naive_dusk:  # Fixed this line
        tomorrow = today + timedelta(days=1)
        s = sun(location.observer, date=tomorrow)
        dawn = s["dawn"]
        dusk = s["dusk"]
    
    # Access current user's crontab
    cron = CronTab(user=True)
    
    # Remove any existing moth collection jobs
    cron.remove_all(comment='moth_collection')
    
    # Create dawn job
    dawn_job = cron.new(
        command='python3 /home/moth/Documents/collecting_data/attractive_mode.py',  # Updated path
        comment='moth_collection'
    )
    dawn_job.hour.on(dawn.hour)
    dawn_job.minute.on(dawn.minute)
    
    # Create dusk job
    dusk_job = cron.new(
        command='python3 /home/moth/Documents/collecting_data/attractive_mode.py',  # Updated path
        comment='moth_collection'
    )
    dusk_job.hour.on(dusk.hour)
    dusk_job.minute.on(dusk.minute)
    
    # Save the cron jobs
    cron.write()
    
    print(f"Scheduled moth collection for:")
    print(f"Dawn: {dawn.strftime('%H:%M')}")
    print(f"Dusk: {dusk.strftime('%H:%M')}")

if __name__ == "__main__":  # Fixed the name == main line
    schedule_dawn_dusk()
