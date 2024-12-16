import time
import os
import board
import neopixel
import subprocess
from datetime import datetime

# LED Ring Configuration
LED_PIN = board.D18       # GPIO pin connected to the pixels (must support PWM)
LARGE_RING_NUM = 24
SMALL_RING_NUM = 16
NUM_PIXELS = LARGE_RING_NUM+SMALL_RING_NUM  # Total number of LEDs
pixels = neopixel.NeoPixel(LED_PIN, NUM_PIXELS, brightness=0.5, auto_write=False)

def create_directory(base_dir, subfolder):
    """Create a subfolder within the base directory."""
    folder_path = os.path.join(base_dir, subfolder)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def attractive_light_on():
    """
    Simulates light with wavelengths attractive to moths (UV to blue-violet range).
    """
    violet = (148, 0, 211)  # Approx. 405-420 nm
    deep_blue = (0, 0, 255)  # Approx. 450 nm

    for i in range(LARGE_RING_NUM):
        if i % 2 == 0:
            pixels[i] = violet  # Set even LEDs to violet
        else:
            pixels[i] = deep_blue  # Set odd LEDs to deep blue

    print("Attractive light ON.")
    pixels.show()

def half_red_light():
    """
    Turns half the NeoPixel ring to red and the other half off.
    """
    red = (255, 0, 0)  # Red color
    off = (0, 0, 0)    # Off

    for i in range(LARGE_RING_NUM):
        if i < NUM_PIXELS // 2:
            pixels[i] = red  # First half red
        else:
            pixels[i] = off  # Second half off

    print("Half red light ON.")
    pixels.show()

def capture_images(duration_minutes, interval_seconds, save_dir):
    """
    Captures images at regular intervals for a specified duration.
    """
    total_iterations = int((duration_minutes * 60) / interval_seconds)

    for i in range(total_iterations):
        # Generate a timestamped filename
        timestamp = datetime.now().strftime("%H-%M-%S")
        image_path = os.path.join(save_dir, f"{timestamp}.jpg")

        # Capture the image using libcamera
        subprocess.run(["libcamera-jpeg", "-o", image_path], check=True)
        print(f"Captured image: {image_path}")

        # Wait for the next capture
        time.sleep(interval_seconds)

def main():
    # Create a directory for today's date
    date_str = datetime.now().strftime("%Y-%m-%d")
    base_dir = f"./{date_str}"
    os.makedirs(base_dir, exist_ok=True)

    # Attractive Light Phase
    attractive_light_dir = create_directory(base_dir, "attractive_light")
    attractive_light_on()
    capture_images(duration_minutes=30, interval_seconds=15, save_dir=attractive_light_dir)

    # Turn off lights after capturing
    pixels.fill((0, 0, 0))
    pixels.show()

    # Red Light Phase
    red_light_dir = create_directory(base_dir, "red_light")
    half_red_light()
    capture_images(duration_minutes=30, interval_seconds=15, save_dir=red_light_dir)

    # Turn off lights at the end
    pixels.fill((0, 0, 0))
    pixels.show()
    print("Session complete.")

if __name__ == "__main__":
    main()

