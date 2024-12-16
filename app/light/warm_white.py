# warm_white.py
import board
import neopixel

# Configuration
NUM_LEDS_RING1 = 24
NUM_LEDS_RING2 = 16
TOTAL_LEDS = NUM_LEDS_RING1 + NUM_LEDS_RING2
DATA_PIN = board.D18

# Initialize the LED strip
pixels = neopixel.NeoPixel(DATA_PIN, TOTAL_LEDS, brightness=0.5, auto_write=False)

def warm_white():
    # Warm white color (RGB values for a warm white)
    warm_white_color = (200, 130,80)  # Slightly yellow-tinted white
    
    # Set only Ring 2 LEDs (the last 16 LEDs)
    for i in range(NUM_LEDS_RING1, TOTAL_LEDS):
        pixels[i] = warm_white_color
    
    pixels.show()

if __name__ == "__main__":
    warm_white()
